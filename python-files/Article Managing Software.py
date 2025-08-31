import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import os
import platform
import subprocess
import tempfile

class ArticleManagerApp:
    def __init__(self, root):
        self.root = root
        root.title("Article Counting Software")
        root.geometry("950x650")
        root.configure(bg='lightblue')

        self.df = None
        self.corrected_df = None

        left_frame = tk.Frame(root, bg='lightblue')
        left_frame.pack(side='left', fill='y', padx=15, pady=10)

        self.btn_load_orig = tk.Button(left_frame, text="Upload Original CSV", width=25, command=self.load_csv)
        self.btn_load_orig.pack(pady=5)

        self.req_fields_label = tk.Label(left_frame,
                                         text="Original CSV Must Contain Only:\nARTICLE NUMBER\nARTICLE TYPE\nINSURED FLAG\nUSER ID",
                                         bg='lightblue', justify='left', fg='darkblue', font=('Arial', 10, 'bold'))
        self.req_fields_label.pack(pady=(0, 15))

        self.btn_delete_dups = tk.Button(left_frame, text="Delete Duplicate Articles", width=25,
                                        command=self.delete_duplicates_and_save, state='disabled')
        self.btn_delete_dups.pack(pady=5)

        self.btn_load_corrected = tk.Button(left_frame, text="Upload Corrected CSV", width=25,
                                            command=self.load_corrected_csv, state='disabled')
        self.btn_load_corrected.pack(pady=5)

        self.btn_article_types = tk.Button(left_frame, text="Show Article Types Count", width=25,
                                          command=self.show_article_types, state='disabled')
        self.btn_article_types.pack(pady=5)

        self.btn_user_count = tk.Button(left_frame, text="Show User Article Counts", width=25,
                                        command=self.show_articles_by_user, state='disabled')
        self.btn_user_count.pack(pady=5)

        self.btn_print_output = tk.Button(left_frame, text="Print Output", width=25,
                                          command=self.print_output, state='disabled')
        self.btn_print_output.pack(pady=20)

        tk.Button(left_frame, text="Exit", width=25, command=root.quit).pack(pady=20)

        self.text = scrolledtext.ScrolledText(root, wrap='none')
        self.text.pack(side='right', fill='both', expand=True, padx=10, pady=10)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        df = pd.read_csv(path)
        cols = [c.strip().upper() for c in df.columns]
        required_cols = ['ARTICLE NUMBER', 'ARTICLE TYPE', 'INSURED FLAG', 'USER ID']
        disallowed_cols = ['BAG NUMBER', 'DESTN OFFICE PIN', 'BOOKING OFFICE NAME', 'OFFICE NAME', 'BOOKING REFERENCE ID']
        extra_cols = [c for c in cols if (c not in required_cols) and (c not in disallowed_cols)]
        disallowed_present = [c for c in cols if c in disallowed_cols]
        missing_cols = [c for c in required_cols if c not in cols]

        warning_msgs = []
        if missing_cols:
            warning_msgs.append("Missing columns: " + ", ".join(missing_cols))
        if extra_cols:
            warning_msgs.append("Unexpected extra columns: " + ", ".join(extra_cols))
        if disallowed_present:
            warning_msgs.append("Remove these unwanted columns if present: " + ", ".join(disallowed_present))

        if warning_msgs:
            full_msg = "Warning: Original CSV file should contain only these columns:\n" \
                       "ARTICLE NUMBER\nARTICLE TYPE\nINSURED FLAG\nUSER ID\n\n" + "\n".join(warning_msgs)
            messagebox.showwarning("Column Warning", full_msg)

        self.df = df
        self.df.columns = df.columns.str.strip()
        self.text_clear()
        self.text_insert(f"Loaded original CSV:\n{path}\nColumns: {', '.join(self.df.columns)}\n")
        self.btn_delete_dups.config(state='normal')
        self.btn_load_corrected.config(state='disabled')
        self.btn_article_types.config(state='disabled')
        self.btn_user_count.config(state='disabled')
        self.btn_print_output.config(state='disabled')

    def delete_duplicates_and_save(self):
        if self.df is None:
            messagebox.showerror("Error", "Please upload the original CSV file first.")
            return

        duplicates = self.df[self.df.duplicated(subset=['Article Number'], keep='first')]
        total_duplicates = len(duplicates)

        self.text_clear()
        self.text_insert(f"Total duplicate articles found: {total_duplicates}\n\n")

        self.corrected_df = self.df.drop_duplicates(subset=['Article Number'], keep='first')

        app_folder = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(app_folder, "CORRECTED_CSV_FILE.csv")

        try:
            self.corrected_df.to_csv(save_path, index=False)
            self.text_insert(f"Corrected CSV automatically saved as:\n{save_path}\n")
        except Exception as e:
            self.text_insert(f"Failed to save corrected file automatically: {e}\n")

        self.text_insert(f"Deleted {len(self.df) - len(self.corrected_df)} duplicate articles.\n")

        self.btn_load_corrected.config(state='normal')
        self.btn_article_types.config(state='disabled')
        self.btn_user_count.config(state='disabled')
        self.btn_print_output.config(state='disabled')

    def load_corrected_csv(self):
        path = filedialog.askopenfilename(title="Select Corrected CSV File", filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        self.corrected_df = pd.read_csv(path)
        self.corrected_df.columns = self.corrected_df.columns.str.strip()
        self.text_clear()
        self.text_insert(f"Loaded corrected CSV:\n{path}\nColumns: {', '.join(self.corrected_df.columns)}\n")
        self.btn_article_types.config(state='normal')
        self.btn_user_count.config(state='normal')
        self.btn_print_output.config(state='disabled')
        messagebox.showinfo("Upload Complete", "Corrected CSV file uploading successfully.")

    def show_article_types(self):
        if self.corrected_df is None:
            messagebox.showerror("Error", "Please upload the corrected CSV file first.")
            return
        article_types = ['BUSINESS_PARCEL', 'FGN_AIR_PARCEL', 'FGN_BL', 'GYAN_POST', 'PARCEL', 'SP_INLAND_PARCEL']
        counts = self.corrected_df['Article Type'].value_counts()
        total_count = counts.sum()
        self.text_clear()
        self.text_insert("Article Types Count:\n")
        self.text_insert(f"{'Article Type':25}Count\n")
        self.text_insert("-" * 40 + "\n")
        for art in article_types:
            self.text_insert(f"{art:25}{counts.get(art, 0)}\n")
        others = set(counts.index) - set(article_types)
        for art in others:
            self.text_insert(f"{art:25}{counts[art]}\n")
        self.text_insert("-" * 40 + "\n")
        self.text_insert(f"{'Total':25}{total_count}\n\n")

    def show_articles_by_user(self):
        if self.corrected_df is None:
            messagebox.showerror("Error", "Please upload the corrected CSV file first.")
            return
        df = self.corrected_df.copy()
        df['Insured Flag'] = df['Insured Flag'].astype(str).str.strip().str.upper() == 'YES'

        user_ids = df['User Id'].dropna().unique()
        if len(user_ids) == 0:
            self.text_clear()
            self.text_insert("No User IDs found in data.\n")
            self.btn_print_output.config(state='disabled')
            return

        self.text_clear()
        header = f"{'User Id':15}{'Ordinary Articles':20}{'Insured Articles':20}{'Total Articles':20}\n"
        self.text_insert(header)
        self.text_insert("-" * 75 + "\n")

        grand_ordinary = 0
        grand_insured = 0
        grand_total = 0

        for uid in user_ids:
            subset = df[df['User Id'] == uid]
            insured_count = subset['Insured Flag'].sum()
            total_count = len(subset)
            ordinary_count = total_count - insured_count

            grand_ordinary += ordinary_count
            grand_insured += insured_count
            grand_total += total_count

            line = f"{str(uid):15}{ordinary_count:<20}{insured_count:<20}{total_count:<20}\n"
            self.text_insert(line)

        self.text_insert("-" * 75 + "\n")
        grand_line = f"{'Grand Total':15}{grand_ordinary:<20}{grand_insured:<20}{grand_total:<20}\n"
        self.text_insert(grand_line)
        self.text_insert("\n")

        self.btn_print_output.config(state='normal')

    def print_output(self):
        content = self.text.get(1.0, 'end').strip()
        if not content:
            messagebox.showwarning("Warning", "No output to print.")
            return

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w+', encoding='utf-8') as tmpfile:
                tmpfile.write(content)
                tmpfile_path = tmpfile.name

            system = platform.system()

            if system == 'Windows':
                os.startfile(tmpfile_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', tmpfile_path])
            else:  # Linux and others
                subprocess.run(['xdg-open', tmpfile_path])

            messagebox.showinfo("Print", f"Output opened for manual printing:\n{tmpfile_path}")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to open output for printing:\n{e}")

    def text_insert(self, msg):
        self.text.insert('end', msg)
        self.text.see('end')

    def text_clear(self):
        self.text.delete(1.0, 'end')


if __name__ == "__main__":
    import platform
    import subprocess
    import tempfile
    root = tk.Tk()
    app = ArticleManagerApp(root)
    root.mainloop()

