class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.bookings = []

    def add_room(self, room_number, room_type, price):
        room = {
            'room_number': room_number,
            'room_type': room_type,
            'price': price,
            'is_booked': False
        }
        self.rooms.append(room)

    def view_rooms(self):
        print(f"\nДоступные номера в {self.name}:")
        for room in self.rooms:
            status = "Забронирован" if room['is_booked'] else "Доступен"
            print(f"Номер {room['room_number']} ({room['room_type']}): ${room['price']} - {status}")

    def book_room(self, room_number, customer_name):
        for room in self.rooms:
            if room['room_number'] == room_number:
                if not room['is_booked']:
                    room['is_booked'] = True
                    self.bookings.append({
                        'customer_name': customer_name,
                        'room_number': room_number
                    })
                    print(f"Номер {room_number} успешно забронирован для {customer_name}.")
                    return
                else:
                    print(f"Номер {room_number} уже забронирован.")
                    return
        print(f"Номер {room_number} не существует.")

    def view_bookings(self):
        print("\nТекущие бронирования:")
        if not self.bookings:
            print("Нет активных бронирований.")
            return
        for booking in self.bookings:
            print(f"Клиент: {booking['customer_name']}, Номер: {booking['room_number']}")

# Пример использования приложения
def main():
    hotel = Hotel("Городской Центр Отель")

    # Добавление номеров
    hotel.add_room(101, "Одноместный", 100)
    hotel.add_room(102, "Двухместный", 150)
    hotel.add_room(103, "Люкс", 250)

    while True:
        print("\nВыберите действие:")
        print("1. Посмотреть номера")
        print("2. Забронировать номер")
        print("3. Посмотреть бронирования")
        print("4. Выход")
        choice = input("Ваш выбор: ")

        if choice == '1':
            hotel.view_rooms()
        elif choice == '2':
            room_number = int(input("Введите номер для бронирования: "))
            customer_name = input("Введите ваше имя: ")
            hotel.book_room(room_number, customer_name)
        elif choice == '3':
            hotel.view_bookings()
        elif choice == '4':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()
