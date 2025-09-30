import json

source = "fribbels-optimizer-save.json"
out = f"{source.split('.')[0]}-min.json"
data = json.load(open(source, encoding="utf-8"))

keep = []

for char in data["characters"]:
    keep += [relic_id for relic_id in char["equipped"].values()]

# remove all relics except for the ones in keep
data["relics"] = [relic for relic in data["relics"] if relic["id"] in keep]

json.dump(data, open(out, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
