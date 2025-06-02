import math

def calculate_pyramid_volume():
    """
    محاسبه حجم هرم با قاعده مربع و وجه جانبی مثلث متساوی الساقین.
    """
    try:
        side_length = float(input("اندازه ضلع قاعده مربع را وارد کنید: "))
        leg_length = float(input("اندازه ساق مثلث متساوی الساقین را وارد کنید: "))

        if side_length <= 0 or leg_length <= 0:
            print("اندازه ضلع و ساق باید مقداری مثبت باشند.")
            return

        # محاسبه مساحت قاعده
        base_area = side_length ** 2

        # محاسبه ارتفاع هرم
        # ابتدا ارتفاع وجه جانبی را محاسبه می کنیم
        # در مثلث قائم الزاویه ای که با ساق مثلث متساوی الساقین، نصف قاعده (ضلع مربع) و ارتفاع وجه جانبی تشکیل می شود.
        # leg_length^2 = face_height^2 + (side_length/2)^2
        # face_height^2 = leg_length^2 - (side_length/2)^2

        # بررسی می‌کنیم که آیا ساق مثلث به اندازه کافی بزرگ هست که مثلث تشکیل شود (ارتفاع وجه جانبی حقیقی باشد)
        if (leg_length ** 2) < ((side_length / 2) ** 2):
            print("ساق مثلث متساوی الساقین برای تشکیل وجه جانبی معتبر نیست. (ساق از نصف ضلع قاعده کوچکتر است)")
            return

        face_height = math.sqrt(leg_length**2 - (side_length/2)**2)

        # محاسبه ارتفاع هرم
        # در مثلث قائم الزاویه ای که با ارتفاع هرم، نصف ضلع قاعده و ارتفاع وجه جانبی تشکیل می شود.
        # face_height^2 = pyramid_height^2 + (side_length/2)^2
        # pyramid_height^2 = face_height^2 - (side_length/2)^2

        # بررسی می‌کنیم که آیا ارتفاع وجه جانبی به اندازه کافی بزرگ هست که هرم تشکیل شود
        if (face_height ** 2) < ((side_length / 2) ** 2):
            print("ارتفاع وجه جانبی برای تشکیل هرم معتبر نیست. (وجه جانبی خیلی تخت است)")
            return

        pyramid_height = math.sqrt(face_height**2 - (side_length/2)**2)

        # محاسبه حجم هرم
        volume = (1/3) * base_area * pyramid_height

        print(f"\nمساحت قاعده: {base_area:.2f}")
        print(f"ارتفاع هرم: {pyramid_height:.2f}")
        print(f"حجم هرم: {volume:.2f}")

    except ValueError:
        print("ورودی نامعتبر است. لطفاً اعداد را وارد کنید.")
    except Exception as e:
        print(f"خطایی رخ داد: {e}")

# اجرای برنامه
calculate_pyramid_volume()
