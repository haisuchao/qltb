# 🤖 HƯỚNG DẪN SỬ DỤNG BOT QUẢN LÝ TRỰC BAN (QLTB)

Chào mừng bạn đến với hệ thống quản lý lịch trực ban tự động qua Telegram. Hệ thống giúp tra cứu lịch, đổi ca trực, tìm kiếm cá nhân và tự động nhắc việc hàng ngày.

---

## 🛠 1. CÀI ĐẶT HỆ THỐNG

### Bước 1: Chuẩn bị môi trường
Máy tính cần cài đặt **Python 3.8** trở lên.

1. Tải mã nguồn về máy.
2. Mở Terminal/Command Prompt tại thư mục dự án và cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```

### Bước 2: Cấu hình Bot Telegram
1. Chat với [@BotFather](https://t.me/botfather) trên Telegram.
2. Gửi lệnh `/newbot`, đặt tên cho bot và nhận **API Token**.
3. Mở file `config.py`, dán Token vào dòng:
   ```python
   TELEGRAM_BOT_TOKEN = "DÁN_TOKEN_CỦA_BẠN_VÀO_ĐÂY"
   ```

### Bước 3: Chuẩn bị file Excel Lịch trực (Template)
Hệ thống yêu cầu file Excel phải đúng định dạng để có thể đọc được dữ liệu.

1. **Cấu trúc file**: 
   - Tên file mở rộng là `.xlsx`.
   - Mỗi tháng là một **Sheet** riêng biệt. Tên Sheet phải đặt theo định dạng `m-yyyy` (Ví dụ: `1-2026`, `2-2026`,...).
   - **Cấu trúc cột** (Bắt đầu từ dòng số 4):
     - Cột A: Ngày (VD: 01/01/2026)
     - Cột B: Thứ
     - Cột C: Trực sáng (Tên cán bộ)
     - Cột D: Trực chiều (Tên cán bộ)
     - Cột E: Lãnh đạo trực (Tên cán bộ)

2. **Cách tạo nhanh**:
   - Bạn có thể tạo file mới và copy cấu trúc như hình dưới đây:
   
   | Ngày | Thứ | Trực sáng | Trực chiều | Lãnh đạo |
   | :--- | :--- | :--- | :--- | :--- |
   | 01/01/2026 | Thứ Năm | Nguyễn Văn A | Lê Văn B | Trần Văn C |
   | 02/01/2026 | Thứ Sáu | Phạm Văn D | ... | ... |

   > [!TIP]
   > Bạn có thể tham khảo file mẫu có sẵn tại: `lich-truc-ban/LichTrucBan_2025-2026.xlsx`

   > [!IMPORTANT]
   > Dữ liệu cán bộ phải bắt đầu từ **Dòng 5** trở đi (Dòng 4 là tiêu đề cột).

3. **Tải lên Google Drive**:
   - Truy cập [Google Drive](https://drive.google.com/).
   - Nhấn **Mới** -> **Tải tệp lên** -> Chọn file Excel vừa tạo.
   - Chuột phải vào file vừa tải lên -> **Chia sẻ** -> **Chia sẻ**.
   - Copy Email của Service Account (từ bước 4) vào ô người nhận -> Chọn quyền **Người chỉnh sửa (Editor)** -> **Gửi**.
   - Copy **ID file** từ thanh địa chỉ (đoạn mã nằm giữa `/d/` và `/edit`) và dán vào `config.py`.

### Bước 4: Cấu hình Google Drive (Bắt buộc để đồng bộ)
1. Để Bot có thể đọc lịch từ file Excel trên Drive, bạn cần file `credentials.json`.
2. Truy cập [Google Cloud Console](https://console.cloud.google.com/), tạo project và bật **Google Drive API**.
3. Tạo **Service Account**, tải Key dưới dạng JSON, đổi tên thành `credentials.json` và chép vào thư mục gốc của Bot.
4. Copy Email của Service Account và **Chia sẻ quyền Chỉnh sửa (Editor)** cho file Excel lịch trực của bạn trên Google Drive.
5. Lấy ID file Excel (đoạn mã trên thanh địa chỉ giữa `/d/` và `/edit`) và dán vào `config.py`:
   ```python
   DRIVE_FILE_ID = "ID_FILE_EXCEL_CỦA_BẠN"
   ```

---

## 📋 2. CÁC LỆNH ĐIỀU KHIỂN BOT

Sử dụng trực tiếp trong khung chat với Bot:

| Lệnh | Mô tả | Ví dụ |
| :--- | :--- | :--- |
| `/start` | Khởi động Bot và xem menu lệnh | `/start` |
| `/today` | Xem lịch trực hôm nay nhanh | `/today` |
| `/tomorrow` | Xem lịch trực ngày mai nhanh | `/tomorrow` |
| `/check` | Tra cứu lịch của một ngày bất kỳ | `/check 30/01/2026` |
| `/search` | Tìm toàn bộ lịch trực của bạn trong tháng | `/search Nguyễn Văn A` |
| `/register` | Đăng ký tài khoản để nhận thông báo tự động | `/register Nguyễn Văn A` |
| `/change` | Thay đổi người trực cho một ca cụ thể | `/change 30/01/2026 sáng "Lê Văn B" "Đi công tác"` |
| `/swap` | Hoán đổi ca trực giữa 2 người (2 ca bất kỳ) | `/swap 01/02/2026 sáng 02/02/2026 chiều` |
| `/help` | Xem hướng dẫn sử dụng nhanh | `/help` |

> [!TIP]
> **Lưu ý về Họ tên:** Khi nhập tên người dùng trong lệnh `/change`, nếu tên có khoảng trắng, bạn nên để trong dấu ngoặc kép (Ví dụ: `"Nguyễn Văn A"`).

---

## 🔔 3. THÔNG BÁO TỰ ĐỘNG
* **Thời gian**: Bot tự động gửi tin nhắn nhắc lịch vào lúc **15:00** hàng ngày cho những ai có lịch trực vào ngày hôm sau.
* **Điều kiện**: Bạn cần chạy lệnh `/register [Họ tên]` một lần duy nhất để Bot biết bạn là ai và gửi tin nhắn riêng.

---

## 🚀 4. VẬN HÀNH BOT
Để Bot hoạt động, bạn chỉ cần chạy lệnh sau và giữ cho Terminal luôn mở:
```bash
python bot.py
```

Nếu muốn chạy Bot ở chế độ chạy ngầm (trên Windows):
1. Nhấn `Win + R`, gõ `cmd`.
2. Gõ lệnh: `start /b python bot.py`

---

## ❓ 5. CÂU HỎI THƯỜNG GẶP (FAQ)
* **Q: Tại sao tôi không nhận được thông báo?**
  * A: Bạn hãy kiểm tra xem đã dùng lệnh `/register` chưa, và đảm bảo Bot đang được chạy.
* **Q: Bot báo lỗi "Không tìm thấy sheet"?**
  * A: File Excel của bạn cần có các sheet tên theo dạng `m-yyyy` (Ví dụ: `1-2026`).
* **Q: Đổi lịch trên Bot có cập nhật file Excel không?**
  * A: Có. Bot sẽ tự cập nhật file Excel cục bộ và đồng bộ ngược lên Google Drive ngay lập tức.

---

## 🏗 6. LÊN GITHUB & TRIỂN KHAI MÁY KHÁC

Để đưa project lên GitHub và deploy sang máy tính khác, hãy làm theo các bước sau để đảm bảo an toàn (không bị lộ Token):

### Bước 1: Chuẩn bị repo (Tại máy gốc)
1. Đảm bảo file `.gitignore` đã có `config.py`, `credentials.json`, `*.db` và `lich-truc-ban/*.xlsx`.
2. Khởi tạo Git và push:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Duty Bot"
   # Sau đó tạo repo trên GitHub và làm theo hướng dẫn để push
   ```

### Bước 2: Triển khai trên máy mới
1. Tải project từ GitHub về máy mới.
2. Cài đặt Python và thư viện: `pip install -r requirements.txt`.
3. **Quan trọng**: Tạo lại các file bị ẩn (vì không được push lên GitHub):
   - Copy file `config_example.py` thành `config.py` và điền lại thông tin Bot Token, Drive ID.
   - Chép file `credentials.json` của bạn vào cùng thư mục.
   - Đảm bảo trong thư mục có thư mục `lich-truc-ban`.
4. Run Bot: `python bot.py`.

---
*Chúc bạn quản lý trực ban hiệu quả!*
