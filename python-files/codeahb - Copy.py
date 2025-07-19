import cv2
import os

def play_birthday_video():
    video_path = "aadhvik_ai_birthday.mp4"
    if not os.path.exists(video_path):
        print("Video not found!")
        return

    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("🎂 wishing Aadhvik", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Main trigger
user_input = input("Enter your message: ").lower()
if "wish" in user_input and "aadhvik" in user_input:
    play_birthday_video()
else:
    print("No matching trigger found.")
