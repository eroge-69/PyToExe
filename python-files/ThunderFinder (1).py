import cv2
import numpy as np
import time
import sounddevice as sd

def detect_flash(camera_index=0, threshold=50, mic_threshold=0.1):
    cap = cv2.VideoCapture(camera_index)
    prev_brightness = None
    detection = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_brightness = np.mean(gray)

        if prev_brightness is not None:
            if curr_brightness - prev_brightness > threshold and not detection:
                print("Flash detected! Listening for thunder...")
                detection = True
                listen_for_thunder(threshold=mic_threshold)  # Pass sensitivity

        prev_brightness = curr_brightness

        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def listen_for_thunder(threshold=0.0, duration=15):
    print("Detecting thunder...")
    start_time = time.time()
    timer_running = True

    def callback(indata, frames, time_info, status):
        nonlocal timer_running, start_time
        volume_norm = np.linalg.norm(indata)
        print(f"Mic volume: {volume_norm}")  # Show live mic volume for calibration
        if timer_running and volume_norm > threshold:
            elapsed_ms = int((time.time() - start_time) * 1000)
            print(f"Thunder heard! Time elapsed: {elapsed_ms} ms")
            timer_running = False
            print(elapsed_ms)
            print("Now calculating distance...")
            # Calculating distance
            distance = (343 * (elapsed_ms / 1000))
            print()
            print()
            print()
            print("Distance in km:", distance / 1000)
            print("Distance in miles:", distance / 1609.34)
            print("Distance in feet:", distance / 0.3048)
            print("Distance in meters:", distance)
            print("Distance in yards:", distance / 0.9144)
            if elapsed_ms < 1500: print("Seek shelter immediately! It's very close! and not safe to be outside!")
            if elapsed_ms >= 1500 and elapsed_ms < 2500: print("It's very close, you shall not be outside!")
            if elapsed_ms >= 2500 and elapsed_ms < 3500: print("It's close, you should get inside fast!")
            if elapsed_ms >= 3500 and elapsed_ms < 4500: print("It's getting closer, you should just get inside.")
            if elapsed_ms >= 4500 and elapsed_ms < 6000: print("You should get inside soon, don't stay in large open areas!")
            if elapsed_ms >= 6000 and elapsed_ms < 9000: print("Get off large open areas, you should go somewhere dry and safe!")
            if elapsed_ms >= 9000 and elapsed_ms < 14000: print("Get inside if you want, but it's safe for now, slowly get of large open areas.")
            if elapsed_ms >= 14000 and elapsed_ms < 19000: print("It's okay to be outside, but keep checking if it gets closer")
            if elapsed_ms >= 19000: print("You're fine, but keep checking if it gets closer")
            print("Thunder detection complete.")
            print("Press 'q' to quit, 'i' for auto-restart mode, or 'r' to restart,")
            user_choice = input("Enter your choice: ").lower()
            if user_choice == 'q':
                exit()
            elif user_choice == 'i':
                print("Auto-restart mode enabled.")
                timer_running = True
                start_time = time.time()
            elif user_choice == 'r':
                print("Restarting detection...")
                timer_running = True
                start_time = time.time()
    with sd.InputStream(callback=callback, channels=1):
        while timer_running and (time.time() - start_time) < duration:
            sd.sleep(100)

if __name__ == "__main__":
    try:
        mic_threshold = float(input("Enter microphone sensitivity threshold (suggest 20-25 but feel free to test): "))
        print("Note that this detection can vary based on your environment and microphone quality. Adjust the threshold as needed. I am not responsible for any damage or injury because of this program. Use at your own risk.")
        print("If it doesn't false trigger, this program can be pretty accurate, but if it does, you can adjust the threshold.")
    except ValueError:
        mic_threshold = 22.5 # Default value if input is invalid
    detect_flash(mic_threshold=mic_threshold)  # Change this value to adjust sensitivity
