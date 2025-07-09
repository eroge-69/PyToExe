import requests
import json

class BaseForAPI:
    host_verify = True
    fhir_login_url = 'admin/login/?next=/'
    fhir_logout_url = 'dtr/logout/'
    request = requests.session()
    csrfmiddlewaretoken = None

    # Load from JSON
    data_file = "D:\\script_data.json"
    with open(data_file, "r") as file:
        data = json.load(file)

    dpa_host = data['url']
    username = data['username']
    password = data['password']

    @classmethod
    def login_api(cls, url=None, username=None, password=None):
        if url is None:
            url = cls.fhir_login_url
        if username is None:
            username = cls.username
        if password is None:
            password = cls.password

        response = cls.request.get(cls.dpa_host + url, verify=cls.host_verify, timeout=60)
        csrftoken = response.text.split('id="csrf-token" type="application/json">')[1].split('</')[0]
        cls.csrfmiddlewaretoken = csrftoken

        login_data = {
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrftoken,
            "next": "/"
        }

        response_login = cls.request.post(
            cls.dpa_host + url,
            data=login_data,
            headers={"Referer": cls.dpa_host},
            verify=cls.host_verify,
            timeout=60
        )

        fe_dtr_sid = None
        if response_login.status_code == 200:
            print(f"✅ Successfully logged in to '{cls.dpa_host}' as '{username}'")
            if 'csrftoken' in response_login.cookies:
                csrftoken = response_login.cookies['csrftoken']
            if 'FE_dtr_sid' in response_login.cookies:
                fe_dtr_sid = response_login.cookies['FE_dtr_sid']
            print("CSRF Token:", csrftoken)
            print("FE_dtr_sid:", fe_dtr_sid)
            return csrftoken, fe_dtr_sid
        else:
            print(f"❌ Login failed. Status code: {response_login.status_code}")
            return None, None


if __name__ == "__main__":
    obj = BaseForAPI()
    obj.login_api()
