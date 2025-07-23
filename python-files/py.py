import requests
import time
import json
import os
from colorama import Fore, Back, Style, init

init(autoreset=True)

def fetch_discord_data(token, server_id):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    server_data = {'server_id': server_id, 'categories': [], 'channels': [], 'roles': []}

    try:
        roles_url = f"https://discord.com/api/v9/guilds/{server_id}/roles"
        roles_response = requests.get(roles_url, headers=headers)
        if roles_response.status_code == 200:
            roles = sorted(roles_response.json(), key=lambda r: r['position'], reverse=True)
            for role in roles:
                server_data['roles'].append({
                    'id': role['id'],
                    'name': role['name'],
                    'color': role['color'],
                    'position': role['position'],
                    'permissions': role['permissions'],
                    'hoist': role.get('hoist', False),
                    'mentionable': role.get('mentionable', False)
                })
            print(f"✓ {len(roles)} rôles sauvegardés")
        
        channels_url = f"https://discord.com/api/v9/guilds/{server_id}/channels"
        channels_response = requests.get(channels_url, headers=headers)
        if channels_response.status_code == 200:
            all_channels = channels_response.json()
            
            categories = [channel for channel in all_channels if channel['type'] == 4]
            channels = [channel for channel in all_channels if channel['type'] != 4]
            
            categories = sorted(categories, key=lambda c: c['position'])
            for category in categories:
                server_data['categories'].append({
                    'id': category['id'],
                    'name': category['name'],
                    'position': category['position'],
                    'permission_overwrites': category.get('permission_overwrites', [])
                })
            print(f"{len(categories)} catégories sauvegardées")
            
            for category in server_data['categories']:
                category_channels = [c for c in channels if c.get('parent_id') == category['id']]
                category_channels = sorted(category_channels, key=lambda c: c['position'])
                
                for channel in category_channels:
                    server_data['channels'].append({
                        'id': channel['id'],
                        'name': channel['name'],
                        'type': channel['type'],
                        'position': channel['position'],
                        'parent_id': channel['parent_id'],
                        'topic': channel.get('topic'),
                        'rate_limit_per_user': channel.get('rate_limit_per_user'),
                        'permission_overwrites': channel.get('permission_overwrites', []),
                        'nsfw': channel.get('nsfw', False)
                    })
            
            uncategorized_channels = [c for c in channels if not c.get('parent_id')]
            uncategorized_channels = sorted(uncategorized_channels, key=lambda c: c['position'])
            for channel in uncategorized_channels:
                server_data['channels'].append({
                    'id': channel['id'],
                    'name': channel['name'],
                    'type': channel['type'],
                    'position': channel['position'],
                    'parent_id': None,
                    'topic': channel.get('topic'),
                    'rate_limit_per_user': channel.get('rate_limit_per_user'),
                    'permission_overwrites': channel.get('permission_overwrites', []),
                    'nsfw': channel.get('nsfw', False)
                })
            print(f"{len(channels)} salons sauvegardés")

        filename = f"{server_id}-backup.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(server_data, f, indent=4, ensure_ascii=False)

        print(f"Backup complète sauvegardée: {filename}")
        return True
    except Exception as e:
        print(f"Erreur: {e}")
        return False


def delete_all_channels_and_roles(token, server_id):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    
    try:
        channels_url = f"https://discord.com/api/v9/guilds/{server_id}/channels"
        channels_response = requests.get(channels_url, headers=headers)
        if channels_response.status_code == 200:
            channels = channels_response.json()
            
            non_categories = [channel for channel in channels if channel['type'] != 4]
            print(f"[{Fore.YELLOW}/{Fore.RESET}] Suppression de {len(non_categories)} salons...")
            for channel in non_categories:
                delete_url = f"https://discord.com/api/v9/channels/{channel['id']}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 200:
                    print(f"[{Fore.GREEN}+{Fore.RESET}] Salon {channel['name']} supprimé")
                else:
                    print(f"[{Fore.RED}#{Fore.RESET}] Erreur suppression salon {channel['name']}: {response.status_code}")
                time.sleep(0.5)
            
            categories = [channel for channel in channels if channel['type'] == 4]
            print(f"[{Fore.YELLOW}/{Fore.RESET}] Suppression de {len(categories)} catégories...")
            for category in categories:
                delete_url = f"https://discord.com/api/v9/channels/{category['id']}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 200:
                    print(f"[{Fore.GREEN}+{Fore.RESET}] Catégorie {category['name']} supprimée")
                else:
                    print(f"Erreur suppression catégorie {category['name']}: {response.status_code}")
                time.sleep(0.5)
            
        roles_url = f"https://discord.com/api/v9/guilds/{server_id}/roles"
        roles_response = requests.get(roles_url, headers=headers)
        if roles_response.status_code == 200:
            roles = roles_response.json()
            
            deletable_roles = [role for role in roles if role['name'] != '@everyone']
            print(f"[{Fore.YELLOW}/{Fore.RESET}] Suppression de {len(deletable_roles)} rôles...")
            for role in deletable_roles:
                delete_url = f"https://discord.com/api/v9/guilds/{server_id}/roles/{role['id']}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 204:
                    print(f"[{Fore.GREEN}+{Fore.RESET}] Rôle {role['name']} supprimé")
                else:
                    print(f"[{Fore.RED}#{Fore.RESET}] Erreur suppression rôle {role['name']}: {response.status_code}")
                time.sleep(0.5)
            
        print(f"[{Fore.GREEN}+{Fore.RESET}] Suppression terminée !")
        return True
    except Exception as e:
        print(f"[{Fore.RED}#{Fore.RESET}] Erreur lors de la suppression: {e}")
        return False


def find_everyone_role(token, server_id):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    roles_url = f"https://discord.com/api/v9/guilds/{server_id}/roles"
    
    try:
        response = requests.get(roles_url, headers=headers)
        if response.status_code == 200:
            roles = response.json()
            for role in roles:
                if role['name'] == '@everyone':
                    return role['id']
    except Exception:
        pass
    
    return None


def restore_discord_data(token, server_id, backup_file, include_tickets=True):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    category_id_mapping = {} 
    role_id_mapping = {}    
    
    try:
        delete_all_channels_and_roles(token, server_id)
        
        everyone_role_id = find_everyone_role(token, server_id)
        if everyone_role_id:
            role_id_mapping['everyone'] = everyone_role_id
        
        print("Chargement de la sauvegarde...")
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print("Restauration des rôles avec leurs permissions...")
        for role in backup_data['roles']:
            if role['name'] == '@everyone':
                if everyone_role_id:
                    role_id_mapping[role['id']] = everyone_role_id
                continue
                
            role_data = {
                "name": role['name'],
                "color": role['color'],
                "permissions": role['permissions'],
                "hoist": role.get('hoist', False),
                "mentionable": role.get('mentionable', False)
            }
            response = requests.post(f"https://discord.com/api/v9/guilds/{server_id}/roles", headers=headers, json=role_data)
            if response.status_code in [200, 201]:
                new_role = response.json()
                role_id_mapping[role['id']] = new_role['id']  
                print(f"✓ Rôle {role['name']} créé avec permissions")
            else:
                print(f"[{Fore.RED}#{Fore.RESET}] Erreur création rôle {role['name']}: {response.status_code}")
            time.sleep(0.5)

        for category in backup_data['categories']:
            updated_overwrites = []
            for overwrite in category.get('permission_overwrites', []):
                if overwrite.get('type') == 0 and overwrite.get('id') in role_id_mapping:
                    updated_overwrite = overwrite.copy()
                    updated_overwrite['id'] = role_id_mapping[overwrite['id']]
                    updated_overwrites.append(updated_overwrite)
                elif overwrite.get('id') in role_id_mapping:
                    updated_overwrite = overwrite.copy()
                    updated_overwrite['id'] = role_id_mapping[overwrite['id']]
                    updated_overwrites.append(updated_overwrite)
                else:
                    updated_overwrites.append(overwrite)
            
            category_data = {
                "name": category['name'],
                "type": 4, 
                "permission_overwrites": updated_overwrites
            }
            response = requests.post(f"https://discord.com/api/v9/guilds/{server_id}/channels", headers=headers, json=category_data)
            if response.status_code == 201:
                new_category = response.json()
                category_id_mapping[category['id']] = new_category['id']
                print(f"Catégorie {category['name']} créée avec permissions")
            else:
                print(f"[{Fore.RED}#{Fore.RESET}] Erreur création catégorie {category['name']}: {response.status_code}")
            time.sleep(0.5)
        
        ticket_count = 0
        non_ticket_count = 0
        
        for channel in backup_data['channels']:
            is_ticket_channel = "ticket" in channel['name'].lower()
            
            if (is_ticket_channel and not include_tickets) or (not is_ticket_channel and include_tickets):
                if is_ticket_channel:
                    ticket_count += 1
                continue
                
            parent_id = None
            if channel.get('parent_id'):
                parent_id = category_id_mapping.get(channel['parent_id'])
            
            updated_overwrites = []
            for overwrite in channel.get('permission_overwrites', []):
                if overwrite.get('type') == 0 and overwrite.get('id') in role_id_mapping:
                    updated_overwrite = overwrite.copy()
                    updated_overwrite['id'] = role_id_mapping[overwrite['id']]
                    updated_overwrites.append(updated_overwrite)
                elif overwrite.get('id') in role_id_mapping:
                    updated_overwrite = overwrite.copy()
                    updated_overwrite['id'] = role_id_mapping[overwrite['id']]
                    updated_overwrites.append(updated_overwrite)
                else:
                    updated_overwrites.append(overwrite)
            
            channel_data = {
                "name": channel['name'],
                "type": channel['type'],
                "parent_id": parent_id,
                "topic": channel.get('topic'),
                "rate_limit_per_user": channel.get('rate_limit_per_user'),
                "permission_overwrites": updated_overwrites,
                "nsfw": channel.get('nsfw', False)
            }
            
            response = requests.post(f"https://discord.com/api/v9/guilds/{server_id}/channels", headers=headers, json=channel_data)
            if response.status_code == 201:
                status = "ticket" if is_ticket_channel else "standard"
                print(f"✓ Salon {channel['name']} ({status}) créé avec permissions")
                if is_ticket_channel:
                    ticket_count += 1
                else:
                    non_ticket_count += 1
            else:
                print(f"[{Fore.RED}#{Fore.RESET}] Erreur création salon {channel['name']}: {response.status_code}")
            time.sleep(0.5)

        if include_tickets:
            print(f"[{Fore.GREEN}+{Fore.RESET}] Restauration terminée avec succès! ({ticket_count + non_ticket_count} salons restaurés, dont {ticket_count} tickets)")
        else:
            print(f"[{Fore.GREEN}+{Fore.RESET}] Restauration terminée avec succès! ({non_ticket_count} salons restaurés, {ticket_count} tickets ignorés)")
    except Exception as e:
        print(f"[{Fore.RED}#{Fore.RESET}] Erreur lors de la restauration: {e}")


def main():
    print("[1] Backup\n[2] Load")
    choice = input("Choix: ")
    
    if choice == '1':
        token = input(f"[{Fore.YELLOW}-{Fore.RESET}] Token Discord: ")
        server_id = input("ID du serveur: ")
        fetch_discord_data(token, server_id)
    elif choice == '2':
        token = input("Token Discord: ")
        backup_file = input("Nom du fichier backup: ")
        server_id = input("ID du serveur cible: ")
        
        confirm = input(f"[{Fore.YELLOW}-{Fore.RESET}] Cette action va supprimer TOUS les salons et rôles existants (sauf @everyone)! Confirmer? (O/N): ")
        if confirm.upper() == 'O':
            load_tickets = input("Load tickets ? (O/N): ")
            include_tickets = load_tickets.lower() in ['o', 'oui', 'yes', 'y']
            
            restore_discord_data(token, server_id, backup_file, include_tickets)
        else:
            print("Opération annulée.")
    else:
        print("Aller casse toi")

if __name__ == "__main__":
    main()