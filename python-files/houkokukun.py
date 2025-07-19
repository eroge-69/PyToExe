# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# --- 設定項目 ---

# プルダウンに表示する社員名のリスト
EMPLOYEE_LIST = [
    "田中 太郎",
    "鈴木 一郎",
    "佐藤 花子",
    "高橋 次郎",
    "渡辺 三郎"
]

# --- メール設定 ---
# ご利用のメールサービスに合わせて設定してください
# 例: Gmailの場合
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
#
# 例: Outlook/Office365の場合
# SMTP_SERVER = "smtp.office365.com"
# SMTP_PORT = 587

SMTP_SERVER = "smtp.gmail.com"  # ★★★ 送信に使うメールサーバーのアドレス
SMTP_PORT = 587                       # ★★★ メールサーバーのポート番号
SENDER_EMAIL = "tatsuya-yamamoto@tsp.co.jp" # ★★★ 送信元のメールアドレス
SENDER_PASSWORD = "nkco krnu jdpe wvqz"   # ★★★ 送信元メールのパスワード（※Gmailなどは「アプリパスワード」を推奨）

# ★★★ 送信先の管理者メールアドレス（複数指定可）
# 以下のようにカンマ区切りで複数人のメールアドレスを追加できます
ADMIN_EMAIL_LIST = [
    "zyakki2010@gmail.com",
    "admin2@example.com",
]

# --- アプリケーションの作成 ---

def send_email():
    """
    入力された内容をメールで送信する関数
    """
    # フォームから入力内容を取得
    sender_name = name_combobox.get()
    report_content = content_text.get("1.0", tk.END).strip()

    # 入力チェック
    if not sender_name:
        messagebox.showwarning("入力エラー", "報告者を選択してください。")
        return
    if not report_content:
        messagebox.showwarning("入力エラー", "トラブル内容を入力してください。")
        return

    # メールの件名と本文を作成
    subject = f"【トラブル報告】{sender_name}さんからの報告"
    body = f"""
    管理者様

    以下の内容でトラブル報告がありました。

    --------------------------------
    報告者: {sender_name}
    --------------------------------
    内容:
    {report_content}
    --------------------------------
    """

    # メールを送信
    try:
        # メールオブジェクトを作成
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SENDER_EMAIL
        # 複数の宛先をカンマ区切りで設定
        msg['To'] = ", ".join(ADMIN_EMAIL_LIST)

        # サーバーに接続してメールを送信
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLSで暗号化
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        messagebox.showinfo("送信完了", "トラブル報告を送信しました。")
        # 送信後に内容をクリア
        content_text.delete("1.0", tk.END)
        name_combobox.set("")

    except Exception as e:
        # エラーが発生した場合
        error_message = f"メールの送信に失敗しました。\n\nエラー内容:\n{e}\n\n設定を確認してください。"
        messagebox.showerror("送信エラー", error_message)


# --- GUIの作成 ---

# メインウィンドウ
root = tk.Tk()
root.title("トラブル報告フォーム")
root.geometry("450x400") # ウィンドウサイズ

# メインフレーム
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 報告者ラベルとプルダウンメニュー
name_label = ttk.Label(main_frame, text="報告者名:")
name_label.pack(fill=tk.X, pady=(0, 5))

name_combobox = ttk.Combobox(main_frame, values=EMPLOYEE_LIST, state="readonly")
name_combobox.pack(fill=tk.X, pady=(0, 15))

# トラブル内容ラベルとテキストボックス
content_label = ttk.Label(main_frame, text="トラブル内容:")
content_label.pack(fill=tk.X, pady=(0, 5))

content_text = tk.Text(main_frame, height=10)
content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

# 送信ボタン
send_button = ttk.Button(main_frame, text="送信", command=send_email)
send_button.pack(fill=tk.X)


# ウィンドウの表示
root.mainloop()
```

### 主な変更点

* `ADMIN_EMAIL` という変数を `ADMIN_EMAIL_LIST` というリスト（複数の値を入れられる箱）に変更しました。
* このリストに、報告メールを送りたい担当者のメールアドレスを必要なだけ追加できるようになっています。
* メール送信時に、このリストにあるすべてのアドレス宛にメールが送信されるように処理を修正しま