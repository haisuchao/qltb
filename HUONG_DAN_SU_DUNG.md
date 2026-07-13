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

   > [!NOTE]
   > Từ phiên bản này, hệ thống **không còn hardcode tên file** trong `config.py` nữa. Tên file lịch trực theo năm học (VD: `LichTrucBan_2025-2026.xlsx`) được quản lý tự động qua lệnh `/start_new_year` (xem mục 3 bên dưới). Nếu bạn có sẵn file cũ đúng định dạng tên `LichTrucBan_<năm bắt đầu>-<năm kết thúc>.xlsx` trong thư mục `lich-truc-ban`, bot sẽ tự nhận diện khi khởi động lần đầu.

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
| `/start_new_year` | (Admin) Tạo file lịch trực cho năm học mới | `/start_new_year 2026` |
| `/set_current_year` | (Admin) Chỉnh tay năm học đang được quản lý | `/set_current_year 2026` |
| `/help` | Xem hướng dẫn chi tiết | `/help` |

---

## 🎓 3. QUẢN LÝ NĂM HỌC MỚI (ADMIN)
Khi kết thúc năm học, dùng lệnh `/start_new_year` để tự động tạo file Excel chuẩn cho năm học tiếp theo, không cần tạo file thủ công hay sửa code.

**Lệnh:**
```bash
# Tạo năm học mới bắt đầu từ năm chỉ định (năm kết thúc = năm + 1)
/start_new_year 2026

# Không nhập năm -> mặc định lấy năm hiện tại
/start_new_year
```

**File được tạo ra** (`LichTrucBan_<year>-<year+1>.xlsx`) gồm:
- Sheet **"DS trực"**: copy danh sách cán bộ từ năm hiện tại (xóa cột Miễn/Lý do để bạn cập nhật lại theo tình hình nhân sự năm mới).
- Sheet **"Tổng"**: liệt kê sẵn cán bộ (số buổi trực = 0), sẽ được `/stats` tự động cập nhật số liệu thật khi có lịch trực.
- 11 sheet tháng, từ **tháng 8 của năm bắt đầu** đến **tháng 6 của năm kết thúc** — mỗi sheet đã điền sẵn Ngày/Thứ, cột trực để trống, sẵn sàng dùng `/auto_schedule` hoặc nhập tay.

> [!IMPORTANT]
> Nếu file của năm đó đã tồn tại sẵn, bot sẽ **báo lỗi và không tạo file mới** (tránh ghi đè/mất dữ liệu đã có). Nếu muốn tạo lại từ đầu, hãy tự đổi tên hoặc xóa file cũ trong thư mục `lich-truc-ban` trước khi chạy lại lệnh.

Sau khi tạo file, hệ thống tự so sánh năm vừa tạo với năm hiện tại đang quản lý, năm nào lớn hơn sẽ tự động trở thành năm hiện tại (`current_year`) — tức là bot sẽ đọc/ghi lịch trên file của năm đó cho các lệnh `/today`, `/check`, `/change`,...

Nếu cần **chỉnh tay** năm đang quản lý (VD: quay lại năm cũ để tra cứu), dùng:
```bash
/set_current_year 2025
```
Lệnh này chỉ chấp nhận năm đã từng được tạo bằng `/start_new_year` (hoặc đã có sẵn file đúng định dạng tên khi bot khởi động lần đầu).

---

## 📅 4. TỰ ĐỘNG XẾP LỊCH (ADMIN)
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

## 🔔 5. THÔNG BÁO TỰ ĐỘNG
* **Thời gian**: Hệ thống tự động kiểm tra và nhắc lịch vào lúc **16:00** hàng ngày cho ngày hôm sau.
* **Đăng ký**: Cần chạy lệnh `/register` một lần duy nhất để hệ thống ghi nhận Telegram ID của bạn.
* **Xếp lịch tự động hàng tháng**: Hệ thống tự động xếp lịch cho tháng tiếp theo vào ngày 23 hàng tháng (cấu hình trong `config.py`).

---

## 🚀 6. VẬN HÀNH BOT

```bash
python bot.py
```

---

## ❓ 7. CÂU HỎI THƯỜNG GẶP (FAQ)
* **Q: Dữ liệu lịch trực lưu ở đâu?**
  - A: Dữ liệu lịch trực được lưu trong file Excel tại thư mục `lich-truc-ban/`. Các log thông báo, lịch sử đổi ca và danh sách năm học (`available_years`) được lưu trong database `truc_ban.db`.
* **Q: Làm sao để thêm cán bộ mới?**
  - A: Thêm tên cán bộ vào sheet `DS trực` trong file Excel. Cán bộ cũng cần chạy lệnh `/register` trên Telegram để nhận thông báo.
* **Q: Ai có quyền Admin?**
  - A: Cấu hình danh sách Admin ID trong file `config.py` tại biến `ADMIN_IDS`.
* **Q: Làm sao để chuyển sang năm học mới?**
  - A: Dùng lệnh `/start_new_year [year]` (xem mục 3). Không cần sửa `config.py` nữa.

---
*Chúc bạn quản lý trực ban hiệu quả!*
