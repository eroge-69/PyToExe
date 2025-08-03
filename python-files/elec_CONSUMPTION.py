import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os
import numpy as np
# تابع تبدیل ایندکس به تاریخ شمسی

def index_to_persian_date(index_in_pandas):
    day_of_year = index_in_pandas - 1
    
    # تعریف تقویم شمسی
    cumulative_days = [0, 31, 62, 93, 124, 155, 186, 216, 246, 276, 306, 336, 365]
    month_names = [
        "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
        "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"
    ]
    
    # پیدا کردن ماه
    month = 1
    for i in range(1, len(cumulative_days)):
        if day_of_year < cumulative_days[i]:
            month = i
            break
    
    # محاسبه روز در ماه
    day_in_month = day_of_year - cumulative_days[month-1] + 1
    
    return {
        "day_of_year": day_of_year,
        "month": month,
        "month_name": month_names[month-1],
        "day_in_month": day_in_month,
        "persian_date": f"{month_names[month-1]} {day_in_month}"
    }


def main():
    try:
        # 1. تنظیم مسیرهای فایل
        file_path = r"z:\4-ELECTRICITY CONSUMPTION\ENERGY Report -24 o'clock-1404.xlsb"
        bg_image_path = r'C:\Temp\Tennet.jpg'
        output_path = r'C:\Users\samsami.e\Desktop\Energy_Report.png'
        
        # بررسی وجود فایل اکسل
        if not os.path.exists(file_path):
            local_path = r"z:\4-ELECTRICITY CONSUMPTION\ENERGY Report -24 o'clock-1404.xlsb"
            if os.path.exists(local_path):
                file_path = local_path
            else:
                raise FileNotFoundError("Excel file not found. Please check the file path.")
        
        # بررسی وجود تصویر پس‌زمینه
        if not os.path.exists(bg_image_path):
            raise FileNotFoundError("Background image not found. Please check the image path.")
        
        # 2. خواندن فایل اکسل بدون هدر
        sheet_name = 'DAILY'
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', header=None)
        
        # 3. پیدا کردن ردیف‌های معتبر
        valid_rows = df[df[1].notna() & df[1].apply(lambda x: isinstance(x, (int, float, np.number)))]
        
        # اطمینان از وجود حداقل 3 ردیف معتبر برای محاسبه (برای دو روز قبل)
        if len(valid_rows) < 3:
            raise ValueError("Need at least 3 data rows for calculations (current, previous, and day before previous)")
        
        # گرفتن ردیف‌های مورد نیاز
        last_row_index = valid_rows.index[-1]  # ردیف فعلی
        prev_row_index = valid_rows.index[-2]   # ردیف قبلی
        prev_prev_row_index = valid_rows.index[-3]  # ردیف دو روز قبل
        
        current_row = df.loc[last_row_index]
        previous_row = df.loc[prev_row_index]
        day_before_prev_row = df.loc[prev_prev_row_index]
        
        # 4. استخراج تاریخ‌ها
        current_date = str(current_row[0]) if pd.notna(current_row[0]) else "Current Date Not Available"
        prev_date = str(previous_row[0]) if pd.notna(previous_row[0]) else "Previous Date Not Available"
        
        # 5. محاسبات اصلی برای روز فعلی
        P_D = (current_row[1] + current_row[2]) - (previous_row[1] + previous_row[2])
        Q_D = (current_row[4] + current_row[5]) - (previous_row[4] + previous_row[5])
        
        # محاسبات برای ستون‌های I تا O (شماره 8 تا 14) - روز فعلی
        TR_columns = [8, 9, 10, 11, 12, 13, 14]
        TR_values = []
        TR_labels = [
            'P_TR1_D:', 'P_TR2_D:', 'P_TR3_D:', 'P_TR4_D:',
            'P_TR6_D:', 'P_HEX_TRA_D:', 'P_HEX_TRB_D:'
        ]
        
        for col in TR_columns:
            if col < df.shape[1]:
                try:
                    diff = current_row[col] - previous_row[col]
                    TR_values.append(diff)
                except:
                    TR_values.append(0)
            else:
                TR_values.append(0)
        
        # محاسبات P_GPPS_D و P_HEX_D - روز فعلی
        gpps_columns = [8, 9, 10, 11, 12]
        available_gpps = [col for col in gpps_columns if col < df.shape[1]]
        P_GPPS_D = current_row[available_gpps].sum() - previous_row[available_gpps].sum() if available_gpps else 0
        
        hex_columns = [13, 14]
        available_hex = [col for col in hex_columns if col < df.shape[1]]
        P_HEX_D = current_row[available_hex].sum() - previous_row[available_hex].sum() if available_hex else 0
        
        # 6. محاسبات اصلی برای روز قبل
        P_D_prev = (previous_row[1] + previous_row[2]) - (day_before_prev_row[1] + day_before_prev_row[2])
        Q_D_prev = (previous_row[4] + previous_row[5]) - (day_before_prev_row[4] + day_before_prev_row[5])
        
        # محاسبات برای ستون‌های I تا O (شماره 8 تا 14) - روز قبل
        TR_values_prev = []
        for col in TR_columns:
            if col < df.shape[1]:
                try:
                    diff = previous_row[col] - day_before_prev_row[col]
                    TR_values_prev.append(diff)
                except:
                    TR_values_prev.append(0)
            else:
                TR_values_prev.append(0)
        
        # محاسبات P_GPPS_D و P_HEX_D - روز قبل
        P_GPPS_D_prev = previous_row[available_gpps].sum() - day_before_prev_row[available_gpps].sum() if available_gpps else 0
        P_HEX_D_prev = previous_row[available_hex].sum() - day_before_prev_row[available_hex].sum() if available_hex else 0


        # 7. محاسبه مصرف ماهانه
                # محاسبه مصرف ماهانه بر اساس ساختار دقیق فایل اکسل شما
        print("\n" + "="*50)
        print("STARTING MONTHLY CONSUMPTION CALCULATION")
        print("="*50)

        try:
            # 1. بررسی وجود متغیرهای مورد نیاز
            print(f"\n🔍 Step 0: Checking required variables")
            
            # تأیید وجود متغیرهای ضروری
            if 'df' not in locals() and 'df' not in globals():
                raise NameError("DataFrame 'df' is not defined. Please make sure the Excel file is loaded correctly.")
            
            if 'current_row' not in locals() and 'current_row' not in globals():
                raise NameError("Variable 'current_row' is not defined. Please make sure the current row is selected.")
            
            # 2. استخراج اطلاعات اولیه
            print(f"\n🔍 Step 1: Getting current row information")
            
            # تأیید وجود last_row_index یا استخراج آن
            if 'last_row_index' not in locals() and 'last_row_index' not in globals():
                print("  - 'last_row_index' not found. Extracting from valid_rows...")
                valid_rows = df[df[1].notna() & df[1].apply(lambda x: isinstance(x, (int, float, np.number)))]
                if len(valid_rows) == 0:
                    raise ValueError("No valid data rows found in Column B")
                last_row_index = valid_rows.index[-1]
                print(f"  ✓ Extracted last_row_index: {last_row_index}")
            
            print(f"  - Current row index in Pandas: {last_row_index}")
            print(f"  - Value in Column A (index 0): {current_row[0]}")
            
            # تبدیل مقدار ستون A به روز سال
            try:
                # اگر مقدار عددی باشد
                if isinstance(current_row[0], (int, float)):
                    current_day = int(current_row[0])
                    print(f"  ✓ Directly using numeric value as day of year: {current_day}")
                # اگر مقدار رشته‌ای باشد
                elif isinstance(current_row[0], str) and current_row[0].strip() != '':
                    # اگر حاوی عدد باشد
                    if current_row[0].strip().replace('.', '').isdigit():
                        current_day = int(float(current_row[0].strip()))
                        print(f"  ✓ Extracted numeric value from string: {current_day}")
                    # اگر فرمت تاریخ شمسی باشد (مثلاً 1404/03/15)
                    elif '/' in current_row[0]:
                        parts = current_row[0].split('/')
                        if len(parts) >= 3:
                            year = parts[0]
                            month = int(parts[1])
                            day = int(parts[2])
                            
                            # محاسبه روز سال (فقط برای 6 ماه اول که هر ماه 31 روزه است)
                            current_day = (month - 1) * 31 + day
                            print(f"  ✓ Calculated day of year from Persian date: Year={year}, Month={month}, Day={day} → {current_day}")
                        else:
                            raise ValueError("Invalid Persian date format")
                    else:
                        raise ValueError("Cannot parse string value")
                else:
                    raise ValueError("Invalid or empty value in Column A")
                
                print(f"  ✓ Final day of year: {current_day}")
            except Exception as e:
                print(f"  ✗ Error extracting day of year: {str(e)}")
                # در صورت شکست، سعی می‌کنیم روز سال را از ایندکس محاسبه کنیم
                # فرض: روز سال = ایندکس پانداس - 1
                current_day = last_row_index - 1
                print(f"  ✓ Fallback: Calculated day of year from index: {current_day} (index {last_row_index} - 1)")
            
            # 2. محاسبه ماه شمسی
            print(f"\n🔍 Step 2: Calculating Persian month")
            persian_month = (current_day - 1) // 31 + 1
            print(f"  - Day of year: {current_day}")
            print(f"  - Persian month: {persian_month}")
            
            # 3. محاسبه روز اول ماه جاری
            first_day_of_month = (persian_month - 1) * 31 + 1
            print(f"  - First day of current month (day of year): {first_day_of_month}")
            
            # 4. تبدیل روز اول ماه به ایندکس پانداس
            # توضیح: 
            # - ردیف 1 اکسل = ایندکس 0 پانداس (خالی)
            # - ردیف 2 اکسل = ایندکس 1 پانداس (نام ستون‌ها)
            # - پس روز D در اکسل = ایندکس (D + 1) در پانداس
            first_day_row_index = first_day_of_month + 1
            print(f"  - Expected Pandas index for first day of month: {first_day_row_index}")
            
            # 5. بررسی وجود این ردیف در داده‌ها
            print(f"\n🔍 Step 3: Checking if first day row exists")
            print(f"  - Available row indices in DataFrame: {df.index.min()} to {df.index.max()}")
            
            if first_day_row_index in df.index:
                print(f"  ✓ First day of month row ({first_day_row_index}) found in data")
                first_day_row = df.loc[first_day_row_index]
                
                # نمایش مقادیر مربوطه برای دیباگ
                print("\n🔍 Step 4: Displaying relevant values for calculation")
                
                print(f"  - Current row (index {last_row_index}):")
                print(f"    * Column B (index 1): {current_row[1]}")
                print(f"    * Column C (index 2): {current_row[2]}")
                print(f"    * Column E (index 4): {current_row[4]}")
                print(f"    * Column F (index 5): {current_row[5]}")
                
                print(f"  - First day row (index {first_day_row_index}):")
                print(f"    * Column B (index 1): {first_day_row[1]}")
                print(f"    * Column C (index 2): {first_day_row[2]}")
                print(f"    * Column E (index 4): {first_day_row[4]}")
                print(f"    * Column F (index 5): {first_day_row[5]}")
                
                # محاسبه مصرف ماهانه
                print("\n🔍 Step 5: Calculating monthly consumption")
                
                # محاسبه P_D ماهانه
                monthly_P_D = (current_row[1] + current_row[2]) - (first_day_row[1] + first_day_row[2])
                print(f"  ✓ Monthly P_D calculation: ({current_row[1]} + {current_row[2]}) - ({first_day_row[1]} + {first_day_row[2]}) = {monthly_P_D}")
                
                # محاسبه Q_D ماهانه
                monthly_Q_D = (current_row[4] + current_row[5]) - (first_day_row[4] + first_day_row[5])
                print(f"  ✓ Monthly Q_D calculation: ({current_row[4]} + {current_row[5]}) - ({first_day_row[4]} + {first_day_row[5]}) = {monthly_Q_D}")
                
                # محاسبه مصرف ماهانه برای ستون‌های TR
                print("\n  TR Columns Calculation:")
                monthly_TR_values = []
                for i, col in enumerate(TR_columns):
                    if col < df.shape[1]:
                        try:
                            diff = current_row[col] - first_day_row[col]
                            monthly_TR_values.append(diff)
                            print(f"  ✓ {TR_labels[i]}: {current_row[col]} - {first_day_row[col]} = {diff:.2f}")
                        except Exception as e:
                            monthly_TR_values.append(0)
                            print(f"  ✗ {TR_labels[i]} calculation error: {str(e)}")
                    else:
                        monthly_TR_values.append(0)
                        print(f"  ✗ {TR_labels[i]} column {col} not available (file has only {df.shape[1]} columns)")
                
                # محاسبه P_GPPS_D ماهانه
                print("\n  P_GPPS_D Calculation:")
                if available_gpps:
                    sum_current = current_row[available_gpps].sum()
                    sum_first_day = first_day_row[available_gpps].sum()
                    monthly_P_GPPS_D = sum_current - sum_first_day
                    
                    print(f"  ✓ Columns used: {available_gpps}")
                    print(f"  ✓ Current sum: {sum_current}")
                    print(f"  ✓ First day sum: {sum_first_day}")
                    print(f"  ✓ Result: {sum_current} - {sum_first_day} = {monthly_P_GPPS_D}")
                else:
                    monthly_P_GPPS_D = 0
                    print("  ✗ No columns available for P_GPPS_D calculation")
                
                # محاسبه P_HEX_D ماهانه
                print("\n  P_HEX_D Calculation:")
                if available_hex:
                    sum_current = current_row[available_hex].sum()
                    sum_first_day = first_day_row[available_hex].sum()
                    monthly_P_HEX_D = sum_current - sum_first_day
                    
                    print(f"  ✓ Columns used: {available_hex}")
                    print(f"  ✓ Current sum: {sum_current}")
                    print(f"  ✓ First day sum: {sum_first_day}")
                    print(f"  ✓ Result: {sum_current} - {sum_first_day} = {monthly_P_HEX_D}")
                else:
                    monthly_P_HEX_D = 0
                    print("  ✗ No columns available for P_HEX_D calculation")
                
                # تعیین نام ماه برای نمایش
                month_names = [
                    "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
                    "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"
                ]
                month_name = month_names[persian_month - 1] if 1 <= persian_month <= 12 else "Unknown"
                print(f"\n  ✓ Month name: {month_name}")
                
            else:
                print(f"  ✗ First day of month row ({first_day_row_index}) NOT found in data")
                monthly_P_D = 0
                monthly_Q_D = 0
                monthly_TR_values = [0] * len(TR_labels)
                monthly_P_GPPS_D = 0
                monthly_P_HEX_D = 0
                month_name = "Unknown"
                
                # تلاش برای پیدا کردن نزدیک‌ترین ردیف
                closest_index = None
                for idx in df.index:
                    if idx < first_day_row_index:
                        closest_index = idx
                    else:
                        break
                
                if closest_index is not None:
                    print(f"  ✓ Found closest available row: {closest_index}")
                    first_day_row = df.loc[closest_index]
                    
                    # محاسبه ماه شمسی برای ردیف پیدا شده
                    day_of_year = closest_index - 1
                    persian_month = (day_of_year - 1) // 31 + 1
                    month_name = month_names[persian_month - 1] if 1 <= persian_month <= 12 else "Unknown"
                    print(f"  ✓ Using data from {month_name} instead of current month")
                    
                    # محاسبه مجدد مصرف ماهانه با ردیف پیدا شده
                    monthly_P_D = (current_row[1] + current_row[2]) - (first_day_row[1] + first_day_row[2])
                    monthly_Q_D = (current_row[4] + current_row[5]) - (first_day_row[4] + first_day_row[5])
                else:
                    print("  ✗ No suitable row found for monthly calculation")

        except NameError as e:
            print(f"\n✗ NAME ERROR: {str(e)}")
            print("  This usually happens when required variables are not defined.")
            print("  Please make sure you have executed the previous sections of the code that define:")
            print("  - df (DataFrame)")
            print("  - current_row")
            print("  - last_row_index")
            print("  - TR_columns, TR_labels, etc.")
            monthly_P_D = 0
            monthly_Q_D = 0
            monthly_TR_values = [0] * len(TR_labels)
            monthly_P_GPPS_D = 0
            monthly_P_HEX_D = 0
            month_name = "Unknown"

        except Exception as e:
            print(f"\n✗ CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            monthly_P_D = 0
            monthly_Q_D = 0
            monthly_TR_values = [0] * len(TR_labels)
            monthly_P_GPPS_D = 0
            monthly_P_HEX_D = 0
            month_name = "Unknown"

        # خلاصه نتایج
        print("\n" + "="*50)
        print("MONTHLY CONSUMPTION CALCULATION RESULTS")
        print("="*50)
        print(f"- Month: {month_name}")
        print(f"- Monthly P_D: {monthly_P_D:.2f}")
        print(f"- Monthly Q_D: {monthly_Q_D:.2f}")
        print(f"- Monthly P_GPPS_D: {monthly_P_GPPS_D:.2f}")
        print(f"- Monthly P_HEX_D: {monthly_P_HEX_D:.2f}")
        print("- TR Values:")
        for label, value in zip(TR_labels, monthly_TR_values):
            print(f"  * {label}: {value:.2f}")
        print("="*50 + "\n")



# 8. ایجاد گزارش گرافیکی
        plt.figure(figsize=(12, 8))
        ax = plt.gca()
        
        # بارگذاری تصویر پس‌زمینه
        try:
            bg_image = plt.imread(bg_image_path)
            ax.imshow(bg_image, aspect='auto')
        except:
            ax.set_facecolor('black')  # پس‌زمینه سیاه در صورت عدم وجود تصویر
        
        ax.axis('off')
        
        # تنظیمات متن
        line_height = 0.05
        
        # افزودن تاریخ‌ها به صورت برجسته
        ax.text(0.10, 0.95, current_date, transform=ax.transAxes, 
                color='white', fontsize=24, fontweight='bold', 
                ha='center', backgroundcolor='black')
        
        ax.text(0.6, 0.95, prev_date, transform=ax.transAxes, 
                color='white', fontsize=24, fontweight='bold', 
                ha='center', backgroundcolor='black')
        
        # خط جداکننده زیر تاریخ‌ها
        line = mlines.Line2D([0, 1], [0.88, 0.88], 
                             color='white', alpha=0.3, 
                             transform=ax.transAxes)
        ax.add_line(line)
        
        # افزودن برچسب‌ها برای ستون‌ها
        ax.text(0.1, 0.90, "TODAY", transform=ax.transAxes, 
                color='yellow', fontsize=16, fontweight='bold', 
                ha='center', backgroundcolor='black')
        
        ax.text(0.6, 0.90, "YESTERDAY", transform=ax.transAxes, 
                color='yellow', fontsize=16, fontweight='bold', 
                ha='center', backgroundcolor='black')
        
        # نمایش مقادیر اصلی - ستون چپ (امروز)
        text_y = 0.80
        ax.text(0.05, text_y, f'P_D: {P_D:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        
        ax.text(0.05, text_y - line_height, f'Q_D: {Q_D:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        
        # نمایش مقادیر اصلی - ستون راست (دیروز)
        ax.text(0.55, text_y, f'P_D: {P_D_prev:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        
        ax.text(0.55, text_y - line_height, f'Q_D: {Q_D_prev:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        
        text_y -= line_height * 2.5
        
        # نمایش مقادیر TR - ستون چپ (امروز)
        ax.text(0.05, text_y, "TR Values (Today):", transform=ax.transAxes, 
                color='yellow', fontsize=12, fontweight='bold', backgroundcolor='black')
        text_y -= line_height
        
        for label, value in zip(TR_labels, TR_values):
            if value != 0:
                ax.text(0.05, text_y, f'{label} {value:.2f}', transform=ax.transAxes, 
                        color='white', fontsize=12, backgroundcolor='black')
                text_y -= line_height
        
        # نمایش مقادیر TR - ستون راست (دیروز)
        text_y_right = 0.80 - line_height * 2.5
        ax.text(0.55, text_y_right, "TR Values (Yesterday):", transform=ax.transAxes, 
                color='yellow', fontsize=12, fontweight='bold', backgroundcolor='black')
        text_y_right -= line_height
        
        for label, value in zip(TR_labels, TR_values_prev):
            if value != 0:
                ax.text(0.55, text_y_right, f'{label} {value:.2f}', transform=ax.transAxes, 
                        color='white', fontsize=12, backgroundcolor='black')
                text_y_right -= line_height
        
        # نمایش مقادیر نهایی - ستون چپ (امروز)
        text_y = 0.33
        ax.text(0.05, text_y, f'P_GPPS_D: {P_GPPS_D:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        text_y -= line_height
        ax.text(0.05, text_y, f'P_HEX_D: {P_HEX_D:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        
        # نمایش مقادیر نهایی - ستون راست (دیروز)
        ax.text(0.55, 0.33, f'P_GPPS_D: {P_GPPS_D_prev:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        ax.text(0.55, 0.33 - line_height, f'P_HEX_D: {P_HEX_D_prev:.2f}', transform=ax.transAxes, 
                color='white', fontsize=14, fontweight='bold', backgroundcolor='black')
        
        # افزودن خط عمودی برای جدا کردن ستون‌ها
        line = mlines.Line2D([0.5, 0.5], [0, 1], 
                             color='white', alpha=0.3, linestyle='--',
                             transform=ax.transAxes)
        ax.add_line(line)

 


        
        # 9. افزودن مصرف ماهانه در پایین گزارش
        monthly_y = 0.25
        line = mlines.Line2D([0, 1], [0.22, 0.22], 
                             color='white', alpha=0.9, 
                             transform=ax.transAxes)
        ax.add_line(line)
        monthly_y -= line_height * 1.2
        
        # خط جداکننده برای بخش ماهانه
        line = mlines.Line2D([0.05, 0.95], [monthly_y + 0.02, monthly_y + 0.02], 
                             color='cyan', alpha=0.5, 
                             transform=ax.transAxes)
        ax.add_line(line)
        
        # ابتدا محاسبه مقدار ماه قبل (برای مقایسه)
        try:
            # محاسبه ماه قبل
            prev_month = persian_month - 1 if persian_month > 1 else 12
            prev_month_name = month_names[prev_month - 1]
            
            # محاسبه روز اول ماه قبل
            first_day_of_prev_month = (prev_month - 1) * 31 + 1
            first_day_prev_month_index = first_day_of_prev_month + 1
            
            # بررسی وجود ردیف ماه قبل
            if first_day_prev_month_index in df.index:
                first_day_prev_month_row = df.loc[first_day_prev_month_index]
                
                # محاسبه مصرف ماه قبل
                prev_month_P_D = (first_day_row[1] + first_day_row[2]) - (first_day_prev_month_row[1] + first_day_prev_month_row[2])
                prev_month_Q_D = (first_day_row[4] + first_day_row[5]) - (first_day_prev_month_row[4] + first_day_prev_month_row[5])
                prev_month_P_GPPS_D = first_day_row[available_gpps].sum() - first_day_prev_month_row[available_gpps].sum() if available_gpps else 0
                prev_month_P_HEX_D = first_day_row[available_hex].sum() - first_day_prev_month_row[available_hex].sum() if available_hex else 0
            else:
                prev_month_P_D = 0
                prev_month_Q_D = 0
                prev_month_P_GPPS_D = 0
                prev_month_P_HEX_D = 0
                
        except:
            prev_month_P_D = 0
            prev_month_Q_D = 0
            prev_month_P_GPPS_D = 0
            prev_month_P_HEX_D = 0
            prev_month_name = "Unknown"
        
        # نمایش مقادیر ماهانه با فاصله و مقایسه با ماه قبل
        ax.text(0.35, monthly_y, f'Month: {month_name}', transform=ax.transAxes, 
                color='white', fontsize=14, backgroundcolor='black')
        monthly_y -= line_height
        
        # Monthly P_D با مقایسه ماه قبل
        ax.text(0.05, monthly_y, f'Monthly P_D:', transform=ax.transAxes, 
                color='white', fontsize=14, backgroundcolor='black')
        ax.text(0.30, monthly_y, f'{monthly_P_D:.2f}', transform=ax.transAxes, 
                color='yellow', fontsize=14, backgroundcolor='black')
        ax.text(0.55, monthly_y, f'(Prev: {prev_month_P_D:.2f})', transform=ax.transAxes, 
                color='green', fontsize=12, backgroundcolor='black')
        monthly_y -= line_height
        
        # Monthly Q_D با مقایسه ماه قبل
        ax.text(0.05, monthly_y, f'Monthly Q_D:', transform=ax.transAxes, 
                color='white', fontsize=14, backgroundcolor='black')
        ax.text(0.30, monthly_y, f'{monthly_Q_D:.2f}', transform=ax.transAxes, 
                color='yellow', fontsize=14, backgroundcolor='black')
        ax.text(0.55, monthly_y, f'(Prev: {prev_month_Q_D:.2f})', transform=ax.transAxes, 
                color='green', fontsize=12, backgroundcolor='black')
        monthly_y -= line_height
        
        # Monthly P_GPPS_D با مقایسه ماه قبل
        ax.text(0.05, monthly_y, f'Monthly P_GPPS_D:', transform=ax.transAxes, 
                color='white', fontsize=14, backgroundcolor='black')
        ax.text(0.30, monthly_y, f'{monthly_P_GPPS_D:.2f}', transform=ax.transAxes, 
                color='yellow', fontsize=14, backgroundcolor='black')
        ax.text(0.55, monthly_y, f'(Prev: {prev_month_P_GPPS_D:.2f})', transform=ax.transAxes, 
                color='green', fontsize=12, backgroundcolor='black')
        monthly_y -= line_height
        
        # Monthly P_HEX_D با مقایسه ماه قبل
        ax.text(0.05, monthly_y, f'Monthly P_HEX_D:', transform=ax.transAxes, 
                color='white', fontsize=14, backgroundcolor='black')
        ax.text(0.30, monthly_y, f'{monthly_P_HEX_D:.2f}', transform=ax.transAxes, 
                color='yellow', fontsize=14, backgroundcolor='black')
        ax.text(0.55, monthly_y, f'(Prev: {prev_month_P_HEX_D:.2f})', transform=ax.transAxes, 
                color='green', fontsize=12, backgroundcolor='black')
        monthly_y -= line_height
        
        # نمایش نام ماه با مقایسه ماه قبل
        ax.text(0.05, monthly_y, f'Current Month:', transform=ax.transAxes, 
                color='white', fontsize=14, backgroundcolor='black')
        ax.text(0.30, monthly_y, f'{month_name}', transform=ax.transAxes, 
                color='yellow', fontsize=14, backgroundcolor='black')
        ax.text(0.55, monthly_y, f'Previous: {prev_month_name}', transform=ax.transAxes, 
                color='green', fontsize=12, backgroundcolor='black')



        
        # 10. ذخیره و نمایش گزارش
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='black')
        plt.show()
        
        print(f"\n✅ Report generated successfully: {output_path}")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
