
import logging
import asyncio
from datetime import datetime, time, timezone, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import config
from schedule_manager import ScheduleManager
from database import DatabaseManager
import sys
import shlex

# Force UTF-8 encoding for stdout (Windows fix)
sys.stdout.reconfigure(encoding='utf-8')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Silence noisy httpx logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Múi giờ Việt Nam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))

class DutyBot:
    def __init__(self):
        self.schedule_mgr = ScheduleManager()
        self.db = DatabaseManager()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Chào mừng bạn đến với Bot Quản lý Trực ban!\n"
            "Các lệnh có sẵn:\n"
            "🔹 /today - Xem lịch trực hôm nay\n"
            "🔹 /tomorrow - Xem lịch trực ngày mai\n"
            "🔹 /check - Tra cứu lịch theo ngày\n"
            "   <i>VD: /check 30/01/2026</i>\n"
            "🔹 /search - Tìm lịch cá nhân\n"
            "   <i>VD: /search An | /search 3/2026 (Tìm lịch của mình)</i>\n"
            "🔹 /change - Đổi người trực (1 ca)\n"
            "   <i>VD: /change 01/05/2026 sáng \"Nguyễn Văn A\" \"Bận việc\"</i>\n"
            "🔹 /swap - Hoán đổi 2 ca trực\n"
            "   <i>VD: /swap 01/02 sáng 02/02 chiều</i>\n"
            "🔹 /register - Đăng ký nhận thông báo\n"
            "   <i>VD: /register Nguyễn Văn A</i>\n"
            "🔹 /help - Xem hướng dẫn chi tiết",
            parse_mode='HTML'
        )
        user = update.effective_user
        logger.info(f"User {user.full_name} ({user.id}) started the bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "📖 <b>HƯỚNG DẪN SỬ DỤNG CHI TIẾT</b>\n\n"
            "1️⃣ <b>Xem lịch:</b>\n"
            "• <code>/today</code>: Xem lịch trực hôm nay\n"
            "• <code>/tomorrow</code>: Xem lịch trực ngày mai\n"
            "• <code>/check [ngày]</code>: Tra cứu ngày bất kỳ\n"
            "   <i>VD: /check 30/01/2026 (hoặc /check để xem hôm nay)</i>\n\n"
            "2️⃣ <b>Tìm kiếm & Đăng ký:</b>\n"
            "• <code>/search [tên]</code>: Tìm lịch cán bộ trong tháng hiện tại\n"
            "• <code>/search [m/yyyy]</code>: Tìm lịch của <b>bản thân</b> trong tháng chỉ định\n"
            "• <code>/search [tên] [m/yyyy]</code>: Tìm lịch cán bộ trong tháng chỉ định\n"
            "   <i>VD: /search An | /search 3/2026 | /search An 3/2026</i>\n"
            "• <code>/register [họ tên]</code>: Đăng ký ID để nhận tin nhắn\n"
            "   <i>VD: /register Nguyễn Văn A</i>\n\n"
            "3️⃣ <b>Đổi lịch & Hoán đổi:</b>\n"
            "• <code>/change [ngày] [ca] [tên mới] [lý do]</code>: Đổi 1 ca\n"
            "   <i>VD: /change 01/05/2026 sáng \"Trần Văn B\" \"Lý do...\"</i>\n"
            "• <code>/swap [ngày1] [ca1] [ngày2] [ca2]</code>: Đổi chéo 2 ca\n"
            "   <i>VD: /swap 01/02 sáng 02/02 chiều</i>\n\n"
            "4️⃣ <b>Quy định:</b>\n"
            "• Bot tự động gửi thông báo nhắc lịch vào 15:00 hàng ngày.\n"
            "• Lệnh <code>/swap</code> yêu cầu chính chủ hoặc Admin xác nhận."
        )
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def today_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        today = datetime.now()
        info = self.schedule_mgr.get_duty_info_for_date(today)
        msg = self._format_duty_message(info, "HÔM NAY")
        await update.message.reply_text(msg, parse_mode='HTML')

    async def tomorrow_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        info = self.schedule_mgr.get_tomorrow_duty()
        msg = self._format_duty_message(info, "NGÀY MAI")
        await update.message.reply_text(msg, parse_mode='HTML')

    async def check_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tra cứu lịch trực theo ngày"""
        try:
            if not context.args:
                # Nếu không nhập ngày, mặc định lấy ngày hôm nay
                date = datetime.now()
                date_str = date.strftime('%d/%m/%Y')
                info = self.schedule_mgr.get_duty_info_for_date(date)
                msg = self._format_duty_message(info, f"HÔM NAY ({date_str})")
                await update.message.reply_text(msg, parse_mode='HTML')
                return

            date_str = context.args[0]
            try:
                date = datetime.strptime(date_str, '%d/%m/%Y')
                info = self.schedule_mgr.get_duty_info_for_date(date)
                msg = self._format_duty_message(info, f"NGÀY {date_str}")
                await update.message.reply_text(msg, parse_mode='HTML')
            except ValueError:
                await update.message.reply_text("❌ Định dạng ngày không đúng. Ví dụ: /check 30/01/2026")

        except Exception as e:
            logger.error(f"Error checking schedule: {e}")
            await update.message.reply_text("❌ Có lỗi xảy ra khi tra cứu.")

    def _format_duty_message(self, info, title):
        if not info:
             return f"❌ Không tìm thấy lịch trực {title}!"
             
        if info.get('is_off'):
            return f"📅 <b>LỊCH TRỰC {title} ({info['date']} - {info['day_of_week']})</b>\n\n🏖️ Không có lịch trực (Ngày nghỉ/Lễ)"
            
        return (
            f"📅 <b>LỊCH TRỰC {title} ({info['date']} - {info['day_of_week']})</b>\n\n"
            f"☀️ <b>Sáng:</b> {info['morning_officer'] or 'Trống'}\n"
            f"🌙 <b>Chiều:</b> {info['afternoon_officer'] or 'Trống'}\n"
            f"👮 <b>Lãnh đạo:</b> {info['leader'] or 'Trống'}"
        )

    async def change_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh đổi lịch với cú pháp 1 dòng"""
        # Cú pháp mong đợi: /doi_lich <ngày> <ca> <người mới> <lý do>
        # Sử dụng shlex để xử lý chuỗi trong ngoặc kép
        try:
            command_args = shlex.split(update.message.text)[1:] # Bỏ command /doi_lich
            
            if len(command_args) < 4:
                await update.message.reply_text(
                    "❌ Sai cú pháp! Vui lòng nhập đủ 4 thông tin:\n"
                    "/doi_lich [ngày] [ca] [tên người mới] [lý do]\n"
                    "Ví dụ: /doi_lich 01/05/2026 sáng \"Nguyễn Văn A\" \"Bận việc gia đình\""
                )
                return

            date_str = command_args[0]
            shift = command_args[1].lower()
            new_officer = command_args[2]
            reason = " ".join(command_args[3:]) # Ghép phần còn lại thành lý do nếu không dùng quote

            # Validate ngày
            try:
                date = datetime.strptime(date_str, '%d/%m/%Y')
            except ValueError:
                await update.message.reply_text("❌ Định dạng ngày không đúng (dd/mm/yyyy). Ví dụ: 01/01/2026")
                return

            # Validate ca
            if shift not in ['sáng', 'chiều']:
                await update.message.reply_text("❌ Ca trực chỉ được là 'sáng' hoặc 'chiều'.")
                return

            # Thực hiện đổi lịch
            # Lấy thông tin cũ để log cho đẹp
            info = self.schedule_mgr.get_duty_info_for_date(date)
            old_officer = "N/A"
            if info and not info.get('is_off'):
                old_officer = info['morning_officer'] if shift == 'sáng' else info['afternoon_officer']

            success = self.schedule_mgr.update_schedule(
                date=date,
                shift=shift,
                new_officer=new_officer,
                old_officer=old_officer,
                reason=reason,
                changed_by=update.effective_user.full_name
            )
            
            if success:
                await update.message.reply_text(
                    f"✅ <b>ĐỔI LỊCH THÀNH CÔNG</b>\n"
                    f"- Ngày: {date_str}\n"
                    f"- Ca: {shift}\n"
                    f"- Mới: {new_officer}\n"
                    f"- Lý do: {reason}",
                    parse_mode='HTML'
                )
            else:
                 await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng kiểm tra lại file lịch hoặc log hệ thống.")

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            await update.message.reply_text(f"❌ Lỗi xử lý lệnh: {str(e)}")

    # --- Background Job ---
    async def manual_notification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gửi thông báo thủ công: /send_noti dd/mm/yyyy [sáng/chiều]"""
        # Kiểm tra quyền Admin
        user_id = str(update.effective_user.id)
        if hasattr(config, 'ADMIN_IDS') and user_id not in config.ADMIN_IDS:
             await update.message.reply_text("⛔ Bạn không có quyền thực hiện lệnh này. Chỉ Admin mới có quyền gửi thông báo thủ công.")
             return

        try:
            if not context.args:
                await update.message.reply_text("❌ Vui lòng nhập ngày. Ví dụ: /send_noti 30/01/2026 [sáng/chiều]")
                return

            date_str = context.args[0]
            shift_filter = context.args[1].lower() if len(context.args) > 1 else None
            
            if shift_filter and shift_filter not in ['sáng', 'chiều']:
                await update.message.reply_text("❌ Ca trực không hợp lệ. Chỉ dùng 'sáng' hoặc 'chiều'.")
                return

            try:
                date = datetime.strptime(date_str, '%d/%m/%Y')
                duty_info = self.schedule_mgr.get_duty_info_for_date(date)
            except ValueError:
                await update.message.reply_text("❌ Định dạng ngày không đúng. Ví dụ: /send_noti 30/01/2026")
                return

            if not duty_info or duty_info.get('is_off'):
                await update.message.reply_text(f"⚠️ Ngày {date_str} không có lịch trực (Ngày nghỉ/Lễ).")
                return

            # Xác định người cần gửi
            officers_to_notify = []
            
            # Nếu không chỉ định ca hoặc chỉ định sáng -> Thêm sáng
            if not shift_filter or shift_filter == 'sáng':
                if duty_info['morning_officer']:
                    officers_to_notify.append((duty_info['morning_officer'], 'sáng'))
            
            # Nếu không chỉ định ca hoặc chỉ định chiều -> Thêm chiều
            if not shift_filter or shift_filter == 'chiều':
                if duty_info['afternoon_officer']:
                    officers_to_notify.append((duty_info['afternoon_officer'], 'chiều'))

            if not officers_to_notify:
                await update.message.reply_text(f"⚠️ Không tìm thấy cán bộ trực nào trong ngày {date_str} (theo bộ lọc).")
                return

            sent_count = 0
            log_messages = []

            for name, shift in officers_to_notify:
                # Lookup contact
                contact = self.db.get_officer_contact(name)
                chat_id = None
                if contact and contact[2]: # Telegram ID
                    chat_id = contact[2]
                elif name in config.TELEGRAM_CHAT_IDS:
                    chat_id = config.TELEGRAM_CHAT_IDS[name]
                
                if chat_id:
                    try:
                        personal_msg = (
                            f"🔔 <b>THÔNG BÁO LỊCH TRỰC BAN (Gửi thủ công)</b>\n\n"
                            f"Đồng chí <b>{name}</b> có lịch trực buổi <b>{shift}</b> ngày {duty_info['date']}.\n"
                            f"Lãnh đạo trực: {duty_info['leader']}.\n\n"
                            f"Đề nghị đồng chí thực hiện nhiệm vụ nghiêm túc."
                        )
                        await context.bot.send_message(chat_id=chat_id, text=personal_msg, parse_mode='HTML')
                        sent_count += 1
                        log_messages.append(f"✅ Đã gửi cho {name} ({shift})")
                        logger.info(f"Manually sent notification to {name} ({chat_id})")
                        # Log to database
                        self.db.log_notification(duty_info['date'], shift, name, "Success")
                    except Exception as e:
                        log_messages.append(f"❌ Lỗi gửi {name}: {e}")
                        logger.error(f"Failed to send to {name}: {e}")
                        # Log to database
                        self.db.log_notification(duty_info['date'], shift, name, "Failed", str(e))
                else:
                    log_messages.append(f"⚠️ Không tìm thấy ID của {name}")
                    self.db.log_notification(duty_info['date'], shift, name, "Failed", "Không tìm thấy ID")

            # Report back to admin
            summary = "\n".join(log_messages)
            await update.message.reply_text(
                f"<b>KẾT QUẢ GỬI THÔNG BÁO NGÀY {date_str}</b>\n\n"
                f"{summary}\n\n"
                f"Tổng cộng: {sent_count} tin nhắn thành công.",
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Error manual notification: {e}")
            await update.message.reply_text("❌ Có lỗi xảy ra khi gửi thông báo.")

    async def find_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tìm lịch trực theo tên và/hoặc tháng.
        Cú pháp:
          /search [tên]            → Tìm theo tên trong tháng hiện tại
          /search [m/yyyy]         → Xem toàn bộ lịch của tháng chỉ định
          /search [tên] [m/yyyy]   → Tìm theo tên trong tháng chỉ định
        """
        try:
            search_date = datetime.now()
            name_query = ""

            if not context.args:
                # Nếu không nhập gì, tự động tìm theo Telegram ID của người dùng
                user_id = str(update.effective_user.id)
                officer = self.db.get_officer_by_telegram_id(user_id)
                
                if officer:
                    name_query = officer[1] # Cột 'name' trong bảng officers_contact
                    await update.message.reply_text(f"🔍 Đang tìm lịch cho đồng chí <b>{name_query}</b>...", parse_mode='HTML')
                else:
                    await update.message.reply_text(
                        "❌ Bạn chưa đăng ký họ tên. Vui lòng cung cấp tên hoặc dùng lệnh /register.\n"
                        "Ví dụ: /search Nguyễn Văn A hoặc /register Nguyễn Văn A\n"
                        "Hoặc xem lịch theo tháng: /search 3/2026"
                    )
                    return
            else:
                args = list(context.args)
                
                # Thử parse đối số cuối cùng xem có phải tháng/năm không (m/yyyy hoặc mm/yyyy)
                last_arg = args[-1]
                month_parsed = False
                if '/' in last_arg:
                    parts = last_arg.split('/')
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and len(parts[1]) == 4:
                        try:
                            month = int(parts[0])
                            year = int(parts[1])
                            if 1 <= month <= 12:
                                search_date = datetime(year, month, 1)
                                args = args[:-1]  # Bỏ phần tháng/năm ra khỏi danh sách tên
                                month_parsed = True
                        except ValueError:
                            pass  # Không phải tháng/năm, coi như phần tên

                name_query = " ".join(args).strip()

                # --- Trường hợp: CHỈ nhập tháng (không có tên) ---
                if month_parsed and not name_query:
                    # Lấy tên người dùng hiện tại từ Database
                    user_id = str(update.effective_user.id)
                    officer = self.db.get_officer_by_telegram_id(user_id)
                    
                    if officer:
                        name_query = officer[1]
                        await update.message.reply_text(f"🔍 Đang tìm lịch trực của đồng chí <b>{name_query}</b> trong tháng {search_date.month}/{search_date.year}...", parse_mode='HTML')
                    else:
                        await update.message.reply_text(
                            f"❌ Bạn chưa đăng ký họ tên nên không thể tự tìm lịch trong tháng {search_date.month}/{search_date.year}.\n"
                            "Vui lòng dùng lệnh /register [Họ tên] trước, hoặc nhập tên kèm theo tháng.\n"
                            "Ví dụ: /search Nguyễn Văn A 3/2026"
                        )
                        return

            # --- Tìm theo tên (có hoặc không có tháng) ---
            if len(name_query) < 2:
                 await update.message.reply_text(
                     "⚠️ Vui lòng nhập họ tên đầy đủ (ít nhất 2 ký tự) hoặc nhập tháng theo định dạng m/yyyy.\n"
                     "Ví dụ: /search An | /search 3/2026 | /search An 3/2026"
                 )
                 return

            results = self.schedule_mgr.search_duty_schedule(name_query, search_date)
            
            if not results:
                await update.message.reply_text(
                    f"⚠️ Không tìm thấy lịch trực nào cho \"{name_query}\" trong tháng {search_date.month}/{search_date.year}."
                )
                return
            
            # Format output cho tìm kiếm theo tên
            msg = f"🔎 <b>KẾT QUẢ TÌM KIẾM: {name_query} (Tháng {search_date.month}/{search_date.year})</b>\n\n"
            for item in results:
                roles_str = ", ".join(item['roles'])
                msg += f"🗓 <b>{item['date']} ({item['day_of_week']})</b>: {roles_str}\n"
            
            await update.message.reply_text(msg, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Error searching schedule: {e}")
            await update.message.reply_text("❌ Có lỗi xảy ra khi tìm kiếm.")

    async def register_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Đăng ký thông tin người dùng: /dang_ky [Họ tên]"""
        try:
            if not context.args:
                await update.message.reply_text("❌ Vui lòng nhập họ tên đầy đủ. Ví dụ: /dang_ky Nguyễn Văn A")
                return

            full_name = " ".join(context.args)
            chat_id = update.effective_chat.id
            
            # Thêm hoặc cập nhật thông tin trong database
            self.db.add_or_update_officer_contact(full_name, telegram_id=str(chat_id))
            
            await update.message.reply_text(
                f"✅ <b>ĐĂNG KÝ THÀNH CÔNG</b>\n"
                f"- Họ tên: {full_name}\n"
                f"- Telegram ID: <code>{chat_id}</code>\n\n"
                f"Bạn sẽ nhận được thông báo khi có lịch trực ban.",
                parse_mode='HTML'
            )
            logger.info(f"User {full_name} registered with chat_id {chat_id}")

        except Exception as e:
            logger.error(f"Error registering user: {e}")
            await update.message.reply_text("❌ Có lỗi xảy ra khi đăng ký.")

    async def swap_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Đổi ca trực cho nhau: /doi_nhau dd/mm/yyyy [sáng/chiều] dd/mm/yyyy [sáng/chiều]"""
        try:
            if len(context.args) < 4:
                await update.message.reply_text(
                    "❌ Thiếu thông tin. Ví dụ: /doi_nhau 01/02/2026 sáng 02/02/2026 chiều"
                )
                return

            date_str1 = context.args[0]
            shift1 = context.args[1].lower()
            date_str2 = context.args[2]
            shift2 = context.args[3].lower()

            # Validate input
            try:
                date1 = datetime.strptime(date_str1, '%d/%m/%Y')
                date2 = datetime.strptime(date_str2, '%d/%m/%Y')
            except ValueError:
                await update.message.reply_text("❌ Định dạng ngày không đúng. Dùng dd/mm/yyyy")
                return

            if shift1 not in ['sáng', 'chiều'] or shift2 not in ['sáng', 'chiều']:
                await update.message.reply_text("❌ Ca trực không hợp lệ. Dùng 'sáng' hoặc 'chiều'")
                return

            # --- KIỂM TRA QUYỀN ĐỔI CA ---
            user_id = str(update.effective_user.id)
            is_admin = hasattr(config, 'ADMIN_IDS') and user_id in config.ADMIN_IDS
            
            if not is_admin:
                # Lấy tên người yêu cầu từ Database
                requester = self.db.get_officer_by_telegram_id(user_id)
                if not requester:
                    await update.message.reply_text("❌ Bạn chưa đăng ký tài khoản. Vui lòng dùng lệnh /register [Họ tên] trước.")
                    return
                
                requester_name = requester[1].lower().strip()
                
                # Lấy thông tin 2 ca trực cần đổi
                duty1 = self.schedule_mgr.get_duty_info_for_date(date1)
                duty2 = self.schedule_mgr.get_duty_info_for_date(date2)
                
                if not duty1 or not duty2:
                    await update.message.reply_text("❌ Không tìm thấy thông tin lịch trực để xác thực quyền.")
                    return
                
                officer1 = str(duty1['morning_officer'] if shift1 == 'sáng' else duty1['afternoon_officer']).lower().strip()
                officer2 = str(duty2['morning_officer'] if shift2 == 'sáng' else duty2['afternoon_officer']).lower().strip()
                
                # Kiểm tra người gửi có là 1 trong 2 người trực không
                if requester_name != officer1 and requester_name != officer2:
                    await update.message.reply_text(
                        f"⛔ Bạn không có quyền đổi hai ca này.\n"
                        f"Yêu cầu đổi ca phải do chính chủ thực hiện (Đ/c {officer1} hoặc {officer2})."
                    )
                    return
            # -----------------------------

            # Gọi logic đổi ca
            user_info = update.effective_user.full_name
            success, message = self.schedule_mgr.swap_shifts(date1, shift1, date2, shift2, changed_by=user_info)

            if success:
                await update.message.reply_text(f"✅ {message}")
                logger.info(f"Schedule swapped: {message} (by {user_info})")
            else:
                await update.message.reply_text(f"❌ Lỗi: {message}")

        except Exception as e:
            logger.error(f"Error swapping schedule: {e}")
            await update.message.reply_text("❌ Có lỗi xảy ra khi đổi ca.")

    # --- Background Job ---
    async def daily_notification(self, context: ContextTypes.DEFAULT_TYPE):
        """Gửi thông báo hàng ngày"""
        logger.info("Running daily notification job...")
        duty_info = self.schedule_mgr.get_tomorrow_duty()
        
        if not duty_info or duty_info.get('is_off'):
            logger.info("No duty schedule for tomorrow (Off/Empty).")
            return
            
        sent_count = 0
        officers = [
            (duty_info['morning_officer'], 'sáng'),
            (duty_info['afternoon_officer'], 'chiều')
        ]
        
        for name, shift in officers:
            if not name: continue
            
            # Lookup contact
            contact = self.db.get_officer_contact(name)
            chat_id = None
            if contact and contact[2]: # Telegram ID
                chat_id = contact[2]
            elif name in config.TELEGRAM_CHAT_IDS:
                chat_id = config.TELEGRAM_CHAT_IDS[name]
                
            if chat_id:
                try:
                    personal_msg = (
                        f"🔔 <b>THÔNG BÁO LỊCH TRỰC BAN</b>\n\n"
                        f"Đồng chí <b>{name}</b> có lịch trực buổi <b>{shift}</b> ngày {duty_info['date']}.\n"
                        f"Lãnh đạo trực: {duty_info['leader']}.\n\n"
                        f"Đề nghị đồng chí thực hiện nhiệm vụ nghiêm túc."
                    )
                    await context.bot.send_message(chat_id=chat_id, text=personal_msg, parse_mode='HTML')
                    sent_count += 1
                    logger.info(f"Sent notification to {name} ({chat_id})")
                    # Log to database
                    self.db.log_notification(duty_info['date'], shift, name, "Success")
                except Exception as e:
                     logger.error(f"Failed to send to {name}: {e}")
                     # Log to database
                     self.db.log_notification(duty_info['date'], shift, name, "Failed", str(e))
            else:
                    logger.warning(f"Không tìm thấy ID của {name}")
                    self.db.log_notification(duty_info['date'], shift, name, "Failed", "Không tìm thấy ID")
        
        logger.info(f"Daily notification job finished. Sent {sent_count} messages.")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Thống kê chi tiết cho Admin: /stats"""
        # Kiểm tra quyền Admin
        user_id = str(update.effective_user.id)
        if hasattr(config, 'ADMIN_IDS') and user_id not in config.ADMIN_IDS:
             await update.message.reply_text("⛔ Bạn không có quyền thực hiện lệnh này.")
             return

        await update.message.reply_text("📊 Đang tổng hợp dữ liệu thống kê từ tất cả các tháng, vui lòng chờ trong giây lát...")
        
        success, message = self.schedule_mgr.generate_full_report()
        
        if success:
            # Gửi file Excel đã cập nhật cho Admin
            filepath = self.schedule_mgr.get_master_schedule_path()
            try:
                with open(filepath, 'rb') as doc:
                    await update.message.reply_document(
                        document=doc,
                        filename="Bao_Cao_Thong_Ke.xlsx",
                        caption=f"✅ {message}\nBảng thống kê đã được thêm vào sheet đầu tiên của file Excel."
                    )
            except Exception as e:
                await update.message.reply_text(f"❌ Lỗi khi gửi file: {str(e)}")
        else:
            await update.message.reply_text(f"❌ Lỗi khi tạo thống kê: {message}")

    # --- Monthly Auto-Schedule Job ---
    async def monthly_auto_schedule_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Job chạy hàng ngày, kiểm tra nếu đúng ngày cấu hình thì tự động xếp lịch tháng tiếp theo"""
        today = datetime.now(VN_TZ)
        target_day = getattr(config, 'AUTO_SCHEDULE_DAY', 25)
        
        # Chỉ chạy vào đúng ngày đã cấu hình
        if today.day != target_day:
            return
        
        logger.info(f"🗓️ Bắt đầu xếp lịch tự động cho tháng tiếp theo (ngày {target_day} hàng tháng)...")
        
        # Tính tháng tiếp theo
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year
        
        month_year = f"{next_month}-{next_year}"
        
        # Lấy danh sách lãnh đạo từ config
        leaders = getattr(config, 'AUTO_SCHEDULE_LEADERS', None)
        if not leaders:
            error_msg = "❌ Chưa cấu hình AUTO_SCHEDULE_LEADERS trong config.py. Không thể xếp lịch tự động."
            logger.error(error_msg)
            for admin_id in config.ADMIN_IDS:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=error_msg)
                except Exception as e:
                    logger.error(f"Lỗi gửi thông báo lỗi cho Admin {admin_id}: {e}")
            return
        
        # Gọi hàm xếp lịch (names=None để tự lấy từ sheet 'DS trực')
        success, message = self.schedule_mgr.auto_generate_round_robin(month_year, names=None, leaders=leaders)
        
        # Gửi kết quả cho tất cả Admin
        for admin_id in config.ADMIN_IDS:
            try:
                if success:
                    filepath = self.schedule_mgr.get_master_schedule_path()
                    with open(filepath, 'rb') as doc:
                        await context.bot.send_document(
                            chat_id=admin_id,
                            document=doc,
                            filename=f"Lich_Truc_{month_year}.xlsx",
                            caption=(
                                f"📅 <b>XẾP LỊCH TỰ ĐỘNG THÀNH CÔNG</b>\n\n"
                                f"✅ {message}\n"
                                f"Tháng: <b>{month_year}</b>\n"
                                f"Lãnh đạo: {', '.join(leaders)}\n\n"
                                f"Hãy kiểm tra sheet '<b>{month_year}</b>' trong file đính kèm."
                            ),
                            parse_mode='HTML'
                        )
                    logger.info(f"Đã gửi lịch tự động tháng {month_year} cho Admin {admin_id}")
                else:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=(
                            f"❌ <b>XẾP LỊCH TỰ ĐỘNG THẤT BẠI</b>\n\n"
                            f"Tháng: {month_year}\n"
                            f"Lỗi: {message}"
                        ),
                        parse_mode='HTML'
                    )
                    logger.error(f"Xếp lịch tự động tháng {month_year} thất bại: {message}")
            except Exception as e:
                logger.error(f"Lỗi gửi kết quả auto-schedule cho Admin {admin_id}: {e}")

    async def auto_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xếp lịch tự động: /auto_schedule [m-yyyy] [danh_sách_cán_bộ] | [danh_sách_lãnh_đạo]"""
        user_id = str(update.effective_user.id)
        if hasattr(config, 'ADMIN_IDS') and user_id not in config.ADMIN_IDS:
             await update.message.reply_text("⛔ Bạn không có quyền thực hiện lệnh này.")
             return

        if not context.args:
            await update.message.reply_text(
                "⚠️ Cách dùng 1 (Lấy tên từ DS trực): /auto_schedule [m-yyyy] | [Lãnh đạo]\n"
                "Ví dụ: /auto_schedule 3-2026 | Lãnh Đạo A, Lãnh Đạo B\n\n"
                "⚠️ Cách dùng 2 (Chỉ định người bắt đầu): /auto_schedule [m-yyyy] [Tên] | [Lãnh đạo]\n"
                "Ví dụ: /auto_schedule 3-2026 Hải | Lãnh Đạo A\n\n"
                "⚠️ Cách dùng 3 (Nhập DS thủ công): /auto_schedule [m-yyyy] [Tên_A, Tên_B] | [Lãnh đạo]\n"
                "Ví dụ: /auto_schedule 3-2026 Hải, Việt | Lãnh Đạo A"
            )
            return

        try:
            full_text = " ".join(context.args)
            month_year = context.args[0]
            
            # Phần còn lại sau month_year
            content = full_text.replace(month_year, "", 1).strip()
            
            if '|' in content:
                parts = content.split('|')
                names_str = parts[0].strip()
                leaders_str = parts[1].strip()
                
                leaders = [n.strip() for n in leaders_str.split(',') if n.strip()]
                
                # Phân biệt 3 trường hợp:
                # 1. Không nhập tên (trước dấu | trống) → names=None, start_name=None
                # 2. Nhập 1 tên (không có dấu phẩy) → đó là người bắt đầu, start_name=tên đó
                # 3. Nhập nhiều tên (có dấu phẩy) → đó là danh sách đầy đủ, names=list
                names = None
                start_name = None
                
                if names_str:
                    if ',' in names_str:
                        # Nhiều tên → danh sách đầy đủ
                        names = [n.strip() for n in names_str.split(',') if n.strip()]
                    else:
                        # 1 tên duy nhất → người bắt đầu
                        start_name = names_str
            else:
                # Nếu không có dấu |, coi như chỉ nhập tháng (lỗi hoặc thiếu)
                await update.message.reply_text("❌ Vui lòng cung cấp danh sách lãnh đạo sau dấu gạch đứng '|'.")
                return
            
            if not leaders:
                await update.message.reply_text("❌ Thiếu danh sách lãnh đạo.")
                return

            if start_name:
                await update.message.reply_text(f"⏳ Đang xếp lịch vòng tròn cho tháng {month_year}, bắt đầu từ <b>{start_name}</b>...", parse_mode='HTML')
            else:
                await update.message.reply_text(f"⏳ Đang tự động xếp lịch vòng tròn cho tháng {month_year}...")
            
            success, message = self.schedule_mgr.auto_generate_round_robin(month_year, names, leaders, start_name=start_name)
            
            if success:
                 # Gửi file Excel cho Admin kiểm tra
                filepath = self.schedule_mgr.get_master_schedule_path()
                with open(filepath, 'rb') as doc:
                    await update.message.reply_document(
                        document=doc,
                        filename=f"Lich_Truc_{month_year}.xlsx",
                        caption=f"✅ {message}\nBạn hãy kiểm tra sheet '{month_year}' trong file đính kèm."
                    )
            else:
                await update.message.reply_text(f"❌ Lỗi: {message}")

        except Exception as e:
            logger.error(f"Error in auto_schedule: {e}")
            await update.message.reply_text(f"❌ Có lỗi xảy ra: {str(e)}")


if __name__ == '__main__':
    if 'YOUR_TELEGRAM_BOT_TOKEN' in config.TELEGRAM_BOT_TOKEN:
        print("⚠️ Vui lòng cấu hình TELEGRAM_BOT_TOKEN trong config.py trước khi chạy bot!")
        exit(1)

    bot_logic = DutyBot()
    
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Add Command Handlers
    app.add_handler(CommandHandler("start", bot_logic.start))
    app.add_handler(CommandHandler("help", bot_logic.help_command))
    app.add_handler(CommandHandler("today", bot_logic.today_schedule))
    app.add_handler(CommandHandler("tomorrow", bot_logic.tomorrow_schedule))
    app.add_handler(CommandHandler("check", bot_logic.check_schedule))
    app.add_handler(CommandHandler("change", bot_logic.change_schedule))
    app.add_handler(CommandHandler("send_noti", bot_logic.manual_notification))
    app.add_handler(CommandHandler("search", bot_logic.find_schedule))
    app.add_handler(CommandHandler("register", bot_logic.register_user))
    app.add_handler(CommandHandler("swap", bot_logic.swap_schedule))
    app.add_handler(CommandHandler("stats", bot_logic.stats_command))
    app.add_handler(CommandHandler("auto_schedule", bot_logic.auto_schedule_command))
    
    # Job Queue
    job_queue = app.job_queue
    # Parse configured time
    try:
        notify_time_str = config.NOTIFICATION_TIME
        h, m = map(int, notify_time_str.split(':'))
        notify_time = time(hour=h, minute=m, tzinfo=VN_TZ)
        job_queue.run_daily(bot_logic.daily_notification, time=notify_time)
        print(f"✅ Đã lên lịch gửi thông báo hàng ngày vào lúc {notify_time_str} (Múi giờ: {VN_TZ})")
    except Exception as e:
        print(f"❌ Lỗi cấu hình thời gian: {e}")

    # Monthly auto-schedule job (chạy daily, kiểm tra ngày bên trong)
    try:
        auto_time_str = getattr(config, 'AUTO_SCHEDULE_TIME', '08:00')
        ah, am = map(int, auto_time_str.split(':'))
        auto_time = time(hour=ah, minute=am, tzinfo=VN_TZ)
        job_queue.run_daily(bot_logic.monthly_auto_schedule_job, time=auto_time)
        auto_day = getattr(config, 'AUTO_SCHEDULE_DAY', 25)
        print(f"✅ Đã lên lịch xếp lịch tự động vào ngày {auto_day} hàng tháng lúc {auto_time_str}")
    except Exception as e:
        print(f"❌ Lỗi cấu hình auto schedule: {e}")

    print("🤖 Bot đang chạy...")
    app.run_polling()
