import webview

# Açmak istediğin site
url = "http://localhost:8000"

# Pencere oluştur
webview.create_window("Benim Uygulamam", url, width=1024, height=768)

# Uygulamayı başlat
webview.start()