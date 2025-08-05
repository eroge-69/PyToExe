import subprocess
import re
import signal
import os
import sys
from colorama import Fore, Style, init
from typing import List, Optional, Tuple

init(autoreset=True)  # Auto-reset colors after each print

# Color configuration class
class ColorConfig:
    IP = Fore.GREEN
    LABEL = Fore.MAGENTA
    ERROR = Fore.RED
    VALUE = Fore.GREEN

# Compiled regex patterns for better performance
IP_PATTERN = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
TIME_PATTERN = re.compile(r'^\d+\.\d+ms$')
VALIDATION_PATTERN = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

# Configuration constants
DEFAULT_IP = "1.1.1.1"
DEFAULT_PORT = "80"
PAPIN_EXECUTABLE = r'C:\Users\q70\paping.exe'
PROCESS_TIMEOUT = 2

# Set window title
sys.stdout.write(f"\033]0;Python Tool 1rrk > q70\007")
sys.stdout.flush()

def validate_ip(ip: str) -> bool:
    """Validate IP address format and range.
    
    Args:
        ip: IP address string to validate
        
    Returns:
        bool: True if valid IP address, False otherwise
    """
    if not VALIDATION_PATTERN.match(ip):
        return False
    # Check each octet is between 0 and 255
    octets = ip.split('.')
    try:
        for octet in octets:
            if not 0 <= int(octet) <= 255:
                return False
    except ValueError:
        return False
    return True

def format_word(word: str) -> str:
    """Format a single word with appropriate colors based on its content.
    
    Args:
        word: The word to format
        
    Returns:
        str: Formatted word with color codes
    """
    # Check if the word is exactly '80'
    if word == '80':
        return f"{ColorConfig.VALUE}80{Style.RESET_ALL}"
    # Check if the word is exactly 'TCP'
    elif word == 'TCP':
        return f"{ColorConfig.VALUE}TCP{Style.RESET_ALL}"
    # Check if the word matches a time value pattern (e.g., 5.76ms)
    elif TIME_PATTERN.match(word):
        return f"{ColorConfig.VALUE}{word}{Style.RESET_ALL}"
    # Check if the word is an IP address
    elif IP_PATTERN.match(word):
        return f"{ColorConfig.IP}{word}{Style.RESET_ALL}"
    # Check if the word is a colon
    elif word == ':':
        return f"{ColorConfig.LABEL}:{Style.RESET_ALL}"
    # Check if the word is 'Connected' or 'Connecting'
    elif word in ['Connected', 'Connecting']:
        return f"{ColorConfig.LABEL}{word}{Style.RESET_ALL}"
    # Check if the word is 'to' or 'on'
    elif word in ['to', 'on']:
        return f"{ColorConfig.LABEL}{word}{Style.RESET_ALL}"
    # Check for time=X.XXms pattern
    elif word.startswith('time='):
        parts = word.split('=')
        if len(parts) > 1 and TIME_PATTERN.match(parts[1]):
            return f"{ColorConfig.LABEL}time={ColorConfig.VALUE}{parts[1]}{Style.RESET_ALL}"
        else:
            return word
    # Check for protocol=TCP pattern
    elif word.startswith('protocol='):
        parts = word.split('=')
        if len(parts) > 1 and parts[1] == 'TCP':
            return f"{ColorConfig.LABEL}protocol={ColorConfig.VALUE}TCP{Style.RESET_ALL}"
        else:
            return word
    # Check for port=80 pattern
    elif word.startswith('port='):
        parts = word.split('=')
        if len(parts) > 1 and parts[1] == '80':
            return f"{ColorConfig.LABEL}port={ColorConfig.VALUE}80{Style.RESET_ALL}"
        else:
            return word
    else:
        return word

def format_output_line(line: str) -> str:
    """Format an entire output line with appropriate colors.
    
    Args:
        line: The line to format
        
    Returns:
        str: Formatted line with color codes
    """
    words = line.strip().split()
    formatted_words = [format_word(word) for word in words]
    return ' '.join(formatted_words)

def run_paping(ip: str, port: str) -> None:
    """Run paping command and display formatted output.
    
    Args:
        ip: IP address to scan
        port: Port number to scan
    """
    # Check if paping.exe exists
    if not os.path.exists(PAPIN_EXECUTABLE):
        print(f"{ColorConfig.ERROR}Error: paping.exe not found at {PAPIN_EXECUTABLE}{Style.RESET_ALL}")
        return
        
    command = fr'{PAPIN_EXECUTABLE} {ip} -p {port}'
    
    print(f"Scanning {ColorConfig.IP}{ip}{Style.RESET_ALL}:{port}\n")
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            bufsize=1,
            universal_newlines=True
        )
        
        try:
            for line in process.stdout:
                # Format and print the line using the extracted formatting function
                formatted_line = format_output_line(line)
                print(formatted_line)
        except KeyboardInterrupt:
            print("\nScan interrupted by user.")
            # Try to terminate the process gracefully
            process.terminate()
            try:
                process.wait(timeout=PROCESS_TIMEOUT)
            except subprocess.TimeoutExpired:
                process.kill()
        finally:
            # Make sure we clean up the process
            if process.poll() is None:
                process.terminate()

    except FileNotFoundError:
        print(f"{ColorConfig.ERROR}Error: paping.exe not found at {PAPIN_EXECUTABLE}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{ColorConfig.ERROR}Failed to run command: {e}{Style.RESET_ALL}")

def get_user_input() -> Tuple[str, str]:
    """Get and validate user input for IP address and port.
    
    Returns:
        tuple: (ip_address, port) as strings
    """
    # Get IP address input
    ip_input = input(f"IP > ").strip()
    if not ip_input:
        ip_input = DEFAULT_IP
    elif not validate_ip(ip_input):
        print(f"{ColorConfig.ERROR}Invalid IP address format. Using default {DEFAULT_IP}{Style.RESET_ALL}")
        ip_input = DEFAULT_IP
        
    # Get port input
    port_input = input(f"port >").strip()
    if not port_input:
        port_input = DEFAULT_PORT
    elif not port_input.isdigit() or not 1 <= int(port_input) <= 65535:
        print(f"{ColorConfig.ERROR}Invalid port number. Using default {DEFAULT_PORT}{Style.RESET_ALL}")
        port_input = DEFAULT_PORT
        
    return ip_input, port_input

def main() -> None:
    """Main function to run the paping scanner."""
    try:
        ip_address, port = get_user_input()
        run_paping(ip_address, port)
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"{ColorConfig.ERROR}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
