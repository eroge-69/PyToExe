import  requests



def open_site(urls,i):
    bad_getway = 500;  # bad getway
    url_not_found = 404;  # url not found
    internet_server_error = 500;  # internet server error
    forbidden = 403;  # 403 Forbidden
    timeout = 504;  # 504 Gateway Timeout
    not_acceptable = 406;  # 406 Not Acceptable
    service_unavilable = 503  # 503 Service Unavailable

    try:
        #br = Browser()
        #br.open(urls)
        r = requests.get(urls)
        if(r.status_code == 200):
            print(i," -| " + urls + " [ Found ]")
        elif (r.status_code  == bad_getway):
            print(i," -| " + urls + " [ 502 Bad Gateway ]")
        elif (r.status_code  == url_not_found):
            print(i," -| " + urls + " [ 404 Not Found ]")
        elif (r.status_code  == internet_server_error):
            print(i," -| " + urls + " [ 500 Internal Server Error ]")
        elif (r.status_code  == forbidden):
            print(i," -| " + urls + " [ 403 Forbidden ]")
        elif (r.status_code  == timeout):
            print(i," -| " + urls + " [ 504 Gateway Timeout ]")
        elif (r.status_code  == not_acceptable):
            print(i," -| " + urls + " [ 406 Not Acceptable ]")
        elif (r.status_code  == service_unavilable):
            print(i," -| " + urls + " [ 503 Service Unavailable ]")
    except:
        print("Request Faild : ",r.status_code);


'''
list = ["404", "500"]
res = "\n".join(list)
#res apnar value
print(res)
'''


urls=input("Enter Your List : ");
i = 0;
with open(urls, "r") as fd:
    for line in fd:
        line = line.replace("\r", "").replace("\n", "")
        #print("LINE : ",line)
        ishttp = line.startswith('http')
        ishttps = line.startswith('https')
        if ishttp == False and ishttps == False:
            line = "http://"+line;

        #now call this
        #print(line)
        i=i+1;
        open_site(line,i)