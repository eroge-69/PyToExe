import os
import requests

def make_minecraft_bucket_server(server_dir='minecraft_server'):
    # 1. 폴더 만들기
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)

    # 2. PaperMC 최신 빌드 정보 가져오기
    paper_api = "https://papermc.io/api/v2/projects/paper"
    project_info = requests.get(paper_api).json()
    latest_version = project_info['versions'][-1]
    build_info = requests.get(f"{paper_api}/versions/{latest_version}/builds").json()
    latest_build = build_info['builds'][-1]['build']

    # 3. PaperMC 서버 jar 다운로드 URL
    jar_url = f"https://papermc.io/api/v2/projects/paper/versions/{latest_version}/builds/{latest_build}/downloads/paper-{latest_version}-{latest_build}.jar"
    jar_path = os.path.join(server_dir, "server.jar")

    print(f"Downloading PaperMC server jar for version {latest_version} build {latest_build}...")
    r = requests.get(jar_url)
    with open(jar_path, "wb") as f:
        f.write(r.content)
    print("Download complete.")

    # 4. eula.txt 생성 (동의)
    with open(os.path.join(server_dir, "eula.txt"), "w") as f:
        f.write("eula=true\n")

    # 5. start.sh 생성 (리눅스/mac용)
    start_sh = f"""#!/bin/bash
java -Xms1G -Xmx2G -jar server.jar nogui
"""
    with open(os.path.join(server_dir, "start.sh"), "w") as f:
        f.write(start_sh)
    os.chmod(os.path.join(server_dir, "start.sh"), 0o755)

    # 6. start.bat 생성 (윈도우용)
    start_bat = """@echo off
java -Xms1G -Xmx2G -jar server.jar nogui
pause
"""
    with open(os.path.join(server_dir, "start.bat"), "w") as f:
        f.write(start_bat)

    print(f"Minecraft server setup completed in folder: {server_dir}")

if __name__ == "__main__":
    make_minecraft_bucket_server()
