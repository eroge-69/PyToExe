# snip.py
import os, subprocess, sys

def try_ms_screenclip():
    # Windows 11/10 の多くで使えるURIスキーム
    try:
        os.startfile("ms-screenclip:")  # 即、範囲選択オーバーレイへ
        return True
    except OSError:
        # 一部環境で startfile が失敗する場合は explorer 経由
        try:
            subprocess.run(["explorer.exe", "ms-screenclip:"], check=True)
            return True
        except Exception:
            return False

def try_snippingtool_clip():
    # 旧来のコマンドライン。Win10/11の多くで有効
    for cmd in ("snippingtool.exe", "SnippingTool.exe"):
        try:
            subprocess.run([cmd, "/clip"], check=True)
            return True
        except Exception:
            continue
    return False

if __name__ == "__main__":
    if not (try_ms_screenclip() or try_snippingtool_clip()):
        # 失敗時メッセージ（任意・消してもOK）
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            None,
            "スクリーンショットの起動に失敗しました。\nSnipping Toolがインストール済みかご確認ください。",
            "Snip Launcher",
            0x00000040  # MB_ICONINFORMATION
        )
        sys.exit(1)
