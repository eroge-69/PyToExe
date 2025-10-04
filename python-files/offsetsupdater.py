import json
import os
import urllib.request
from collections import OrderedDict
 
# Reading latest offsets from Github
URL_OFFSETS = "https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/offsets.json"
URL_CLIENT  = "https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/client_dll.json"
 
LOCAL_FILE = "offsets.json"
 
KEYS_ORDER = [
    "dwViewMatrix",
    "dwLocalPlayerPawn",
    "dwEntityList",
    "m_hPlayerPawn",
    "m_iHealth",
    "m_lifeState",
    "m_iTeamNum",
    "m_vOldOrigin",
    "m_pGameSceneNode",
    "m_modelState",
    "m_boneArray",
    "m_nodeToWorld",
    "m_sSanitizedPlayerName",
]
 
def fetch_json(url):
    with urllib.request.urlopen(url) as response:
        return json.load(response)
 
def build_whitelisted_offsets(remote_offsets, remote_client):
    result = {}
 
    # from offsets.json
    offsets = remote_offsets.get("client.dll", {})
    for key in ["dwViewMatrix", "dwLocalPlayerPawn", "dwEntityList"]:
        if key in offsets:
            result[key] = offsets[key]
 
    # from client_dll.json
    classes = remote_client.get("client.dll", {}).get("classes", {})
    for class_name, class_data in classes.items():
        fields = class_data.get("fields", {})
        for field, value in fields.items():
            if field in KEYS_ORDER:
                result[field] = value
 
    result["m_boneArray"] = 128
 
    return result
 
def save_ordered_json(data, file_path):
    ordered = OrderedDict()
    for key in KEYS_ORDER:
        if key in data:
            ordered[key] = data[key]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2)
 
def update_local_offsets():
    print("[INFO] Fetching latest offsets from GitHub...")
    remote_offsets = fetch_json(URL_OFFSETS)
    remote_client  = fetch_json(URL_CLIENT)
 
    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        print("[INFO] Loaded existing local offsets.json")
    else:
        # Create new JSON if don't exists
        local_data = build_whitelisted_offsets(remote_offsets, remote_client)
        save_ordered_json(local_data, LOCAL_FILE)
        print("[SUCCESS] Local offsets.json not found, created new offsets.json")
        return
 
    updated = False
 
    # Update only whitelisted keys
    latest_data = build_whitelisted_offsets(remote_offsets, remote_client)
    for key in KEYS_ORDER:
        if key in latest_data:
            new_value = latest_data[key]
            if key in local_data:
                if local_data[key] != new_value:
                    print(f"[UPDATE] {key}: {local_data[key]} → {new_value}")
                    local_data[key] = new_value
                    updated = True
            else:
                print(f"[ADD] {key}: {new_value}")
                local_data[key] = new_value
                updated = True
 
    if updated:
        save_ordered_json(local_data, LOCAL_FILE)
        print("[SUCCESS] offsets.json updated")
    else:
        print("[INFO] Local offsets.json already up to date")
 
if __name__ == "__main__":
    update_local_offsets()