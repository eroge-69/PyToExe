 	
# gemini_terminal_flash_fullcolor.py

import os
import re
import sys
import subprocess
import google.generativeai as genai
from colorama import init, Fore, Style

print("Google Gemini and Edison Rees [Version 10.0.26220.5790]")
print("(c) Edison Rees. All rights reserved.")

# ==============================
# CONFIGURATION
# ==============================
GEMINI_API_KEY = "AIzaSyCwN8tpXysg4sHGs-ziHUr75VTaWX19q7U"
MODEL = "gemini-2.5-flash"  # fast flash model

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    sys.exit(1)

# Initialize colorama
init(autoreset=True)

# Regex patterns
LOCAL_CMD_PATTERN = re.compile(r"\*\*__(.*?)__\*\*", re.DOTALL)
CWD_PATTERN = re.compile(r"<cwd>(.*?)</cwd>", re.DOTALL)
CODE_BLOCK_PATTERN = re.compile(r"```(.*?)```", re.DOTALL)

# ==============================
# SYSTEM PROMPT
# ==============================
SYSTEM_PROMPT = """
You are an advanced terminal simulation engine. Only reply with terminal output inside one unique code block. 
Do not provide explanations unless instructed. Maintain session state including the current working directory.
How to explain: Explain in the format {Command run} was incorrect because in {terminal type} {Command run} is {reason incorrect}. To fix this, you can run {fixed command} to {what this does} instead of {what incorrect command run}. Use backtick formatting of the terminal type you are in. After you finish your explanation, resume character as terminal.
Under NO CIRCUMSTANCES OTHER THAN EXPLANATIONS ARE YOU TO BREAK CHARACTER
If no terminal type is provided, default to the most widely used terminal in which the users latest command was valid. for example if i do not specify a terminal but i type Get-Process notepad, you default to powershell, otherwise, follow up at your next chance.
"""

# ==============================
# HELPER FUNCTIONS
# ==============================
def run_local_command(command: str, cwd: str) -> str:
    """Run commands locally for accuracy."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            output += ("\n" + result.stderr.strip())
        return output or "[No output returned]"
    except Exception as e:
        return f"Error executing command: {e}"

def strip_metadata(text: str) -> str:
    """Remove metadata like CWD or local execution markers."""
    text = LOCAL_CMD_PATTERN.sub("", text)
    text = CWD_PATTERN.sub("", text)
    return text.strip()

def colorize_terminal(text: str) -> str:
    """
    Fully colorize terminal output:
    - Commands → cyan
    - Errors → red
    - Disabled commands/topics (*) → bright red
    - Paths or directories → green
    - Prompt (`unix>` / `PS>` etc.) → bright cyan
    """
    def replacer(match):
        code_content = match.group(1)
        lines = code_content.splitlines()
        colored_lines = []
        for line in lines:
            # Highlight errors
            if "not recognized" in line or "Error" in line:
                colored_lines.append(Fore.RED + line + Style.RESET_ALL)
            # Highlight disabled topics
            elif "*" in line:
                colored_lines.append(Fore.LIGHTRED_EX + line + Style.RESET_ALL)
            # Highlight directories / paths
            elif os.path.exists(line.strip()):
                colored_lines.append(Fore.GREEN + line + Style.RESET_ALL)
            # Highlight commands
            elif any(cmd in line for cmd in ["cd", "ls", "dir", "mkdir", "rm", "echo", "help", "exit", "clear"]):
                colored_lines.append(Fore.CYAN + line + Style.RESET_ALL)
            else:
                colored_lines.append(line)
        return "\n".join(colored_lines)

    text = CODE_BLOCK_PATTERN.sub(replacer, text)
    # Highlight prompt itself
    text = re.sub(r"^(\w+>)", Fore.CYAN + r"\1" + Style.RESET_ALL, text, flags=re.MULTILINE)
    return text

# ==============================
# MAIN TERMINAL LOOP
# ==============================
def main():
    print(Fore.YELLOW + "=== GemiTerm ===" + Style.RESET_ALL)
    term_type = input("Enter terminal type (linux/windows/unix/bash): ").strip()
    
    model = genai.GenerativeModel(MODEL)
    chat = model.start_chat()
    chat.send_message(f"I want you to act as a {term_type} terminal. {SYSTEM_PROMPT}")

    cwd = os.path.expanduser("~")
    
    while True:
        try:
            cmd = input(Fore.CYAN + f"{term_type}> " + Style.RESET_ALL).strip()
            if not cmd:
                continue
            if cmd.lower() in ["exitgemiterm", "exitgemterm"]:
                subprocess.run("exit", shell=True)
                break

            # Special command: &cls& clears the screen
            if cmd.lower() == "&cls&":
                subprocess.run("cls", shell=True)
                continue
   # Special command: &cls& clears the screen
            if cmd.lower() == "wrongterminalsorry!":
                subprocess.run("cls", shell=True)
                main()
# Special command: &cls& clears the screen
            if cmd.lower() == "showmecopyrightdetailspleaseandthankyouhowlongdoesthisgo":
                subprocess.run("msg * Made by Edison Rees. Uses Google Gemini API. Please dont steal it. I love you! Designed by a single man crew on a boring sunday. Made using python and Google Gemini 2.5 Flash (c)", shell=True)
                continue

            response = chat.send_message(cmd)
            output = response.text

            # Handle local execution
            local_matches = LOCAL_CMD_PATTERN.findall(output)
            if local_matches:
                feedback = []
                for local_cmd in local_matches:
                    local_out = run_local_command(local_cmd, cwd)
                    feedback.append(f"***{local_cmd}*** ___{local_out}___")
                feedback_text = "\n".join(feedback)
                output = chat.send_message(feedback_text).text

            # Update CWD if reported
            cwd_match = CWD_PATTERN.search(output)
            if cwd_match and os.path.isdir(cwd_match.group(1).strip()):
                cwd = cwd_match.group(1).strip()

            cleaned = strip_metadata(output)
            print(colorize_terminal(cleaned))

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"CRITICAL ERROR: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
