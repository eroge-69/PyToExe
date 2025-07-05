import os

# List of websites to block
websites_to_block = [
    "www.xhamster19.com",
    "m.xhamster19.com",
    "mobile.xhamster19.com",
    "www.xhamster2.com",
    "m.xhamster2.com",
    "mobile.xhamster2.com",
    "www.xhaccess.com",
    "m.xhaccess.com",
    "mobile.xhaccess.com",
    "www.xvideos2.com",
    "m.xvideos2.com",
    "mobile.xvideos2.com",
    "www.pornxnow.me",
    "m.pornxnow.me",
    "mobile.pornxnow.me",
    "www.erome.com",
    "m.erome.com",
    "mobile.erome.com",
    "www.xxxbp.tv",
    "m.xxxbp.tv",
    "mobile.xxxbp.tv",
    "www.jilhub.org",
    "m.jilhub.org",
    "moile.jilhub.org",
    "www.xhamster.desi",
    "m.xhamster.desi",
    "mobile.xhamster.desi",
    "www.xvideos.com",
    "m.xvideos.com",
    "mobile.xvideos.com",
    "pornhub.com",
    "www.pornhub.com",
    "m.pornhub.com",
    "mobile.pornhub.com",
    "www.xhamster.com",
    "m.xhamster.com",
    "mobile.xhamster.com",
    "www.xnxx.com",
    "m.xnxx.com",
    "mobile.xnxx.com",
    "youporn.com",
    "www.porn.com",
    "m.porn.com",
    "mobile.porn.com",
    "tube8.com",
    "www.ixxx.com",
    "m.ixxx.com",
    "mobile.ixxx.com",
    "porn300.com",
    "www.sexvid.xxx",
    "m.sexvid.xxx",
    "mobile.sexvid.xxx",
    "www.rexporn.sex",
    "m.rexporn.sex",
    "mobile.rexporn.sex",
    "fuq.com",
    "beeg.com",
    "sunporno.com",
    "www.redtube.com",
    "m.redtube.com",
    "mobile.redtube.com",
    "tube8.com",
    "pornhat.com"
    "pornone.com",
    "zbporn.com",
    "ok.xxx",
    "tubegalore.com",
    "theyarehuge.com",
    "perfectgirls.xxx",
    "gptgirlfriend.online",
    "made.porn",
    "sexy.ai",
    "spicychat.ai",
    "landing.brazzersnetwork.com/?ad_id=84990_TPS&ats=eyJhIjoxMDc0NCwiYyI6NDQ3NDc0ODgsIm4iOjE0LCJzIjo5MCwiZSI6ODgwMywicCI6NTd9",
    "natour.naughtyamerica.com/track/MTEyNDg3LjEwMDI1LjguOC4xOC4wLjAuMC4w",
    "landing.rk.com/?ad_id=84990_TPS&ats=eyJhIjoxMDc0NCwiYyI6NDQ3NDc0ODgsIm4iOjIwLCJzIjozNTgsImUiOjg5ODMsInAiOjU3fQ",
    "g2fame.com/adulttime/go.php?pr=8&su=2&si=247&ad=264593&pa=index&ar=&campaign=275281&buffer=",
    "digitalplayground.com/landing/tgp5/?ats=eyJhIjoxMDc0NCwiYyI6NDQ3NDc0ODgsIm4iOjE3LCJzIjoxMzUsImUiOjQ5MiwicCI6MjA1fQ=="
]

# Hosts file path
hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
redirect_ip = "127.0.0.1"

# Read the current hosts file
with open(hosts_path, 'r+') as file:
    content = file.read()
    for website in websites_to_block:
        entry = f"{redirect_ip} {website}"
        if entry not in content:
            file.write(f"\n{entry}")
            print(f"Blocked: {website}")
        else:
            print(f"Already blocked: {website}")
