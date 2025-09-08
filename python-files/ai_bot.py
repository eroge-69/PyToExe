import subprocess
import requests
import pyperclip
import sys
import time
import ollama 

# -------------------------
# Available models
# -------------------------
MODELS = ["llama3.1", "llama3", "mistral:7b", "qwen2.5", "codellama:7b"]

def select_model():
    print("\nAvailable Models:")
    for i, model in enumerate(MODELS, 1):
        print(f"{i}. {model}")
    choice = input("\nSelect a model (1-{}): ".format(len(MODELS)))
    try:
        return MODELS[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Defaulting to llama3.1")
        return "llama3.1"

def ollama_chat(model, message):
    """Send a message to Ollama and return streaming response."""
    process = subprocess.Popen(
        ["ollama", "run", model],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    response = ""
    try:
        # Send message
        process.stdin.write(message + "\n")
        process.stdin.close()

        # Stream output like typing
        for line in iter(process.stdout.readline, ""):
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.01)  # typing effect
            response += line
        process.stdout.close()
        process.wait()
    except KeyboardInterrupt:
        process.kill()
    return response

def web_search(query):
    """Basic web search using Wikipedia/Reddit/other APIs."""
    print(f"\n[Searching the web for: {query}]...\n")
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("extract", "No summary found.")
        else:
            return "No results found on Wikipedia."
    except Exception as e:
        return f"Error during search: {e}"

def main():
    model = select_model()
    print(f"\n[You are now chatting with {model}]")
    print("Type 'exit' to quit.\n")

    last_response = ""

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        elif user_input.lower() == "copy":
            if last_response.strip():
                pyperclip.copy(last_response.strip())
                print("[Response copied to clipboard!]")
            else:
                print("[Nothing to copy yet.]")

        elif user_input.lower().startswith("search:"):
            query = user_input.split("search:", 1)[1].strip()
            result = web_search(query)
            print("\nSearch Result:\n", result)
            last_response = result

        else:
            print(f"\n{model}: ", end="", flush=True)
            last_response = ollama_chat(model, user_input)

if __name__ == "__main__":
    main()
