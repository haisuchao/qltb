# database.py
# Module quản lý database cho hệ thống lịch trực ban

import sqlite3
from datetime import datetime
import config

class DatabaseManager:
    def __init__(self):
        self.db_file = config.DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database và các bảng cần thiết"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Bảng lưu nhật ký thông báo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                shift TEXT NOT NULL,
                officer_name TEXT NOT NULL,
                notification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                message TEXT
            )
        ''')
        
        # Bảng lưu nhật ký đổi lịch
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule_change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duty_date TEXT NOT NULL,
                shift TEXT NOT NULL,
                old_officer TEXT NOT NULL,
                new_officer TEXT NOT NULL,
                reason TEXT,
                approved_by TEXT
            )
        ''')
        
        # Bảng lưu thông tin liên hệ cán bộ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS officers_contact (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                telegram_id TEXT,
                phone TEXT,
                email TEXT
            )
        ''')

        # Bảng lưu các năm học đã có file template và năm đang được quản lý (current)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS available_years (
                year INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                is_current BOOLEAN NOT NULL DEFAULT 0
            )
        ''')

        # Migration: xóa cột facebook_id nếu còn tồn tại từ phiên bản cũ
        cursor.execute('PRAGMA table_info(officers_contact)')
        columns = [col[1] for col in cursor.fetchall()]
        if 'facebook_id' in columns:
            cursor.execute('''
                CREATE TABLE officers_contact_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    telegram_id TEXT,
                    phone TEXT,
                    email TEXT
                )
            ''')
            cursor.execute('''
                INSERT INTO officers_contact_new (id, name, telegram_id, phone, email)
                SELECT id, name, telegram_id, phone, email FROM officers_contact
            ''')
            cursor.execute('DROP TABLE officers_contact')
            cursor.execute('ALTER TABLE officers_contact_new RENAME TO officers_contact')
        
        conn.commit()
        conn.close()
    
    def log_notification(self, date, shift, officer_name, status, message=""):
        """Ghi log thông báo"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notification_log (date, shift, officer_name, status, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, shift, officer_name, status, message))
        conn.commit()
        conn.close()
    
    def log_schedule_change(self, duty_date, shift, old_officer, new_officer, reason="", approved_by=""):
        """Ghi log đổi lịch trực"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO schedule_change_log (duty_date, shift, old_officer, new_officer, reason, approved_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (duty_date, shift, old_officer, new_officer, reason, approved_by))
        conn.commit()
        conn.close()
    
    def add_or_update_officer_contact(self, name, telegram_id=None, phone=None, email=None):
        """Thêm hoặc cập nhật thông tin liên hệ cán bộ"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO officers_contact (name, telegram_id, phone, email)
            VALUES (?, ?, ?, ?)
        ''', (name, telegram_id, phone, email))
        conn.commit()
        conn.close()
    
    def get_officer_contact(self, name):
        """Lấy thông tin liên hệ của cán bộ"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM officers_contact WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_officer_by_telegram_id(self, telegram_id):
        """Lấy thông tin cán bộ qua Telegram ID"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM officers_contact WHERE telegram_id = ?', (str(telegram_id),))
        result = cursor.fetchone()
        conn.close()
        return result

    def rename_officer_contact(self, old_name, new_name):
        """Đổi tên trong officers_contact (khi admin sửa tên cán bộ bị ghi sai).
        Trả về 'renamed', 'not_found', hoặc 'conflict' (tên mới đã được đăng ký bởi người khác)."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM officers_contact WHERE name = ?', (old_name,))
        if not cursor.fetchone():
            conn.close()
            return 'not_found'

        cursor.execute('SELECT id FROM officers_contact WHERE name = ?', (new_name,))
        if cursor.fetchone():
            conn.close()
            return 'conflict'

        cursor.execute('UPDATE officers_contact SET name = ? WHERE name = ?', (new_name, old_name))
        conn.commit()
        conn.close()
        return 'renamed'

    def add_available_year(self, year, filename):
        """Đăng ký một năm học có file template tương ứng (không tự đổi is_current)"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO available_years (year, filename, is_current)
            VALUES (?, ?, 0)
            ON CONFLICT(year) DO UPDATE SET filename = excluded.filename
        ''', (year, filename))
        conn.commit()
        conn.close()

    def set_current_year(self, year):
        """Đặt một năm học làm năm hiện tại (is_current=True), các năm khác về False"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM available_years WHERE year = ?', (year,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Năm {year} chưa có trong danh sách available_years")
        cursor.execute('UPDATE available_years SET is_current = 0')
        cursor.execute('UPDATE available_years SET is_current = 1 WHERE year = ?', (year,))
        conn.commit()
        conn.close()

    def get_current_year_row(self):
        """Lấy (year, filename) của năm đang được quản lý hiện tại, hoặc None"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT year, filename FROM available_years WHERE is_current = 1 LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result

    def get_all_years(self):
        """Lấy toàn bộ danh sách năm học đã có template: [(year, filename, is_current), ...]"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT year, filename, is_current FROM available_years ORDER BY year')
        results = cursor.fetchall()
        conn.close()
        return results


    def get_notification_history(self, start_date=None, end_date=None):
        """Lấy lịch sử thông báo"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT * FROM notification_log 
                WHERE date BETWEEN ? AND ?
                ORDER BY notification_time DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('SELECT * FROM notification_log ORDER BY notification_time DESC LIMIT 100')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_schedule_change_history(self, start_date=None, end_date=None):
        """Lấy lịch sử đổi lịch"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT * FROM schedule_change_log 
                WHERE duty_date BETWEEN ? AND ?
                ORDER BY change_date DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('SELECT * FROM schedule_change_log ORDER BY change_date DESC LIMIT 100')
        
        results = cursor.fetchall()
        conn.close()
        return results
