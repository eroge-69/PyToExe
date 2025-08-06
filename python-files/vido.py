import requests

video_url = input("Enter English video URL: ").strip()

headers = {
    "Content-Type": "application/json",
    "VIZARDAI_API_KEY": "06b92a015afd45899d1251d72dbcb412"
}

data = {
    "lang": "ar",
    "preferLength": [5],
    "minLength": 90,
    "videoUrl": video_url,
    "videoType": 2,
    "aspectRatio": "9:16",
    "showHeadline": True,
    "showSubtitleIfAny": True,
    "generateScript": True,
    "autoSubtitle": True,
    "voiceover": False,
    "translateFrom": "en",
    "translateTo": "ar",
    "enableTranslation": True
}

try:
    response = requests.post(
        "https://elb-api.vizard.ai/hvizard-server-front/open-api/v1/project/create",
        headers=headers,
        json=data
    )

    with open("vizard_response.txt", "w", encoding="utf-8") as file:
        file.write(response.text)

    if response.status_code == 200:
        print("✅ Saved to 'vizard_response.txt'")
    else:
        print("❌ Request failed. Check the file.")

except Exception as e:
    print("Error:", str(e))
