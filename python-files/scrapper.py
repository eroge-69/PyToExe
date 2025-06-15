import json
import time
import colorama
import os
import signal

colorama.init()

DATABASES_FOLDER = "databases"
RESULTS_FOLDER = "results"

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

all_databases = []

for filename in os.listdir(DATABASES_FOLDER):
    if filename.endswith(".json"):
        with open(os.path.join(DATABASES_FOLDER, filename), "r") as file:
            all_databases.extend(json.load(file))


print(colorama.Fore.RED + r"""
      (       )   (    (       ) (         (     
   (  )\ ) ( /(   )\ ) )\ ) ( /( )\ )      )\ )  
 ( )\(()/( )\()) (()/((()/( )\()|()/(  (  (()/(  
 )((_)/(_)|(_)\   /(_))/(_)|(_)\ /(_)) )\  /(_)) 
((_)_(_))  _((_) (_))_(_))  _((_|_))_ ((_)(_))   
 | _ )_ _|| \| | | |_ |_ _|| \| ||   \| __| _ \  
 | _ \| | | .` | | __| | | | .` || |) | _||   /  
 |___/___||_|\_| |_|  |___||_|\_||___/|___|_|_\                                                                      
""" + colorama.Style.RESET_ALL)

print(colorama.Fore.GREEN + f"Found {len(all_databases)} bins")

if not all_databases:
    print(colorama.Fore.RED + "No bins found")
    exit()

def signal_handler(sig, frame):
    print('\n' + colorama.Style.RESET_ALL)
    raise SystemExit

signal.signal(signal.SIGINT, signal_handler)

while True:
    search_term = input(colorama.Fore.YELLOW + "Enter keyword to search (or Ctrl+C to exit): ")
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"{timestamp}-{search_term}"

    results = [
        bin_data for bin_data in all_databases
        if any(search_term in value for value in bin_data.values())
    ]

    print(colorama.Fore.GREEN + f"Found {len(results)} bins")

    if not results:
        print(colorama.Fore.RED + "No bins found")
        continue

    with open(os.path.join(RESULTS_FOLDER, f"{file_name}.txt"), "w") as file:
        file.write('\n'.join('|'.join(bin_data.values()) for bin_data in results))
    
    print(colorama.Fore.GREEN + f"Saved to {os.path.join(RESULTS_FOLDER, f'{file_name}.txt')}")

