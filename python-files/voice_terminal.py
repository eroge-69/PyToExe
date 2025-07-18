
import pyttsx3

def process_command(command):
    pitch = 1.0
    rate = 150
    gender = None
    msg_text = command

    if "-p" in command:
        try:
            pitch_val = int(command.split("-p")[1].split()[0])
            pitch = pitch_val / 100
        except:
            pass
        msg_text = msg_text.replace(f"-p {pitch_val}", "").strip()

    if "-r" in command:
        try:
            rate_val = int(command.split("-r")[1].split()[0])
            rate = rate_val
        except:
            pass
        msg_text = msg_text.replace(f"-r {rate_val}", "").strip()

    if "-m" in command:
        gender = "male"
        msg_text = msg_text.replace("-m", "").strip()
    elif "-w" in command:
        gender = "female"
        msg_text = msg_text.replace("-w", "").strip()

    engine = pyttsx3.init()
    engine.setProperty('rate', rate)

    voices = engine.getProperty('voices')
    if gender == "male":
        voice = next((v for v in voices if 'male' in v.name.lower()), voices[0])
    elif gender == "female":
        voice = next((v for v in voices if 'female' in v.name.lower()), voices[0])
    else:
        voice = voices[0]

    engine.setProperty('voice', voice.id)
    engine.say(msg_text)
    engine.runAndWait()

print("🔊 Voice Terminal (Python App)")
print("พิมพ์ข้อความแล้ว Enter เพื่อให้พูด (พิมพ์ 'exit' เพื่อออก)")
print("คำสั่งเสริม: -p <pitch> -r <rate> -m (ชาย) -w (หญิง)")

while True:
    user_input = input("> ").strip()
    if user_input.lower() == "exit":
        print("👋 ออกแอปแล้ว")
        break
    if user_input:
        process_command(user_input)
