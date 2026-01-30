#!/usr/bin/env python
# setup.py
# Script thiết lập hệ thống lần đầu

import os
import sys
import subprocess

def print_header(text):
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")

def install_requirements():
    """Cài đặt các thư viện cần thiết"""
    print_header("BƯỚC 1: CÀI ĐẶT THƯ VIỆN")
    
    print("Đang cài đặt các thư viện cần thiết...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Đã cài đặt thành công!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Cài đặt thất bại! Vui lòng kiểm tra lại.")
        return False

def create_directories():
    """Tạo các thư mục cần thiết"""
    print_header("BƯỚC 2: TẠO THƯ MỤC")
    
    directories = ['lich-truc-ban', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Đã tạo thư mục: {directory}")
        else:
            print(f"• Thư mục đã tồn tại: {directory}")
    
    return True

def setup_config():
    """Thiết lập cấu hình"""
    print_header("BƯỚC 3: CẤU HÌNH HỆ THỐNG")
    
    print("Vui lòng nhập thông tin cấu hình:")
    print("\n[Cấu hình Telegram Bot]")
    bot_token = input("Telegram Bot Token (bỏ trống nếu chưa có): ").strip()
    
    if bot_token:
        print("\nĐã nhận Bot Token!")
        print("\nLưu ý: Bạn cần thêm Chat ID của các cán bộ vào file config.py sau.")
    else:
        print("\nChưa có Bot Token. Bạn có thể cấu hình sau trong file config.py")
    
    # Cập nhật config.py nếu có bot token
    if bot_token and os.path.exists('config.py'):
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.replace(
                'TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"',
                f'TELEGRAM_BOT_TOKEN = "{bot_token}"'
            )
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ Đã cập nhật Bot Token vào config.py")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật config: {e}")
    
    return True

def initialize_database():
    """Khởi tạo database"""
    print_header("BƯỚC 4: KHỞI TẠO DATABASE")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✓ Đã khởi tạo database thành công!")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo database: {e}")
        return False

def create_sample_schedule():
    """Tạo file lịch trực mẫu"""
    print_header("BƯỚC 5: TẠO FILE LỊCH TRỰC MẪU")
    
    create = input("Bạn có muốn tạo file lịch trực mẫu không? (y/n): ").strip().lower()
    
    if create == 'y':
        try:
            subprocess.check_call([sys.executable, "create_sample_schedule.py"])
            print("✓ Đã tạo file lịch trực mẫu!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Không thể tạo file mẫu!")
            return False
    else:
        print("• Đã bỏ qua bước này.")
        return True

def print_next_steps():
    """In hướng dẫn các bước tiếp theo"""
    print_header("CÁC BƯỚC TIẾP THEO")
    
    print("""
1. Cấu hình Telegram Bot:
   - Mở file config.py
   - Thêm Chat ID của các cán bộ vào TELEGRAM_CHAT_IDS
   - Hoặc sử dụng chức năng [5] trong menu chính để thêm

2. Chuẩn bị file lịch trực:
   - Đặt file Excel vào thư mục 'lich-truc-ban/'
   - Định dạng tên: lich-truc-ban-thangMM-YYYY.xlsx
   - Đảm bảo đúng cấu trúc như trong README.md

3. Chạy thử hệ thống:
   python main.py

4. Chạy demo để làm quen:
   python demo_usage.py

5. Thiết lập gửi thông báo tự động:
   python scheduler.py

Xem chi tiết trong file README.md
""")

def main():
    """Chạy toàn bộ quá trình setup"""
    print_header("THIẾT LẬP HỆ THỐNG QUẢN LÝ LỊCH TRỰC BAN")
    
    print("Chào mừng bạn đến với hệ thống quản lý lịch trực ban!")
    print("Script này sẽ giúp bạn thiết lập hệ thống lần đầu tiên.\n")
    
    input("Nhấn Enter để bắt đầu...")
    
    # Các bước thiết lập
    steps = [
        ("Cài đặt thư viện", install_requirements),
        ("Tạo thư mục", create_directories),
        ("Cấu hình hệ thống", setup_config),
        ("Khởi tạo database", initialize_database),
        ("Tạo file mẫu", create_sample_schedule),
    ]
    
    for step_name, step_func in steps:
        success = step_func()
        if not success:
            print(f"\n❌ Thiết lập thất bại ở bước: {step_name}")
            return False
    
    print_header("HOÀN TẤT THIẾT LẬP!")
    print("✓ Hệ thống đã sẵn sàng sử dụng!")
    
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy thiết lập!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
