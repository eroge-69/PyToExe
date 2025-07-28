
import datetime

# Simple date conversion placeholder functions based on VBA logic
def is_leap_year(year):
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)

def nepali_to_english(bs_year, bs_month, bs_day):
    # Dummy conversion for demonstration
    # The actual conversion is complex with the data given
    # Here we just add 57 years as an example (approximate)
    ad_year = bs_year - 57
    return f"{ad_year}-{bs_month}-{bs_day}"

def english_to_nepali(ad_year, ad_month, ad_day):
    # Dummy conversion for demonstration
    bs_year = ad_year + 57
    return f"{bs_year}-{ad_month}-{ad_day}"

def main():
    print("Nepali-English Date Converter")
    print("1: Nepali to English")
    print("2: English to Nepali")
    choice = input("Choose conversion (1 or 2): ").strip()
    if choice == "1":
        y = int(input("Enter BS year: "))
        m = int(input("Enter BS month (1-12): "))
        d = int(input("Enter BS day (1-32): "))
        print("Converted AD date:", nepali_to_english(y, m, d))
    elif choice == "2":
        y = int(input("Enter AD year: "))
        m = int(input("Enter AD month (1-12): "))
        d = int(input("Enter AD day (1-31): "))
        print("Converted BS date:", english_to_nepali(y, m, d))
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
