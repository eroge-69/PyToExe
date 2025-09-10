import os
import sys
import re
import random
import string
import time
import threading
import sqlite3
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


# Utilities and Constants


APP_NAME = "Shift Cipher Decrypter"
APP_INTRO = "A simple lab for classical ciphers and secure file handling."
VERSION = "1.0.0"

SUPPORTED_UI_LANGS = ["en", "Big5", "GB", "japanese", "spanish"]

# language packs
LANG_PACKS: Dict[str, Dict[str, str]] = {
    "en": {
        "title": APP_NAME,
        "intro": APP_INTRO,
        "start": "Start",
        "morse": "Morse Code",
        "caesar": "Caesar Cipher",
        "vigenere": "Vigenère Cipher",
        "ai_auto": "AI Auto",
        "learn_more": "Click bold name to learn more.",
        "info": "Information",
        "ok": "OK",
        "cancel": "Cancel",
        "exit": "Exit",
        "restart": "Restart",
        "settings": "Settings",
        "language": "Language",
        "login": "Login",
        "logout": "Logout",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "member_login": "Member Login",
        "member_register": "Member Registration",
        "save": "Save",
        "download": "Download",
        "help": "Help",
        "how_to_use": "How to Use",
        "how_text": (
            "1) Choose a mode.\n"
            "2) For encryption/decryption, choose language and input a valid file.\n"
            "3) Wait for progress to complete, then download the result.\n"
            "4) Exit after encryption will show a 6-char key storing original content in this session."
        ),
        "theme_auto": "Auto Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "choose_lang": "Choose language for processing:",
        "encrypt": "Encrypt",
        "decrypt": "Decrypt",
        "file_hint_txt": "Use a .txt file with at least 100 words. Drop/select file below.",
        "file_hint_txt_pdf": "Use a .txt or .pdf file (no word limit). Drop/select file below.",
        "browse": "Browse...",
        "file_selected": "File selected:",
        "confirm": "Confirm",
        "invalid_file": "Invalid file. Please provide a .txt file with > 100 words.",
        "invalid_file_ai": "Invalid file. Please provide a .txt or .pdf file.",
        "progress_encrypt": "Encrypting...",
        "progress_decrypt": "Decrypting...",
        "completed": "Completed",
        "result": "Result",
        "save_as": "Save As",
        "exit_key_msg": "Your 6-character key (stores original text in this session):",
        "need_login": "AI Auto requires member login.",
        "already_logged_in": "Already logged in.",
        "login_first": "Please login first.",
        "login_success": "Login successful.",
        "logout_success": "Logged out.",
        "register_success": "Registration successful. You can now login.",
        "user_exists": "Username already exists.",
        "weak_password": "Password must be at least 12 chars and include upper, lower, digit, and symbol.",
        "password_mismatch": "Passwords do not match.",
        "bad_credentials": "Invalid username or password.",
        "db_view_title": "Database Viewer",
        "db_view_denied": "Access denied.",
        "select_mode": "Select Mode",
        "choose_option": "Choose an option",
        "morse_info": "Morse Code: encodes text as sequences of dots and dashes.",
        "caesar_info": "Caesar Cipher: shifts letters by a fixed amount (default 3).",
        "vigenere_info": "Vigenère Cipher: polyalphabetic cipher using a keyword.",
        "ai_info": "AI Auto: automatic heuristic cipher (no length limit; requires login).",
        "language_select_label": "Processing language",
        "enter_key": "Enter 6-char key",
        "invalid_key": "Invalid key format. It must be 6 chars of letters, digits, or symbols.",
        "not_enough_words": "The file must contain more than 100 words.",
        "drag_here": "Drop file here or click to select",
        "file_error": "File Error",
        "pdf_parse_warn": "PDF text extraction is basic and may fail on complex PDFs.",
    },
    "Big5": {
        "title": APP_NAME,
        "intro": "一個簡單的古典加密與檔案處理工具。",
        "start": "開始",
        "morse": "摩斯密碼",
        "caesar": "凱撒密碼",
        "vigenere": "維吉尼亞多表代換密碼",
        "ai_auto": "AI 自動",
        "learn_more": "按粗體名稱查看介紹。",
        "info": "資訊",
        "ok": "確定",
        "cancel": "取消",
        "exit": "離開程式",
        "restart": "重新使用",
        "settings": "設定",
        "language": "系統語言",
        "login": "會員登入",
        "logout": "登出",
        "register": "註冊",
        "username": "會員名稱",
        "password": "密碼",
        "confirm_password": "確認密碼",
        "member_login": "會員登入",
        "member_register": "會員註冊",
        "save": "儲存",
        "download": "下載",
        "help": "說明書",
        "how_to_use": "使用說明",
        "how_text": (
            "1) 選擇模式。\n"
            "2) 加/解密時選擇語言並提供符合規則的檔案。\n"
            "3) 等待進度完成後可下載結果。\n"
            "4) 加密後離開會顯示 6 位鎖匙（本次啟動有效）。"
        ),
        "theme_auto": "自動模式",
        "theme_light": "淺色",
        "theme_dark": "深色",
        "choose_lang": "選擇處理語言：",
        "encrypt": "加密",
        "decrypt": "解密",
        "file_hint_txt": "請使用 .txt 且字數需超過 100，將檔案拖放/選取於下方。",
        "file_hint_txt_pdf": "請使用 .txt 或 .pdf（字數不限），將檔案拖放/選取於下方。",
        "browse": "選取檔案...",
        "file_selected": "已選擇檔案：",
        "confirm": "確認",
        "invalid_file": "檔案無效。請提供 .txt 且字數超過 100。",
        "invalid_file_ai": "檔案無效。只接受 .txt 或 .pdf。",
        "progress_encrypt": "加密中...",
        "progress_decrypt": "解密中...",
        "completed": "完成",
        "result": "結果",
        "save_as": "另存新檔",
        "exit_key_msg": "你的 6 位數鎖匙（保存原文，僅本次）：",
        "need_login": "AI 自動需要會員登入。",
        "already_logged_in": "已登入。",
        "login_first": "請先登入。",
        "login_success": "登入成功。",
        "logout_success": "已登出。",
        "register_success": "註冊成功，請登入。",
        "user_exists": "會員名稱已存在。",
        "weak_password": "密碼至少 12 字且包含大小寫、數字與符號。",
        "password_mismatch": "兩次密碼不一致。",
        "bad_credentials": "帳號或密碼錯誤。",
        "db_view_title": "資料庫檢視",
        "db_view_denied": "拒絕存取。",
        "select_mode": "選擇模式",
        "choose_option": "選擇項目",
        "morse_info": "摩斯密碼：以點與劃表示字元。",
        "caesar_info": "凱撒密碼：將字母以固定位移（預設 3）。",
        "vigenere_info": "維吉尼亞：用關鍵字的多表代換。",
        "ai_info": "AI 自動：啟發式自動加解密（需登入，不限長度）。",
        "language_select_label": "處理語言",
        "enter_key": "輸入 6 位鎖匙",
        "invalid_key": "鎖匙格式錯誤，需為 6 位字母、數字或符號。",
        "not_enough_words": "檔案字數需超過 100。",
        "drag_here": "將檔案拖放於此或點擊選擇",
        "file_error": "檔案錯誤",
        "pdf_parse_warn": "PDF 萃文字功能簡易，可能無法處理複雜 PDF。",
    },
    "GB": {
        "title": APP_NAME,
        "intro": "一个简单的古典加密与文件处理工具。",
        "start": "开始",
        "morse": "摩斯密码",
        "caesar": "凯撒密码",
        "vigenere": "维吉尼亚多表代换密码",
        "ai_auto": "AI 自动",
        "learn_more": "点粗体名称查看介绍。",
        "info": "信息",
        "ok": "确定",
        "cancel": "取消",
        "exit": "退出程序",
        "restart": "重新使用",
        "settings": "设置",
        "language": "系统语言",
        "login": "会员登录",
        "logout": "登出",
        "register": "注册",
        "username": "会员名称",
        "password": "密码",
        "confirm_password": "确认密码",
        "member_login": "会员登录",
        "member_register": "会员注册",
        "save": "保存",
        "download": "下载",
        "help": "说明书",
        "how_to_use": "使用说明",
        "how_text": (
            "1) 选择模式。\n"
            "2) 加/解密时选择语言并提供合规文件。\n"
            "3) 等待进度完成后可下载结果。\n"
            "4) 加密后退出会显示 6 位钥匙（仅本次有效）。"
        ),
        "theme_auto": "自动模式",
        "theme_light": "浅色",
        "theme_dark": "深色",
        "choose_lang": "选择处理语言：",
        "encrypt": "加密",
        "decrypt": "解密",
        "file_hint_txt": "请使用 .txt 且字数需超过 100，将文件拖放/选择于下方。",
        "file_hint_txt_pdf": "请使用 .txt 或 .pdf（字数不限），将文件拖放/选择于下方。",
        "browse": "选择文件...",
        "file_selected": "已选择文件：",
        "confirm": "确认",
        "invalid_file": "文件无效。请提供 .txt 且字数超过 100。",
        "invalid_file_ai": "文件无效。仅接受 .txt 或 .pdf。",
        "progress_encrypt": "加密中...",
        "progress_decrypt": "解密中...",
        "completed": "完成",
        "result": "结果",
        "save_as": "另存为",
        "exit_key_msg": "你的 6 位钥匙（保存原文，仅本次）：",
        "need_login": "AI 自动需要会员登录。",
        "already_logged_in": "已登录。",
        "login_first": "请先登录。",
        "login_success": "登录成功。",
        "logout_success": "已登出。",
        "register_success": "注册成功，请登录。",
        "user_exists": "会员名称已存在。",
        "weak_password": "密码至少 12 字且包含大小写、数字与符号。",
        "password_mismatch": "两次密码不一致。",
        "bad_credentials": "账号或密码错误。",
        "db_view_title": "数据库查看",
        "db_view_denied": "拒绝访问。",
        "select_mode": "选择模式",
        "choose_option": "选择项目",
        "morse_info": "摩斯密码：用点与划表示字符。",
        "caesar_info": "凯撒密码：把字母按固定位移（默认 3）。",
        "vigenere_info": "维吉尼亚：用关键字的多表代换。",
        "ai_info": "AI 自动：启发式自动加解密（需登录，不限长度）。",
        "language_select_label": "处理语言",
        "enter_key": "输入 6 位钥匙",
        "invalid_key": "钥匙格式错误，需为 6 位字母、数字或符号。",
        "not_enough_words": "文件字数需超过 100。",
        "drag_here": "将文件拖放到此或点击选择",
        "file_error": "文件错误",
        "pdf_parse_warn": "PDF 文本提取功能简单，可能无法处理复杂 PDF。",
    },
    "japanese": {
        "title": APP_NAME,
        "intro": "古典暗号とファイル処理のための簡単なツール。",
        "start": "開始",
        "morse": "モールス信号",
        "caesar": "シーザー暗号",
        "vigenere": "ヴィジュネル暗号",
        "ai_auto": "AI 自動",
        "learn_more": "太字名をクリックで詳細。",
        "info": "情報",
        "ok": "OK",
        "cancel": "キャンセル",
        "exit": "終了",
        "restart": "再起動",
        "settings": "設定",
        "language": "言語",
        "login": "ログイン",
        "logout": "ログアウト",
        "register": "登録",
        "username": "ユーザー名",
        "password": "パスワード",
        "confirm_password": "パスワード確認",
        "member_login": "会員ログイン",
        "member_register": "会員登録",
        "save": "保存",
        "download": "ダウンロード",
        "help": "ヘルプ",
        "how_to_use": "使い方",
        "how_text": (
            "1) モードを選ぶ。\n"
            "2) 暗号化/復号では言語と有効なファイルを指定。\n"
            "3) 進行が完了したら結果を保存。\n"
            "4) 暗号化後に終了すると 6 文字キーが表示されます（セッション限定）。"
        ),
        "theme_auto": "自動テーマ",
        "theme_light": "ライト",
        "theme_dark": "ダーク",
        "choose_lang": "処理言語を選択：",
        "encrypt": "暗号化",
        "decrypt": "復号",
        "file_hint_txt": ".txt（100語以上）を下にドロップ/選択してください。",
        "file_hint_txt_pdf": ".txt または .pdf（語数無制限）を下にドロップ/選択してください。",
        "browse": "参照...",
        "file_selected": "選択ファイル：",
        "confirm": "確認",
        "invalid_file": "無効なファイル。.txt で 100 語以上が必要です。",
        "invalid_file_ai": "無効なファイル。.txt または .pdf のみ対応。",
        "progress_encrypt": "暗号化中...",
        "progress_decrypt": "復号中...",
        "completed": "完了",
        "result": "結果",
        "save_as": "名前を付けて保存",
        "exit_key_msg": "6 文字キー（原文をセッション保存）：",
        "need_login": "AI 自動はログインが必要です。",
        "already_logged_in": "既にログイン済み。",
        "login_first": "先にログインしてください。",
        "login_success": "ログイン成功。",
        "logout_success": "ログアウトしました。",
        "register_success": "登録成功。ログインしてください。",
        "user_exists": "ユーザー名は既に存在します。",
        "weak_password": "12文字以上で大小英字・数字・記号を含めてください。",
        "password_mismatch": "パスワードが一致しません。",
        "bad_credentials": "ユーザー名またはパスワードが違います。",
        "db_view_title": "データベース表示",
        "db_view_denied": "アクセス拒否。",
        "select_mode": "モード選択",
        "choose_option": "オプションを選択",
        "morse_info": "モールス信号：点と線で文字を表す。",
        "caesar_info": "シーザー暗号：固定シフト（既定 3）。",
        "vigenere_info": "ヴィジュネル：キーワードによる多表式。",
        "ai_info": "AI 自動：ヒューリスティック自動暗号（ログイン必須）。",
        "language_select_label": "処理言語",
        "enter_key": "6文字のキーを入力",
        "invalid_key": "キー形式が不正。英数記号6文字です。",
        "not_enough_words": "100語を超える必要があります。",
        "drag_here": "ここへドロップまたはクリックで選択",
        "file_error": "ファイルエラー",
        "pdf_parse_warn": "PDF テキスト抽出は簡易的です。",
    },
    "spanish": {
        "title": APP_NAME,
        "intro": "Un laboratorio simple para cifrados clásicos y archivos.",
        "start": "Comenzar",
        "morse": "Código Morse",
        "caesar": "Cifrado César",
        "vigenere": "Cifrado Vigenère",
        "ai_auto": "AI Auto",
        "learn_more": "Haz clic en el nombre en negrita para ver info.",
        "info": "Información",
        "ok": "OK",
        "cancel": "Cancelar",
        "exit": "Salir",
        "restart": "Reiniciar",
        "settings": "Ajustes",
        "language": "Idioma",
        "login": "Iniciar sesión",
        "logout": "Cerrar sesión",
        "register": "Registrar",
        "username": "Usuario",
        "password": "Contraseña",
        "confirm_password": "Confirmar",
        "member_login": "Inicio de sesión",
        "member_register": "Registro",
        "save": "Guardar",
        "download": "Descargar",
        "help": "Ayuda",
        "how_to_use": "Cómo usar",
        "how_text": (
            "1) Elige un modo.\n"
            "2) Para cifrar/descifrar, elige idioma y un archivo válido.\n"
            "3) Espera la barra de progreso y guarda el resultado.\n"
            "4) Al salir tras cifrar se muestra una clave de 6 caracteres (solo sesión actual)."
        ),
        "theme_auto": "Tema automático",
        "theme_light": "Claro",
        "theme_dark": "Oscuro",
        "choose_lang": "Idioma de procesamiento:",
        "encrypt": "Cifrar",
        "decrypt": "Descifrar",
        "file_hint_txt": "Usa .txt con más de 100 palabras. Suelta/selecciona abajo.",
        "file_hint_txt_pdf": "Usa .txt o .pdf (sin límite). Suelta/selecciona abajo.",
        "browse": "Examinar...",
        "file_selected": "Archivo:",
        "confirm": "Confirmar",
        "invalid_file": "Archivo inválido. Se requiere .txt con > 100 palabras.",
        "invalid_file_ai": "Archivo inválido. Solo .txt o .pdf.",
        "progress_encrypt": "Cifrando...",
        "progress_decrypt": "Descifrando...",
        "completed": "Completado",
        "result": "Resultado",
        "save_as": "Guardar como",
        "exit_key_msg": "Tu clave de 6 caracteres (guarda original en esta sesión):",
        "need_login": "AI Auto requiere inicio de sesión.",
        "already_logged_in": "Ya has iniciado sesión.",
        "login_first": "Primero inicia sesión.",
        "login_success": "Inicio de sesión correcto.",
        "logout_success": "Sesión cerrada.",
        "register_success": "Registro correcto. Ahora inicia sesión.",
        "user_exists": "Usuario ya existe.",
        "weak_password": "La contraseña debe tener 12+ y mezclar mayúsculas, minúsculas, dígitos y símbolos.",
        "password_mismatch": "Las contraseñas no coinciden.",
        "bad_credentials": "Usuario o contraseña incorrectos.",
        "db_view_title": "Visor de Base de Datos",
        "db_view_denied": "Acceso denegado.",
        "select_mode": "Selecciona modo",
        "choose_option": "Elige opción",
        "morse_info": "Morse: puntos y rayas para representar texto.",
        "caesar_info": "César: desplazamiento fijo (por defecto 3).",
        "vigenere_info": "Vigenère: polialfabético con palabra clave.",
        "ai_info": "AI Auto: cifrado heurístico automático (requiere login).",
        "language_select_label": "Idioma de proceso",
        "enter_key": "Ingresa clave de 6 caracteres",
        "invalid_key": "Formato inválido: 6 caracteres alfanuméricos o símbolos.",
        "not_enough_words": "El archivo debe tener más de 100 palabras.",
        "drag_here": "Suelta aquí o haz clic para elegir",
        "file_error": "Error de archivo",
        "pdf_parse_warn": "La extracción PDF es básica; puede fallar en PDFs complejos.",
    },
}

PROCESS_LANGS = ["English", "中文", "日本語", "Español", "Français", "Deutsch"]

# key to store original_text
SESSION_KEYS: Dict[str, str] = {}

def generate_key() -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(random.choice(chars) for _ in range(6))

def validate_key(k: str) -> bool:
    return isinstance(k, str) and len(k) == 6


# Database (membership)


DB_FILE = "cipherlab_users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            uses INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def db_user_exists(username: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def db_register(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users(username,password,uses) VALUES(?,?,0)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def db_login(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    return row is not None

def db_increment_uses(username: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE users SET uses = uses + 1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def db_get_all() -> List[Tuple[str,int]]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT username, uses FROM users ORDER BY username")
    rows = cur.fetchall()
    conn.close()
    return rows


# Cipher Implementations

MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
    '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
    ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
    '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
}
MORSE_DECODE = {v: k for k, v in MORSE_CODE.items()}

def morse_encrypt(text: str) -> str:
    return ' '.join(MORSE_CODE.get(ch.upper(), '') for ch in text)

def morse_decrypt(code: str) -> str:
    words = code.split(' ')
    return ''.join(MORSE_DECODE.get(w, '') for w in words).replace('/', ' ')

def caesar_encrypt(text: str, shift: int = 3) -> str:
    out = []
    for ch in text:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        elif 'A' <= ch <= 'Z':
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            out.append(ch)
    return ''.join(out)

def caesar_decrypt(text: str, shift: int = 3) -> str:
    return caesar_encrypt(text, -shift)

def vigenere_encrypt(text: str, key: str = "KEY") -> str:
    out = []
    key = re.sub(r'[^A-Za-z]', '', key)
    if not key:
        key = "KEY"
    ki = 0
    for ch in text:
        if ch.isalpha():
            shift = (ord(key[ki % len(key)].upper()) - 65)
            if ch.isupper():
                out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
            else:
                out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

def vigenere_decrypt(text: str, key: str = "KEY") -> str:
    out = []
    key = re.sub(r'[^A-Za-z]', '', key)
    if not key:
        key = "KEY"
    ki = 0
    for ch in text:
        if ch.isalpha():
            shift = (ord(key[ki % len(key)].upper()) - 65)
            if ch.isupper():
                out.append(chr((ord(ch) - 65 - shift) % 26 + 65))
            else:
                out.append(chr((ord(ch) - 97 - shift) % 26 + 97))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

# Heuristic "AI" cipher: deterministic substitution + block shuffle
AI_SUBST = dict(zip(string.printable, reversed(string.printable)))
def ai_auto_encrypt(text: str) -> str:
    # block shuffle of 64 chars chunks reversed order + substitution
    chunks = [text[i:i+64] for i in range(0, len(text), 64)]
    chunks.reverse()
    j = ''.join(chunks)
    return ''.join(AI_SUBST.get(c, c) for c in j)

def ai_auto_decrypt(text: str) -> str:
    inv = {v: k for k, v in AI_SUBST.items()}
    j = ''.join(inv.get(c, c) for c in text)
    chunks = [j[i:i+64] for i in range(0, len(j), 64)]
    chunks.reverse()
    return ''.join(chunks)


# PDF Extractor


def extract_text_from_pdf_basic(path: str) -> str:
    # Very naive: pulls text between parentheses in BT/ET sections
    try:
        with open(path, 'rb') as f:
            data = f.read()
        text = data.decode('latin1', errors='ignore')
        # Warn: extremely basic and may fail often
        matches = re.findall(r'\((.*?)\)', text, flags=re.S)
        out = []
        for m in matches:
            m = m.replace('\\)', ')').replace('\\(', '(').replace('\\n', '\n')
            out.append(m)
        return ''.join(out)
    except Exception:
        return ""


# File Helpers


def read_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def count_words(text: str) -> int:
    return len(re.findall(r'\b\S+\b', text))

def save_text_dialog(default_name: str, content: str, lang_dict: Dict[str, str]):
    file = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("Text", "*.txt")],
                                        initialfile=default_name,
                                        title=lang_dict["save_as"])
    if file:
        with open(file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)


# auto, light, dark
@dataclass
class Theme:
    name: str
    bg: str
    fg: str
    accent: str
    panel: str
    dashed_border: str

LIGHT_THEME = Theme("light", "#f5f7fa", "#111111", "#4f7cff", "#ffffff", "#95a5a6")
DARK_THEME  = Theme("dark",  "#0f141a", "#e8e8e8", "#6ea8fe", "#1c2630", "#7f8c8d")


# Main

class CipherLabApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # prepare then show

        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("980x640")
        self.minsize(900, 560)

        # State
        self.ui_lang = "en"
        self.theme_mode = "auto"  # auto/light/dark
        self.logged_in_user: Optional[str] = None

        self.lang = LANG_PACKS[self.ui_lang]

        self.style = ttk.Style()
        self._apply_theme()

        self.container = tk.Frame(self, bg=self._theme().bg)
        self.container.pack(fill="both", expand=True)

        self.bg_canvas = tk.Canvas(self.container, highlightthickness=0, bd=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._redraw_background)

        # Top bar
        self.top_bar = tk.Frame(self.container, bg=self._theme().panel)
        self.top_bar.place(relx=0, rely=0, relwidth=1, height=48)

        self.title_label = tk.Label(self.top_bar, text=APP_NAME, font=("Segoe UI", 14, "bold"),
                                    bg=self._theme().panel, fg=self._theme().fg)
        self.title_label.pack(side="left", padx=12)

        self.help_btn = tk.Button(self.top_bar, text="❓", command=self._show_help,
                                  bg=self._theme().panel, fg=self._theme().fg, bd=0, font=("Segoe UI", 14))
        self.help_btn.pack(side="right", padx=8)

        # theme auto toggle & settings buttion
        self.bottom_bar = tk.Frame(self.container, bg=self._theme().panel)
        self.bottom_bar.place(relx=0, rely=1, anchor="sw", relwidth=1, height=48)

        self.theme_var = tk.StringVar(value="auto")
        self.theme_menu = ttk.Combobox(self.bottom_bar, textvariable=self.theme_var, state="readonly",
                                       values=[self.lang["theme_auto"], self.lang["theme_light"], self.lang["theme_dark"]])
        self.theme_menu.current(0)
        self.theme_menu.bind("<<ComboboxSelected>>", self._on_theme_change)
        self.theme_menu.place(x=8, y=10, width=160)

        self.settings_btn = ttk.Button(self.bottom_bar, text=self.lang["settings"], command=self._open_settings)
        self.settings_btn.place(x=180, y=10, width=120)

        # frame
        self.main_frame = tk.Frame(self.container, bg=self._theme().bg)
        self.main_frame.place(relx=0, rely=0, y=48, relwidth=1, relheight=1, height=-96)

        self._show_start_screen()

        self.after(50, self.deiconify)

        # Drag and drop
        self._enable_drop(self.main_frame)

# auto background: light during day, dark at night
    def _theme(self) -> Theme:
        if self.theme_mode == "light":
            return LIGHT_THEME
        if self.theme_mode == "dark":
            return DARK_THEME

        hour = time.localtime().tm_hour
        return LIGHT_THEME if 7 <= hour <= 18 else DARK_THEME

    def _apply_theme(self):
        t = self._theme()
        self.configure(bg=t.bg)
        try:
            self.style.theme_use('default')
        except:
            pass
        self.style.configure("TFrame", background=t.bg)
        self.style.configure("TLabel", background=t.bg, foreground=t.fg)
        self.style.configure("TButton", background=t.panel, foreground=t.fg)
        self.style.configure("TNotebook", background=t.bg)
        self.style.configure("TNotebook.Tab", background=t.panel, foreground=t.fg)
        self.style.configure("TCombobox", fieldbackground=t.panel, background=t.panel, foreground=t.fg)
        self.style.configure("Horizontal.TProgressbar", troughcolor=t.panel, background=t.accent)

    def _on_theme_change(self, _event=None):
        val = self.theme_var.get()
        if val == self.lang["theme_light"]:
            self.theme_mode = "light"
        elif val == self.lang["theme_dark"]:
            self.theme_mode = "dark"
        else:
            self.theme_mode = "auto"
        self._apply_theme()
        self._refresh_all()

    def _refresh_all(self):
        # Repaint basic areas
        self.container.configure(bg=self._theme().bg)
        self.top_bar.configure(bg=self._theme().panel)
        self.title_label.configure(bg=self._theme().panel, fg=self._theme().fg)
        self.help_btn.configure(bg=self._theme().panel, fg=self._theme().fg)
        self.bottom_bar.configure(bg=self._theme().panel)
        self.settings_btn.configure(style="TButton")
        self._redraw_background()
        # Rebuild central frame content to apply colors
        current_children = list(self.main_frame.children.values())
        for w in current_children:
            w.destroy()
        # Re-render current state:
        if hasattr(self, "_current_screen") and self._current_screen == "mode":
            self._show_mode_screen()
        elif hasattr(self, "_current_screen") and self._current_screen.startswith("cipher:"):
            _, name = self._current_screen.split(":", 1)
            self._show_cipher_screen(name)
        elif hasattr(self, "_current_screen") and self._current_screen == "ai":
            self._show_ai_screen()
        else:
            self._show_start_screen()

    def _redraw_background(self, _event=None):
        t = self._theme()
        self.bg_canvas.delete("all")
        self.bg_canvas.configure(bg=t.bg)
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        # Draw a simple tech grid and nodes
        step = 40
        color = "#1f2a36" if t.name == "dark" else "#dce3ea"
        for x in range(0, w, step):
            self.bg_canvas.create_line(x, 0, x, h, fill=color)
        for y in range(0, h, step):
            self.bg_canvas.create_line(0, y, w, y, fill=color)
        # Nodes
        for _ in range(60):
            nx = random.randint(0, max(0, w-1))
            ny = random.randint(0, max(0, h-1))
            self.bg_canvas.create_oval(nx-1, ny-1, nx+1, ny+1, fill=self._theme().accent, outline="")

    def _show_help(self):
        messagebox.showinfo(self.lang["how_to_use"], self.lang["how_text"])

    def _open_settings(self):
        dlg = tk.Toplevel(self)
        dlg.title(self.lang["settings"])
        dlg.geometry("420x280")
        dlg.configure(bg=self._theme().bg)
        ttk.Label(dlg, text=self.lang["language"]).pack(pady=8)
        lang_var = tk.StringVar(value=self.ui_lang)
        ttk.Combobox(dlg, textvariable=lang_var, values=SUPPORTED_UI_LANGS, state="readonly").pack(pady=4)

        def apply_lang():
            self.ui_lang = lang_var.get()
            self.lang = LANG_PACKS[self.ui_lang]
            # Update labels
            self.settings_btn.configure(text=self.lang["settings"])
            self.theme_menu.configure(values=[self.lang["theme_auto"], self.lang["theme_light"], self.lang["theme_dark"]])
            if self.theme_mode == "auto":
                self.theme_menu.current(0)
            elif self.theme_mode == "light":
                self.theme_menu.current(1)
            else:
                self.theme_menu.current(2)
            self._refresh_all()

        ttk.Button(dlg, text=self.lang["save"], command=apply_lang).pack(pady=8)

        # Login/Logout function
        login_frame = ttk.LabelFrame(dlg, text=self.lang["login"])
        login_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(login_frame, text=self.lang["username"]).grid(row=0, column=0, padx=6, pady=4, sticky="e")
        ttk.Label(login_frame, text=self.lang["password"]).grid(row=1, column=0, padx=6, pady=4, sticky="e")
        u_var = tk.StringVar()
        p_var = tk.StringVar()
        u_entry = ttk.Entry(login_frame, textvariable=u_var)
        p_entry = ttk.Entry(login_frame, textvariable=p_var, show="*")
        u_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        p_entry.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        login_frame.columnconfigure(1, weight=1)

        def do_login():
            u = u_var.get().strip()
            p = p_var.get()
            if db_login(u, p):
                self.logged_in_user = u
                messagebox.showinfo(self.lang["login"], self.lang["login_success"])
                if u == "000" and p == "abc1230":
                    self._show_db_viewer()
            else:
                messagebox.showerror(self.lang["login"], self.lang["bad_credentials"])

        def do_logout():
            self.logged_in_user = None
            messagebox.showinfo(self.lang["logout"], self.lang["logout_success"])

        btns = tk.Frame(login_frame, bg=self._theme().bg)
        btns.grid(row=2, column=0, columnspan=2, pady=4)
        ttk.Button(btns, text=self.lang["login"], command=do_login).pack(side="left", padx=4)
        ttk.Button(btns, text=self.lang["logout"], command=do_logout).pack(side="left", padx=4)

        # Register
        reg_frame = ttk.LabelFrame(dlg, text=self.lang["register"])
        reg_frame.pack(fill="x", padx=10, pady=8)
        ru_var = tk.StringVar()
        rp_var = tk.StringVar()
        rc_var = tk.StringVar()
        ttk.Label(reg_frame, text=self.lang["username"]).grid(row=0, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(reg_frame, textvariable=ru_var).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        ttk.Label(reg_frame, text=self.lang["password"]).grid(row=1, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(reg_frame, textvariable=rp_var, show="*").grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        ttk.Label(reg_frame, text=self.lang["confirm_password"]).grid(row=2, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(reg_frame, textvariable=rc_var, show="*").grid(row=2, column=1, padx=6, pady=4, sticky="ew")
        reg_frame.columnconfigure(1, weight=1)

        def strong_password(pw: str) -> bool:
            return (
                len(pw) >= 12
                and re.search(r'[a-z]', pw)
                and re.search(r'[A-Z]', pw)
                and re.search(r'\d', pw)
                and re.search(r'[^A-Za-z0-9]', pw)
            )

        def do_register():
            u = ru_var.get().strip()
            p = rp_var.get()
            c = rc_var.get()
            if db_user_exists(u):
                messagebox.showerror(self.lang["register"], self.lang["user_exists"])
                return
            if p != c:
                messagebox.showerror(self.lang["register"], self.lang["password_mismatch"])
                return
            if not strong_password(p):
                messagebox.showerror(self.lang["register"], self.lang["weak_password"])
                return
            if db_register(u, p):
                messagebox.showinfo(self.lang["register"], self.lang["register_success"])
            else:
                messagebox.showerror(self.lang["register"], self.lang["user_exists"])

    def _show_db_viewer(self):
        dlg = tk.Toplevel(self)
        dlg.title(self.lang["db_view_title"])
        dlg.geometry("380x300")
        dlg.configure(bg=self._theme().bg)
        lst = tk.Listbox(dlg)
        lst.pack(fill="both", expand=True, padx=8, pady=8)
        for u, uses in db_get_all():
            lst.insert("end", f"{u}: {uses} uses")

    # Start screen
    def _show_start_screen(self):
        self._current_screen = "start"
        f = tk.Frame(self.main_frame, bg=self._theme().bg)
        f.pack(fill="both", expand=True)
        title = tk.Label(f, text=self.lang["title"], font=("Segoe UI", 26, "bold"), bg=self._theme().bg, fg=self._theme().fg)
        title.pack(pady=(50, 10))
        intro = tk.Label(f, text=self.lang["intro"], font=("Segoe UI", 12), bg=self._theme().bg, fg=self._theme().fg)
        intro.pack(pady=(0, 20))
        start_btn = ttk.Button(f, text=self.lang["start"], command=self._show_mode_screen)
        start_btn.pack(pady=12, ipady=6, ipadx=16)

 # Mode screen
    def _show_mode_screen(self):
        self._current_screen = "mode"
        for w in self.main_frame.winfo_children():
            w.destroy()
        f = tk.Frame(self.main_frame, bg=self._theme().bg)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(f, text=self.lang["select_mode"], font=("Segoe UI", 16, "bold"),
                 bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w")

        grid = tk.Frame(f, bg=self._theme().bg)
        grid.pack(fill="both", expand=True, pady=10)

        options = [
            ("•", self.lang["morse"], "morse", self.lang["morse_info"]),
            ("↻", self.lang["caesar"], "caesar", self.lang["caesar_info"]),
            ("🔑", self.lang["vigenere"], "vigenere", self.lang["vigenere_info"]),
            ("🤖", self.lang["ai_auto"], "ai", self.lang["ai_info"]),
        ]

        def mk_card(parent, icon, label, code, info):
            card = tk.Frame(parent, bg=self._theme().panel, bd=0, highlightthickness=0)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=8)
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 48),
                     bg=self._theme().panel, fg=self._theme().fg).pack(pady=(12, 0))
            name_btn = tk.Button(card, text=label, font=("Segoe UI", 12, "bold"),
                                 bg=self._theme().panel, fg=self._theme().fg, bd=0,
                                 command=lambda c=code: self._open_option(c))
            name_btn.pack(pady=(4, 2))
            info_btn = tk.Button(card, text="ℹ", bd=0, font=("Segoe UI", 12),
                                 bg=self._theme().panel, fg=self._theme().fg,
                                 command=lambda: messagebox.showinfo(self.lang["info"], info))
            info_btn.pack(pady=(0, 8))
            card.bind("<Button-1>", lambda e, c=code: self._open_option(c))

        for icon, label, code, info in options:
            mk_card(grid, icon, label, code, info)

    def _open_option(self, code: str):
        if code == "ai":
            self._show_ai_screen()
        else:
            self._show_cipher_screen(code)

    # Cipher screen (Morse/Caesar/Vigenere)
    def _show_cipher_screen(self, name: str):
        self._current_screen = f"cipher:{name}"
        for w in self.main_frame.winfo_children():
            w.destroy()

        f = tk.Frame(self.main_frame, bg=self._theme().bg)
        f.pack(fill="both", expand=True, padx=20, pady=10)

        hdr = tk.Frame(f, bg=self._theme().bg)
        hdr.pack(fill="x")
        title = {
            "morse": self.lang["morse"],
            "caesar": self.lang["caesar"],
            "vigenere": self.lang["vigenere"]
        }.get(name, "")
        tk.Label(hdr, text=title, font=("Segoe UI", 16, "bold"), bg=self._theme().bg, fg=self._theme().fg).pack(side="left")

        nb = ttk.Notebook(f)
        nb.pack(fill="both", expand=True, pady=10)

        encrypt_tab = tk.Frame(nb, bg=self._theme().bg)
        decrypt_tab = tk.Frame(nb, bg=self._theme().bg)
        nb.add(encrypt_tab, text=self.lang["encrypt"])
        nb.add(decrypt_tab, text=self.lang["decrypt"])

        def build_tab(tab: tk.Frame, mode: str):
            # mode = "encrypt" or "decrypt"
            tk.Label(tab, text=self.lang["choose_lang"], bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w", padx=8, pady=(6, 2))
            lang_var = tk.StringVar(value=PROCESS_LANGS[0])
            ttk.Combobox(tab, textvariable=lang_var, values=PROCESS_LANGS, state="readonly").pack(fill="x", padx=8)

            if name == "vigenere":
                key_frame = tk.Frame(tab, bg=self._theme().bg)
                key_frame.pack(fill="x", padx=8, pady=(6, 0))
                tk.Label(key_frame, text="Key:", bg=self._theme().bg, fg=self._theme().fg).pack(side="left")
                key_var = tk.StringVar(value="KEY")
                ttk.Entry(key_frame, textvariable=key_var).pack(side="left", fill="x", expand=True, padx=6)
            else:
                key_var = None

            if mode == "encrypt":
                hint = self.lang["file_hint_txt"]
            else:
                hint = self.lang["file_hint_txt"]
            tk.Label(tab, text=hint, bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w", padx=8, pady=(8, 2))

            if mode == "decrypt":
                key_frame2 = tk.Frame(tab, bg=self._theme().bg)
                key_frame2.pack(fill="x", padx=8, pady=(0, 6))
                tk.Label(key_frame2, text=self.lang["enter_key"], bg=self._theme().bg, fg=self._theme().fg).pack(side="left")
                unlock_var = tk.StringVar()
                ttk.Entry(key_frame2, textvariable=unlock_var).pack(side="left", fill="x", expand=True, padx=6)
            else:
                unlock_var = None

            drop = self._make_drop_area(tab)

            status_var = tk.StringVar(value="")
            status = tk.Label(tab, textvariable=status_var, bg=self._theme().bg, fg=self._theme().fg)
            status.pack(anchor="w", padx=8, pady=(4, 6))

            pb = ttk.Progressbar(tab, mode="determinate", maximum=100)
            pb.pack(fill="x", padx=8, pady=(4, 8))

            btn_frame = tk.Frame(tab, bg=self._theme().bg)
            btn_frame.pack(fill="x", padx=8, pady=(6, 8))
            def on_confirm():
                file_path = drop.file_path
                if not file_path or not file_path.lower().endswith(".txt"):
                    messagebox.showerror(self.lang["file_error"], self.lang["invalid_file"])
                    return
                text = read_txt(file_path)
                if count_words(text) <= 100:
                    messagebox.showerror(self.lang["file_error"], self.lang["not_enough_words"])
                    return

                if mode == "decrypt":
                    k = (unlock_var.get() if unlock_var else "").strip()
                    if not validate_key(k):
                        messagebox.showerror(self.lang["file_error"], self.lang["invalid_key"])
                        return

                # Run
                result = None
                original_text = text
                def work():
                    pb["value"] = 0
                    status_var.set(self.lang["progress_encrypt"] if mode == "encrypt" else self.lang["progress_decrypt"])
                    for i in range(25):
                        time.sleep(0.04)
                        self._safe_progress(pb, i*4)
                    # Cipher
                    nonlocal result
                    if name == "morse":
                        result = morse_encrypt(text) if mode == "encrypt" else morse_decrypt(text)
                    elif name == "caesar":
                        result = caesar_encrypt(text) if mode == "encrypt" else caesar_decrypt(text)
                    elif name == "vigenere":
                        key = key_var.get() if key_var else "KEY"
                        result = vigenere_encrypt(text, key) if mode == "encrypt" else vigenere_decrypt(text, key)
                    self._safe_progress(pb, 100)
                    status_var.set(self.lang["completed"])
                    self.after(10, lambda: self._show_result_screen(result, original_text, mode))

                threading.Thread(target=work, daemon=True).start()

            ttk.Button(btn_frame, text=self.lang["confirm"], command=on_confirm).pack(side="left")
            ttk.Button(btn_frame, text=self.lang["restart"], command=self._show_mode_screen).pack(side="left", padx=6)

        build_tab(encrypt_tab, "encrypt")
        build_tab(decrypt_tab, "decrypt")

    # AI part screen
    def _show_ai_screen(self):
        self._current_screen = "ai"
        for w in self.main_frame.winfo_children():
            w.destroy()
        f = tk.Frame(self.main_frame, bg=self._theme().bg)
        f.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Label(f, text=self.lang["ai_auto"], font=("Segoe UI", 16, "bold"), bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w")

        if not self.logged_in_user:
            tk.Label(f, text=self.lang["need_login"], bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w", pady=8)
            self._build_login_register(f)
            return

        nb = ttk.Notebook(f)
        nb.pack(fill="both", expand=True, pady=10)

        encrypt_tab = tk.Frame(nb, bg=self._theme().bg)
        decrypt_tab = tk.Frame(nb, bg=self._theme().bg)
        nb.add(encrypt_tab, text=self.lang["encrypt"])
        nb.add(decrypt_tab, text=self.lang["decrypt"])

        def build_tab(tab: tk.Frame, mode: str):
            tk.Label(tab, text=self.lang["choose_lang"], bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w", padx=8, pady=(6, 2))
            lang_var = tk.StringVar(value=PROCESS_LANGS[0])
            ttk.Combobox(tab, textvariable=lang_var, values=PROCESS_LANGS, state="readonly").pack(fill="x", padx=8)

            hint = self.lang["file_hint_txt_pdf"]
            tk.Label(tab, text=hint, bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w", padx=8, pady=(8, 2))

            if mode == "decrypt":
                key_frame2 = tk.Frame(tab, bg=self._theme().bg)
                key_frame2.pack(fill="x", padx=8, pady=(0, 6))
                tk.Label(key_frame2, text=self.lang["enter_key"], bg=self._theme().bg, fg=self._theme().fg).pack(side="left")
                unlock_var = tk.StringVar()
                ttk.Entry(key_frame2, textvariable=unlock_var).pack(side="left", fill="x", expand=True, padx=6)
            else:
                unlock_var = None

            drop = self._make_drop_area(tab, allow_pdf=True)
            status_var = tk.StringVar(value="")
            status = tk.Label(tab, textvariable=status_var, bg=self._theme().bg, fg=self._theme().fg)
            status.pack(anchor="w", padx=8, pady=(4, 6))
            pb = ttk.Progressbar(tab, mode="determinate", maximum=100)
            pb.pack(fill="x", padx=8, pady=(4, 8))

            def on_confirm():
                file_path = drop.file_path
                if not file_path or not (file_path.lower().endswith(".txt") or file_path.lower().endswith(".pdf")):
                    messagebox.showerror(self.lang["file_error"], self.lang["invalid_file_ai"])
                    return
                if file_path.lower().endswith(".txt"):
                    text = read_txt(file_path)
                else:
                    messagebox.showwarning(self.lang["help"], self.lang["pdf_parse_warn"])
                    text = extract_text_from_pdf_basic(file_path)
                    if not text:
                        messagebox.showerror(self.lang["file_error"], self.lang["invalid_file_ai"])
                        return

                if mode == "decrypt":
                    k = (unlock_var.get() if unlock_var else "").strip()
                    if not validate_key(k):
                        messagebox.showerror(self.lang["file_error"], self.lang["invalid_key"])
                        return

                original_text = text
                result = None

                def work():
                    pb["value"] = 0
                    status_var.set(self.lang["progress_encrypt"] if mode == "encrypt" else self.lang["progress_decrypt"])
                    for i in range(25):
                        time.sleep(0.04)
                        self._safe_progress(pb, i*4)
                    nonlocal result
                    if mode == "encrypt":
                        result = ai_auto_encrypt(text)
                        db_increment_uses(self.logged_in_user)
                    else:
                        result = ai_auto_decrypt(text)
                        db_increment_uses(self.logged_in_user)
                    self._safe_progress(pb, 100)
                    status_var.set(self.lang["completed"])
                    self.after(10, lambda: self._show_result_screen(result, original_text, mode, ai=True))

                threading.Thread(target=work, daemon=True).start()

            btns = tk.Frame(tab, bg=self._theme().bg)
            btns.pack(fill="x", padx=8, pady=(6, 8))
            ttk.Button(btns, text=self.lang["confirm"], command=on_confirm).pack(side="left")
            ttk.Button(btns, text=self.lang["restart"], command=self._show_mode_screen).pack(side="left", padx=6)

        build_tab(encrypt_tab, "encrypt")
        build_tab(decrypt_tab, "decrypt")

    def _build_login_register(self, parent: tk.Frame):
        frame = tk.Frame(parent, bg=self._theme().bg)
        frame.pack(fill="x", pady=8)

        # Login
        lf = ttk.LabelFrame(frame, text=self.lang["member_login"])
        lf.pack(fill="x", padx=8, pady=6)
        tk.Label(lf, text=self.lang["username"], bg=self._theme().bg, fg=self._theme().fg).grid(row=0, column=0, padx=6, pady=4, sticky="e")
        tk.Label(lf, text=self.lang["password"], bg=self._theme().bg, fg=self._theme().fg).grid(row=1, column=0, padx=6, pady=4, sticky="e")
        u_var = tk.StringVar()
        p_var = tk.StringVar()
        ttk.Entry(lf, textvariable=u_var).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        ttk.Entry(lf, textvariable=p_var, show="*").grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        lf.columnconfigure(1, weight=1)

        def do_login():
            u = u_var.get().strip()
            p = p_var.get()
            if db_login(u, p):
                self.logged_in_user = u
                messagebox.showinfo(self.lang["login"], self.lang["login_success"])
                if u == "000" and p == "abc1230":
                    self._show_db_viewer()
                self._show_ai_screen()
            else:
                messagebox.showerror(self.lang["login"], self.lang["bad_credentials"])

        ttk.Button(lf, text=self.lang["login"], command=do_login).grid(row=2, column=0, columnspan=2, pady=6)

        # Register
        rf = ttk.LabelFrame(frame, text=self.lang["member_register"])
        rf.pack(fill="x", padx=8, pady=6)
        ru_var = tk.StringVar()
        rp_var = tk.StringVar()
        rc_var = tk.StringVar()
        tk.Label(rf, text=self.lang["username"], bg=self._theme().bg, fg=self._theme().fg).grid(row=0, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(rf, textvariable=ru_var).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        tk.Label(rf, text=self.lang["password"], bg=self._theme().bg, fg=self._theme().fg).grid(row=1, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(rf, textvariable=rp_var, show="*").grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        tk.Label(rf, text=self.lang["confirm_password"], bg=self._theme().bg, fg=self._theme().fg).grid(row=2, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(rf, textvariable=rc_var, show="*").grid(row=2, column=1, padx=6, pady=4, sticky="ew")
        rf.columnconfigure(1, weight=1)

        def strong_password(pw: str) -> bool:
            return (
                len(pw) >= 12
                and re.search(r'[a-z]', pw)
                and re.search(r'[A-Z]', pw)
                and re.search(r'\d', pw)
                and re.search(r'[^A-Za-z0-9]', pw)
            )

        def do_register():
            u = ru_var.get().strip()
            p = rp_var.get()
            c = rc_var.get()
            if db_user_exists(u):
                messagebox.showerror(self.lang["register"], self.lang["user_exists"])
                return
            if p != c:
                messagebox.showerror(self.lang["register"], self.lang["password_mismatch"])
                return
            if not strong_password(p):
                messagebox.showerror(self.lang["register"], self.lang["weak_password"])
                return
            if db_register(u, p):
                messagebox.showinfo(self.lang["register"], self.lang["register_success"])
            else:
                messagebox.showerror(self.lang["register"], self.lang["user_exists"])

    # Result view
    def _show_result_screen(self, result_text: str, original_text: str, mode: str, ai: bool=False):
        for w in self.main_frame.winfo_children():
            w.destroy()
        f = tk.Frame(self.main_frame, bg=self._theme().bg)
        f.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(f, text=self.lang["result"], font=("Segoe UI", 16, "bold"),
                 bg=self._theme().bg, fg=self._theme().fg).pack(anchor="w")
        txt = scrolledtext.ScrolledText(f, wrap="word")
        txt.pack(fill="both", expand=True, pady=8)
        txt.insert("1.0", result_text)
        txt.configure(state="disabled")

        btns = tk.Frame(f, bg=self._theme().bg)
        btns.pack(fill="x")
        ttk.Button(btns, text=self.lang["download"], command=lambda: save_text_dialog("result.txt", result_text, self.lang)).pack(side="left")
        ttk.Button(btns, text=self.lang["restart"], command=self._show_mode_screen).pack(side="left", padx=6)

        def on_exit():
            if mode == "encrypt":
                k = generate_key()
                SESSION_KEYS[k] = original_text
                messagebox.showinfo(self.lang["completed"], f"{self.lang['exit_key_msg']} {k}")
            self.destroy()

        ttk.Button(btns, text=self.lang["exit"], command=on_exit).pack(side="right")

    # Drop widget
    class DropArea(tk.Frame):
        def __init__(self, master, app, allow_pdf=False):
            super().__init__(master, bg=app._theme().panel, highlightthickness=2, highlightbackground=app._theme().dashed_border)
            self.app = app
            self.allow_pdf = allow_pdf
            self.file_path: Optional[str] = None
            self.configure(cursor="hand2")
            self.pack(fill="x", padx=8, pady=8, ipady=24)
            self.label = tk.Label(self, text=app.lang["drag_here"], bg=app._theme().panel, fg=app._theme().fg)
            self.label.pack(pady=6)
            self.sel = tk.Label(self, text="", bg=app._theme().panel, fg=app._theme().fg)
            self.sel.pack(pady=2)
            self.bind("<Button-1>", self._browse)
            self.label.bind("<Button-1>", self._browse)
            self.sel.bind("<Button-1>", self._browse)

        def _browse(self, _e=None):
            if self.allow_pdf:
                file = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("PDF", "*.pdf")])
            else:
                file = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
            if file:
                self.file_path = file
                self.sel.config(text=f"{self.app.lang['file_selected']} {os.path.basename(file)}")

    def _make_drop_area(self, parent, allow_pdf=False):
        return self.DropArea(parent, self, allow_pdf=allow_pdf)

    def _safe_progress(self, pb: ttk.Progressbar, value: int):
        try:
            pb["value"] = value
        except:
            pass


    def _enable_drop(self, widget):
        pass


def main():
    init_db()
    app = CipherLabApp()
    app.mainloop()

if __name__ == "__main__":
    main()
