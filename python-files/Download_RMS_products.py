import requests
from requests_ntlm import HttpNtlmAuth
import os
import wget
import argparse,shutil
import json;

try:
    import requests
    import requests_ntlm
    import wget
    
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install",\
                        "requests"])
    subprocess.check_call([sys.executable, "-m", "pip", "install",\
                        "requests_ntlm"])
    subprocess.check_call([sys.executable, "-m", "pip", "install",\
                        "wget"])
    import requests
    import requests_ntlm
    import wget

# Credentials field
#username = 'XXXXX'
#password = 'XXXX'

def download_product(product_name,group_name,username,password):
    type="internal"
    data = {
    "group": group_name,
    "product": product_name,
    "releasetype": type
    }
    #input = json.dumps(data, indent=4)

    input = {"group": group_name, "product": product_name, "releasetype": "internal"}
    #print(input)
    ScriptPath = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(ScriptPath, '')

    headers = {'Content-Type': 'application/json'}

    print(f'Get Build Download URL for {product_name}')
    #GetBuildDownloadURLApi = 'http://rmsapi/download/activerelease'
    GetBuildDownloadURLApi = 'http://rmsapi/download/lastestsdprelease'
    response = requests.post(GetBuildDownloadURLApi, auth=HttpNtlmAuth(username, password), json=input, headers=headers)
    
    if response.status_code == 200:
        files = response.content
        response_decode = files.decode('utf-8').replace('"', '')
        print("\n\n")
        print(f"File Download starts for {product_name}")
        print(response_decode)
        print("\n\n")
        src = wget.download(response_decode)
        print("\n\n")
        print(src)
        print("\n\n")
        #current_directory = os.getcwd()
        #print(current_directory)
        # Get the absolute path of the current script
        pyscript_path = os.path.abspath(__file__)
        # Get the directory containing the script
        pyscript_dir = os.path.dirname(pyscript_path)
        #print("Script is running from:", pyscript_dir)
        newproduct_name = product_name.replace(' ', '_')
        shutil.move(src, pyscript_dir+"\\"+newproduct_name+".zip")
    else:
        print(f"Failed to get download URL for {product_name}. Status code: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description='Script to download product binaries from RMS API')
    parser.add_argument('-p', '--product', required=True, help='Product name to download')
    parser.add_argument('-g', '--group', required=True, help='Group name of the product')
    parser.add_argument('-user', '--user', required=True, help='Group name of the product')
    parser.add_argument('-pass', '--password', required=True, help='Group name of the product')
    
    args = parser.parse_args()

    download_product(args.product, args.group, args.user, args.password)
    
def main11():
    parser = argparse.ArgumentParser(description='Script to download product binaries from RMS API')
    parser.add_argument('-p', required=True, help='eg. python uploadfiles.py -p productname')
    parser.add_argument('-g', required=True, help='eg. python uploadfiles.py -g groupname')
    
    args = parser.parse_args()
    #print(args)
    results_file = main()
    #versionno=results_file[1]
    productname=results_file[0]
    groupname=results_file[1]
    #for product_name in args.products:
    download_product(productname,groupname)
    return args.product,args.group

if __name__ == "__main__":
    main()