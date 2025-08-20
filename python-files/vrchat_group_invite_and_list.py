import requests
import json
import os
from time import sleep

# Base URL for VRChat API
API_BASE = "https://api.vrchat.cloud/api/1"

def get_auth_cookie():
    """Prompt user for VRChat authentication cookie."""
    cookie = input("Enter your VRChat authentication cookie (from browser): ")
    return cookie.strip()

def get_group_id():
    """Prompt user for the Group ID to invite users to."""
    group_id = input("Enter the Group ID (e.g., grp_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx): ")
    return group_id.strip()

def get_current_instance_id(cookie):
    """Fetch the current instance ID of the user."""
    headers = {
        "Cookie": f"auth={cookie}",
        "User-Agent": "VRChatAutoInviteScript/1.0"
    }
    try:
        response = requests.get(f"{API_BASE}/auth/user", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        if user_data.get("currentWorldId"):
            instance_id = user_data.get("currentWorldId")
            return instance_id
        else:
            print("Error: You are not in a world/instance.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching current instance: {e}")
        return None

def get_instance_users(cookie, instance_id):
    """Fetch all users in the current instance."""
    headers = {
        "Cookie": f"auth={cookie}",
        "User-Agent": "VRChatAutoInviteScript/1.0"
    }
    try:
        response = requests.get(f"{API_BASE}/instances/{instance_id}", headers=headers)
        response.raise_for_status()
        instance_data = response.json()
        users = instance_data.get("users", [])
        return [user["id"] for user in users]
    except requests.RequestException as e:
        print(f"Error fetching instance users: {e}")
        return []

def invite_user_to_group(cookie, group_id, user_id, progress_file="invite_progress.json"):
    """Send a group invite to a user and track progress."""
    headers = {
        "Cookie": f"auth={cookie}",
        "User-Agent": "VRChatAutoInviteScript/1.0",
        "Content-Type": "application/json"
    }
    data = {"userId": user_id}
    try:
        response = requests.post(f"{API_BASE}/groups/{group_id}/invites", json=data, headers=headers)
        if response.status_code == 200:
            print(f"Successfully invited user {user_id}")
            return True
        else:
            print(f"Failed to invite user {user_id}: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"Error inviting user {user_id}: {e}")
        return False

def load_progress(progress_file="invite_progress.json"):
    """Load progress from file."""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error: The invite progress file is corrupted or invalid.")
            return []
    return []

def save_progress(invited_users, progress_file="invite_progress.json"):
    """Save progress to file."""
    try:
        with open(progress_file, "w") as f:
            json.dump(invited_users, f)
    except Exception as e:
        print(f"Error saving progress: {e}")

def invite_users_to_group():
    """Invite all users in the current instance to the specified group."""
    auth_cookie = get_auth_cookie()
    group_id = get_group_id()
    
    # Load previously invited users to avoid duplicates
    invited_users = load_progress()
    
    # Get current instance
    instance_id = get_current_instance_id(auth_cookie)
    if not instance_id:
        print("Exiting: Could not determine current instance.")
        return
    
    # Get users in the instance
    users = get_instance_users(auth_cookie, instance_id)
    if not users:
        print("No users found in the current instance or an error occurred.")
        return
    
    print(f"Found {len(users)} users in the instance.")
    
    # Invite each user who hasn't been invited yet
    for user_id in users:
        if user_id in invited_users:
            print(f"Skipping user {user_id}: Already invited.")
            continue
        
        success = invite_user_to_group(auth_cookie, group_id, user_id)
        if success:
            invited_users.append(user_id)
            save_progress(invited_users)
        
        # Respect API rate limits
        sleep(1)
    
    print("Invitation process completed.")

def list_invited_users(progress_file="invite_progress.json"):
    """List all users who have been invited to the group."""
    if not os.path.exists(progress_file):
        print("No invite progress file found. No users have been invited yet.")
        return
    
    try:
        with open(progress_file, "r") as f:
            invited_users = json.load(f)
        
        if not invited_users:
            print("No users have been invited yet.")
            return
        
        print("List of invited users (User IDs):")
        for index, user_id in enumerate(invited_users, 1):
            print(f"{index}. {user_id}")
        
        print(f"\nTotal users invited: {len(invited_users)}")
    
    except json.JSONDecodeError:
        print("Error: The invite progress file is corrupted or invalid.")
    except Exception as e:
        print(f"Error reading invite progress file: {e}")

def main():
    """Main menu to choose between inviting users or listing invited users."""
    while True:
        print("\nVRChat Group Invite and List Script")
        print("1. Invite users in current lobby to group")
        print("2. List all invited users")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            invite_users_to_group()
        elif choice == "2":
            list_invited_users()
        elif choice == "3":
            print("Exiting script.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()