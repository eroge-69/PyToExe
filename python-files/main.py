from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Received webhook: {data}")

    # Run a command (example: list directory contents)
    command = ["ls", "-l"]  # Replace with your actual command
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Command output:\n", result.stdout)
        return "Command executed successfully."
    except subprocess.CalledProcessError as e:
        print("Command failed:\n", e.stderr)
        return "Command execution failed.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1967)
