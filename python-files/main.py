import os
import random
import shutil
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# CONFIG
TOKEN = "8192304202:AAGwNko3yUCVdha7WqDfC2XTDja3WqQof1E"
MEDIA_FOLDER = "media"
DONE_FOLDER = "done"
FAILED_FOLDER = "failed"
SENT_LOG = "sent_files.txt"
FAILED_LOG = "failed_files.txt"
ALLOWED_GROUP_ID = -1002846544658  # Only this group can use the bot

# CONTROL LIMITS
TOTAL_MEDIA_LIMIT = 25  # /send command (total media)
PHOTO_LIMIT_SEND = 5    # number of photos in /send
PHOTO_LIMIT_ONLY = 10   # number of photos in /photos
PHOTO_ALBUM_SIZE = 5    # number of photos per album

# CLEAR TERMINAL
os.system("cls" if os.name == "nt" else "clear")

def load_sent_files():
    return set(open(SENT_LOG).read().splitlines()) if os.path.exists(SENT_LOG) else set()

def add_to_log(filename, logfile):
    with open(logfile, "a") as f:
        f.write(filename + "\n")

def move_file(file, target_folder):
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(os.path.join(MEDIA_FOLDER, file), os.path.join(target_folder, file))

def get_media_files():
    return [f for f in os.listdir(MEDIA_FOLDER) if os.path.isfile(os.path.join(MEDIA_FOLDER, f))]

def separate_files(files):
    images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]
    videos = [f for f in files if f.lower().endswith((".mp4", ".mkv", ".mov", ".avi"))]
    return images, videos

async def send_video_file(context: ContextTypes.DEFAULT_TYPE, chat_id, file):
    filepath = os.path.join(MEDIA_FOLDER, file)
    try:
        with open(filepath, "rb") as media:
            await context.bot.send_video(chat_id=chat_id, video=media)
        add_to_log(file, SENT_LOG)
        move_file(file, DONE_FOLDER)
        print(f"✅ Sent video: {file}")
        return True
    except:
        add_to_log(file, FAILED_LOG)
        move_file(file, FAILED_FOLDER)
        print(f"❌ Failed video: {file}")
        return False

async def send_photo_album(context: ContextTypes.DEFAULT_TYPE, chat_id, photo_files):
    album = []
    sent_count = 0
    fail_count = 0
    for file in photo_files:
        filepath = os.path.join(MEDIA_FOLDER, file)
        try:
            with open(filepath, "rb") as img:
                album.append(InputMediaPhoto(img.read()))
        except:
            add_to_log(file, FAILED_LOG)
            move_file(file, FAILED_FOLDER)
            print(f"❌ Failed photo: {file}")
            fail_count += 1

    if album:
        try:
            await context.bot.send_media_group(chat_id=chat_id, media=album)
            for file in photo_files:
                add_to_log(file, SENT_LOG)
                move_file(file, DONE_FOLDER)
                print(f"✅ Sent photo: {file}")
                sent_count += 1
        except:
            for file in photo_files:
                add_to_log(file, FAILED_LOG)
                move_file(file, FAILED_FOLDER)
                print(f"❌ Failed album: {file}")
                fail_count += 1

    return sent_count, fail_count

async def send_photos_in_albums(context, chat_id, photo_files):
    total_sent = 0
    total_failed = 0
    for i in range(0, len(photo_files), PHOTO_ALBUM_SIZE):
        batch = photo_files[i:i+PHOTO_ALBUM_SIZE]
        sent, failed = await send_photo_album(context, chat_id, batch)
        total_sent += sent
        total_failed += failed
    return total_sent, total_failed

async def send_command_message_cleanup(update, context):
    await update.message.delete()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Access restricted. Join https://t.me/golobackup")
        return
    await update.message.reply_text("👋 Welcome! You can now use the media bot.")

async def send_mixed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Access restricted. Join https://t.me/golobackup")
        return

    await send_command_message_cleanup(update, context)

    chat_id = update.message.chat_id
    sent_files = load_sent_files()
    all_files = get_media_files()
    remaining_files = [f for f in all_files if f not in sent_files]
    images, videos = separate_files(remaining_files)

    if not images and not videos:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ No media files available.")
        return

    num_photos = min(PHOTO_LIMIT_SEND, len(images))
    num_videos = min(TOTAL_MEDIA_LIMIT - num_photos, len(videos))

    selected_photos = random.sample(images, num_photos)
    selected_videos = random.sample(videos, num_videos)

    photo_sent, photo_failed = await send_photos_in_albums(context, chat_id, selected_photos)

    video_sent = 0
    for video in selected_videos:
        success = await send_video_file(context, chat_id, video)
        if success:
            video_sent += 1

    total = photo_sent + video_sent
    print("\n----- SUMMARY -----")
    print(f"✅ Photos sent: {photo_sent}")
    print(f"❌ Photos failed: {photo_failed}")
    print(f"✅ Videos sent: {video_sent}")
    print(f"🎯 Total sent: {total}")

    await context.bot.send_message(chat_id=chat_id, text=f"✅ {total} media sent successfully!")

async def send_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Access restricted. Join https://t.me/golobackup")
        return

    await send_command_message_cleanup(update, context)

    chat_id = update.message.chat_id
    sent_files = load_sent_files()
    all_files = get_media_files()
    remaining_files = [f for f in all_files if f not in sent_files]
    images, _ = separate_files(remaining_files)

    if not images:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ No images available.")
        return

    selected_photos = random.sample(images, min(PHOTO_LIMIT_ONLY, len(images)))
    sent, failed = await send_photos_in_albums(context, chat_id, selected_photos)

    print("\n----- PHOTO SUMMARY -----")
    print(f"✅ Photos sent: {sent}")
    print(f"❌ Photos failed: {failed}")

    await context.bot.send_message(chat_id=chat_id, text=f"✅ {sent} photos sent successfully!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_mixed))
    app.add_handler(CommandHandler("photos", send_photos))

    app.run_polling()

if __name__ == '__main__':
    main()
