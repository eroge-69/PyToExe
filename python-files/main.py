from flask import Flask, render_template, abort
import os, json

app = Flask(__name__)
LOGS_DIR = "logs/user_files"

# Главная страница — таблица всех бэкапов
@app.route("/")
def index():
    backups = []

    if not os.path.exists(LOGS_DIR):
        return f"Папка {LOGS_DIR} не найдена"

    for filename in os.listdir(LOGS_DIR):
        if filename.endswith(".json"):
            full_path = os.path.join(LOGS_DIR, filename)
            try:
                with open(full_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                backups.append({
                    "filename": filename,
                    "snapshot": data.get("Snapshot"),
                    "date": data.get("Start", {}).get("DateTime"),
                    "files_copied": data.get("FilesCopied"),
                    "files_linked": data.get("FilesLinked"),
                })
            except Exception as e:
                backups.append({
                    "filename": filename,
                    "snapshot": "Ошибка",
                    "date": "Ошибка",
                    "files_copied": 0,
                    "files_linked": 0
                })

    # Сортируем по дате, если нужно можно по файлу
    backups.sort(key=lambda x: x["date"], reverse=True)
    return render_template("index.html", backups=backups)

# Детальная страница конкретного бэкапа
@app.route("/backup/<filename>")
def backup_detail(filename):
    full_path = os.path.join(LOGS_DIR, filename)
    if not os.path.exists(full_path):
        abort(404)

    try:
        with open(full_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        return f"Ошибка чтения файла: {e}"

    return render_template("backup_detail.html", log=data, filename=filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
