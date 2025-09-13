import json

def load_data():
    with open("qa_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def bot():
    print("🤖 Laptop Guider Bot میں خوش آمدید!")
    print("بچے سوال پوچھ سکتے ہیں (Math, English, Urdu, Science یا Laptop سے متعلق).")
    print("بند کرنے کے لئے 'exit' لکھیں۔\n")

    data = load_data()

    while True:
        q = input("آپ کا سوال: ").strip().lower()
        if q == "exit":
            print("اللہ حافظ 👋")
            break

        # Check if exact question exists
        if q in data:
            print("جواب:", data[q])
        else:
            # Try partial match
            found = False
            for key in data:
                if key in q:
                    print("جواب:", data[key])
                    found = True
                    break
            if not found:
                print("معاف کیجئے، اس سوال کا جواب میرے پاس نہیں ہے۔")

if __name__ == "__main__":
    bot()
