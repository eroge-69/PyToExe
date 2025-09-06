import sqlite3
import re
import hashlib
import uuid
from datetime import datetime

class SparkMessenger:
    def __init__(self):
        self.conn = sqlite3.connect('spark.db')
        self.create_tables()
        self.current_user = None
    
    def create_tables(self):
        users_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            nickname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        '''
        
        chats_query = '''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user1_id) REFERENCES users (id),
            FOREIGN KEY (user2_id) REFERENCES users (id)
        )
        '''
        
        groups_query = '''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            creator_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users (id)
        )
        '''
        
        group_members_query = '''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
        
        channels_query = '''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            creator_id INTEGER NOT NULL,
            is_public BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users (id)
        )
        '''
        
        channel_subscribers_query = '''
        CREATE TABLE IF NOT EXISTS channel_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
        
        messages_query = '''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            chat_id INTEGER,
            group_id INTEGER,
            channel_id INTEGER,
            content TEXT NOT NULL,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (chat_id) REFERENCES chats (id),
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (channel_id) REFERENCES channels (id)
        )
        '''
        
        cursor = self.conn.cursor()
        cursor.execute(users_query)
        cursor.execute(chats_query)
        cursor.execute(groups_query)
        cursor.execute(group_members_query)
        cursor.execute(channels_query)
        cursor.execute(channel_subscribers_query)
        cursor.execute(messages_query)
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_phone(self, phone):
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone) is not None

    def register_user(self):
        print("\nРегистрация в Spark Messenger")
        
        while True:
            phone = input("Введите номер телефона: ").strip()
            if self.validate_phone(phone):
                if self.check_existing_phone(phone):
                    print("Этот номер уже зарегистрирован!")
                else:
                    break
            else:
                print("Неверный формат номера!")
        
        name = input("Введите ваше имя: ").strip()
        nickname = input("Введите ваш никнейм: ").strip()
        
        while True:
            username = input("Введите юзернейм: ").strip()
            if self.check_existing_username(username):
                print("Этот юзернейм уже занят!")
            else:
                break
        
        while True:
            password = input("Введите пароль: ").strip()
            if len(password) < 6:
                print("Пароль должен содержать минимум 6 символов!")
            else:
                confirm_password = input("Подтвердите пароль: ").strip()
                if password == confirm_password:
                    break
                else:
                    print("Пароли не совпадают!")

        try:
            cursor = self.conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (phone, name, nickname, username, password_hash) VALUES (?, ?, ?, ?, ?)",
                (phone, name, nickname, username, password_hash)
            )
            self.conn.commit()
            print("Регистрация прошла успешно!")
            
        except sqlite3.Error as e:
            print(f"Ошибка при регистрации: {e}")

    def login(self):
        print("\nВход в Spark Messenger")
        
        username = input("Введите юзернейм: ").strip()
        password = input("Введите пароль: ").strip()
        
        password_hash = self.hash_password(password)
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, username FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        if user:
            self.current_user = {
                'id': user[0],
                'name': user[1],
                'username': user[2]
            }
            print(f"Добро пожаловать, {user[1]}!")
            return True
        else:
            print("Неверный юзернейм или пароль!")
            return False

    def check_existing_phone(self, phone):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
        return cursor.fetchone() is not None

    def check_existing_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def create_chat(self, recipient_username):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (recipient_username,))
        recipient = cursor.fetchone()
        
        if not recipient:
            print(f"Пользователь с юзернеймом {recipient_username} не найден!")
            return
        
        recipient_id = recipient[0]
        user_id = self.current_user['id']
        
        cursor.execute(
            "SELECT id FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)",
            (user_id, recipient_id, recipient_id, user_id)
        )
        
        existing_chat = cursor.fetchone()
        if existing_chat:
            print("Чат с этим пользователем уже существует!")
            return existing_chat[0]
        
        cursor.execute(
            "INSERT INTO chats (user1_id, user2_id) VALUES (?, ?)",
            (user_id, recipient_id)
        )
        self.conn.commit()
        
        chat_id = cursor.lastrowid
        print(f"Чат с {recipient_username} создан!")
        return chat_id

    def send_message(self, chat_id=None, group_id=None, channel_id=None, content=None):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        if not content:
            content = input("Введите сообщение: ").strip()
        
        if not content:
            print("Сообщение не может быть пустым!")
            return
        
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO messages (sender_id, chat_id, group_id, channel_id, content) VALUES (?, ?, ?, ?, ?)",
                (self.current_user['id'], chat_id, group_id, channel_id, content)
            )
            self.conn.commit()
            print("Сообщение отправлено!")
        except sqlite3.Error as e:
            print(f"Ошибка при отправке сообщения: {e}")

    def create_group(self):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        name = input("Введите название группы: ").strip()
        description = input("Введите описание группы: ").strip()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO groups (name, description, creator_id) VALUES (?, ?, ?)",
            (name, description, self.current_user['id'])
        )
        self.conn.commit()
        
        group_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
            (group_id, self.current_user['id'])
        )
        self.conn.commit()
        
        print(f"Группа '{name}' создана!")
        return group_id

    def add_to_group(self, group_id, username):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT creator_id FROM groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        
        if not group:
            print("Группа не найдена!")
            return
        
        if group[0] != self.current_user['id']:
            print("Только создатель группы может добавлять участников!")
            return
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Пользователь с юзернеймом {username} не найден!")
            return
        
        user_id = user[0]
        
        cursor.execute(
            "SELECT id FROM group_members WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        
        if cursor.fetchone():
            print("Пользователь уже в группе!")
            return
        
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
            (group_id, user_id)
        )
        self.conn.commit()
        
        print(f"Пользователь {username} добавлен в группу!")

    def create_channel(self):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        name = input("Введите название канала: ").strip()
        description = input("Введите описание канала: ").strip()
        
        is_public_input = input("Канал будет публичным? (y/n): ").strip().lower()
        is_public = is_public_input == 'y'
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO channels (name, description, creator_id, is_public) VALUES (?, ?, ?, ?)",
            (name, description, self.current_user['id'], is_public)
        )
        self.conn.commit()
        
        channel_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO channel_subscribers (channel_id, user_id) VALUES (?, ?)",
            (channel_id, self.current_user['id'])
        )
        self.conn.commit()
        
        print(f"Канал '{name}' создан!")
        return channel_id

    def subscribe_to_channel(self, channel_id):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id, is_public FROM channels WHERE id = ?", (channel_id,))
        channel = cursor.fetchone()
        
        if not channel:
            print("Канал не найден!")
            return
        
        cursor.execute(
            "SELECT id FROM channel_subscribers WHERE channel_id = ? AND user_id = ?",
            (channel_id, self.current_user['id'])
        )
        
        if cursor.fetchone():
            print("Вы уже подписаны на этот канал!")
            return
        
        if not channel[1]:
            print("Это приватный канал. Для подписки нужно приглашение!")
            return
        
        cursor.execute(
            "INSERT INTO channel_subscribers (channel_id, user_id) VALUES (?, ?)",
            (channel_id, self.current_user['id'])
        )
        self.conn.commit()
        
        print("Вы подписались на канал!")

    def show_user_chats(self):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.id, u.username, u.name 
            FROM chats c
            JOIN users u ON (c.user1_id = u.id OR c.user2_id = u.id) AND u.id != ?
            WHERE c.user1_id = ? OR c.user2_id = ?
        ''', (self.current_user['id'], self.current_user['id'], self.current_user['id']))
        
        chats = cursor.fetchall()
        
        if not chats:
            print("У вас нет чатов!")
            return
        
        print("\nВаши чаты:")
        for chat in chats:
            print(f"{chat[0]}: {chat[1]} ({chat[2]})")
        
        return chats

    def show_user_groups(self):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, g.description 
            FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = ?
        ''', (self.current_user['id'],))
        
        groups = cursor.fetchall()
        
        if not groups:
            print("Вы не состоите в группах!")
            return
        
        print("\nВаши группы:")
        for group in groups:
            print(f"{group[0]}: {group[1]} - {group[2]}")
        
        return groups

    def show_user_channels(self):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.description 
            FROM channels c
            JOIN channel_subscribers cs ON c.id = cs.channel_id
            WHERE cs.user_id = ?
        ''', (self.current_user['id'],))
        
        channels = cursor.fetchall()
        
        if not channels:
            print("Вы не подписаны на каналы!")
            return
        
        print("\nВаши каналы:")
        for channel in channels:
            print(f"{channel[0]}: {channel[1]} - {channel[2]}")
        
        return channels

    def show_messages(self, chat_id=None, group_id=None, channel_id=None):
        if not self.current_user:
            print("Сначала войдите в систему!")
            return
        
        cursor = self.conn.cursor()
        
        if chat_id:
            cursor.execute(
                "SELECT id FROM chats WHERE id = ? AND (user1_id = ? OR user2_id = ?)",
                (chat_id, self.current_user['id'], self.current_user['id'])
            )
            if not cursor.fetchone():
                print("У вас нет доступа к этому чату!")
                return
            
            cursor.execute('''
                SELECT m.content, u.username, m.sent_at 
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.chat_id = ?
                ORDER BY m.sent_at
            ''', (chat_id,))
            
            messages = cursor.fetchall()
            print(f"\nСообщения в чате {chat_id}:")
            
        elif group_id:
            cursor.execute(
                "SELECT id FROM group_members WHERE group_id = ? AND user_id = ?",
                (group_id, self.current_user['id'])
            )
            if not cursor.fetchone():
                print("Вы не состоите в этой группе!")
                return
            
            cursor.execute('''
                SELECT m.content, u.username, m.sent_at 
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.group_id = ?
                ORDER BY m.sent_at
            ''', (group_id,))
            
            messages = cursor.fetchall()
            print(f"\nСообщения в группе {group_id}:")
            
        elif channel_id:
            cursor.execute(
                "SELECT id FROM channel_subscribers WHERE channel_id = ? AND user_id = ?",
                (channel_id, self.current_user['id'])
            )
            if not cursor.fetchone():
                print("Вы не подписаны на этот канал!")
                return
            
            cursor.execute('''
                SELECT m.content, u.username, m.sent_at 
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.channel_id = ?
                ORDER BY m.sent_at
            ''', (channel_id,))
            
            messages = cursor.fetchall()
            print(f"\nСообщения в канале {channel_id}:")
            
        else:
            print("Не указан чат, группа или канал!")
            return
        
        if not messages:
            print("Сообщений нет!")
            return
        
        for message in messages:
            print(f"[{message[2]}] {message[1]}: {message[0]}")

def main():
    messenger = SparkMessenger()
    
    while True:
        print("\n=== Spark Messenger ===")
        if messenger.current_user:
            print(f"Вы вошли как: {messenger.current_user['name']} (@{messenger.current_user['username']})")
            print("1. Открыть чаты")
            print("2. Создать чат")
            print("3. Отправить сообщение")
            print("4. Создать группу")
            print("5. Добавить в группу")
            print("6. Создать канал")
            print("7. Подписаться на канал")
            print("8. Показать мои группы")
            print("9. Показать мои каналы")
            print("10. Выйти из аккаунта")
            print("0. Выход")
        else:
            print("1. Регистрация")
            print("2. Вход")
            print("0. Выход")
        
        choice = input("Выберите действие: ").strip()
        
        if not messenger.current_user:
            if choice == '1':
                messenger.register_user()
            elif choice == '2':
                messenger.login()
            elif choice == '0':
                print("До свидания!")
                break
            else:
                print("Неверный выбор!")
        else:
            if choice == '1':
                chats = messenger.show_user_chats()
                if chats:
                    chat_id = input("Введите ID чата для просмотра: ").strip()
                    if chat_id.isdigit():
                        messenger.show_messages(chat_id=int(chat_id))
            elif choice == '2':
                username = input("Введите юзернейм пользователя: ").strip()
                messenger.create_chat(username)
            elif choice == '3':
                chat_id = input("Введите ID чата: ").strip()
                if chat_id.isdigit():
                    messenger.send_message(chat_id=int(chat_id))
            elif choice == '4':
                messenger.create_group()
            elif choice == '5':
                group_id = input("Введите ID группы: ").strip()
                username = input("Введите юзернейм пользователя: ").strip()
                if group_id.isdigit():
                    messenger.add_to_group(int(group_id), username)
            elif choice == '6':
                messenger.create_channel()
            elif choice == '7':
                channel_id = input("Введите ID канала: ").strip()
                if channel_id.isdigit():
                    messenger.subscribe_to_channel(int(channel_id))
            elif choice == '8':
                groups = messenger.show_user_groups()
            elif choice == '9':
                channels = messenger.show_user_channels()
            elif choice == '10':
                messenger.current_user = None
                print("Вы вышли из аккаунта!")
            elif choice == '0':
                print("До свидания!")
                break
            else:
                print("Неверный выбор!")

if __name__ == "__main__":
    main()