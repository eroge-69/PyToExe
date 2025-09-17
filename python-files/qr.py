import pandas as pd
import qrcode
import os

def main():
    csv_file = "Tokens.csv"   # CSV file ka naam (exe ke folder me hona chahiye)

    if not os.path.exists(csv_file):
        print("❌ Tokens.csv file nahi mili! Kripya CSV ko exe ke folder me rakho.")
        input("Exit karne ke liye Enter dabaye...")
        return

    df = pd.read_csv(csv_file)

    output_folder = "QR_Codes"
    os.makedirs(output_folder, exist_ok=True)

    for i, link in enumerate(df['Tokens Link'], start=1):
        if pd.notna(link):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            filename = f"QR_{str(i).zfill(5)}.png"
            img.save(os.path.join(output_folder, filename))

    print(f"✅ {len(df)} QR codes QR_Codes folder me save ho gaye!")
    input("Exit karne ke liye Enter dabaye...")

if __name__ == "__main__":
    main()
