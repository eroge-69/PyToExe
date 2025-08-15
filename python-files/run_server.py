import uvicorn
import webbrowser
import os
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

def run_migrations():
    # Make sure alembic.ini is available at runtime (PyInstaller datas include it)
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    # Load env (fallback to SQLite if .env missing)
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write("DATABASE_URL=sqlite:///./mfi.db\n")
    load_dotenv(".env")

    # Run DB migrations before starting
    run_migrations()

    # Open Swagger in default browser
    try:
        webbrowser.open("http://127.0.0.1:8000/docs")
    except Exception:
        pass

    # Start API
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
