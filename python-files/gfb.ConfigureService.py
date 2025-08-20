import sys
import subprocess
import os

def replace_config_values(file_path, values):

    abs_path = file_path + "/conf/nginx_template.conf"

    # Read in the file
    with open(abs_path, 'r') as file:
        filedata = file.read()

    # Replace the target strings
    placeholders = ['{HTTPPORT}', '{HTTPSPORT}', '{CERTPATH}', '{KEYPATH}', '{URL}', '{NGINXPATH}']
    for placeholder, value in zip(placeholders, values):
        filedata = filedata.replace(placeholder, value)

    filedata = filedata.replace('\\', '/')
    
    # Write the file out again
    abs_path_write = file_path + "/conf/nginx.conf"
    with open(abs_path_write, 'w') as file:
        file.write(filedata)
        
    print(f"Config successfully created in: " +  abs_path_write)

def install_nginx_service(service_name):
    subprocess.run(f"install-nginx-service.bat {service_name}", shell=True)
    print(f"{service_name} service installed and started.")

def uninstall_nginx_service(service_name):
    subprocess.run(f"uninstall-nginx-service.bat {service_name}", shell=True)
    print(f"{service_name} service uninstalled.")

if __name__ == "__main__":
    print("       python script.py --uninstall")

    if len(sys.argv) < 2:
        print("Usage: python script.py --config <HTTPPORT> <HTTPSPORT> <CERTPATH> <KEYPATH> <URL> <NGINXPATH>")
        print("       python script.py --install <PATH>")
        print("       python script.py --uninstall")
        sys.exit(1)

    if sys.argv[1] == "--config":
        if len(sys.argv) < 8:
            print("Usage: python script.py --config <HTTPPORT> <HTTPSPORT> <CERTPATH> <KEYPATH> <URL> <NGINXPATH>")
            sys.exit(1)
        values = sys.argv[2:]
        replace_config_values(sys.argv[7], values)
    elif sys.argv[1] == "--install":
        service_name = sys.argv[2] if len(sys.argv) >= 2 else "gfb-nginx-service"
        install_nginx_service(service_name)
    elif sys.argv[1] == "--uninstall":
        service_name = sys.argv[2] if len(sys.argv) >= 2 else "gfb-nginx-service"
        uninstall_nginx_service(service_name)
    else:
        print("First argument must be --config, --install or --uninstall")
