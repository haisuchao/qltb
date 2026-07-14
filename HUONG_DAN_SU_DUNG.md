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
| `/add_officer` | (Admin) Thêm cán bộ mới vào DS trực | `/add_officer Nguyễn Văn A` |
| `/remove_officer` | (Admin) Xóa cán bộ khỏi DS trực | `/remove_officer Nguyễn Văn A` |
| `/deactive_officer` | (Admin) Miễn trực cho cán bộ (kèm lý do) | `/deactive_officer "Nguyễn Văn A" "Đi học VB2"` |
| `/active_officer` | (Admin) Bỏ miễn trực, về trực bình thường | `/active_officer Nguyễn Văn A` |
| `/edit_officer` | (Admin) Sửa tên cán bộ ghi sai | `/edit_officer "Nguyễn Văn A" "Nguyễn Văn B"` |
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

## 👥 4. QUẢN LÝ DANH SÁCH CÁN BỘ (ADMIN)
Quản lý trực tiếp sheet "DS trực" của năm hiện tại mà không cần mở Excel thủ công.

**Thêm cán bộ mới:**
```bash
/add_officer Nguyễn Văn A
```
- Bot tự kiểm tra trùng tên (không phân biệt hoa/thường, khoảng trắng thừa) — nếu đã có sẽ báo lỗi kèm số dòng.
- STT mới = STT lớn nhất hiện có + 1.
- Sau khi thêm, chạy `/stats` để cập nhật số liệu vào sheet "Tổng".

**Xóa cán bộ khỏi danh sách:**
```bash
/remove_officer Nguyễn Văn A
```
- Báo lỗi nếu không tìm thấy tên trong DS trực.
- Nếu phát hiện nhiều dòng trùng tên (dữ liệu bị sửa tay trước đó), bot sẽ **không tự xóa** để tránh xóa nhầm — bạn cần vào Excel kiểm tra thủ công.
- Lưu ý: xóa khỏi DS trực **không** tự động xóa các ca đã phân công cho người này trong các sheet tháng — cần dùng `/change` để thay người nếu họ đã có lịch sắp tới.

**Miễn trực (kèm lý do):**
```bash
/deactive_officer "Nguyễn Văn A" "Đi học VB2"
# Hoặc không cần lý do:
/deactive_officer "Nguyễn Văn A"
```
- Đặt tên trong dấu ngoặc kép (bắt buộc nếu tên có khoảng trắng, luôn đúng với tên tiếng Việt).
- Đánh dấu cột "Miễn" = `x`, ghi lý do vào cột "Lý do" nếu có.
- Cán bộ bị miễn sẽ không được đưa vào danh sách khi chạy `/auto_schedule` (nếu để bot tự lấy tên từ DS trực).
- Nếu cán bộ đã được miễn trước đó, chạy lại lệnh sẽ chỉ cập nhật lý do mới.

**Bỏ miễn trực (về trực bình thường):**
```bash
/active_officer Nguyễn Văn A
```
- Xóa đánh dấu "x" và lý do, cán bộ được đưa lại vào danh sách khi chạy `/auto_schedule`.
- Nếu cán bộ vốn không bị miễn, bot sẽ báo "không có gì để thay đổi" (không lỗi).

**Sửa tên cán bộ ghi sai:**
```bash
/edit_officer "Nguyễn Văn A" "Nguyễn Văn B"
```
- Đặt cả 2 tên trong dấu ngoặc kép.
- Bot tự động đồng bộ tên mới vào: sheet "DS trực", sheet "Tổng" (nếu đã có), **tất cả các ca đã phân công sẵn trong các sheet tháng** (Trực sáng/chiều/Lãnh đạo), và danh sách liên hệ Telegram (`officers_contact`) nếu cán bộ đã từng `/register` — để không bị gián đoạn nhận thông báo.
- Báo lỗi nếu tên mới đã trùng với một người khác trong DS trực.
- Lịch sử đổi ca cũ (`/change`, `/swap`) và lịch sử thông báo đã gửi trước đó **không** bị sửa lại (giữ nguyên như một nhật ký, đúng với tên đã dùng tại thời điểm đó).

> [!NOTE]
> Cả 5 lệnh trên đều thao tác trên file của **năm hiện tại** (`current_year`). Nếu cần sửa DS trực của năm khác, dùng `/set_current_year` để chuyển trước.

---

## 📅 5. TỰ ĐỘNG XẾP LỊCH (ADMIN)
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

## 🔔 6. THÔNG BÁO TỰ ĐỘNG
* **Thời gian**: Hệ thống tự động kiểm tra và nhắc lịch vào lúc **16:00** hàng ngày cho ngày hôm sau.
* **Đăng ký**: Cần chạy lệnh `/register` một lần duy nhất để hệ thống ghi nhận Telegram ID của bạn.
* **Xếp lịch tự động hàng tháng**: Hệ thống tự động xếp lịch cho tháng tiếp theo vào ngày 23 hàng tháng (cấu hình trong `config.py`).

---

## 🚀 7. VẬN HÀNH BOT

```bash
python bot.py
```

---

## ❓ 8. CÂU HỎI THƯỜNG GẶP (FAQ)
* **Q: Dữ liệu lịch trực lưu ở đâu?**
  - A: Dữ liệu lịch trực được lưu trong file Excel tại thư mục `lich-truc-ban/`. Các log thông báo, lịch sử đổi ca và danh sách năm học (`available_years`) được lưu trong database `truc_ban.db`.
* **Q: Làm sao để thêm cán bộ mới?**
  - A: Dùng lệnh `/add_officer [Họ tên]` (xem mục 4), hoặc thêm trực tiếp vào sheet `DS trực` trong file Excel. Cán bộ cũng cần chạy lệnh `/register` trên Telegram để nhận thông báo.
* **Q: Ai có quyền Admin?**
  - A: Cấu hình danh sách Admin ID trong file `config.py` tại biến `ADMIN_IDS`.
* **Q: Làm sao để chuyển sang năm học mới?**
  - A: Dùng lệnh `/start_new_year [year]` (xem mục 3). Không cần sửa `config.py` nữa.
* **Q: Cán bộ nghỉ việc/chuyển công tác thì xử lý thế nào?**
  - A: Dùng `/remove_officer [Họ tên]` để xóa hẳn khỏi DS trực, hoặc `/deactive_officer "[Họ tên]" "[Lý do]"` nếu chỉ tạm miễn trực một thời gian (vẫn giữ tên trong danh sách). Dùng `/active_officer [Họ tên]` khi cán bộ quay lại trực bình thường.
* **Q: Lỡ ghi sai tên cán bộ trong DS trực thì sửa thế nào?**
  - A: Dùng `/edit_officer "[Tên cũ]" "[Tên mới]"` — không nên xóa rồi thêm lại, vì lệnh này còn tự động sửa tên trong các ca đã phân công sẵn ở sheet tháng.

---
*Chúc bạn quản lý trực ban hiệu quả!*
