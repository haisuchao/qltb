# schedule_manager.py
# Module quản lý lịch trực ban từ file Excel (Format mới Multi-sheet)

import pandas as pd
import os
import glob
from datetime import datetime, timedelta
import config
from database import DatabaseManager
from drive_client import DriveClient

class ScheduleManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.drive = DriveClient()
        self.use_drive = hasattr(config, 'DRIVE_FILE_ID') and config.DRIVE_FILE_ID != "YOUR_DRIVE_FILE_ID_HERE"
    
    def get_schedule_sheet_name(self, date):
        """Lấy tên sheet tương ứng với tháng của ngày cần tra cứu"""
        # Format sheet name: m-yyyy (ví dụ: 8-2025)
        return f"{date.month}-{date.year}"
    
    
    def sync_from_drive(self):
        """Tải file mới nhất từ Drive về"""
        if not self.use_drive:
            return False
            
        local_path = self.get_master_schedule_path()
        if not local_path:
             local_path = os.path.join(config.SCHEDULE_FOLDER, config.MASTER_SCHEDULE_FILE)
             
        print("Đang đồng bộ từ Drive...")
        return self.drive.download_file(config.DRIVE_FILE_ID, local_path)

    def get_master_schedule_path(self):
        """Lấy đường dẫn file lịch trực tổng hợp"""
        # Ưu tiên file master được cấu hình
        if hasattr(config, 'MASTER_SCHEDULE_FILE'):
             path = os.path.join(config.SCHEDULE_FOLDER, config.MASTER_SCHEDULE_FILE)
             if os.path.exists(path):
                 return path
        
        # Fallback: tìm file Excel bất kỳ trong thư mục
        files = glob.glob(os.path.join(config.SCHEDULE_FOLDER, "*.xlsx"))
        if files:
            return files[0]
        return None
    
    def read_schedule_for_date(self, date):
        """Đọc lịch trực từ file Excel (Sheet tương ứng)"""
        filepath = self.get_master_schedule_path()
        if not filepath:
            print(f"Không tìm thấy file lịch trực trong {config.SCHEDULE_FOLDER}")
            return None
            
        sheet_name = self.get_schedule_sheet_name(date)
        
        try:
            # Kiểm tra xem sheet có tồn tại không
            xl = pd.ExcelFile(filepath)
            if sheet_name not in xl.sheet_names:
                # Thử format mm-yyyy nếu m-yyyy không có (ví dụ 08-2025)
                sheet_name_alt = f"{date.month:02d}-{date.year}"
                if sheet_name_alt in xl.sheet_names:
                    sheet_name = sheet_name_alt
                else:
                    print(f"Không tìm thấy sheet {sheet_name} trong file {filepath}")
                    return None
            
            # Đọc dữ liệu với header ở dòng 4 (index 3)
            # Columns: Ngày, Thứ, Trực ban 1 (Sáng), Trực ban 2 (Chiều), Trực lãnh đạo
            df = pd.read_excel(filepath, sheet_name=sheet_name, header=3)
            
            # Chuẩn hóa tên cột để dễ xử lý (lấy theo index vì tên cột có thể thay đổi)
            # Index: 0=Date, 1=Day, 2=Morning, 3=Afternoon, 4=Leader
            if len(df.columns) < 5:
                print("File Excel không đủ số cột yêu cầu")
                return None
                
            # Đổi tên cột tạm thời để truy cập
            df.columns.values[0] = 'Date'
            df.columns.values[2] = 'Morning'
            df.columns.values[3] = 'Afternoon'
            df.columns.values[4] = 'Leader'
            
            return df
        except Exception as e:
            print(f"Lỗi khi đọc file {filepath} (Sheet {sheet_name}): {str(e)}")
            return None
    
    def get_duty_info_for_date(self, date):
        """Lấy thông tin trực ban cho một ngày cụ thể"""
        # Nếu dùng Drive, thử sync trước khi đọc
        if self.use_drive:
            self.sync_from_drive()
            
        df = self.read_schedule_for_date(date)
        
        if df is None:
            return None
        
        # Tìm dòng ứng với ngày
        # Chuyển đổi cột Date sang datetime để so sánh
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        target_date = pd.Timestamp(date.year, date.month, date.day)
        
        # Lọc dữ liệu
        duty_row = df[df['Date'] == target_date]
        
        if duty_row.empty:
            return None
        
        row = duty_row.iloc[0]
        
        # Xử lý các ô merged/empty (Weekend/Holiday)
        morning = row['Morning'] if pd.notna(row['Morning']) else None
        afternoon = row['Afternoon'] if pd.notna(row['Afternoon']) else None
        leader = row['Leader'] if pd.notna(row['Leader']) else None
        
        # Nếu không có ai trực (ngày nghỉ/lễ mà không phân công)
        if not morning and not afternoon and not leader:
             # Có thể trả về None hoặc object báo là ngày nghỉ
             return {
                'date': date.strftime('%d/%m/%Y'),
                'day_of_week': row.iloc[1] if pd.notna(row.iloc[1]) else '',
                'is_off': True,
                'morning_officer': None,
                'afternoon_officer': None,
                'leader': None
            }

        result = {
            'date': date.strftime('%d/%m/%Y'),
            'day_of_week': row.iloc[1] if pd.notna(row.iloc[1]) else '',
            'is_off': False,
            'morning_officer': str(morning).strip() if morning else None,
            'afternoon_officer': str(afternoon).strip() if afternoon else None,
            'leader': str(leader).strip() if leader else None
        }
        
        return result
    
    def get_tomorrow_duty(self):
        """Lấy thông tin trực ban ngày mai"""
        tomorrow = datetime.now() + timedelta(days=1)
        return self.get_duty_info_for_date(tomorrow)
    
    def update_schedule(self, date, shift, new_officer, old_officer=None, reason="", changed_by=""):
        """Cập nhật lịch trực (đổi người trực)"""
        if shift not in ['sáng', 'chiều']:
             print("Ca trực không hợp lệ")
             return False

        filepath = self.get_master_schedule_path()
        if not filepath:
            return False
            
        sheet_name = self.get_schedule_sheet_name(date)
        
        try:
             # Đọc file để lấy index dòng cần sửa
             # Lưu ý: openpyxl index bắt đầu từ 1.
             # Pandas read_excel header=3 nghĩa là dữ liệu bắt đầu từ row 5 (index 4 trong 0-based của list, nhưng row 5 trong Excel)
             
             # Pull latest version first to avoid conflicts
             if self.use_drive:
                 self.sync_from_drive()

             # Cách an toàn nhất: Dùng openpyxl trực tiếp để load và save bảo toàn định dạng
             from openpyxl import load_workbook
             
             wb = load_workbook(filepath, data_only=True)
             if sheet_name not in wb.sheetnames:
                 # Check alt name
                 alt_name = f"{date.month:02d}-{date.year}"
                 if alt_name in wb.sheetnames:
                    sheet_name = alt_name
                 else:
                    return False
             
             ws = wb[sheet_name]
             
             # Tìm dòng chứa ngày
             target_row = None
             date_col_idx = 1 # Column A
             
             # Duyệt qua các dòng (bắt đầu từ dòng 5 do header là dòng 4)
             # So sánh dạng text để tránh lỗi định dạng
             target_date_str = date.strftime('%d/%m/%Y')
             
             for row in ws.iter_rows(min_row=5):
                 cell_val = row[0].value # Cột A
                 cell_date_str = None

                 if isinstance(cell_val, datetime):
                     cell_date_str = cell_val.strftime('%d/%m/%Y')
                 elif isinstance(cell_val, str):
                     # Chuẩn hóa về định dạng dd/mm/yyyy
                     cell_val_clean = cell_val.strip()
                     # Thử parse và format lại
                     for fmt in ('%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%d'):
                         try:
                             parsed = datetime.strptime(cell_val_clean, fmt)
                             cell_date_str = parsed.strftime('%d/%m/%Y')
                             break
                         except ValueError:
                             continue
                     # Nếu không parse được, so sánh trực tiếp
                     if not cell_date_str:
                         cell_date_str = cell_val_clean
                 print(f'cell_date_str: {cell_date_str}')
                 
                 if cell_date_str and cell_date_str == target_date_str:
                     target_row = row
                     break
            
             if not target_row:
                 print(f"Không tìm thấy ngày {date} trong sheet {sheet_name}")
                 return False
             
             # Xác định cột cần sửa
             # A=1, B=2, C=3 (Sáng), D=4 (Chiều)
             if shift == 'sáng':
                 cell_to_edit = target_row[2] # Cột C
                 current_val = cell_to_edit.value
             else:
                 cell_to_edit = target_row[3] # Cột D
                 current_val = cell_to_edit.value
             
             if old_officer is None:
                 old_officer = current_val
             
             # Cập nhật giá trị
             cell_to_edit.value = new_officer
             
             wb.save(filepath)
             
             # Push to Drive
             if self.use_drive:
                 print("Đang đẩy lên Drive...")
                 self.drive.upload_file(config.DRIVE_FILE_ID, filepath)
             
             # Log
             self.db.log_schedule_change(
                duty_date=date.strftime('%d/%m/%Y'),
                shift=shift,
                old_officer=str(old_officer) if old_officer else "N/A",
                new_officer=new_officer,
                reason=reason,
                approved_by=changed_by
            )
             
             return True
             
        except Exception as e:
            print(f"Lỗi update: {e}")
            return False

    def get_statistics(self, start_date, end_date):
        """Thống kê số buổi trực"""
        stats = {}
        # Duyệt qua các tháng trong khoảng thời gian
        # Để đơn giản, duyệt qua từng ngày (hơi chậm nếu range lớn nhưng chính xác)
        # Tối ưu: Duyệt qua từng tháng, đọc sheet tương ứng 1 lần
        
        current_month_start = start_date.replace(day=1)
        
        while current_month_start <= end_date:
            # Xác định sheet của tháng này
            df = self.read_schedule_for_date(current_month_start)
            
            if df is not None:
                # Lọc các ngày trong tháng nằm trong khoảng start-end
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                mask = (df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))
                df_filtered = df[mask]
                
                for _, row in df_filtered.iterrows():
                     morning = row['Morning']
                     afternoon = row['Afternoon']
                     
                     if pd.notna(morning):
                         stats[morning] = stats.get(morning, 0) + 1
                     if pd.notna(afternoon):
                         stats[afternoon] = stats.get(afternoon, 0) + 1
            
            # Sang tháng tiếp theo
            if current_month_start.month == 12:
                current_month_start = current_month_start.replace(year=current_month_start.year+1, month=1)
            else:
                current_month_start = current_month_start.replace(month=current_month_start.month+1)
                
        return stats

    def export_statistics_to_excel(self, start_date, end_date, output_file):
        """Xuất thống kê ra file Excel"""
        stats = self.get_statistics(start_date, end_date)
        
        df = pd.DataFrame(list(stats.items()), columns=['Họ tên', 'Số buổi trực'])
        df = df.sort_values('Số buổi trực', ascending=False)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            period = f"Thống kê từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
            header_df = pd.DataFrame([period])
            header_df.to_excel(writer, index=False, header=False, sheet_name='Thống kê')
            df.to_excel(writer, index=False, startrow=2, sheet_name='Thống kê')
            
        print(f"Đã xuất thống kê ra file: {output_file}")
        return output_file

    def search_duty_schedule(self, name_query, date=None):
        """Tìm lịch trực của một người trong tháng (theo ngày cung cấp hoặc tháng hiện tại)"""
        if date is None:
            date = datetime.now()
            
        # Đảm bảo có dữ liệu mới nhất
        if self.use_drive:
            self.sync_from_drive()
            
        df = self.read_schedule_for_date(date)
        if df is None:
            return []
            
        results = []
        name_query = name_query.lower()
        
        # Duyệt qua từng dòng
        # Chuẩn hóa cột Date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        for index, row in df.iterrows():
            # Check Morning
            morning = str(row.get('Morning', '')).lower()
            # Check Afternoon
            afternoon = str(row.get('Afternoon', '')).lower()
            # Check Leader
            leader = str(row.get('Leader', '')).lower()
            
            matched_role = []
            if name_query in morning:
                matched_role.append('Sáng')
            if name_query in afternoon:
                matched_role.append('Chiều')
            if name_query in leader:
                matched_role.append('Lãnh đạo')
                
            if matched_role:
                duty_date = row['Date']
                if pd.notna(duty_date):
                    results.append({
                        'date': duty_date.strftime('%d/%m/%Y'),
                        'day_of_week': row.iloc[1] if pd.notna(row.iloc[1]) else '',
                        'roles': matched_role
                    })
                    
        return results

    def swap_shifts(self, date1, shift1, date2, shift2, changed_by=""):
        """Đổi chỗ hai ca trực (có thể cùng ngày hoặc khác ngày)"""
        if shift1 not in ['sáng', 'chiều'] or shift2 not in ['sáng', 'chiều']:
             print("Ca trực không hợp lệ")
             return False, "Ca trực không hợp lệ (chỉ 'sáng' hoặc 'chiều')"

        filepath = self.get_master_schedule_path()
        if not filepath:
            return False, "Không tìm thấy file lịch trực"
            
        try:
             # Sync before change
             if self.use_drive:
                 self.sync_from_drive()

             from openpyxl import load_workbook
             # Load with data_only=True to read formula values as dates
             wb = load_workbook(filepath, data_only=True)
             
             # Sheets for both dates
             sheet_name1 = self.get_schedule_sheet_name(date1)
             sheet_name2 = self.get_schedule_sheet_name(date2)
             
             if sheet_name1 not in wb.sheetnames or sheet_name2 not in wb.sheetnames:
                 return False, "Không tìm thấy sheet tương ứng với tháng/năm"

             ws1 = wb[sheet_name1]
             ws2 = wb[sheet_name2]
             
             target_date_str1 = date1.strftime('%d/%m/%Y')
             target_date_str2 = date2.strftime('%d/%m/%Y')
             
             row1_idx = None
             row2_idx = None
             
             # Helper to normalize date and find row
             def find_row_idx(ws, target_str):
                 for i, row in enumerate(ws.iter_rows(min_row=5), start=5):
                     cell_val = row[0].value
                     cell_date_str = None
                     if isinstance(cell_val, datetime):
                         cell_date_str = cell_val.strftime('%d/%m/%Y')
                     elif isinstance(cell_val, str):
                         cell_val_clean = cell_val.strip()
                         for fmt in ('%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%d'):
                             try:
                                 cell_date_str = datetime.strptime(cell_val_clean, fmt).strftime('%d/%m/%Y')
                                 break
                             except ValueError: continue
                         if not cell_date_str: cell_date_str = cell_val_clean
                     if cell_date_str == target_str:
                         return i
                 return None

             row1_idx = find_row_idx(ws1, target_date_str1)
             row2_idx = find_row_idx(ws2, target_date_str2)

             if not row1_idx or not row2_idx:
                 return False, "Không tìm thấy ngày trực trong lịch"

             # Identify columns: C=3 (morning), D=4 (afternoon)
             col1 = 3 if shift1 == 'sáng' else 4
             col2 = 3 if shift2 == 'sáng' else 4
             
             officer1 = ws1.cell(row=row1_idx, column=col1).value
             officer2 = ws2.cell(row=row2_idx, column=col2).value
             
             # Swap values
             ws1.cell(row=row1_idx, column=col1, value=officer2)
             ws2.cell(row=row2_idx, column=col2, value=officer1)
             
             wb.save(filepath)
             
             if self.use_drive:
                 self.drive.upload_file(config.DRIVE_FILE_ID, filepath)
                 
             # Log changes
             self.db.log_schedule_change(
                 duty_date=target_date_str1, shift=shift1,
                 old_officer=str(officer1), new_officer=str(officer2),
                 reason="Đổi chéo ca", approved_by=changed_by
             )
             self.db.log_schedule_change(
                 duty_date=target_date_str2, shift=shift2,
                 old_officer=str(officer2), new_officer=str(officer1),
                 reason="Đổi chéo ca", approved_by=changed_by
             )
             
             return True, f"Đã đổi '{officer1}' ({target_date_str1} {shift1}) với '{officer2}' ({target_date_str2} {shift2})"
             
        except Exception as e:
            print(f"Lỗi swap: {e}")
            return False, str(e)
