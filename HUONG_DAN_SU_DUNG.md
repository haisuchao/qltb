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

2. **Ví dụ cấu trúc**:
   
   | Ngày | Thứ | Trực sáng | Trực chiều | Lãnh đạo |
   | :--- | :--- | :--- | :--- | :--- |
   | 01/01/2026 | Thứ Năm | Nguyễn Văn A | Lê Văn B | Trần Văn C |
   | 02/01/2026 | Thứ Sáu | Phạm Văn D | ... | ... |

   > [!TIP]
   > Bạn có thể tham khảo file mẫu có sẵn tại: `lich-truc-ban/LichTrucBan_2025-2026.xlsx`

   > [!IMPORTANT]
   > Dữ liệu cán bộ phải bắt đầu từ **Dòng 5** trở đi (Dòng 4 là tiêu đề cột).

3. **Vị trí file**:
   - Chép file Excel vào thư mục `lich-truc-ban` ngay trong thư mục dự án.

---

## 📋 2. CÁC LỆNH ĐIỀU KHIỂN BOT

| Lệnh | Mô tả | Ví dụ |
| :--- | :--- | :--- |
| `/start` | Khởi động Bot và xem menu lệnh | `/start` |
| `/today` | Xem lịch trực hôm nay | `/today` |
| `/tomorrow` | Xem lịch trực ngày mai | `/tomorrow` |
| `/check` | Tra cứu lịch của một ngày bất kỳ | `/check 30/01/2026` |
| `/search` | Tìm lịch trực của một người | `/search Nguyễn Văn A` |
| `/search [m/yyyy]` | Tìm lịch của bản thân trong tháng chỉ định | `/search 3/2026` |
| `/search [tên] [m/yyyy]` | Tìm lịch cán bộ trong tháng chỉ định | `/search An 3/2026` |
| `/register` | Đăng ký tài khoản nhận thông báo | `/register Nguyễn Văn A` |
| `/change` | Thay đổi người trực cho một ca | `/change 30/01/2026 sáng "Lê Văn B" "Lý do"` |
| `/swap` | Hoán đổi ca trực giữa 2 người | `/swap 01/02/2026 sáng 02/02/2026 chiều` |
| `/stats` | (Admin) Thống kê tổng hợp số buổi trực | `/stats` |
| `/send_noti` | (Admin) Gửi thông báo thủ công | `/send_noti 30/01/2026` |
| `/auto_schedule` | (Admin) Xếp lịch tự động vòng tròn | `/auto_schedule 3-2026 \| Lãnh Đạo A, Lãnh Đạo B` |
| `/help` | Xem hướng dẫn chi tiết | `/help` |

---

## 📅 3. TỰ ĐỘNG XẾP LỊCH (ADMIN)
Hệ thống hỗ trợ tính năng tự động xếp lịch theo vòng tròn (Round-robin) giúp tiết kiệm thời gian.

**Đặc điểm:**
* Dùng chung một danh sách cho cả ca Sáng và Chiều.
* Tự động luân phiên: Nếu lần này trực Sáng, lần sau sẽ trực Chiều.
* Tự động bỏ qua Thứ 7 và Chủ nhật.
* Thêm Sheet mới vào file Excel đúng định dạng Template.

**Cách dùng:**
```bash
# Cách 1: Tên tự lấy từ sheet 'DS trực'
/auto_schedule 3-2026 | Lãnh Đạo 1, Lãnh Đạo 2

# Cách 2: Chỉ định người bắt đầu
/auto_schedule 3-2026 Hải | Lãnh Đạo 1, Lãnh Đạo 2

# Cách 3: Nhập danh sách tên thủ công
/auto_schedule 3-2026 Nguyễn Văn A, Lê Văn B | Lãnh Đạo 1, Lãnh Đạo 2
```
*Lưu ý: Dùng dấu gạch đứng `|` để phân tách danh sách cán bộ và danh sách lãnh đạo. Nếu để trống phần trước dấu `|`, Bot sẽ tự động lấy danh sách từ sheet **'DS trực'** (trừ những người bị đánh dấu 'x' miễn trực).*

---

## 🔔 4. THÔNG BÁO TỰ ĐỘNG
* **Thời gian**: Hệ thống tự động kiểm tra và nhắc lịch vào lúc **16:15** hàng ngày cho ngày hôm sau.
* **Đăng ký**: Cần chạy lệnh `/register` một lần duy nhất để hệ thống ghi nhận Telegram ID của bạn.
* **Xếp lịch tự động hàng tháng**: Hệ thống tự động xếp lịch cho tháng tiếp theo vào ngày 23 hàng tháng (cấu hình trong `config.py`).

---

## 🚀 5. VẬN HÀNH BOT

```bash
python bot.py
```

---

## ❓ 6. CÂU HỎI THƯỜNG GẶP (FAQ)
* **Q: Dữ liệu lịch trực lưu ở đâu?**
  - A: Dữ liệu lịch trực được lưu trong file Excel tại thư mục `lich-truc-ban/`. Các log thông báo và lịch sử đổi ca được lưu trong database `truc_ban.db`.
* **Q: Làm sao để thêm cán bộ mới?**
  - A: Thêm tên cán bộ vào sheet `DS trực` trong file Excel. Cán bộ cũng cần chạy lệnh `/register` trên Telegram để nhận thông báo.
* **Q: Ai có quyền Admin?**
  - A: Cấu hình danh sách Admin ID trong file `config.py` tại biến `ADMIN_IDS`.

---
*Chúc bạn quản lý trực ban hiệu quả!*
