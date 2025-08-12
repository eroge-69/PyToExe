import webview

APP_NAME = "Datairs Desktop"
SITE_URL = "https://datairs.xyz"

if __name__ == '__main__':
    webview.create_window(APP_NAME, SITE_URL, width=1200, height=800)
    webview.start()
