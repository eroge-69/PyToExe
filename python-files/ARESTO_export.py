import requests
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


# === CORE FUNCTIONS ===

def get_session_key(api_url, api_key):
    response = requests.post(api_url, json={
        "method": "get_session_key",
        "params": [api_key],
        "id": 1
    }).json()
    if response.get('result'):
        return response['result']
    else:
        raise Exception("Could not get session key: " + str(response.get('error')))


def get_text_question_codes(api_url, session_key, survey_id):
    response = requests.post(api_url, json={
        "method": "list_questions",
        "params": [session_key, survey_id, 1],
        "id": 2
    }).json()

    questions = response['result']
    text_types = {'T', 'S', 'U', 'Q'}
    return [q['title'] for q in questions if q['type'] in text_types]


def export_responses(api_url, session_key, survey_id):
    response = requests.post(api_url, json={
        "method": "export_responses",
        "params": [
            session_key,
            survey_id,
            "json",
            "en",
            "code",
            "complete",
            "all"
        ],
        "id": 3
    }).json()

    return response['result']


def save_text_responses_to_excel(text_codes, responses_json):
    df = pd.read_json(responses_json)
    df_text = df[text_codes]
    output_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save filtered responses as..."
    )
    if output_path:
        df_text.to_excel(output_path, index=False)
        return output_path
    else:
        raise Exception("Export cancelled")


# === GUI ===

def export_text_responses():
    api_url = url_entry.get()
    api_key = key_entry.get()
    try:
        survey_id = int(id_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Survey ID must be a number.")
        return

    try:
        status_label.config(text="Getting session key...")
        root.update()
        session_key = get_session_key(api_url, api_key)

        status_label.config(text="Fetching questions...")
        root.update()
        text_qcodes = get_text_question_codes(api_url, session_key, survey_id)

        status_label.config(text="Downloading responses...")
        root.update()
        responses = export_responses(api_url, session_key, survey_id)

        status_label.config(text="Saving to Excel...")
        root.update()
        filepath = save_text_responses_to_excel(text_qcodes, responses)

        status_label.config(text=f"✅ Exported: {filepath}")
        messagebox.showinfo("Success", f"Text responses saved:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="❌ Error occurred")


# === TKINTER SETUP ===

root = tk.Tk()
root.title("Aresto Text Response Exporter")
root.geometry("480x300")

tk.Label(root, text="Aresto RemoteControl2 API URL:").pack(pady=(10, 0))
url_entry = tk.Entry(root, width=60)
url_entry.pack()

tk.Label(root, text="API Key:").pack(pady=(10, 0))
key_entry = tk.Entry(root, width=60, show="*")
key_entry.pack()

tk.Label(root, text="Survey ID:").pack(pady=(10, 0))
id_entry = tk.Entry(root, width=20)
id_entry.pack()

tk.Button(root, text="Export Text Responses", command=export_text_responses, bg="#14AE5C", fg="white").pack(pady=20)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
