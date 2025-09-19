import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys

# Activation key from the original constants
CORRECT_KEY = '8899'

# Global entry (set later)
entry_path: tk.Entry


def check_key():
    """Prompt for activation key (or accept from argv[1]) and exit if invalid."""
    if len(sys.argv) > 1:
        entered_key = sys.argv[1]
    else:
        entered_key = simpledialog.askstring(
            'Password Required',
            'Enter the activation key:',
            show='*'
        )
    if entered_key != CORRECT_KEY:
        messagebox.showerror('Access Denied', 'Invalid key! Program will exit.')
        sys.exit(1)


def browse_file():
    """Open a file dialog for a BIOS .bin and place the path into the entry."""
    file_path = filedialog.askopenfilename(
        filetypes=[('Binary files', '*.bin'), ('All files', '*.*')]
    )
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)


def patch_8mb():
    """Patch two byte positions for 8MB BIOS images and write out a new file."""
    input_path = entry_path.get()
    if not input_path:
        messagebox.showerror('Error', 'Please select a file first!')
        return
    if not os.path.exists(input_path):
        messagebox.showerror('Error', 'File does not exist!')
        return

    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        # Addresses from the disassembly
        address1 = 4163303
        address2 = 4163352

        # Bounds check (addresses must be within data size)
        if address1 >= len(data) or address2 >= len(data):
            messagebox.showerror('Error', 'Hex addresses are out of file bounds!')
            return

        # Write ASCII '0' (48) at both positions
        data[address1] = 48
        data[address2] = 48

        base_path, ext = os.path.splitext(input_path)
        output_path = f"{base_path} DEV_ANAND 8MB_patched{ext}"

        with open(output_path, 'wb') as f:
            f.write(data)

        messagebox.showinfo('Success', f'8MB BIOS patched successfully!\nSaved as: {output_path}')
    except Exception as e:  # Match original behavior of broad catch
        messagebox.showerror('Error', 'An error occurred:\n' + str(e))


def patch_16mb():
    """Apply multiple single-byte patches for 16MB BIOS images and write out."""
    input_path = entry_path.get()
    if not input_path:
        messagebox.showerror('Error', 'Please select a file first!')
        return
    if not os.path.exists(input_path):
        messagebox.showerror('Error', 'File does not exist!')
        return

    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())

        # (address, new_byte) pairs from the disassembly
        patches = [
            (11503342, 48),
            (11503362, 48),
            (11503394, 48),
            (11503427, 48),
            (12584484, 48),
            (12584487, 49),
            (12584489, 65),
            (12584619, 48),
            (12584622, 49),
            (12584624, 65),
            (12584744, 98),
            (12584745, 102),
        ]

        for address, new_value in patches:
            if address >= len(data):
                messagebox.showwarning('Warning', 'Address ' + hex(address) + ' is out of file bounds!')
                continue
            data[address] = new_value

        base_path, ext = os.path.splitext(input_path)
        output_path = f"{base_path} DEV_ANAND 16MB_patched{ext}"

        with open(output_path, 'wb') as f:
            f.write(data)

        messagebox.showinfo('Success', f'16MB BIOS patched successfully!\nSaved as: {output_path}')
    except Exception as e:
        messagebox.showerror('Error', 'An error occurred:\n' + str(e))


def main():
    # Gate the UI behind the key check (mirrors the original call order)
    check_key()

    root = tk.Tk()
    root.title('DEV_ANAND CHROMEBOOK ENROLLMENT PATCH TOOL')
    root.geometry('750x500')
    root.configure(bg='#f5f5f5')
    root.resizable(False, False)

    # Fonts from constants
    title_font = ('Segoe UI', 12, 'bold')
    button_font = ('Segoe UI', 10, 'bold')
    label_font = ('Segoe UI', 9)
    instruction_font = ('Segoe UI', 9)  # kept for parity, not used separately

    # Header
    header_frame = tk.Frame(root, bg='#3f51b5', padx=10, pady=10)
    header_frame.pack(fill=tk.X)
    tk.Label(
        header_frame,
        text='*** DEV_ANAND BIOS SOLUTION --- CHROMEBOOK UNLOCKER ***',
        bg='#3f51b5',
        fg='white',
        font=title_font
    ).pack()

    # File chooser
    file_frame = tk.Frame(root, bg='#f5f5f5', padx=10, pady=10)
    file_frame.pack(fill=tk.X)
    tk.Label(file_frame, text='Select BIOS File:', bg='#f5f5f5', font=label_font).grid(row=0, column=0, sticky='w')

    global entry_path
    entry_path = tk.Entry(file_frame, width=90, font=label_font, highlightthickness=1, highlightbackground='#bdbdbd')
    entry_path.grid(row=1, column=0, padx=(0, 5), pady=5, sticky='ew')

    button_browse = tk.Button(
        file_frame,
        text='Browse',
        command=browse_file,
        bg='#4CAF50',
        fg='white',
        font=button_font,
        relief=tk.FLAT,
        padx=15,
        activebackground='#43A047'
    )
    button_browse.grid(row=1, column=1, pady=5)

    # Patch buttons
    button_frame = tk.Frame(root, bg='#f5f5f5', padx=10, pady=10)
    button_frame.pack(fill=tk.X)

    button_patch_8mb = tk.Button(
        button_frame,
        text='8MB BIOS PATCH',
        command=patch_8mb,
        height=2,
        width=20,
        bg='#2196F3',
        fg='white',
        font=button_font,
        relief=tk.FLAT,
        activebackground='#1976D2'
    )
    button_patch_8mb.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

    button_patch_16mb = tk.Button(
        button_frame,
        text='16MB BIOS PATCH',
        command=patch_16mb,
        height=2,
        width=20,
        bg='#FF5722',
        fg='white',
        font=button_font,
        relief=tk.FLAT,
        activebackground='#E64A19'
    )
    button_patch_16mb.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

    # Instructions panels
    instruction_frame = tk.Frame(root, bg='#ffffff', padx=15, pady=15, highlightbackground='#e0e0e0', highlightthickness=1)
    instruction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    instruction_frame = tk.Frame(root, bg='#ffffff', padx=15, pady=15, highlightbackground='#e0e0e0', highlightthickness=1)
    instruction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 20))

    instructions = (
        'Instructions:\n'
        '1. Backup the System BIOS and patch it using our tool\n'
        '2. Select the appropriate patch based on your BIOS size (8MB or 16MB)\n'
        '3. Flash the patched system BIOS and Turn on your Chromebook\n'
        '4. Switch to Dev Mode, hold (ESC + REFRESH + POWER button at the same time)\n'
        '5. After logging in, press (SHIFT + CTRL + ALT + R) and click RESTART\n'
        '6. After returning to the login screen, click POWERWASH\n'
        '7. Install new Chrome OS after flashing patched BIOS'
    )
    instruction_label = tk.Label(
        instruction_frame,
        text=instructions,
        bg='#ffffff',
        fg='#008000',
        font=('Arial', 10),
        justify=tk.LEFT,
        anchor='w',
        wraplength=550,
    )
    instruction_label.pack(fill=tk.BOTH, expand=True)

    # Status bar
    status_var = tk.StringVar()
    status_var.set('TELEGRAM --- @DEV_ANAND')
    status_bar = tk.Label(root, textvariable=status_var, bg='#3f51b5', fg='white', font=('Segoe UI', 9), anchor='w', padx=10)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    root.mainloop()


if __name__ == '__main__':
    main()
