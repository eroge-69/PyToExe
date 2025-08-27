import webbrowser

# Deschide Microsoft Edge cu un URL
url = "https://www.google.com"

# 'microsoft-edge:' este protocolul Windows pentru Edge
webbrowser.open("microsoft-edge:" + url)
