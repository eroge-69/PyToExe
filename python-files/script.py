while True:
    tab_open = False
    if tab_open == False:
        import webbrowser
        url = "https://www.google.com/search?q=where+can+i+get+cp+as+a+30+year+old+man+in+arizona%3F&rlz=1C1ONGR_enUS1148US1148&oq=where+can+i+get+cp+as+a+30+year+old+man+in+arizona%3F&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRigATIHCAUQIRigATIHCAYQIRirAjIHCAcQIRiPAjIHCAgQIRiPAtIBCDg0MTJqMGo3qAIIsAIB8QVjEGg5xN8J9A&sourceid=chrome&ie=UTF-8"
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe %s"
        webbrowser.get(chrome_path).open_new_tab(url)
        tab_open = True