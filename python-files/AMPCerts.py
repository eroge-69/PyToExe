import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys

amp={"3b1efd3a66ea28b16697394703a72ca340a05bd5":'CN=Microsoft Root Certificate Authority 2010, O=Microsoft Corporation, L=Redmond, S=Washington, C=US',
     "d69b561148f01c77c54578c10926df5b856976ad":'CN=GlobalSign, O=GlobalSign, OU=GlobalSign Root CA - R3',
    "d1eb23a46d17d68fd92564c2f1f1601764d8e349":'CN=AAA Certificate Services, O=Comodo CA Limited, L=Salford, S=Greater Manchester, C=GB',
    "b1bc968bd4f49d622aa89a81f2150152a41d829c":'CN=GlobalSign Root CA, OU=Root CA, O=GlobalSign nv-sa, C=BE',
    "ad7e1c28b064ef8f6003402014c3d0e3370eb58a":'OU=Starfield Class 2 Certification Authority, O="Starfield Technologies, Inc.", C=US',
    "a8985d3a65e5e5c4b2d7d66d40c6dd2fb19c5436":'CN=DigiCert Global Root CA, OU=www.digicert.com, O=DigiCert Inc, C=US',
    "742c3192e607e424eb4549542be1bbc53e6174e2":'OU=Class 3 Public Primary Certification Authority, O="VeriSign, Inc.", C=US',
    "5fb7ee0633e259dbad0c4c9ae6d38f1a61c7dc25":'CN=DigiCert High Assurance EV Root CA, OU=www.digicert.com, O=DigiCert Inc, C=US',
    "4eb6d578499b1ccf5f581ead56be3d9b6744a5e5":'CN=VeriSign Class 3 Public Primary Certification Authority - G5, OU="(c) 2006 VeriSign, Inc. - For authorized use only", OU=VeriSign Trust Network, O="VeriSign, Inc.", C=US',
    "2796bae63f1801e277261ba0d77770028f20eee4":'OU=Go Daddy Class 2 Certification Authority, O="The Go Daddy Group, Inc.", C=US',
    "0563b8630d62d75abbc8ab1e4bdfb5a899b24d43":'CN=DigiCert Assured ID Root CA, OU=www.digicert.com, O=DigiCert Inc, C=US',
    "ddfb16cd4931c973a2037d3fc83a4d7d775d05e4":'CN=DigiCert Trusted Root G4, OU=www.digicert.com, O=DigiCert Inc, C=US',
    "ca3afbcf1240364b44b216208880483919937cf7":'CN=QuoVadis Root CA 2, O=QuoVadis Limited, C=BM',
    "2b8f1b57330dbba2d07a6c51f70ee90ddab9ad8e":'CN=USERTrust RSA Certification Authority, O=The USERTRUST Network, L=Jersey City, S=New Jersey, C=US',
    "f40042e2e5f7e8ef8189fed15519aece42c3bfa2":'CN=Microsoft Identity Verification Root Certificate Authority 2020, O=Microsoft Corporation, L=Redmond, S=Washington, C=US',
    "df717eaa4ad94ec9558499602d48de5fbcf03a25":'CN=IdenTrust Commercial Root CA 1,O=IdenTrust,C=US'}
list=[]	
unmatch=[]

def find_all_certs():
    for store in {"CA", "ROOT", "MY"}:
        for cert, encoding, trust in ssl.enum_certificates(store):
            certificate = x509.load_der_x509_certificate(cert, backend=None)
            sha= certificate.fingerprint(hashes.SHA1())
            sha1_hex= sha.hex()
            list.append(sha1_hex)

def display_all_certs():
    installed_text.delete('1.0', tk.END)
    for cert in list:
        installed_text.insert(tk.END, f"{cert}\n")

def find_missing_certs():
    for i in amp:
        if i not in list:
            unmatch.append(i)

def display_missing_certs():
    missing_text.delete('1.0', tk.END)
    for cert in unmatch:
        missing_text.insert(tk.END, f"{cert}\n")
    if unmatch:
        messagebox.showinfo("Warning", "You have missing certificates! Cisco SE might not be working properly")
    else:
        messagebox.showinfo("SUCCESS", "You have all require root certificates installed!")


if __name__ == '__main__':
    
    #print("Finding all Certs and saving them and displaying them ...\n")
    find_all_certs()
    #display_all_certs()
    #print("[+] Finding missing root certificates...\n")
    find_missing_certs()
    #display_missing_certs()
    root = tk.Tk()
    root.title("Cisco Secure Endpoint Missing Certificates Finder")
    root.geometry("500x500")
    root.configure(bg='blue')

    installed_button = tk.Button(root, text= "Display installed certs", command = display_all_certs, bg='skyblue', fg='black')
    installed_button.pack(pady=10)
    installed_text = scrolledtext.ScrolledText(root, width=80, wrap=tk.WORD, bg='black', fg='green', height=10)
    installed_text.pack(pady=10)

    missing_button = tk.Button(root, text= "Display missings ", command= display_missing_certs)
    missing_button.pack(pady=10)
    missing_text = scrolledtext.ScrolledText(root, width=60,  wrap=tk.WORD, bg='black', fg='red', height=10)
    missing_text.pack(pady=10)
    root.mainloop()
        
  
