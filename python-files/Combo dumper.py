import os
import glob
import re

art="""
 __   ___                 _             
 \ \ / / |               (_)            
  \ V /| |_ ___ _ __  ___ _  ___  _ __  
   > < | __/ _ \ '_ \/ __| |/ _ \| '_ \ 
  / . \| ||  __/ | | \__ \ | (_) | | | |
 /_/ \_\\__\___|_| |_|___/_|\___/|_| |_|
                                        
                                        
   ALL in one (Domaim Searcher,Email:Pass Extractor,Duplicate Remover)                                                                                                   
"""
def search_and_save_domain_occurrences(folder_path, domain_names):
    if not os.path.isdir(folder_path):
        print("The provided path is not a directory.")
        return

    domain_credentials = {domain: [] for domain in domain_names}

    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))


    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                for domain in domain_names:
                    if domain in line:

                        email_password = re.search(r'([^:/\s]+@[^:/\s]+:[^:/\s]+)', line)
                        if email_password:
                            domain_credentials[domain].append(email_password.group(1))


    for domain, credentials in domain_credentials.items():
        if credentials:

            unique_credentials = list(set(credentials))

            output_file_path = f'{domain}_credentials.txt'
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write('\n'.join(unique_credentials))
            print(f"Email and password pairs for '{domain}' saved to '{output_file_path}' without duplicates.")
        else:
            print(f"No email and password pairs found for '{domain}'.")


print(art)
folder_path = input("Enter the folder path: ")
domain_names = input("Enter domain names separated by semicolons (;): ").split(';')
search_and_save_domain_occurrences(folder_path, domain_names)
