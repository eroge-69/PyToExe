import requests
import json

class BaseForAPI:
    dpa_host = qa
    host_verify = True
    fhir_login_url = 'admin/login/?next=/'
    fhir_logout_url = 'dtr/logout/'
    request = requests.session()
    csrfmiddlewaretoken = None

    data_file = "D:\\script_data.json"

    with open(data_file, r) as file:
        data = json.load(file)

    dpa_host : data['url']
    username : data['username']
    password : data['password']

    # ------------------------------------------------------------------------------

    @staticmethod
    def login_api(url=fhir_login_url, username=username, password=password):
        response = BaseForAPI.request.get(BaseForAPI.dpa_host + url, verify=BaseForAPI.host_verify, timeout=60)
        csrftoken = response.text.split('id="csrf-token" type="application/json">')[1].split('</')[0]
        # csrftoken = response.cookies['csrftoken']
        BaseForAPI.csrfmiddlewaretoken = csrftoken
        login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken,
                          next='/')
        response_login = BaseForAPI.request.post(BaseForAPI.dpa_host + url, data=login_data,
                                                 headers=dict(Referer=BaseForAPI.dpa_host),
                                                 verify=BaseForAPI.host_verify, timeout=60)
        fe_dtr_sid = None
        if response_login.status_code == 200:
            print(f"********** Successfully logged in to '{BaseForAPI.dpa_host}' as a '{username}'")
            if 'csrftoken' in response_login.cookies.keys():
                csrftoken = response_login.cookies['csrftoken']
            if 'FE_dtr_sid' in response_login.cookies.keys():
                fe_dtr_sid = response_login.cookies['FE_dtr_sid']
            print(csrfmiddlewaretoken, fe_dtr_sid)
            return csrftoken, fe_dtr_sid
        else:
            print(f"********** Response code '{response_login.status_code}'")
            print(f"********** Failed log in to '{BaseForAPI.dpa_host}'")
            assert False


obj = BaseForAPI()
obj.login_api