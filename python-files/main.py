import xml.etree.ElementTree as ET
import json, os, pyperclip


def get_token():
    xml_file = os.path.join("adb pull /data/data/com.percent.royaldice/shared_prefs/com.google.firebase.auth.api.Store.W0RFRkFVTFRd+MTo3NzU1NDYxOTMwMjphbmRyb2lkOjU4Y2Q4NzA2ZGNjY2MwMjc.xml")
    local_file = os.path.join(os.getcwd(),
                              "com.google.firebase.auth.api.Store.W0RFRkFVTFRd+MTo3NzU1NDYxOTMwMjphbmRyb2lkOjU4Y2Q4NzA2ZGNjY2MwMjc.xml")
    os.system(xml_file)

    try:
        tree = ET.parse(local_file)
        root = tree.getroot()

        for child in root.iter('map'):
            for item in child.findall('string'):
                if item.get('name') == 'com.google.firebase.auth.FIREBASE_USER':
                    firebase_user = item.text
                    firebase_user_json = json.loads(firebase_user)
                    cached_token_state = json.loads(firebase_user_json['cachedTokenState'])
                    refresh_token = cached_token_state['refresh_token']
                    print(f"\nToken:\033[32m\n{refresh_token}\033[0m")
                    pyperclip.copy(refresh_token)
                    os.remove(local_file)
                    return True
    except FileNotFoundError:
        print("Не удалось получить Токен. Нажмите Enter для повторной попытки.")
        input()
        return False


while not get_token():
    pass
