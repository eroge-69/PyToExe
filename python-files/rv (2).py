
import datetime

def calculate_appointment_dates(start_date, weeks):
    appointment_dates = []
    for week in weeks:
        appointment_date = start_date + datetime.timedelta(weeks=week)
        appointment_dates.append(appointment_date)
    return appointment_dates

def main():
    start_date = datetime.date.today()
    weeks = [4, 8, 12, 13, 26]
    
    appointment_dates = calculate_appointment_dates(start_date, weeks)
    
    # إضافة رسومات بسيطة
    print("╔═══════════════════════════╗")
    print("║                           ║")
    print("║       مواعيد المرضى       ║")
    print("║                           ║")
    print("╚═══════════════════════════╝")
    
    # طباعة تواريخ المواعيد
    for i, date in enumerate(appointment_dates):
        print(f"rendez-vous {i + 1} mois: {date.strftime('%Y-%m-%d')}")

if __name__ == "_main_":
    print("صنعه: حمد بن عبد العزيز")
main()
