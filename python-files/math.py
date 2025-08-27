import pynput
import time
import json
import threading
import os # os 모듈을 임포트합니다.

# 전역 변수 설정
is_recording = False  # 현재 트래킹 중인지 여부
recorded_events = []  # 기록된 이벤트를 저장할 리스트
current_pressed_keys = set() # 현재 눌려 있는 키들을 추적 (조합 키 감지에 사용)

# --- 파일 저장 경로 설정 변경 부분 ---
# os.path.expanduser('~')는 현재 사용자의 홈 디렉토리 경로를 반환합니다.
# Windows의 경우 C:\Users\YourUserName 형태가 됩니다.
user_home_dir = os.path.expanduser('~')

# 데스크톱 경로를 구성합니다. (운영체제에 따라 'Desktop' 또는 'desktop'일 수 있으나, 일반적으로 대소문자 무관하게 인식됩니다.)
desktop_path = os.path.join(user_home_dir, 'Desktop')

# 최종적으로 파일이 저장될 'secret' 폴더의 전체 경로를 구성합니다.
output_directory = os.path.join(desktop_path, 'secret')

# 로그 파일의 최종 전체 경로를 구성합니다.
output_filename = os.path.join(output_directory, "keyboard_log.json")
# ------------------------------------

def on_press(key):
    """키가 눌렸을 때 호출되는 함수"""
    global is_recording, recorded_events

    try:
        # 현재 눌린 키 집합에 추가
        current_pressed_keys.add(key)

        # 시작 조합 (Shift + A + 1) 감지
        # Shift (왼쪽 또는 오른쪽), 'a', '1'이 모두 눌렸는지 확인
        is_shift_down = pynput.keyboard.Key.shift_l in current_pressed_keys or \
                        pynput.keyboard.Key.shift_r in current_pressed_keys
        is_a_down = pynput.keyboard.KeyCode.from_char('a') in current_pressed_keys
        is_1_down = pynput.keyboard.KeyCode.from_char('1') in current_pressed_keys

        if is_shift_down and is_a_down and is_1_down and not is_recording:
            is_recording = True
            print("\n[시스템 메시지] 키보드 트래킹을 시작합니다. (Shift + A + 1 감지)")
            recorded_events.append({"timestamp": time.time(), "event_type": "START_RECORDING"})
            return # 시작 이벤트를 기록했으므로 다른 키 이벤트 기록은 건너뜀

        # 종료 조합 (Shift + A + 2) 감지
        # Shift (왼쪽 또는 오른쪽), 'a', '2'이 모두 눌렸는지 확인
        is_2_down = pynput.keyboard.KeyCode.from_char('2') in current_pressed_keys
        if is_shift_down and is_a_down and is_2_down and is_recording:
            is_recording = False
            print("\n[시스템 메시지] 키보드 트래킹을 종료합니다. (Shift + A + 2 감지)")
            recorded_events.append({"timestamp": time.time(), "event_type": "STOP_RECORDING"})
            
            # 기록 종료 시 파일에 저장하고 리스너 정지
            save_events_to_file()
            return False # on_press에서 False를 반환하면 리스너가 중지됩니다.

    except AttributeError:
        # 특수 키 (Shift, Ctrl, Alt 등)는 .char 속성이 없습니다.
        key_value = str(key)
    else:
        # 일반 키는 .char 속성이 있습니다.
        key_value = key.char if key.char is not None else str(key)

    if is_recording:
        # 트래킹 중일 때만 키 이벤트 기록
        recorded_events.append({
            "timestamp": time.time(),
            "event_type": "press",
            "key": key_value
        })
        # 기록 중일 때도 사용자에게 피드백 제공 (옵션)
        # print(f"눌림: {key_value}")


def on_release(key):
    """키가 해제되었을 때 호출되는 함수"""
    global is_recording, recorded_events

    try:
        # 현재 눌린 키 집합에서 제거
        if key in current_pressed_keys:
            current_pressed_keys.remove(key)

        try:
            # 특수 키 (Shift, Ctrl, Alt 등)는 .char 속성이 없습니다.
            key_value = str(key)
        except AttributeError:
            # 일반 키는 .char 속성이 있습니다.
            key_value = key.char if key.char is not None else str(key)

        if is_recording:
            # 트래킹 중일 때만 키 이벤트 기록
            recorded_events.append({
                "timestamp": time.time(),
                "event_type": "release",
                "key": key_value
            })
            # 기록 중일 때도 사용자에게 피드백 제공 (옵션)
            # print(f"떼어짐: {key_value}")

    except AttributeError:
        # 특수 키는 .char 속성이 없을 수 있으므로 예외 처리
        pass # 현재 눌린 키 목록 업데이트만 진행


def save_events_to_file():
    """기록된 이벤트를 JSON 파일로 저장하는 함수"""
    global recorded_events

    # 파일이 저장될 디렉토리(폴더)가 없으면 생성합니다.
    # exist_ok=True 옵션은 이미 디렉토리가 존재해도 에러를 발생시키지 않도록 합니다.
    try:
        os.makedirs(output_directory, exist_ok=True)
    except Exception as e:
        print(f"[시스템 메시지] 디렉토리 생성 중 오류 발생: {e}")
        return # 디렉토리 생성 실패 시 파일 저장 시도하지 않음

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(recorded_events, f, indent=4, ensure_ascii=False)
        print(f"[시스템 메시지] 기록된 키 이벤트가 '{output_filename}' 파일에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"[시스템 메시지] 파일 저장 중 오류 발생: {e}")

# 메인 실행 부분
def start_listener():
    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("키보드 트래킹 대기 중...")
        print("시작: Shift + A + 1")
        print("종료: Shift + A + 2 (자동으로 파일 저장 후 프로그램 종료)")
        listener.join() # 리스너가 종료될 때까지 대기

if __name__ == "__main__":
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.daemon = True # 메인 스레드 종료 시 함께 종료되도록 설정
    listener_thread.start()

    try:
        while True:
            time.sleep(1) # 메인 스레드가 바로 종료되지 않도록 잠시 대기
    except KeyboardInterrupt:
        print("\n[시스템 메시지] 사용자에 의해 프로그램이 강제 종료됩니다.")
        # 강제 종료 시에도 지금까지 기록된 내용을 저장하고 싶다면 아래 주석을 해제하세요.
        # save_events_to_file()
