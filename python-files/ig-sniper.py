import json

followers: list[str] = []
following: list[str] = []
exceptions: list[str] = [
    'greenvalleyfc_',
    'linkinpark',
    'muse',
    'borgheseale',
    'avengedsevenfold',
    'mrcarsounds',
    'ravensrock9',
    'tweeneryt',
    'juventus',
    'memphisdepay',
    'dancemalora',
    'azzurri',
    'f1',
    'charles_leclerc',
    'scuderiaferrari',
    'lalisciacatanese'
]

with open("followers.json") as followers_data:
    raw_data = json.loads(followers_data.read())
    for record in raw_data: followers += [record["string_list_data"][0]["value"]]
    
with open("following.json") as followers_data:
    raw_data = json.loads(followers_data.read())["relationships_following"]
    for record in raw_data: following += [record["string_list_data"][0]["value"]]
    
black_list: list[str] = [account for account in following if (account not in followers) and (account not in exceptions)]

print("--- Black-listed accounts ---")
for account in black_list: print("\u2022", account)