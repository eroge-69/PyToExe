import calendar

yy = int(input("Kérem az évet: "))
mm = int(input("Kérem a hónapot: "))

if 1 <= mm <= 12:
	print(calendar.month(yy, mm))
else:
    print("Hiba! A hónap csak 1-12 lehet "

input("\nnyomj Entert a kilépéshez ")	