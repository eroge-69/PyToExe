import sys

def main():
    input_data = """
103.94.48.95>>>Existco Admin;
120.150.197.87>>>rtadmm;
220.233.65.45>>>Administrator;Dr JM;John M;
144.6.23.70>>>orangelane.local\\orangeadmin;
27.50.87.6>>>Administrator;Dkn;tdx account1;
144.6.155.74>>>Code9;
110.142.82.141>>>Admin;Administrator;Sales;
125.253.95.59>>>Admin;Derek;Kate;robot;
60.241.162.3>>>Admin;Sam;Administrator;Anna;
101.187.3.193>>>WISEBERRY\\administrator;
101.187.99.223>>>Administrator;CityeRemit;IME_ADMIN;IME_USER;
103.17.222.16>>>Administrator;michellebrook;Sladen;Accounts;
144.139.163.116>>>Accounts User;admin;
"""

    # پردازش داده‌ها
    lines = [line.strip() for line in input_data.split('\n') if line.strip()]
    
    unique_ips = []
    seen_ips = set()
    
    unique_usernames = []
    seen_usernames = set()

    for line in lines:
        if '>>>' in line:
            ip_part, users_part = line.split('>>>', 1)
            
            if ip_part not in seen_ips:
                unique_ips.append(ip_part)
                seen_ips.add(ip_part)
            
            users_clean = users_part.rstrip(';')
            for user in users_clean.split(';'):
                user = user.strip()
                if user:
                    normalized = user.lower()
                    if normalized not in seen_usernames:
                        unique_usernames.append(user)
                        seen_usernames.add(normalized)

    # ایجاد خروجی
    output = "لیست IP های منحصر به فرد:\n"
    output += "\n".join(unique_ips)
    output += "\n\nلیست کاربران منحصر به فرد:\n"
    output += "\n".join(unique_usernames)
    
    return output

if __name__ == "__main__":
    result = main()
    print(result)
    
    # برای ویندوز: پنجره را باز نگه دار
    if sys.platform.startswith('win'):
        input("\n\nبرای خروج Enter بزنید...")