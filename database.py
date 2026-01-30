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
                facebook_id TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        
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
    
    def add_or_update_officer_contact(self, name, telegram_id=None, facebook_id=None, phone=None, email=None):
        """Thêm hoặc cập nhật thông tin liên hệ cán bộ"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO officers_contact (name, telegram_id, facebook_id, phone, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, telegram_id, facebook_id, phone, email))
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
