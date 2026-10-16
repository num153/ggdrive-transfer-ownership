# Drive Transfer Ownership

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google Drive API](https://img.shields.io/badge/Google%20Drive-API%20v3-4285F4?logo=googledrive&logoColor=white)](https://developers.google.com/drive/api)

**English** | [Tiếng Việt](#tiếng-việt)

## English

A Google Colab script that bulk-transfers **file ownership** in a Google Drive folder from account A to account B (personal Gmail). No download, no re-upload, no duplicate files. Storage quota moves from A to B.

**Why:** Drive counts storage by *file owner*, not folder owner. Files uploaded by A into B's folder still use A's quota.

### Requirements
- Two Google accounts: A (current owner) and B (new owner)
- B has access to the folder (Editor or higher) and enough free storage
- Google Colab (nothing to install)

### Usage
1. Copy `drive_transfer_ownership_colab.py` into a Colab cell and edit the config:
   ```python
   MODE = "REQUEST"            # "REQUEST" (run as A) or "ACCEPT" (run as B)
   FOLDER_ID = "..."           # ID only: drive.google.com/drive/folders/<ID>
   EMAIL_A = "a@gmail.com"     # current owner
   EMAIL_B = "b@gmail.com"     # new owner
   MIN_SIZE_MB = 0             # only files >= X MB
   DRY_RUN = True              # True = list only to check, change nothing
   ```
2. **Run as A** with `MODE = "REQUEST"`. Run with `DRY_RUN = True` first, then `False`.
3. **Run as B** (incognito window or another Chrome profile) with `MODE = "ACCEPT"`. Dry run first, then `False`.
4. Check: A's storage drops, files are now owned by B.

### Notes
- Files only; Drive cannot transfer folder ownership.
- Only files owned by A are processed. Google Docs/Sheets/Slides are skipped (no quota).
- `WARNING ... timeout` / `rateLimitExceeded` messages are normal (auto-retry).
- If ACCEPT shows `insufficientFilePermissions`, re-run REQUEST as A, wait a few minutes, then ACCEPT again.

---

## Tiếng Việt

Script Google Colab chuyển **quyền sở hữu file hàng loạt** trong một thư mục Google Drive từ tài khoản A sang tài khoản B (Gmail cá nhân). Không tải xuống, không upload lại, không nhân đôi file. Dung lượng được chuyển từ A sang B.

**Lý do:** Drive tính dung lượng theo *chủ sở hữu file*, không theo chủ thư mục. File A upload vào thư mục của B vẫn tốn dung lượng của A.

### Yêu cầu
- Hai tài khoản Google: A (đang sở hữu) và B (sẽ nhận)
- B có quyền truy cập thư mục (Người chỉnh sửa trở lên) và còn đủ dung lượng
- Google Colab (không cần cài thêm gì)

### Cách dùng
1. Dán `drive_transfer_ownership_colab.py` vào một ô code trên Colab và sửa cấu hình:
   ```python
   MODE = "REQUEST"            # "REQUEST" (chạy ở A) hoặc "ACCEPT" (chạy ở B)
   FOLDER_ID = "..."           # chỉ lấy ID: drive.google.com/drive/folders/<ID>
   EMAIL_A = "a@gmail.com"     # chủ sở hữu hiện tại
   EMAIL_B = "b@gmail.com"     # người nhận
   MIN_SIZE_MB = 0             # chỉ chuyển file >= X MB
   DRY_RUN = True              # True = chỉ liệt kê để kiểm tra, chưa thay đổi gì
   ```
2. **Chạy bằng A** với `MODE = "REQUEST"`. Chạy `DRY_RUN = True` trước, đúng thì đổi `False`.
3. **Chạy bằng B** (cửa sổ ẩn danh hoặc profile Chrome khác) với `MODE = "ACCEPT"`. Chạy thử trước, rồi `False`.
4. Kiểm tra: dung lượng A giảm, file giờ thuộc về B.

### Lưu ý
- Chỉ chuyển được file, Drive không cho chuyển quyền sở hữu thư mục.
- Chỉ xử lý file đang thuộc A. Google Docs/Sheets/Slides bị bỏ qua (không tính dung lượng).
- Dòng `WARNING ... timeout` / `rateLimitExceeded` là bình thường (tự thử lại).
- Nếu ACCEPT báo `insufficientFilePermissions`, chạy lại REQUEST ở A, đợi vài phút rồi ACCEPT lại.
