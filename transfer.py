# ============================================================
# CHUYỂN QUYỀN SỞ HỮU FILE HÀNG LOẠT (Gmail thường, A -> B)
# Chạy 2 lượt trên Colab:
#   Lượt 1: đăng nhập tài khoản A  -> MODE = "REQUEST"  (gửi yêu cầu)
#   Lượt 2: đăng nhập tài khoản B  -> MODE = "ACCEPT"   (chấp nhận)
# Chỉ chuyển FILE (Drive không cho chuyển quyền sở hữu thư mục).
# ============================================================
import time
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------- CẤU HÌNH ----------
MODE = "REQUEST"                       # "REQUEST" (chạy ở A) hoặc "ACCEPT" (chạy ở B)
FOLDER_ID = "DAN_ID_THU_MUC_O_DAY"     # thư mục chứa các file cần chuyển (quét cả thư mục con)
EMAIL_A = "a@gmail.com"   # tài khoản đang SỞ HỮU file (người up)
EMAIL_B = "b@gmail.com"            # tài khoản sẽ NHẬN quyền sở hữu
MIN_SIZE_MB = 0                        # chỉ chuyển file >= X MB (0 = tất cả)
DRY_RUN = True                         # True = chỉ liệt kê. Kiểm tra xong đổi thành False
# ------------------------------

auth.authenticate_user()
drive = build("drive", "v3")
FOLDER = "application/vnd.google-apps.folder"


def call(req, retries=5):
    for i in range(retries):
        try:
            return req.execute()
        except HttpError as e:
            if e.resp.status in (429, 500, 502, 503, 504) or (
                e.resp.status == 403 and "rateLimit" in str(e)
            ):
                time.sleep(2 ** i)
                continue
            raise
    raise RuntimeError("Thử lại quá số lần cho phép")


def walk(folder_id, path=""):
    """Duyệt đệ quy, trả về mọi file (không phải thư mục) trong cây thư mục."""
    token = None
    while True:
        res = call(drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageToken=token, pageSize=1000,
            fields="nextPageToken, files(id,name,mimeType,size,ownedByMe,owners(emailAddress))",
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ))
        for f in res.get("files", []):
            if f["mimeType"] == FOLDER:
                yield from walk(f["id"], f"{path}/{f['name']}")
            else:
                f["path"] = f"{path}/{f['name']}"
                yield f
        token = res.get("nextPageToken")
        if not token:
            break


def owner_email(f):
    owners = f.get("owners") or [{}]
    return owners[0].get("emailAddress", "").lower()


def request_transfer(f):
    """A gửi yêu cầu chuyển quyền cho B (pendingOwner)."""
    def find_b():
        perms = call(drive.permissions().list(
            fileId=f["id"], fields="permissions(id,emailAddress,role,pendingOwner)",
            supportsAllDrives=True,
        )).get("permissions", [])
        return next((p for p in perms
                     if p.get("emailAddress", "").lower() == EMAIL_B.lower()), None)

    # 1) B đã có quyền sẵn -> cập nhật thẳng permission đó
    p = find_b()
    if p:
        try:
            call(drive.permissions().update(
                fileId=f["id"], permissionId=p["id"],
                body={"role": "writer", "pendingOwner": True},
                supportsAllDrives=True,
            ))
        except HttpError:
            pass
    # 2) Chưa có hoặc cập nhật không được -> tạo quyền trực tiếp
    p = find_b()
    if not p or not p.get("pendingOwner"):
        try:
            call(drive.permissions().create(
                fileId=f["id"],
                body={"type": "user", "role": "writer",
                      "emailAddress": EMAIL_B, "pendingOwner": True},
                sendNotificationEmail=False, supportsAllDrives=True,
            ))
        except HttpError:
            pass
    # 3) Kiểm tra lại: cờ pendingOwner thật sự đã được áp dụng chưa
    p = find_b()
    return bool(p and p.get("pendingOwner"))


def accept_transfer(f, my_perm_id):
    """B chấp nhận: nâng quyền của chính mình lên owner."""
    call(drive.permissions().update(
        fileId=f["id"], permissionId=my_perm_id,
        body={"role": "owner"}, transferOwnership=True,
        supportsAllDrives=True,
    ))


# ---------------- CHẠY ----------------
me = call(drive.about().get(fields="user(emailAddress,permissionId)"))["user"]
print(f"Đang đăng nhập: {me['emailAddress']}  |  MODE = {MODE}")

expected = EMAIL_A if MODE == "REQUEST" else EMAIL_A  # file phải đang thuộc A ở cả 2 lượt
if MODE == "REQUEST" and me["emailAddress"].lower() != EMAIL_A.lower():
    raise SystemExit("Lượt REQUEST phải đăng nhập bằng tài khoản A.")
if MODE == "ACCEPT" and me["emailAddress"].lower() != EMAIL_B.lower():
    raise SystemExit("Lượt ACCEPT phải đăng nhập bằng tài khoản B.")

ok = skip = fail = 0
total_bytes = 0
for f in walk(FOLDER_ID):
    size = int(f.get("size", 0))
    if size < MIN_SIZE_MB * 1024 * 1024:
        continue
    if owner_email(f) != EMAIL_A.lower():
        continue  # chỉ xử lý file đang thuộc A
    if f.get("mimeType", "").startswith("application/vnd.google-apps"):
        continue  # Google Docs/Sheets không tính dung lượng, bỏ qua
    label = f"{f['path']}  ({size / 1024**3:.2f} GB)"

    if DRY_RUN:
        print(f"[DRY ] {label}")
        ok += 1
        total_bytes += size
        continue
    try:
        if MODE == "REQUEST":
            if not request_transfer(f):
                print(f"[FAIL] {label}: Drive không áp dụng yêu cầu chuyển chủ (pendingOwner)")
                fail += 1
                continue
        else:
            accept_transfer(f, me["permissionId"])
        print(f"[ OK ] {label}")
        ok += 1
        total_bytes += size
    except HttpError as e:
        msg = str(e)
        if MODE == "ACCEPT" and ("pendingOwner" in msg or "not pending" in msg.lower()):
            print(f"[SKIP] {label} (chưa có yêu cầu từ A)")
            skip += 1
        else:
            print(f"[FAIL] {label}: {msg[:180]}")
            fail += 1

print(f"\nXong. Thành công/liệt kê: {ok} file ({total_bytes / 1024**3:.2f} GB) | bỏ qua: {skip} | lỗi: {fail}")
