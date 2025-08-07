import os
import json
import urllib.parse
import pandas as pd
import requests
from urllib.parse import urlparse
import tkinter as tk
from tkinter import simpledialog
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

def get_data(url):
    response = requests.get(url, headers=HEADERS)
    json_text = response.text.replace("null", '""').split(")]}'")[1]
    json_data = json.loads(json_text)
    review_data = json_data[6][175][9][0][0][0][0]
    reviwername = review_data[1][4][5][0]
    review = review_data[2][15][0][0]
    review_rate = review_data[2][0][0]
    
    return reviwername, review, review_rate

def create_gmap_url(query_string):
    return (
        f"https://www.google.com/search?tbm=map&authuser=0&hl=en&pb=!4m12!1m3!1d118411.34151971788!2d-4.0!3d54.0!2m3!1f0!2f0!3f0!3m2!1i1536!2i387!4f13.1!7i999!10b1!12m25!1m5!18b1!30b1!31m1!1b1!34e1!2m3!5m1!6e2!20e3!4b0!10b1!12b1!13b1!16b1!17m1!3e1!20m4!5e2!6b1!8b1!14b1!46m1!1b0!96b1!19m4!2m3!1i360!2i120!4i8!20m48!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m33!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3!1e9!2b1!3e2!2b1!9b0!22m6!1seCn6Z4HLPKOX4-EPveiYKA%3A4!2s1i%3A0%2Ct%3A11886%2Cp%3AeCn6Z4HLPKOX4-EPveiYKA%3A4!7e81!12e5!17seCn6Z4HLPKOX4-EPveiYKA%3A41!18e15!24m108!1m32!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m21!3b1!4b1!5b1!6b1!9b1!12b1!13b1!14b1!17b1!20b1!21b1!22b1!25b1!27m1!1b0!28b0!32b1!33m1!1b1!34b0!36e1!10m1!8e3!11m1!3e1!14m1!3b0!17b1!20m2!1e3!1e6!24b1!25b1!26b1!29b1!30m1!2b1!36b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!65m5!3m4!1m3!1m2!1i224!2i298!71b1!72m22!1m8!2b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_google_reviews!6m1!1e1!9b1!89b1!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1!1b1!125b0!126b1!127b1!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i530!2i387!1m6!1m2!1i1486!2i0!2m2!1i1536!2i387!1m6!1m2!1i0!2i0!2m2!1i1536!2i20!1m6!1m2!1i0!2i367!2m2!1i1536!2i387!34m19!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!31b1!37m1!1e81!42b1!47m0!49m10!3b1!6m2!1b1!2b1!7m2!1e3!2b1!8b1!9b1!10e2!50m4!2e2!3m2!1b1!3b1!67m3!7b1!10b1!14b1!69i728"
        f"&q={query_string}&oq={query_string}"
    )

def fetch_google_maps_data(query):
    query_string = urllib.parse.quote(query, safe="")
    url = create_gmap_url(query_string)

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch data for {query}")
        return []
    try:
        json_text = response.text.replace("null", '""').split(")]}'")[1]
        json_data = json.loads(json_text)
        store_list = json_data[64]
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

    return process_places(store_list)

def process_places(store_list):
    results = []

    for store in store_list:
        store = store[1]
              
        place = {
            "business_name": "",
            "website_url": "",
            "email": "",
            "phone": "",
            "address": "",
            "total_reviews": "",
            "avg_rating": "",
            "review_rating": "",
            "reviewer_name": "",
            "review_snippet": "",
        }
        try: place["business_name"] = store[11].replace("'", "\\'")[:512]
        except: pass

        try: 
            address = store[18].replace("'", "\\'")[:512]
            place["address"] = address
        except: pass

        try: place["phone"] = store[178][0][0].replace("'", "\\'")[:30]
        except: pass

        try:
            parsed_uri = urlparse(store[7][0].split("/url?q=")[1])
            website_url = f'{parsed_uri.scheme}://{parsed_uri.netloc}/'
            place["website_url"] = website_url[:100]
        except: pass

        try:
            place["avg_rating"] = store[4][7]
            place["total_reviews"] = store[4][8]
        except: pass

        try:
            a = store[9][2]
            b = store[9][3]
            c = store[89]
            unique_id = store[10]
            # place["url"] = f"https://www.google.com/maps/place/{place['business_name']}/data=!4m5!3m4!1s{unique_id}!8m2!3d{a}!4d{b}!16s{c}"
            pb_template = (
                "!1m16!1s{cid}!3m8!1m3!1d1616.3768893884196!2d{lng}!3d{lat}"
                "!3m2!1i1413!2i338!4f13.1!4m2!3d{lat}!4d{lng}"
                "!15m2!1m1!4s{c_loc}!12m4!2m3!1i360!2i120!4i8"
                "!13m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240"
                "!7m33!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3"
                "!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3!1e9!2b1!3e2!2b1"
                "!9b0!15m8!1m7!1m2!1m1!1e2!2m2!1i195!2i195!3i20!14m2!1st4qTaOh6wO3k2g-09qOgBw!7e81"
                "!15m113!1m33!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m22!3b1!4b1!5b1!6b1"
                "!9b1!12b1!13b1!14b1!17b1!20b1!21b1!22b1!25b1!27m1!1b0!28b0!30b1!32b1!33m1!1b1!34b1"
                "!36e2!10m1!8e3!11m1!3e1!14m1!3b0!17b1!20m2!1e3!1e6!24b1!25b1!26b1!27b1!29b1!30m1"
                "!2b1!36b1!37b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!61m2!1m1!1e1"
                "!65m5!3m4!1m3!1m2!1i224!2i298!72m22!1m8!2b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!4b1"
                "!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_google_review_posts__and__hotel_and_vr_partner_review_posts"
                "!6m1!1e1!9b1!89b1!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1"
                "!1b1!125b0!126b1!127b1!21m28!1m6!1m2!1i0!2i0!2m2!1i530!2i338!1m6!1m2!1i1363!2i0"
                "!2m2!1i1413!2i338!1m6!1m2!1i0!2i0!2m2!1i1413!2i20!1m6!1m2!1i0!2i318!2m2!1i1413!2i338"
                "!22m1!1e81!30m6!3b1!6m1!2b1!7m1!2b1!9b1!34m5!7b1!10b1!14b1!15m1!1b0!37i743!39s{location}"
            )

            encoded_location = place["business_name"]
            pb_final = pb_template.format(
                cid=unique_id,
                lat=b,
                lng=a,
                c_loc = c,
                location=encoded_location
            )

            full_url = f"https://www.google.com/maps/preview/place?authuser=0&hl=en&gl=us&pb={pb_final}&q={encoded_location}"
            place["reviewer_name"],place["review_snippet"],place["review_rating"] = get_data(full_url)
            print(full_url)
        except: pass

        results.append(place)

    return results

def save_to_csv(data, query_string):
    if not data:
        return

    df = pd.DataFrame(data)
    output_path = f"{query}.csv"
    if os.path.exists(output_path):
        df.to_csv(output_path, mode='a', index=False, header=False)
    else:
        df.to_csv(output_path, index=False)

    print(f"{query_string} :----------: [{len(data)}]")

def main():
    global query

    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring("Google Maps Scraper", "Enter search query (e.g., 'restaurants in New York'):")

    if not user_input:
        print("No input provided. Exiting.")
        return

    query = user_input.strip()
    places = fetch_google_maps_data(query)
    query_string = urllib.parse.quote(query, safe="")
    save_to_csv(places, query_string)

if __name__ == "__main__":
    main()
