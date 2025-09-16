import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import subprocess
import os
import re
import json
import csv
from datetime import datetime

# Global metadata for CSV logging
downloaded_metadata = []

def save_metadata_to_csv():
    if not downloaded_metadata:
        return

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"{current_time}_download_log.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Upload Date", "Uploader", "Title", "URL", "Filename", "Duration", "Views", "Likes", "Comments", "Reposts", "Resolution"])
        writer.writerows(downloaded_metadata)


def download_with_ytdlp_gui(links, download_dir, log_output, use_cookies=False, use_watermark=False):
    def log(msg):
        log_output.insert(tk.END, msg + "\n")
        log_output.see(tk.END)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    failed_log_file = f"{current_time}_failed_downloads_log.txt"
    total_links = len(links)
    successful_downloads = 0
    failed_downloads = 0
    failed_links = []

    for index, link in enumerate(links, start=1):
        try:
            log(f"\n[{index}/{total_links}]: {link}")
            output_template = os.path.join(download_dir, "%(upload_date).10s - %(uploader).50s - %(title).180B.%(ext)s")

            cmd_download = [
                "yt-dlp",
                "--progress",
                "--no-warnings",
                "-o", output_template
            ]
            if use_watermark:
                cmd_download += ["--format", "download"]
            if use_cookies:
                cmd_download += ["--cookies", "cookies.txt"]
            cmd_download.append(link)

            subprocess.run(cmd_download, check=True)

            # Get metadata
            cmd_metadata = ["yt-dlp", "--dump-json"]
            if use_cookies:
                cmd_metadata += ["--cookies", "cookies.txt"]
            cmd_metadata.append(link)
            result = subprocess.run(cmd_metadata, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(result.stderr.strip())

            data = json.loads(result.stdout)
            upload_date = data.get("upload_date", "00000000")
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            downloaded_metadata.append([
                formatted_date,
                data.get("uploader", "unknown"),
                data.get("title", "Untitled"),
                link,
                f"{formatted_date} - {data.get('uploader', 'unknown')} - {data.get('title', 'Untitled')}",
                data.get("duration", ""),
                data.get("view_count", ""),
                data.get("like_count", ""),
                data.get("comment_count", ""),
                data.get("repost_count", ""),
                f"{data.get('height', '')}p" if data.get("height") else "",
            ])
            log("SUCCESS")
            successful_downloads += 1

        except Exception as e:
            log("FAILED")
            failed_downloads += 1
            failed_links.append(link)
            with open(failed_log_file, "a", encoding="utf-8") as f:
                f.write(f"{link}\nError: {str(e)}\n{'-'*40}\n")

    save_metadata_to_csv()
    log(f"\nDownload complete. Success: {successful_downloads}, Failed: {failed_downloads}")
    if failed_links:
        log(f"Check {failed_log_file} for details.")


class TikTokDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Bulk Downloader GUI")

        # Widgets
        tk.Label(root, text="Links (1 per line):").grid(row=0, column=0, sticky="w")
        self.links_text = scrolledtext.ScrolledText(root, width=80, height=10)
        self.links_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        tk.Button(root, text="Load from File", command=self.load_links_from_file).grid(row=2, column=0, sticky="w", padx=10)

        self.cookies_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Use Cookies", variable=self.cookies_var).grid(row=2, column=1, sticky="w")

        self.watermark_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Use Watermark Format", variable=self.watermark_var).grid(row=2, column=2, sticky="w")

        tk.Label(root, text="Download Directory:").grid(row=3, column=0, sticky="w", padx=10)
        self.download_dir_entry = tk.Entry(root, width=60)
        self.download_dir_entry.grid(row=3, column=1, columnspan=2, pady=5, sticky="w")
        tk.Button(root, text="Browse", command=self.choose_directory).grid(row=3, column=2, sticky="e", padx=10)

        tk.Button(root, text="Start Download", command=self.start_download).grid(row=4, column=0, columnspan=3, pady=10)

        self.log_output = scrolledtext.ScrolledText(root, width=100, height=20, bg="black", fg="lime")
        self.log_output.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_dir_entry.delete(0, tk.END)
            self.download_dir_entry.insert(0, directory)

    def load_links_from_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    cleaned_links = [line.replace("Link: ", "").strip() for line in lines if line.strip() and not line.startswith("Date:")]
                    self.links_text.insert(tk.END, "\n".join(cleaned_links))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def start_download(self):
        links = self.links_text.get("1.0", tk.END).strip().splitlines()
        links = [l for l in links if re.match(r'https?://', l)]
        download_dir = self.download_dir_entry.get().strip()
        use_cookies = self.cookies_var.get()
        use_watermark = self.watermark_var.get()

        if not links:
            messagebox.showwarning("Input Error", "No valid links found.")
            return
        if not download_dir:
            messagebox.showwarning("Input Error", "Please select a download directory.")
            return

        # Clear previous logs
        self.log_output.delete("1.0", tk.END)

        # Start download in a new thread to prevent GUI freezing
        threading.Thread(
            target=download_with_ytdlp_gui,
            args=(links, download_dir, self.log_output, use_cookies, use_watermark),
            daemon=True
        ).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokDownloaderGUI(root)
    root.mainloop()
