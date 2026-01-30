# facebook_bot.py
# Bot quản lý trực ban trên nền tảng Facebook Messenger (Sử dụng Flask Webhook)

import requests
from flask import Flask, request
from config import FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_VERIFY_TOKEN, FACEBOOK_USER_IDS, ADMIN_IDS
from schedule_manager import ScheduleManager
from database import DatabaseManager
import logging
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Khởi tạo các manager
schedule_mgr = ScheduleManager()
db_mgr = DatabaseManager()

FB_API_URL = "https://graph.facebook.com/v19.0/me/messages"

def send_fb_message(psid, message_text):
    """Gửi tin nhắn đến Facebook User ID (PSID)"""
    payload = {
        "recipient": {"id": psid},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": FACEBOOK_PAGE_ACCESS_TOKEN}
    try:
        response = requests.post(FB_API_URL, json=payload, params=params)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Lỗi gửi tin nhắn FB: {e}")
        return False

@app.route('/webhook', methods=['GET'])
def verify():
    """Xác thực webhook với Facebook Developer Portal"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == FACEBOOK_VERIFY_TOKEN:
        logger.info("Xác thực Webhook thành công!")
        return challenge, 200
    else:
        logger.warning("Xác thực Webhook thất bại!")
        return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Tiếp nhận và xử lý tin nhắn từ Facebook"""
    data = request.json
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '').strip()
                    handle_message(sender_id, message_text)
        return "EVENT_RECEIVED", 200
    return "Not Found", 404

def handle_message(psid, text):
    """Xử lý logic lệnh từ người dùng"""
    if not text: return
    
    command = text.lower().split()[0]
    args = text.split()[1:]
    
    logger.info(f"Nhận lệnh từ {psid}: {text}")
    
    if command in ['/start', 'help', '/help']:
        reply = (
            "🤖 BOT QUẢN LÝ TRỰC BAN (FACEBOOK)\n\n"
            "Các lệnh hỗ trợ:\n"
            "• today: Xem lịch trực hôm nay\n"
            "• tomorrow: Xem lịch trực ngày mai\n"
            "• search [tên]: Tìm lịch trực của ai đó\n"
            "• register [họ tên]: Đăng ký tên để nhận thông báo\n"
            "• help: Xem hướng dẫn này"
        )
        send_fb_message(psid, reply)

    elif command == 'today':
        today_str = datetime.now().strftime("%d/%m/%Y")
        shift_info = schedule_mgr.get_shifts_by_date(today_str)
        if shift_info:
            reply = f"📅 Lịch trực hôm nay ({today_str}):\n"
            reply += f"☀️ Sáng: {shift_info.get('Sáng', 'Trống')}\n"
            reply += f"🌙 Chiều: {shift_info.get('Chiều', 'Trống')}"
        else:
            reply = f"❌ Không tìm thấy lịch trực cho ngày {today_str}."
        send_fb_message(psid, reply)

    elif command == 'tomorrow':
        from datetime import timedelta
        tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        shift_info = schedule_mgr.get_shifts_by_date(tomorrow_str)
        if shift_info:
            reply = f"📅 Lịch trực ngày mai ({tomorrow_str}):\n"
            reply += f"☀️ Sáng: {shift_info.get('Sáng', 'Trống')}\n"
            reply += f"🌙 Chiều: {shift_info.get('Chiều', 'Trống')}"
        else:
            reply = f"❌ Không tìm thấy lịch trực cho ngày {tomorrow_str}."
        send_fb_message(psid, reply)

    elif command == 'search':
        if not args:
            send_fb_message(psid, "⚠️ Vui lòng nhập tên cần tìm. VD: search Hải")
            return
        name = " ".join(args)
        results = schedule_mgr.search_for_name(name)
        if results:
            reply = f"🔍 Kết quả tìm kiếm cho '{name}':\n"
            for r in results[:10]: # Giới hạn 10 kết quả đầu
                reply += f"- Ngày {r['date']}: {r['shift']}\n"
            if len(results) > 10:
                reply += "... và một số ngày khác."
        else:
            reply = f"❌ Không tìm thấy lịch trực nào cho '{name}'."
        send_fb_message(psid, reply)

    elif command == 'register':
        if not args:
            send_fb_message(psid, "⚠️ Vui lòng nhập họ tên đầy đủ. VD: register Nguyễn Đỗ Hải")
            return
        full_name = " ".join(args)
        # Lưu vào database (Sử dụng bảng chung với Telegram, phân biệt qua tiền tố FB_)
        db_mgr.save_user(f"FB_{psid}", full_name)
        send_fb_message(psid, f"✅ Đã đăng ký thành công cán bộ: {full_name}\nID của bạn: {psid}")

    elif command == 'auto_schedule':
        # Kiểm tra Admin
        if str(psid) not in ADMIN_IDS:
            send_fb_message(psid, "⛔ Bạn không có quyền thực hiện lệnh này.")
            return
            
        if not args or '|' not in " ".join(args):
            send_fb_message(psid, "⚠️ Cách dùng: auto_schedule [m-yyyy] [danh_sách] | [lãnh_đạo]\nHoặc: auto_schedule [m-yyyy] | [lãnh_đạo] (lấy tên từ file Excel)")
            return
            
        try:
            full_text = " ".join(args)
            month_year = args[0]
            content = full_text.replace(month_year, "", 1).strip()
            
            parts = content.split('|')
            names_str = parts[0].strip()
            leaders_str = parts[1].strip()
            
            names = [n.strip() for n in names_str.split(',') if n.strip()] if names_str else None
            leaders = [n.strip() for n in leaders_str.split(',') if n.strip()]
            
            success, message = schedule_mgr.auto_generate_round_robin(month_year, names, leaders)
            send_fb_message(psid, f"{'✅' if success else '❌'} {message}")
        except Exception as e:
            send_fb_message(psid, f"❌ Lỗi: {str(e)}")

    else:
        send_fb_message(psid, "❓ Lệnh không hợp lệ. Gõ 'help' để xem danh sách lệnh.")

if __name__ == '__main__':
    # Chạy Flask app trên port 5000
    app.run(port=5000, debug=True)
