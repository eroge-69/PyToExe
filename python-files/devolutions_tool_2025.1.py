__version__ = '2025.1'
__author__  = 'manavich@ru-board'
__warning__ = 'ONLY FOR RU-BOARD. NOT FOR BOARD 4 CHOSEN ONE!'

import uuid
import sys
import mmap
import os
from datetime import datetime, timedelta
from random import choices
from shutil import copy2
from string import ascii_uppercase, digits

from jwt import encode as jwt_encode

if sys.version_info[0] != 3 and sys.version_info[1] < 10:
    print(
        f'Unsupported python version ({sys.version_info[0]}.{sys.version_info[1]}). Minimum supported version is 3.10.')
    sys.exit()

BACKUP = 1
DLL = 'devolutions.licensing.dll'
DEVOLUTIONS_STAGE_PUBKEY = ('MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5Kz4i/+XZhiE+fyrgtx/\r\n'
                            '4yI3i6C6HXbC4QJYpDuSUEKN2bO9RsE+Fnds/FizHtJVWbvya9ktvKdDPBdy58+C\r\n'
                            'IM46HEKJhYLnBVlkEcg9N2RNgR3xHnpRbKfv+BmWjOpSmWrmJSDLY0dbw5X5YL8T\r\n'
                            'U69ImoouCUfStyCgrpwkctR0GD3GfcGjbZRucV7VvVH9bS1jyaT/9yORyzPOSTwb\r\n'
                            '+K9vOr6XlJX0CGvzQeIOcOimejHxACFOCnhEKXiwMsmL8FMz0drkGeMuCODY/OHV\r\n'
                            'mAdXDE5UhroL0oDhSmIrdZ8CxngOxHr1WD2yC0X0jAVP/mrxjSSfBwmmqhSMmONl\r\n'
                            'vQIDAQAB'.encode(encoding='UTF-16LE'))

DEVOLUTIONS_PRODUCTION_PUBKEY = ('MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs+6vV98/K9zqU6KrNuds\r\n'
                                 '4f7P0uqEi29hBEPQvONO2ManNx13KKa2SrO1clH08837FXFxyqLp+0yOwHe2lkRO\r\n'
                                 'XB/iV6pSKK72SYzU8WV/ukHMLKnYgMTVarKogVuNNcycDNKb3xbpTnPFUYCa+pha\r\n'
                                 'Uguc8mUHijGVLK2fxp5LVr/soNdtWjsKy5dFmUOnbPxSvL6qeC3xSFY6T2gMMCCC\r\n'
                                 'yQ8fOwMKa39UZk9m7BQZzZYLMmphXwHB/BWmaGHISkOfcs+Qtez7zZeUr/1U8wCw\r\n'
                                 'LaYnfr9g3lkMpPzKLJ3qxCnaUvLOC9hFNehc3o9SVaXwhYtzhQP0B++ucxKEuuEd\r\n'
                                 'OwIDAQAB'.encode(encoding='UTF-16LE'))

RUBOARD_PUBKEY = ('MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwox0Qve/SpmAFardSka6\r\n'
                  'qyX9sAZybOng/Vt37Jf7g9HQpAU2OnOlBWejcWwXkoqtxVjRVnmx+k75gSdZ33qa\r\n'
                  'OLbG7AOetkO/f98H3ja7OyRDb/r6zjEcwiMNRVjwvnetXDC8jxbXSpRcYWpqthNt\r\n'
                  'w9zu9RcLd9xcGIXKI127C4G0NUZuCjy+hnwInLZ/xP67ZOROtUxFscDpn6StfSS1\r\n'
                  'Zmx8tb7u1BQlrpUnve4ToGnJ2Iougqz8pomLEZcFkklvJwW/DwxrRoq5jOePIu1n\r\n'
                  'v680jj1ghz53KIB2HZANIsh7+aX6aLJZZew+MpEReMofJjqTYPitOdk04OQ13BOj\r\n'
                  'cwIDAQAB'.encode(encoding='UTF-16LE'))

REPLACE_LENGTH = len(RUBOARD_PUBKEY)

PEM = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwox0Qve/SpmAFardSka6qyX9sAZybOng/Vt37Jf7g9HQpAU2
OnOlBWejcWwXkoqtxVjRVnmx+k75gSdZ33qaOLbG7AOetkO/f98H3ja7OyRDb/r6
zjEcwiMNRVjwvnetXDC8jxbXSpRcYWpqthNtw9zu9RcLd9xcGIXKI127C4G0NUZu
Cjy+hnwInLZ/xP67ZOROtUxFscDpn6StfSS1Zmx8tb7u1BQlrpUnve4ToGnJ2Iou
gqz8pomLEZcFkklvJwW/DwxrRoq5jOePIu1nv680jj1ghz53KIB2HZANIsh7+aX6
aLJZZew+MpEReMofJjqTYPitOdk04OQ13BOjcwIDAQABAoIBAC5MFm7JXnB2TxDY
9Ih0hH+uLszw+9IHZk9ksQlQsb4Q9EHUK6+FTcQXgcHAI2vwLKJGHKsjksMqgB3I
K48PMhxFAtmvktl1DeF0Rf8Pr0bHvnSrmXvwHBPnG4VhQQlSmaLSxkyW9uz8mW9l
T7e8r+ZocUVKEqSXgCMl05DPAXAfJ26FJdz9CM+kiyXDziDm3j4P42J1UhtM3KRn
GR2gzjhUUYeIk+7o4QA4NqVKmlmJDgSJcDAAY/paArNPqRM4fnQs2XMUkGUUJ85k
Dp2+iC6Vr2ZkrLTr51WA7gqlp//hHlWPI+cIejU0rGsvJq4v7VAA37PT8xRk4dxS
MheXU+ECgYEA5Qs3Q0wEj+3sfhZ4mbt/CWprzxqc39HD5nds5pHvLxZcty0bETXC
6mDJOIT4xh5OH35eYJmFk2614AGIzobn3Xk+mAAoJy9ioEabTf4eCJ6PNIwMsS+u
MI6Fg+rQW9dvwnhZwgNjCP8cmCjaUrHFX6xPQtZgNwMUhRq5hhDItj8CgYEA2XHx
8WN/lpY9jeaUPYwkP3SwzySe6JbtlWwL9VO0cZykhZXeT1ikF+VyQ7MPs/91bVR3
wjM03wdngy/LkOH9rQwS9fJ+khClwNt5ird4ilBeNgsvH7jbxzO/I6VC1WGFRR2K
C8dD3oXziWnYEZ2cfdHMl3C7aOE3fDaBpMzHjc0CgYEA4X1RQqesNiZ+FQP6Zx73
ykVDLfl9R7wzqMkaJUS2vRy+2ndFloPfCO+QKlx+rk1XjBnUwDVkE+mClK3uCaU2
0At1XB+LaEh2SGQ6sWXkG4g+Y/Uc6bOPQa6OM3kQ99n45POnKiI7dbfyZrqRdage
MDprLdnvjzkxEnlk/F+5ufECgYEA0ZXCXahJkhu9uMhGmgw54+/Ve9MQV58h4KQD
4rKLefZBnYCWhmQpxd6iBB7TQ+s2g+qmg8hXbaD1ZLzsuPkaSXEZ1XWmCaOCICFr
RQkSZj6QkAa3pRvIunhmAzWG9aTJj5SpOjEWeaUi14/tcw03iQ5u5IkEGlL55/+h
dfbrYQECgYA1LyFQuxgGzgrgTZL5CNB1bxIyzQOsQcaEYCcqDX2gemIDJNBS/Tc5
c0i/L5i82or+/+p8hmJxQGRokCDNmzdeDlO8tSRnkenGkIabXgXQFjJKnOkWpOnX
YnpjQOK8azSGL/D8OmG9CArmmX0E3qiMVaCJv0+U8rxDCCDwAdN2PQ==
-----END RSA PRIVATE KEY-----'''

DEVOLUTIONS_PRODUCTS = {
    'rdm': ['RDM', 'Remote Desktop Manager', 'MRDM-PLAT'],
    'dvls': ['DVLS', 'Devolutions Server', 'DVLS-PLAT'],
    'cal': ['CAL', 'Client Access License', 'CAL-PLAT'],
    'dcl': ['DCL', 'Devolutions Launcher', 'DCL-PLAT'],
    'hub': ['HUB', 'Devolutions Hub', 'HUB-PLAT'],
    'gat': ['GAT', 'Devolutions Gateway', '-GAT'],
    'pam': ['PAM', 'Devolutions PAM', '-PAM'],
    'cyb': ['CYB', 'CyberArk', '-CYB'],
    'del': ['DEL', 'Delinea', '-DEL'],
    'bet': ['BET', 'BeyondTrust', '-BET']
}


def patch_pubkey(devolutions_licensing_dll: str = ''):
    if not devolutions_licensing_dll:
        devolutions_licensing_dll = input(
            f'Enter a path to {DLL} library:\n').strip()
    devolutions_licensing_dll = os.path.normpath(
        devolutions_licensing_dll.replace('"', ''))
    if not (os.path.isfile(devolutions_licensing_dll)) or not devolutions_licensing_dll.endswith(DLL):
        while not (os.path.isfile(devolutions_licensing_dll)) or not devolutions_licensing_dll.endswith(DLL):
            print(
                f'{DLL} library not found in path ({devolutions_licensing_dll})!')
            devolutions_licensing_dll = input(
                f'Enter a path to {DLL} library:\n').strip()
            devolutions_licensing_dll = os.path.normpath(
                devolutions_licensing_dll.replace('"', ''))
    try:
        fp = open(devolutions_licensing_dll, 'rb+')
        if BACKUP:
            copy2(devolutions_licensing_dll, devolutions_licensing_dll + '.bak')
        if os.stat(fp.name).st_size > 0:
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_WRITE)
        else:
            print(f'Error mapping {DLL} library into memory')
            return
        pattern_address_stage = mm.find(DEVOLUTIONS_STAGE_PUBKEY)
        if pattern_address_stage != -1:
            print(
                f'Patching {devolutions_licensing_dll} stage pubkey at offset={hex(pattern_address_stage)}')
            mm[pattern_address_stage:pattern_address_stage +
                REPLACE_LENGTH] = RUBOARD_PUBKEY
        else:
            print(f'Stage pubkey not found or already patched!')
        pattern_address_prod = mm.find(DEVOLUTIONS_PRODUCTION_PUBKEY)
        if pattern_address_prod != -1:
            print(
                f'Patching {devolutions_licensing_dll} production pubkey at offset={hex(pattern_address_prod)}')
            mm[pattern_address_prod:pattern_address_prod +
                REPLACE_LENGTH] = RUBOARD_PUBKEY
            mm.close()
        else:
            print(f'Production pubkey not found or already patched!')
            if pattern_address_stage == -1 and pattern_address_prod == -1:
                os.remove(devolutions_licensing_dll + '.bak')
            mm.close()
    except IOError as e:
        print(
            f'I/O error({e.errno}): {e.strerror}, filename={devolutions_licensing_dll}')
        if os.path.exists(devolutions_licensing_dll + '.bak'):
            os.remove(devolutions_licensing_dll + '.bak')
        if not mm.closed:
            mm.close()


def generate_serial_number() -> str:
    _ = ''.join(choices(ascii_uppercase + digits, k=25))
    return '-'.join([_[:5], _[5:10], _[10:15], _[15:20], _[20:25]])


def generate_license_file(product: str):
    product = product.lower()
    if not product in DEVOLUTIONS_PRODUCTS:
        print(f'There is no product {product}. Why did you do this... why... ;( Maybe it\'s a typo...')
        return
    serial_number = generate_serial_number()
    license_struct = {
        'aud': '',
        'exp': int((datetime.now() + timedelta(days=365)).timestamp()),
        'iat': int(datetime.now().timestamp()),
        'iss': 'https://quoting.devolutions.com',
        'jti': str(uuid.uuid4()),
        'nbf': int(datetime.now().timestamp()),
        'osc': serial_number,
        'version': 4,
        'licenses': [
            {
                'EndDate': '01/01/2030 00:00:00',
                'IsExclusive': False,
                'IsFree': False,
                'IsSubscription': False,
                'IsTrial': False,
                'LicenseCount': 0,  # Unlimited
                'ProductGroup': DEVOLUTIONS_PRODUCTS[product][0],
                'ProductName': DEVOLUTIONS_PRODUCTS[product][1],
                'Products': [DEVOLUTIONS_PRODUCTS[product][0]],
                'RegistrationDate': datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                'Serial': serial_number,
                'Sku': DEVOLUTIONS_PRODUCTS[product][2]
            }
        ]
    }

    key = jwt_encode(payload=license_struct, key=PEM, algorithm='RS512', headers={
                     'kid': 'a807c475-234e-4708-85bb-65e04b1183d6'})
    with open(os.getcwd() + f'/{DEVOLUTIONS_PRODUCTS[product][0]}.lic', 'w') as licenseFile:
        try:
            licenseFile.write(key)
            print(
                f'License key was successfully saved to {os.path.normpath(licenseFile.name)}')
        except Exception as error:
            print(f'{error}')


if __name__ == '__main__':
    sys.argv.pop(0)
    argsCount = len(sys.argv)
    for arg in sys.argv:
        sys.argv[sys.argv.index(arg)] = arg.lower()
    validArguments = ('patch', 'rdm', 'dvls', 'cal', 'dcl', 'hub', 'gat', 'pam', 'cyb', 'del', 'bet')
    if not argsCount or not set(sys.argv).intersection(validArguments):
        print(f'''Script misusage. Valid arguments: patch | rdm | dvls | cal | dcl | hub | gat | pam | cyb | del | bet
              - Use patch argument to patch the required DLL;
              - Optionally you can pass a path where Devolutions.Licensing.dll is stored. Do it right after the patch argument;
              - Use one of the product abbreviations to generate a corresponding license file:
              ---
                - rdm  = {DEVOLUTIONS_PRODUCTS["rdm"][1]}
                - dvls = {DEVOLUTIONS_PRODUCTS["dvls"][1]}
                - cal  = {DEVOLUTIONS_PRODUCTS["cal"][1]}
                - dcl  = {DEVOLUTIONS_PRODUCTS["dcl"][1]}
                - hub  = {DEVOLUTIONS_PRODUCTS["hub"][1]}
                - gat  = {DEVOLUTIONS_PRODUCTS["gat"][1]} (Module)
                - pam  = {DEVOLUTIONS_PRODUCTS["pam"][1]} (Module)
                - cyb  = {DEVOLUTIONS_PRODUCTS["cyb"][1]} (Module)
                - del  = {DEVOLUTIONS_PRODUCTS["del"][1]} (Module)
                - bet  = {DEVOLUTIONS_PRODUCTS["bet"][1]} (Module)
                
                If you want to patch the dll and generate some licenses, you can run the script like this ->
                python3 devolutions_tool_2025.1.py patch /opt/devolutions/Devolutions.Licensing.dll rdm dvls gat
                It's just an example, don't copy and run this stupid example as is.
                ''')
        sys.exit()
    match sys.argv[0]:
        case 'patch':
            if argsCount == 2 and sys.argv[1].replace('"', '').endswith(DLL):
                patch_pubkey(sys.argv[1])
            elif argsCount == 2 and sys.argv[1] in ('rdm', 'dvls', 'cal', 'dcl', 'hub', 'gat', 'pam', 'cyb', 'del', 'bet'):
                patch_pubkey()
                generate_license_file(sys.argv[1])
            elif argsCount > 2 and sys.argv[1].replace('"', '').endswith(DLL):
                patch_pubkey(sys.argv[1])
                sys.argv.pop(0)
                sys.argv.pop(0)
                for product in sys.argv:
                    generate_license_file(product)
            elif argsCount > 2 and not sys.argv[1].replace('"', '').endswith(DLL):
                patch_pubkey()
                sys.argv.pop(0)
                for product in sys.argv:
                    generate_license_file(product)
            else:
                patch_pubkey()
        case _:
            for product in sys.argv:
                generate_license_file(product)
