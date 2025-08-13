import os
import paramiko
from getpass import getpass
from stat import S_ISDIR

import subprocess
import time

def is_device_online(ip_address, timeout=30):
    """
    Check if a device with the given IP address is online by pinging it.
    Waits up to 'timeout' seconds for the device to respond.
    Returns True if the device responds, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Use ping command (1 packet, 1 second timeout)
            # For Windows: ['ping', '-n', '1', '-w', '1000', ip_address]
            # For Linux/Mac: ['ping', '-c', '1', '-W', '1', ip_address]
            subprocess.check_output(
                ['ping', '-n', '1', '-w', '1000', ip_address],
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            return True
        except subprocess.CalledProcessError:
            time.sleep(1)  # Wait 1 second before trying again
    return False


def sftp_transfer(host, port, username, password, local_path, remote_path):
    """
    Transfer files from local Windows machine to remote Debian via SFTP
    
    Args:
        host (str): Remote hostname or IP address
        port (int): SSH port (usually 22)
        username (str): SSH username
        password (str): SSH password
        local_path (str): Local Windows directory path
        remote_path (str): Remote directory path
    """
    
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}:{port}...")
        ssh.connect(host, port=port, username=username, password=password)
        
        # Create SFTP client
        sftp = ssh.open_sftp()
        
        print(f"Connected successfully. Starting file transfer...")
        
        # Ensure remote path exists
        try:
            sftp.stat(remote_path)
        except IOError:
            print(f"Remote path {remote_path} doesn't exist, creating...")
            sftp.mkdir(remote_path)
        
        # Walk through local directory
        for root, dirs, files in os.walk(local_path):
            # Create corresponding remote directories
            relative_path = os.path.relpath(root, local_path)
            current_remote_path = os.path.join(remote_path, relative_path).replace('\\', '/')
            
            try:
                sftp.stat(current_remote_path)
            except IOError:
                print(f"Creating remote directory: {current_remote_path}")
                sftp.mkdir(current_remote_path)
            
            # Transfer files
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(current_remote_path, file).replace('\\', '/')
                
                # Step 1: Get the original modification time (mtime)
                file_stat = os.stat(local_file)
                original_mtime = file_stat.st_mtime

                # Step 2: Upload the file
                print(f"Transferring {local_file} to {remote_file}")
                sftp.put(local_file, remote_file)

                # Step 3: Set the remote file's modification time
                sftp.utime(remote_file, (original_mtime, original_mtime))
        print("File transfer completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Close connections
        if 'sftp' in locals():
            sftp.close()
        if 'ssh' in locals():
            ssh.close()
        print("Disconnected from remote server.")


def change_remote_permissions(hostname, username, password, remote_file_path):
    """
    Change permissions of a file on a remote Debian system to make it executable (+x)
    
    Args:
        hostname (str): Remote server hostname or IP address
        username (str): SSH username
        password (str): SSH password
        remote_file_path (str): Path to the file on the remote system
    """
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the remote server
        print(f"Connecting to {hostname}...")
        ssh.connect(hostname, username=username, password=password)
        
        # Execute the chmod command
        command = f"chmod +x {remote_file_path}"
        print(f"Executing: {command}")
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Check for errors
        error_output = stderr.read().decode()
        if error_output:
            print(f"Error: {error_output}")
        else:
            print(f"Successfully changed permissions for {remote_file_path}")
            
        # Verify the new permissions
        verify_command = f"ls -la {remote_file_path}"
        stdin, stdout, stderr = ssh.exec_command(verify_command)
        print("Current permissions:")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the connection
        if ssh:
            ssh.close()
            print("Connection closed.")

def execute_remote_command(hostname, username, password, command):
    # Create an SSH client
    client = paramiko.SSHClient()
    
    # Automatically add the server's host key (this is insecure in production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote server
        client.connect(hostname, username=username, password=password)
        
        # Execute the command with sudo
        stdin, stdout, stderr = client.exec_command(f'sudo -S {command}', get_pty=True)
        
        # Send the password when prompted (for sudo)
        stdin.write(password + '\n')
        stdin.flush()
        
        # Read the output and error
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if output:
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")
            
        return output, error
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, str(e)
    finally:
        # Close the connection
        client.close()


if __name__ == "__main__":
    # Get connection details from user
    host = "169.254.197.30"  #input("Enter remote hostname or IP: ")
    port = 22 #int(input("Enter SSH port (default 22): ") or 22)
    username = "pi" #input("Enter SSH username: ")
    password = "pip" #getpass("Enter SSH password: ")
       
    if is_device_online(host):
        print(f"Device at {host} is online!")
    else:
        print(f"No SilverBox connection at {host} after 30 seconds.")
        exit()
    
    #stop all service
    remote_command = "sudo systemctl stop unicon.hrvsdn.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl stop unicon.istart.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl stop unicon.web.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl stop unicon.core.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl stop scichart.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    #clear unicon_core file flrom remote dir
    remote_path = "/home/pi/projects/unicon_core" 
    remote_command = "sudo rm -f /home/pi/projects/unicon_core/unicon_core"
    print(f"executing remote command {remote_command} on remote server...")  
    execute_remote_command(host, username, password, remote_command)
    # Get paths
    local_path = "C:\\debian\\RST_RELEASE\\rev5\\projects" #input("Enter local Windows directory path: ")
    remote_path = "\home\pi\projects" #"input("Enter remote directory path: ")    
    # Start transfer
    sftp_transfer(host, port, username, password, local_path, remote_path)

    #Copy services from service to /etc/systemd/system
    remote_source =     "projects/system_auto/*"
    remote_destination = "../../etc/systemd/system"     
    #remote_cmd = f"ls"
    remote_cmd = f"sudo cp -R -f {remote_source} {remote_destination}"  
    execute_remote_command(host, username, password, remote_cmd)


    

    # Change file ermissions

    remote_file = "/home/pi/projects/DDE_iStartUSB/bin/ARM64/Debug/DDE_iStartUSB.out"  
    print(f"Changing permissions for {remote_file} on remote server...")
    # Call the function
    change_remote_permissions(host, username, password, remote_file)

    remote_file = "/home/pi/projects/USB_FT240x_test/bin/ARM64/Debug/USB_FT240x_test.out"  
    print(f"Changing permissions for {remote_file} on remote server...")
    # Call the function
    change_remote_permissions(host, username, password, remote_file)

    remote_file = "/home/pi/projects/unicon_core/unicon_core/unicon_core"
    print(f"Changing permissions for {remote_file} on remote server...")
    # Call the function
    change_remote_permissions(host, username, password, remote_file)




    #enabling service
    remote_command = "sudo systemctl enable unicon.hrvsdn.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    #remove unicon.istart.service from autostart    
    remote_command = "sudo systemctl disable unicon.istart.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    #remote_command = "sudo systemctl enable unicon.istart.service"
    #print(f"executing remote command {remote_command} on remote server...")            
    #execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl enable unicon.web.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl enable unicon.core.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo systemctl enable scichart.service"
    print(f"executing remote command {remote_command} on remote server...")            
    execute_remote_command(host, username, password, remote_command)

    remote_command = "sudo reboot"
    print(f"*************")
    print(f"*************")    
    print(f"REBOOT...")

    execute_remote_command(host, username, password, remote_command)
