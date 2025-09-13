import os
import socket
import base64
import logging
from flask import Flask, request, jsonify
from zipfile import ZipFile
from io import BytesIO

app = Flask(__name__)

# --- Directories setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # reliable even in exe
home_dir = os.path.expanduser("~")
documents_dir = os.path.join(home_dir, "Documents")

SCRIPTS_PATH = os.path.join(documents_dir, "scripts")              # where scripts get extracted
SCRIPTS_EXECUTION = os.path.join(home_dir, ".myapp_scriptsExec")   # execution shortcuts (.bat)
CACHE_DIR = os.path.join(BASE_DIR, "cache")                        # cache near exe

for d in (SCRIPTS_PATH, SCRIPTS_EXECUTION, CACHE_DIR):
    os.makedirs(d, exist_ok=True)

framework = "Flask"

# --- Logging ---
log_file = os.path.join(BASE_DIR, "server.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Helpers ---
def safe_name(name: str) -> str:
    """Sanitize script name to avoid path traversal / invalid chars."""
    if not name:
        return "unnamed_script"
    name = os.path.basename(name)
    return "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_", " ")).strip() or "unnamed_script"

def get_hostname_from_file(filename=os.path.join(BASE_DIR, "hostname-config.txt")):
    """Read/write persistent hostname safely."""
    try:
        if not os.path.exists(filename):
            desktop_name = socket.gethostname()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(desktop_name + "\n")
            return desktop_name
        with open(filename, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if not first_line:
                desktop_name = socket.gethostname()
                with open(filename, "w", encoding="utf-8") as f2:
                    f2.write(desktop_name + "\n")
                return desktop_name
            return first_line
    except Exception:
        logging.exception("Failed to handle hostname-config.txt; falling back to socket hostname.")
        return socket.gethostname()

hostname = get_hostname_from_file()

def secure_extractall(zf: ZipFile, path: str):
    """Prevent Zip Slip vulnerability."""
    for member in zf.infolist():
        member_path = os.path.normpath(os.path.join(path, member.filename))
        if not member_path.startswith(os.path.abspath(path)):
            raise Exception("Unsafe zip entry detected!")
    zf.extractall(path)

# --- Routes ---
@app.route("/ping", methods=["GET"])
def ping():
    try:
        return jsonify({"ping": True, "hostname": hostname, "framework": framework})
    except Exception as e:
        logging.exception("Ping route error")
        return jsonify({"ping": False, "error": str(e)}), 500

@app.route("/receive-script", methods=["POST"])
def receive_script():
    """
    Expected JSON payload:
    {
      "script-name": <string>,
      "script-path": <relative path to executable within script folder>,
      "script": <base64 string of zip bytes>
    }
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"ok": False, "error": "No JSON payload"}), 400

        sname = data.get("script-name")
        spath = data.get("script-path")
        sbase64 = data.get("script")

        if not all([sname, spath, sbase64]):
            return jsonify({"ok": False, "error": "Missing script-name, script-path, or script"}), 400

        safe_script_name = safe_name(sname)
        logging.info(f"Receiving script '{safe_script_name}', script-path '{spath}'")

        # Decode base64
        try:
            zip_bytes = base64.b64decode(sbase64)
        except Exception:
            logging.exception("Failed to decode base64 zip")
            return jsonify({"ok": False, "error": "Failed to decode script bytes"}), 400

        # Save zip in cache
        cache_zip_path = os.path.join(CACHE_DIR, f"{safe_script_name}.zip")
        with open(cache_zip_path, "wb") as f:
            f.write(zip_bytes)
        logging.info(f"Saved zip to {cache_zip_path}")

        # Extract zip
        target_dir = os.path.join(SCRIPTS_PATH, safe_script_name)
        os.makedirs(target_dir, exist_ok=True)
        try:
            with ZipFile(BytesIO(zip_bytes)) as zf:
                secure_extractall(zf, target_dir)
        except Exception:
            try:
                with ZipFile(cache_zip_path) as zf:
                    secure_extractall(zf, target_dir)
            except Exception:
                logging.exception("Failed to unzip uploaded script")
                return jsonify({"ok": False, "error": "Failed to unzip uploaded script"}), 500

        logging.info(f"Extracted script to {target_dir}")

        # Validate script-path
        spath_norm = spath.replace("/", os.sep).replace("\\", os.sep)
        kbx_candidate = os.path.normpath(os.path.join(target_dir, spath_norm))
        if not kbx_candidate.startswith(os.path.abspath(target_dir)):
            logging.warning("script-path leads outside target dir; rejecting for safety")
            return jsonify({"ok": False, "error": "script-path invalid or unsafe"}), 400

        # Create .bat file
        bat_name = f"{safe_script_name}.bat"
        bat_path = os.path.join(SCRIPTS_EXECUTION, bat_name)
        kbx_full = os.path.abspath(kbx_candidate)
        bat_contents = f'start "" "{kbx_full}" %*\n'
        try:
            with open(bat_path, "w", encoding="utf-8") as batf:
                batf.write(bat_contents)
        except Exception:
            logging.exception("Failed to write .bat file")
            return jsonify({"ok": False, "error": "Failed to write .bat file"}), 500

        logging.info(f"Created execution .bat at {bat_path} -> starts {kbx_full}")

        return jsonify({
            "ok": True,
            "script_name": safe_script_name,
            "extracted_to": target_dir,
            "bat": bat_path
        }), 201

    except Exception as e:
        logging.exception("Unhandled error in /receive-script")
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Run ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
