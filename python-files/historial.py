import os
import sqlite3
import shutil

def get_edge_profiles(user_profile_path):
    base_path = os.path.join(user_profile_path, r'AppData\Local\Microsoft\Edge\User Data')
    profiles = []
    if os.path.exists(base_path):
        for entry in os.listdir(base_path):
            full_path = os.path.join(base_path, entry)
            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, 'History')):
                profiles.append(entry)
    return profiles

def extract_history(profile_name, profile_path):
    print(f"🔍 Extrayendo historial del perfil: {profile_name}")
    history_file = os.path.join(profile_path, 'History')
    temp_copy = f'temp_History_{profile_name}.db'

    try:
        shutil.copy2(history_file, temp_copy)
        conn = sqlite3.connect(temp_copy)
        cursor = conn.cursor()

        query = """
        SELECT url, title, datetime((last_visit_time/1000000)-11644473600, 'unixepoch') as last_visit
        FROM urls
        ORDER BY last_visit_time DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()

        output_file = f'Historial_Edge_{profile_name}.txt'
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f'Historial de Navegación - Perfil: {profile_name}\n\n')
            for url, title, visit_time in results:
                file.write(f'[{visit_time}] {title}\n{url}\n\n')

        print(f"✅ Historial exportado a '{output_file}'")
        conn.close()
    except Exception as e:
        print(f"❌ Error procesando {profile_name}: {e}")
    finally:
        if os.path.exists(temp_copy):
            os.remove(temp_copy)

def main():
    user_profile = os.environ['USERPROFILE']
    edge_profiles_base = os.path.join(user_profile, r'AppData\Local\Microsoft\Edge\User Data')
    profiles = get_edge_profiles(user_profile)

    if not profiles:
        print("⚠️ No se encontraron perfiles de Edge con historial.")
        return

    for profile in profiles:
        profile_path = os.path.join(edge_profiles_base, profile)
        extract_history(profile, profile_path)

if __name__ == '__main__':
    main()
