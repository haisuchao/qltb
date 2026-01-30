# config_example.py
# File mẫu cấu hình - Hãy đổi tên thành config.py và điền thông tin của bạn

import os

# Cấu hình đường dẫn
SCHEDULE_FOLDER = "lich-truc-ban"
MASTER_SCHEDULE_FILE = "LichTrucBan_2025-2026.xlsx"

LOG_FOLDER = "logs"
DATABASE_FILE = "truc_ban.db"

# Cấu hình Telegram Bot
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Cấu hình thời gian gửi thông báo
NOTIFICATION_TIME = "15:00"

# Cấu hình ánh xạ tĩnh (Nếu không dùng /register)
TELEGRAM_CHAT_IDS = {
    # "Tên Cán Bộ": "ChatID"
}

# Tạo thư mục nếu chưa có
os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
