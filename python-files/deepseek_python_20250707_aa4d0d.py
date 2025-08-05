import subprocess

def run_paping(ip, port):
    try:
        # Construct the command
        command = f"paping.exe {ip} -p {port}"
        
        # Run the command and capture output
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        
        # Print the output
        print("Command Output:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running paping:")
        print(e.stderr)
    except FileNotFoundError:
        print("Error: paping.exe not found. Make sure it's in your PATH or current directory.")

# Example usage
if __name__ == "__main__":
    ip_address = "1.1.1.1"
    port_number = 80
    run_paping(ip_address, port_number)