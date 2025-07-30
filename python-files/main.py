
import tkinter as tk
from tkinter import ttk
import requests
import json
from pynput import keyboard
import threading
import time

try:
    import win32clipboard
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("win32clipboard not available. Clipboard functionality will be limited.")

# Global variable to store API configuration
API_CONFIG = {
    "url": "",
    "headers": {"Content-Type": "application/json"},
    "body_template": "{\"text\": \"%s\", \"source_lang\": \"%s\", \"target_lang\": \"%s\"}"
}

def get_clipboard_text():
    if WIN32_AVAILABLE:
        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return text
        except Exception as e:
            print(f"Error getting clipboard text: {e}")
            return ""
    else:
        # Fallback for non-Windows or if win32clipboard is not installed
        # This is a very basic fallback and might not work universally
        return ""

def set_clipboard_text(text):
    if WIN32_AVAILABLE:
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error setting clipboard text: {e}")
    else:
        print("Cannot set clipboard text: win32clipboard not available.")

def translate_text(text, source_lang, target_lang):
    """Function to call the translation API using configured settings."""
    url = API_CONFIG["url"]
    headers = API_CONFIG["headers"]
    body_template = API_CONFIG["body_template"]

    if not url:
        return "Error: Translation API URL is not configured."

    try:
        # Format the body using the template
        # Assuming %s placeholders for text, source_lang, target_lang
        body = body_template % (text, source_lang, target_lang)
        payload = json.loads(body)

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("translated_text", "Error: No translated text found.")
    except requests.exceptions.RequestException as e:
        return f"Error calling translation API: {e}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON body template or API response."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

class TranslatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Simple Translator")

        # Create tabs for Translator and Settings
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.translator_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.translator_frame, text="Dịch")
        self.notebook.add(self.settings_frame, text="Cài đặt API")

        self._setup_translator_tab()
        self._setup_settings_tab()

        # Hotkey setup
        self.hotkey_listener = None
        self.start_hotkey_listener()

    def _setup_translator_tab(self):
        # Input Text
        self.input_label = tk.Label(self.translator_frame, text="Văn bản gốc:")
        self.input_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_text = tk.Text(self.translator_frame, height=10, width=50)
        self.input_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Language Selection
        self.lang_frame = ttk.Frame(self.translator_frame)
        self.lang_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.source_lang_label = tk.Label(self.lang_frame, text="Từ:")
        self.source_lang_label.pack(side="left", padx=5)
        self.source_lang_combo = ttk.Combobox(self.lang_frame, values=self.get_supported_languages())
        self.source_lang_combo.set("en") # Default source language
        self.source_lang_combo.pack(side="left", padx=5)

        self.target_lang_label = tk.Label(self.lang_frame, text="Sang:")
        self.target_lang_label.pack(side="left", padx=5)
        self.target_lang_combo = ttk.Combobox(self.lang_frame, values=self.get_supported_languages())
        self.target_lang_combo.set("vi") # Default target language
        self.target_lang_combo.pack(side="left", padx=5)

        # Translate Button
        self.translate_button = tk.Button(self.translator_frame, text="Dịch", command=self.perform_translation)
        self.translate_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Output Text
        self.output_label = tk.Label(self.translator_frame, text="Văn bản đã dịch:")
        self.output_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.output_text = tk.Text(self.translator_frame, height=10, width=50)
        self.output_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED) # Make output text read-only

    def _setup_settings_tab(self):
        # API URL
        self.api_url_label = tk.Label(self.settings_frame, text="API URL:")
        self.api_url_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_url_entry = tk.Entry(self.settings_frame, width=60)
        self.api_url_entry.grid(row=0, column=1, padx=5, pady=5)
        self.api_url_entry.insert(0, API_CONFIG["url"])

        # Headers (as JSON string)
        self.headers_label = tk.Label(self.settings_frame, text="Headers (JSON):")
        self.headers_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.headers_entry = tk.Entry(self.settings_frame, width=60)
        self.headers_entry.grid(row=1, column=1, padx=5, pady=5)
        self.headers_entry.insert(0, json.dumps(API_CONFIG["headers"]))

        # Body Template (with %s placeholders)
        self.body_template_label = tk.Label(self.settings_frame, text="Body Template (JSON with %s for text, src_lang, tgt_lang):")
        self.body_template_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.body_template_entry = tk.Entry(self.settings_frame, width=60)
        self.body_template_entry.grid(row=2, column=1, padx=5, pady=5)
        self.body_template_entry.insert(0, API_CONFIG["body_template"])

        # Save Button
        self.save_settings_button = tk.Button(self.settings_frame, text="Lưu cài đặt API", command=self.save_api_settings)
        self.save_settings_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.settings_status_label = tk.Label(self.settings_frame, text="", fg="green")
        self.settings_status_label.grid(row=4, column=0, columnspan=2, pady=5)

    def save_api_settings(self):
        global API_CONFIG
        try:
            API_CONFIG["url"] = self.api_url_entry.get()
            API_CONFIG["headers"] = json.loads(self.headers_entry.get())
            API_CONFIG["body_template"] = self.body_template_entry.get()
            self.settings_status_label.config(text="Cài đặt API đã được lưu thành công!", fg="green")
        except json.JSONDecodeError:
            self.settings_status_label.config(text="Lỗi: Headers hoặc Body Template không phải JSON hợp lệ.", fg="red")
        except Exception as e:
            self.settings_status_label.config(text=f"Lỗi khi lưu cài đặt: {e}", fg="red")

    def get_supported_languages(self):
        # In a real application, this would fetch supported languages from the API
        # For now, a hardcoded list
        return ["en", "vi", "fr", "es", "de", "ja", "ko", "zh"]

    def perform_translation(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        source_lang = self.source_lang_combo.get()
        target_lang = self.target_lang_combo.get()

        if not input_text:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "Vui lòng nhập văn bản để dịch.")
            self.output_text.config(state=tk.DISABLED)
            return

        translated_text = translate_text(input_text, source_lang, target_lang)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, translated_text)
        self.output_text.config(state=tk.DISABLED)

    def on_hotkey_pressed(self):
        print("Hotkey pressed!")
        # Get text from clipboard
        text_to_translate = get_clipboard_text()
        if text_to_translate:
            # Perform translation
            source_lang = self.source_lang_combo.get()
            target_lang = self.target_lang_combo.get()
            translated_text = translate_text(text_to_translate, source_lang, target_lang)

            # Display translated text in a temporary pop-up window
            self.show_popup_translation(translated_text)
        else:
            self.show_popup_translation("Không có văn bản trong clipboard để dịch.")

    def show_popup_translation(self, text):
        popup = tk.Toplevel(self.master)
        popup.title("Dịch nhanh")
        popup.geometry("+%d+%d" % (self.master.winfo_x() + 50, self.master.winfo_y() + 50))

        message = tk.Message(popup, text=text, width=300)
        message.pack(padx=10, pady=10)

        close_button = tk.Button(popup, text="Đóng", command=popup.destroy)
        close_button.pack(pady=5)

        # Automatically close after a few seconds
        popup.after(5000, popup.destroy)

    def start_hotkey_listener(self):
        # Define the hotkey combination (e.g., Ctrl + Alt + T)
        hotkey_combination = "<ctrl>+<alt>+t"

        def on_activate():
            # Run the hotkey action in the main thread to avoid Tkinter issues
            self.master.after(0, self.on_hotkey_pressed)

        self.hotkey_listener = keyboard.GlobalHotKeys({
            hotkey_combination: on_activate
        })
        self.hotkey_listener.start()

    def stop_hotkey_listener(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_hotkey_listener(), root.destroy()))
    root.mainloop()


