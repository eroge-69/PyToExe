import uuid
from tqdm import tqdm
from halo import Halo
import urllib.request
import time
import random
import getpass
import re
import sqlite3
import os

def waiting_time(waiting_type) :
    if (waiting_type == 's') :
        sleep_time = random.uniform(1, 3)
    elif (waiting_type == 'l') :
        sleep_time = random.uniform(6, 10)
        
    time.sleep(sleep_time)

def loading_animation() :
    print('UETR Checker And Download V.8.4 | FOR INTERNAL USAGE ONLY!')
    print('COPYRIGHT (c) 2023 Swift\nAll Right Reserved')
    print('-----------------------------------------------------')
    
    total_iterations = 65
    for _ in tqdm(range(total_iterations), desc="Contacting server node ", unit="server(s) "):
        time.sleep(random.uniform(0.1, 0.9))

def loading_spinner(textLoading, sleep, textSuccess) :
    spinner = Halo(text=textLoading, spinner="dots")
    spinner.start()
    time.sleep(sleep)
    spinner.succeed(textSuccess)

def connection_check() :
    spinner = Halo(text='contacting to swift.com .......', spinner="dots")
    spinner.start()
    time.sleep(random.uniform(6, 10))
    try:
        urllib.request.urlopen("https://swift.com")
        spinner.succeed('connection established')
        return True
    except:
        spinner.fail('connection to swift server failed! exiting...')
        waiting_time('l')
        exit()

def generate_fake_filesystem_name():
    prefixes = ["sys", "usr", "data", "app", "config", "temp"]
    extensions = [".exe", ".dll", ".txt", ".dat", ".config", ".tmp"]
    
    prefix = random.choice(prefixes)
    extension = random.choice(extensions)
    number = random.randint(100, 999)
    
    return f"{prefix}_{number}{extension}"

def fake_loading_animation():
    print("Loading system files:")
    for _ in range(10):
        time.sleep(0.5)  # Simulate loading delay
        
        # Clear the console (works on most terminals)
        print("\033[H\033[J")
        
        fake_filename = generate_fake_filesystem_name()
        print(f"Loading: {fake_filename}...")
        
        print("=" * random.randint(10, 30))
    
    print("Loading complete!")

def validate_uetr(uetr):
    try:
        # Try to create a UUID object from the given UETR string
        uuid_obj = uuid.UUID(uetr)
        # Check if the UUID is version 4 (random)
        if uuid_obj.version != 4:
            return False
        # Check if the variant is 'RFC 4122'
        if uuid_obj.variant != uuid.RFC_4122:
            return False
        return True
    except ValueError:
        return False
    
def generate_random_status():
    if random.random() < 0.5:
        return "valid"
    else:
        return "invalid"
    
def savetoDBAndResult (uetr) :
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    insert_data_query = """
    INSERT INTO uetr (uetr, status) VALUES (?, ?)
    """

    status = generate_random_status()   

    user_data = [uetr, status]

    cursor.execute(insert_data_query, user_data)

    if (status == 'valid') :
        print('UETR is VALID')
        os.system('pause')
        exit()
    else :
        print('UETR is INVALID')
        os.system('pause')
        exit()
    
def checkingDB(uetr) :
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS uetr (
        id INTEGER PRIMARY KEY,
        uetr TEXT,
        status TEXT
    )
    """
    cursor.execute(create_table_query)

    checkingIfInDB = """
    SELECT * FROM uetr WHERE uetr = ?
    """

    uetr_data = [uetr]
    cursor.execute(checkingIfInDB, uetr_data)

    row = cursor.fetchone()
    if row:
        if (row.status == 'valid') :
            print('UETR is VALID')
            time.sleep(10)
            os.system('pause')
            exit()
        else :
            print('UETR is INVALID')
            os.system('pause')
            exit()

    else:
        savetoDBAndResult(uetr)

def start_transaction() :
    fake_loading_animation()
    print('=========================================')
    print('All done, please input your UETR Code.\n')
    uetr = input('UETR CODE : ')

    loading_spinner('encrypting UETR Code....', random.uniform(2,6), 'encrypted')
    loading_spinner('sending UETR to server....', random.uniform(2,6), 'UETR received by swift server')

    spinner = Halo(text='validating UETR code...', spinner="dots")
    spinner.start()
    time.sleep(random.uniform(7,10))

    validator = validate_uetr(uetr)

    if validator :
        spinner.succeed('UETR validated')
        checkingDB(uetr)
    else :
        spinner.fail('INVALID UETR FORMAT!')
        print('exiting...')
        time.sleep(5)
        exit()

def login_page() :
    username = input('username : ')
    password = getpass.getpass('password : ')

    loading_spinner('checking password....', 2, 'password checking successfully...')

    if (username != '111' or password != '111') :
        print('WRONG PASSWORD!! exiting...')
        waiting_time('l')
        exit()
    else :
        start_transaction()

def securing_transaction() :
    loading_spinner('securing connection...', random.uniform(1, 3), 'connection secured')
    loading_spinner('encrypting transport...', random.uniform(1, 3), 'transport encrypted')
    login_page()

def main() :
    loading_animation()
    check_server = connection_check()
    if (check_server) :
        securing_transaction()


main()