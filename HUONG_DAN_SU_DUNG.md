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

4. **Vị trí file**:
   - Chép file Excel vào thư mục `lich-truc-ban` ngay trong thư mục dự án.

### Bước 4: Cấu hình Facebook Messenger Bot (Tùy chọn)
Nếu bạn muốn sử dụng Bot trên Facebook Messenger thay vì hoặc song song với Telegram:

1. **Tạo Fanpage**: Tạo một trang Facebook mới để làm đại diện cho Bot.
2. **Cài đặt Facebook App**:
   - Truy cập [Facebook Developers](https://developers.facebook.com/), tạo App mới loại **"Other"** -> chọn **"Messenger"**.
   - Trong phần cài đặt Messenger, nhấn **"Add or Remove Pages"** để kết nối Fanpage của bạn.
   - Nhấn **"Generate Token"** để lấy mã truy cập trang và dán vào `FACEBOOK_PAGE_ACCESS_TOKEN` trong file `config.py`.
3. **Cấu hình Webhook**:
   - Để nhận tin nhắn, bạn cần một địa chỉ HTTPS công khai. Nếu chạy tại máy cá nhân, hãy dùng **Ngrok** (`ngrok http 5000`).
   - Copy link HTTPS của Ngrok (VD: `https://abcd-123.ngrok-free.app/webhook`) và dán vào phần Webhook của Facebook App.
   - **Verify Token**: Nhập chuỗi trùng với `FACEBOOK_VERIFY_TOKEN` trong `config.py` (mặc định là `my_secret_token_123`).
   - Chọn các trường đăng ký (Subscription Fields): `messages`, `messaging_postbacks`.
4. **Chạy Bot**: Chạy file `facebook_bot.py` để bắt đầu lắng nghe tin nhắn.

---

## 📋 2. CÁC LỆNH ĐIỀU KHIỂN BOT

### 🔹 Trên Telegram (Gõ lệnh có dấu `/`)
| Lệnh | Mô tả | Ví dụ |
| :--- | :--- | :--- |
| `/start` | Khởi động Bot và xem menu lệnh | `/start` |
| `/today` | Xem lịch trực hôm nay | `/today` |
| `/tomorrow` | Xem lịch trực ngày mai | `/tomorrow` |
| `/check` | Tra cứu lịch của một ngày bất kỳ | `/check 30/01/2026` |
| `/search` | Tìm lịch trực của một người | `/search Nguyễn Văn A` |
| `/register` | Đăng ký tài khoản nhận thông báo | `/register Nguyễn Văn A` |
| `/change` | Thay đổi người trực cho một ca | `/change 30/01/2026 sáng "Lê Văn B"` |
| `/swap` | Hoán đổi ca trực giữa 2 người | `/swap 01/02 sáng 02/02 chiều` |

### 🔹 Trên Facebook Messenger (Gõ từ khóa trực tiếp)
| Từ khóa | Mô tả |
| :--- | :--- |
| `today` | Xem lịch trực hôm nay |
| `tomorrow` | Xem lịch trực ngày mai |
| `search [tên]` | Tìm lịch trực của ai đó (VD: `search Hải`) |
| `register [Họ tên]` | Đăng ký nhận thông báo (VD: `register Nguyễn Đỗ Hải`) |
| `auto_schedule` | (Admin) Xếp lịch tự động vòng tròn |
| `help` | Xem hướng dẫn sử dụng |

---

## 📅 3. TỰ ĐỘNG XẾP LỊCH (ADMIN)
Hệ thống hỗ trợ tính năng tự động xếp lịch theo vòng tròn (Round-robin) giúp tiết kiệm thời gian.

**Đặc điểm:**
* Dùng chung một danh sách cho cả ca Sáng và Chiều.
* Tự động luân phiên: Nếu lần này trực Sáng, lần sau sẽ trực Chiều.
* Tự động bỏ qua Thứ 7 và Chủ nhật.
* Thêm Sheet mới vào file Excel đúng định dạng Template.

**Cách dùng (Trên Telegram):**
```bash
# Cách 1: Tên tự lấy từ sheet 'DS trực'
/auto_schedule 3-2026 | Lãnh Đạo 1, Lãnh Đạo 2

# Cách 2: Nhập danh sách tên thủ công
/auto_schedule 3-2026 Nguyễn Văn A, Lê Văn B | Lãnh Đạo 1, Lãnh Đạo 2
```
*Lưu ý: Dùng dấu gạch đứng `|` để phân tách danh sách cán bộ và danh sách lãnh đạo. Nếu để trống phần trước dấu `|`, Bot sẽ tự động lấy danh sách từ sheet **'DS trực'** (trừ những người bị đánh dấu 'x' miễn trực).*

---

## 🔔 4. THÔNG BÁO TỰ ĐỘNG
* **Thời gian**: Hệ thống tự động kiểm tra và nhắc lịch vào lúc **15:00** hàng ngày cho ngày hôm sau.
* **Đăng ký**: Cần chạy lệnh `register` (Facebook) hoặc `/register` (Telegram) một lần duy nhất.
* **Facebook ID**: Khi đăng ký trên Facebook, hệ thống sẽ lưu ID của bạn với tiền tố `FB_` trong cơ sở dữ liệu.

---

## 🚀 5. VẬN HÀNH BOT

- **Chạy Telegram Bot**: `python bot.py`
- **Chạy Facebook Bot**: `python facebook_bot.py`
- **Chạy đồng thời**: Bạn có thể mở 2 cửa sổ Terminal để chạy cả 2 bot cùng lúc.

---

## ❓ 6. CÂU HỎI THƯỜNG GẶP (FAQ)
* **Q: Có cần cấu hình gì trên Facebook không?**
  - A: Có, bạn cần cấu hình Webhook và Token trên Facebook Developer Portal như hướng dẫn ở Bước 4.
* **Q: Dùng chung 1 file Excel và Database không?**
  - A: Có. Cả hai nền tảng đều truy xuất chung dữ liệu từ file Excel trong thư mục `lich-truc-ban` và database `truc_ban.db`.
* **Q: Làm sao để lấy FB PSID của tôi?**
  - A: Bạn chỉ cần gõ lệnh `register [Tên]` trên Messenger, Bot sẽ trả về PSID của bạn sau khi đăng ký thành công.

---
*Chúc bạn quản lý trực ban hiệu quả!*
