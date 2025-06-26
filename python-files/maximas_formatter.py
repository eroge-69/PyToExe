
import tkinter as tk
import pyperclip

def format_job_message(raw_text):
    parts = raw_text.strip().split()
    if len(parts) < 10:
        return "Invalid data. Please copy an entire row from Maximas."

    try:
        slot_time = parts[4]
        wharf = parts[2]
        container = parts[5]
        delivery = " ".join(parts[11:13]).upper() if "DERRIMUT" in parts or "DANDENONG" in parts else "UNKNOWN"

        if slot_time.isdigit():
            hour = int(slot_time)
            suffix = "am" if hour < 12 else "pm"
            hour = hour if hour <= 12 else hour - 12
            slot_time_formatted = f"{hour}{suffix}"
        else:
            slot_time_formatted = slot_time

        formatted = f"""-- NEXT JOB --
Slot Time: {slot_time_formatted}
Wharf: {wharf}
Container: {container}
Delivery: {delivery}"""
        return formatted

    except Exception as e:
        return f"Error parsing row: {str(e)}"

def update_text():
    raw_text = pyperclip.paste()
    result = format_job_message(raw_text)
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, result)

root = tk.Tk()
root.title("Maximas Job Formatter")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label = tk.Label(frame, text="📋 Press Ctrl+C on a Maximas row, then click below to format:")
label.pack()

btn = tk.Button(frame, text="Format Clipboard Text", command=update_text)
btn.pack(pady=5)

text_widget = tk.Text(frame, height=8, width=50)
text_widget.pack()

root.mainloop()
