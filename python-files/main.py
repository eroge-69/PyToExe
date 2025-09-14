import os
import subprocess
import sys
import ctypes

# 메시지 박스 함수 (Windows API)
def msgbox(text, title="알림", style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

def inputbox(prompt, title="입력", default=""):
    # 간단히 콘솔 입력으로 대체
    print(f"{prompt}")
    value = input(f"[{title}] 기본값({default}): ")
    return value if value.strip() else default

def main():
    fso_file = "./FACEDAT.R3"

    # 1. FACEDAT.R3 확인
    if not os.path.exists(fso_file):
        msgbox("FACEDAT.R3 파일이 없습니다.", "에러", 64)
        sys.exit(0)

    # 2. 실행 여부 확인
    if msgbox("실행하시겠습니까?", "확인", 292) == 7:  # 7 = No
        sys.exit(0)

    # 3. 입력값 받기
    n = inputbox("\n\n\n\n\n얼굴을 적용할 번호를 입력하세요 (1~240)", "영걸전 얼굴 적용", "1")

    try:
        num = int(n)
    except ValueError:
        sys.exit(0)

    if not (1 <= num <= 240):
        msgbox("잘못된 번호입니다.", "에러", 64)
        sys.exit(0)

    # 4. Stack.txt에 저장
    os.makedirs("Body", exist_ok=True)
    with open("Body/Stack.txt", "w", encoding="utf-8") as f:
        f.write(str(num))

    # 5. 외부 실행
    try:
        subprocess.run(["taskkill", "/f", "/im", "RPGViewer.exe"], check=False)

        # Call0.bat 관리자 실행
        subprocess.run(["powershell", "Start-Process", "Body\\Call0.bat", "-Verb", "runAs"], shell=True)

        subprocess.run(["cmd", "/c", "Body\\Call1.bat"], check=False)
        subprocess.run(["powershell", "Body\\Schedule.ps1"], check=True)
        subprocess.run(["powershell", "Body\\Write-FACEDAT.ps1"], check=True)
        subprocess.run(["cmd", "/c", "Body\\Call2.bat"], check=False)

        msgbox("FACEDAT.R3 적용 완료!", "완료", 64)
    except Exception as e:
        msgbox(f"실행 중 오류 발생: {e}", "에러", 64)

if __name__ == "__main__":
    main()
