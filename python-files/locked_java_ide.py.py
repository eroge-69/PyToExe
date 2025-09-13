import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess, tempfile, os, re, threading

DEFAULT_TEMPLATE = """public class Main {
    public static void main(String[] args) {
        System.out.println("Locked Fullscreen Java IDE!");
        // Write your Java code here
    }
}
"""

class LockedJavaIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Locked Java IDE")
        self.root.configure(bg="#1e1e1e")

        # === FULLSCREEN LOCK ===
        self.root.attributes("-fullscreen", True)   # fullscreen
        self.root.attributes("-topmost", True)      # always on top
        self.root.overrideredirect(True)            # hide titlebar & cover taskbar

        # Disable window close
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        # Detect tab switching (focus loss)
        self.root.bind("<FocusOut>", self.on_focus_out)

        # Toolbar
        toolbar = tk.Frame(root, bg="#252526")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        button_style = {"bg": "#007acc", "fg": "white", "activebackground": "#005a9e",
                        "activeforeground": "white", "font": ("Segoe UI", 12, "bold"),
                        "relief": "flat", "padx": 10, "pady": 5}

        tk.Button(toolbar, text="New", command=self.on_new, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Save", command=self.on_save, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Run ▶", command=self.on_run, **button_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Clear Output", command=self.on_clear_output, **button_style).pack(side=tk.LEFT, padx=5, pady=5)

        # Split Pane
        container = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#1e1e1e", sashrelief="raised")
        container.pack(fill=tk.BOTH, expand=1)

        # Code Editor
        self.editor = scrolledtext.ScrolledText(container, wrap=tk.NONE, undo=True,
                                                font=("Consolas", 16),
                                                bg="#1e1e1e", fg="#d4d4d4",
                                                insertbackground="white")
        self.editor.insert(tk.END, DEFAULT_TEMPLATE)
        self.disable_copy_paste(self.editor)
        container.add(self.editor, stretch="always")

        # Output Console
        self.output = scrolledtext.ScrolledText(container, wrap=tk.WORD,
                                                font=("Consolas", 14),
                                                bg="black", fg="lime",
                                                insertbackground="white")
        self.output.insert(tk.END, ">>> Output will appear here...\n")
        container.add(self.output, stretch="always")

    # Prevent window close
    def disable_event(self):
        pass

    # Disable copy/paste
    def disable_copy_paste(self, widget):
        def block_event(event=None):
            self.append_output("[Copy/Paste blocked]\n")
            return "break"
        for seq in ("<Control-c>", "<Control-C>", "<Control-v>", "<Control-V>",
                    "<Control-x>", "<Control-X>", "<Button-3>"):
            widget.bind(seq, block_event)

    # Warn if student switches tab
    def on_focus_out(self, event=None):
        self.append_output("\n⚠ WARNING: Tab/Window switch detected! Stay in fullscreen.\n")
        messagebox.showwarning("Warning", "Switching tabs is not allowed!")
        # Bring window back fullscreen
        self.root.after(100, lambda: self.root.attributes("-fullscreen", True))
        self.root.focus_force()

    # === Toolbar Actions ===
    def on_new(self):
        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, DEFAULT_TEMPLATE)
        self.output.delete("1.0", tk.END)

    def on_save(self):
        f = filedialog.asksaveasfilename(defaultextension=".java",
                                         filetypes=[("Java files", "*.java"), ("All files", "*.*")])
        if f:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(self.editor.get("1.0", tk.END))
            self.append_output(f"Saved to: {f}\n")

    def on_clear_output(self):
        self.output.delete("1.0", tk.END)

    def on_run(self):
        code = self.editor.get("1.0", tk.END)
        self.output.delete("1.0", tk.END)
        threading.Thread(target=self.compile_and_run, args=(code,), daemon=True).start()

    def append_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def detect_class_name(self, code):
        m = re.search(r"public\s+class\s+(\w+)", code)
        if m: return m.group(1)
        m = re.search(r"class\s+(\w+)", code)
        if m: return m.group(1)
        return "Main"

    def compile_and_run(self, code):
        class_name = self.detect_class_name(code)
        self.append_output(f"Using class name: {class_name}\n")

        with tempfile.TemporaryDirectory() as tempdir:
            src_file = os.path.join(tempdir, class_name + ".java")
            with open(src_file, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile
            self.append_output("Compiling...\n")
            try:
                compile_proc = subprocess.run(
                    ["javac", src_file],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    cwd=tempdir, text=True, timeout=15
                )
            except FileNotFoundError:
                self.append_output("Error: javac not found. Install JDK.\n")
                return

            self.append_output(compile_proc.stdout)
            if compile_proc.returncode != 0:
                self.append_output("Compilation failed.\n")
                return
            self.append_output("Compilation successful.\n")

            # Run
            self.append_output("Running...\n")
            try:
                run_proc = subprocess.run(
                    ["java", "-cp", tempdir, class_name],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    cwd=tempdir, text=True, timeout=10
                )
                self.append_output(run_proc.stdout)
                self.append_output(f"\nProgram finished with exit code {run_proc.returncode}\n")
            except subprocess.TimeoutExpired:
                self.append_output("Program timed out (10s)\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = LockedJavaIDE(root)
    root.mainloop()
