import struct
import sys
import os
import tempfile
import subprocess
import platform
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
import shutil

yaf_filename=''
yaf_file_path=""
yaf_header= b''
yaf_header_new=b''
at3_count=0
at3_id=[]
at3_offset=[]
at3_size=[]
at3_file=[]

def backup_file(filepath):
    backup_path = filepath + ".bak"
    try:
        shutil.copy2(filepath, backup_path)
        print(f"Backup berhasil: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Gagal backup: {e}")
        return None

def finalize_output(filepath):
    original = filepath
    new_output = filepath.replace(".yaf", "-NEW.yaf")

    if not os.path.exists(new_output):
        print(f"Gagal: {new_output} tidak ditemukan.")
        return False

    try:
        # Hapus file asli jika ada
        if os.path.exists(original):
            os.remove(original)
            print(f"{original} berhasil dihapus.")

        # Ganti nama file -NEW jadi asli
        os.rename(new_output, original)
        print(f"{new_output} berhasil diubah menjadi {original}.")
        return True

    except Exception as e:
        print(f"Terjadi kesalahan saat finalize output: {e}")
        return False

def reset_variables():
    global yaf_filename, yaf_header, yaf_header_new
    global at3_count, at3_id, at3_offset, at3_size, at3_file
    yaf_filename=''
    yaf_header= b''
    yaf_header_new=b''
    at3_count=0
    at3_id=[]
    at3_offset=[]
    at3_size=[]
    at3_file=[]
    pass

def browse_file():
    global yaf_file_path
    yaf_file_path = filedialog.askopenfilename(
    title="Pilih file YAF",
    filetypes=[("Yuke's Audio Files", "*.yaf")]
)
    if yaf_file_path:
        file_path_var.set(yaf_file_path)
        print(f"Selected file: {yaf_file_path}")
        reset_variables()
        read_file()
    else:
        print("No file selected.")

def read_file():
    try:
        with open(yaf_file_path, "r+b") as yaf_file:
            validate_yaf(yaf_file)
            read_header(yaf_file)
            read_at3(yaf_file)
            print_at3()
            pass
    except Exception as e:
        print(f"Failed to read file: {e}")
        pass
    pass

def print_at3():
    at3_listbox.delete(0, tk.END)  # kosongkan dulu listbox
    for i in range(at3_count):
        display_text = f"ID: {at3_id[i]}, Offset: {at3_offset[i]}, Size: {at3_size[i]}"
        at3_listbox.insert(tk.END, display_text)
        pass
    pass

def padding(t):
    current_offset = t.tell()
    column = current_offset % 16
    if column != 0:
        # Cari jumlah padding sampai mencapai kolom 0 berikutnya
        padding = (16 - column) % 16
        if padding == 0:
            padding = 16  # Kalau sudah di kolom 0, skip
        t.write(b'\x00' * padding)
    pass
def validate_yaf(f):
    global yaf_header
    #Validate Header
    f.seek(0)
    word = f.read(4).decode('ascii')
    if word != "SFAY":
        print("Invalid YAF file, SFAY header missing")
        return
    else:
        print("YAF file Header Correct")

    f.read(4)
    raw_name = f.read(16)
    filtered_name = raw_name.replace(b'\x00', b'')
    decoded_name = filtered_name.decode('ascii')
    filename = os.path.basename(f.name)
    if decoded_name != filename:
        print("Invalid YAF file, File Name and Header Not Same")
        return
    else:
        print(f"File Name: {decoded_name}")
def read_header(f):
    global yaf_header, yaf_filename, at3_count
    f.seek(0)
    yaf_header=f.read(44)
    print(f"Read Header:")
    f.seek(8)
    raw_name = f.read(16)
    filtered_name = raw_name.replace(b'\x00', b'')
    decoded_name = filtered_name.decode('ascii')
    yaf_filename=decoded_name
    at3_count = struct.unpack('<I', f.read(4))[0]
    print(f"AT3 Count: {at3_count}")
    pass
def read_at3(f):
    global at3_count, at3_id, at3_offset, at3_size, at3_file
    f.seek(44)
    print(f"Read AT3 File: ")
    for i in range(at3_count):
        at3_size.append(struct.unpack('<I', f.read(4))[0])
        at3_offset.append(struct.unpack('<I', f.read(4))[0])
        at3_id.append(struct.unpack('<I', f.read(4))[0])
        print(f"ID:{at3_id[i]}, Offset:{at3_offset[i]}, Size:{at3_size[i]}")
        pass
    for i in range(at3_count):
        f.seek(at3_offset[i])
        at3_file.append(f.read(at3_size[i]))
        pass
def play_at3(selected):
    global at3_file
    # Tentukan nama file temporer yang sama di setiap eksekusi
    temp_audio_path = os.path.join(tempfile.gettempdir(), "temp_audio.at3")

    # Buat atau timpa file temporer dengan data AT3
    with open(temp_audio_path, "wb") as temp_audio:
        temp_audio.write(at3_file[selected])  # Tulis data AT3 ke file sementara
        temp_audio.flush()  # Pastikan data benar-benar ditulis ke disk

    # Buka file dengan aplikasi default sesuai sistem operasi
    if platform.system() == "Windows":
        os.startfile(temp_audio_path)  # Windows: buka dengan aplikasi default
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", temp_audio_path])  # macOS: buka dengan aplikasi default
    else:  # Linux/Other
        subprocess.run(["xdg-open", temp_audio_path])  # Linux: buka dengan aplikasi default
def export_at3(selected):
    global at3_file, at3_id

    # Saran nama file default
    default_name = f"{at3_id[selected]}.at3"

    # Dialog untuk simpan file
    output_file = filedialog.asksaveasfilename(
        defaultextension=".at3",  # atau ".adx" kalau kamu mau default-nya ke ADX
        initialfile=default_name,
        filetypes=[
            ("AT3 Audio Files", "*.at3"),
            ("ADX Audio Files", "*.adx")
        ],
        title="Simpan Audio"
    )


    # Kalau user cancel, output_file akan kosong
    if not output_file:
        print("Ekspor dibatalkan.")
        return

    try:
        with open(output_file, "wb") as audio_file:
            audio_file.write(at3_file[selected])
            audio_file.flush()

        messagebox.showinfo("Berhasil", f"File berhasil diekspor:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Gagal", f"Gagal menyimpan file:\n{e}")

def replace_at3(selected, at3_path):
    global at3_file, at3_size
    if not os.path.exists(at3_path):
        print("File tidak ditemukan, pastikan path benar.")
        return

    try:
        with open(at3_path, "rb") as f:
            at3_file[selected] = f.read()

        at3_size[selected] = os.path.getsize(at3_path)

        print(f"File {selected} berhasil diganti dengan {at3_path} (size: {at3_size[selected]} bytes)")

    except Exception as e:
        print(f"Terjadi kesalahan saat membaca file: {e}")
def remove_at3(selected):
    global at3_count, at3_id, at3_offset, at3_size, at3_file
    at3_count=at3_count-1
    del at3_id[selected]
    del at3_offset[selected]
    del at3_file[selected]
    del at3_size[selected]
    pass
def add_new_at3(id, at3_path):
    global at3_count, at3_id, at3_file, at3_size, at3_offset
    # Pastikan file benar-benar ada
    if not os.path.exists(at3_path):
        print("File tidak ditemukan, pastikan path benar.")
        messagebox.showerror("File Error", "File AT3 tidak ditemukan.")
        return

    # Baca isi file
    with open(at3_path, "rb") as f:
        at3_data = f.read()

    # Simpan metadata
    at3_count += 1
    at3_id.append(id)
    at3_size.append(len(at3_data))
    at3_offset.append(0)
    at3_file.append(at3_data)

    print(f"File {id} berhasil dibaca dengan ukuran {len(at3_data)} bytes dan disimpan dalam variabel.")

def sort_at3():
    global at3_id, at3_size, at3_offset, at3_file

    # Gabungkan semua dalam satu list sementara dan sort berdasarkan id
    sorted_data = sorted(zip(at3_id, at3_size, at3_offset, at3_file), key=lambda x: x[0])

    # Pisahkan kembali ke masing-masing list
    at3_id, at3_size, at3_offset, at3_file = map(list, zip(*sorted_data))
def rebuild_yaf(f):
    global yaf_header, at3_count, at3_id, at3_offset, at3_size, at3_file, yaf_header_new
    # Tentukan nama file baru dengan suffix "-NEW.yaf"
    file_name_without_ext = os.path.splitext(f.name)[0]
    new_file_name = f"{file_name_without_ext}-NEW.yaf"
    new_file_path = os.path.join(os.getcwd(), new_file_name)

    # Buat file kosong terlebih dahulu
    with open(new_file_path, "wb") as new_file:
        pass  # File dibuat tapi belum diisi, hanya memastikan file ada

    # Buka file dalam mode "r+b" dan tulis data YAF
    with open(new_file_path, "r+b") as t:
        t.write(yaf_header)  # Tulis header YAF ke file
        t.seek(24)
        t.write(struct.pack('<I',at3_count))
        t.seek(0,os.SEEK_END)
        t.write(b'\x00' * 131028)
        t.seek(44)
        for i in range(at3_count):
            t.write(struct.pack('<I',at3_size[i]))
            t.write(struct.pack('<I',at3_offset[i]))
            t.write(struct.pack('<I',at3_id[i]))
            pass
        yaf_header_end_new=t.tell()
        t.seek(0,os.SEEK_END)
        at3_offset_new=[]
        for i in range(at3_count):
            at3_offset_new.append(t.tell())
            t.write(at3_file[i])

            # Hitung padding yang diperlukan
            at3_size = len(at3_file[i])
            padding_needed = (2048 - (at3_size % 2048)) if (at3_size % 2048) != 0 else 0

            # Tulis padding ke file YAF
            t.write(b'\x00' * padding_needed)

        t.seek(44)
        t.read(4)
        for i in range(at3_count):
            t.write(struct.pack('<I',at3_offset_new[i]))
            t.read(8)
            pass
        t.seek(0)
        yaf_header_new=t.read(yaf_header_end_new)
        t.flush()  # Pastikan data benar-benar ditulis ke disk
        pass

    print(f"File {new_file_path} berhasil dibuat dan diisi dengan header YAF.")
def rebuild_sfay(f):
    global yaf_header_new
    file_name_without_ext = os.path.splitext(f.name)[0]
    new_file_name = f"{file_name_without_ext}-NEW.sfay"
    new_file_path = os.path.join(os.getcwd(), new_file_name)
    # Buat file kosong terlebih dahulu
    with open(new_file_path, "wb") as t:
        t.write(yaf_header_new)
        pass  # File dibuat tapi belum diisi, hanya memastikan file ada

def browse_at3_file():
    at3_path_var.set(filedialog.askopenfilename(
    filetypes=[
        ("Audio Files (AT3, ADX)", "*.at3 *.adx"),
        ("All files", "*.*")
    ]
))


def validate_id_input(P):
    return P.isdigit() and len(P) <= 3  # Hanya angka, maksimum 3 digit

def open_add_new_window():
    add_window = tk.Toplevel(root)
    add_window.title("Add New AT3 File")

    tk.Label(add_window, text="ID & Type:").grid(row=0, column=0, padx=10, pady=10)

    id_var = tk.StringVar()
    id_spinbox = tk.Spinbox(add_window, from_=100, to=999, textvariable=id_var, width=5)
    id_spinbox.grid(row=0, column=1, padx=5, pady=10)

    # Mapping label ke kode sebenarnya
    type_labels = {
        "00 (Main)": "00",
        "10 (Face)": "10",
        "20 (Heel)": "20"
    }

    # Buat dropdown dengan label-label lengkap
    type_dropdown = ttk.Combobox(add_window, values=list(type_labels.keys()), width=12)
    type_dropdown.grid(row=0, column=2, padx=5, pady=10)
    type_dropdown.set("00 (Main)")  # Set nilai awal

    tk.Label(add_window, text="AT3 File:").grid(row=1, column=0, padx=10, pady=10)
    at3_path_var.set("")  # Reset variable
    file_entry = tk.Entry(add_window, textvariable=at3_path_var, width=40)
    file_entry.grid(row=1, column=1, padx=10, pady=10)
    browse_button = tk.Button(add_window, text="Browse", command=browse_at3_file)
    browse_button.grid(row=1, column=2, padx=10, pady=10)

    ok_button = tk.Button(
        add_window,
        text="OK",
        command=lambda: add_new_entry(
            at3_path_var.get(),
            int(id_var.get() + type_labels.get(type_dropdown.get(), "00")),
            add_window  # <-- Kirim window-nya
        )
    )

    ok_button.grid(row=2, column=1, pady=10)
    add_window.grab_set()           # Kunci fokus ke window baru
    root.wait_window(add_window)   # Tunggu sampai window baru ditutup

def add_new_entry(at3_path, combined_id, window):
    try:
        # Validasi path tidak kosong dan file-nya ada
        if not at3_path or not os.path.exists(at3_path):
            print("Path AT3 kosong atau file tidak ditemukan.")
            messagebox.showerror("AT3 Tidak Valid", "Silakan pilih file AT3 yang valid.")
            return

        combined_id = int(combined_id)

        backup_file(yaf_file_path)

        if combined_id in at3_id:
            print(f"ID {combined_id} sudah digunakan. Gunakan ID lain.")
            messagebox.showwarning("ID Duplikat", f"ID {combined_id} sudah digunakan. Silakan pilih ID yang berbeda.")
            return

        add_new_at3(combined_id, at3_path)

        with open(yaf_file_path, "r+b") as yaf_file:
            sort_at3()
            rebuild_yaf(yaf_file)
            rebuild_sfay(yaf_file)

        finalize_output(yaf_file_path)
        reset_variables()
        read_file()

        messagebox.showinfo("Berhasil", f"File berhasil ditambahkan.")
        window.destroy()

    except Exception as e:
        print(f"Failed to read file: {e}")
        messagebox.showerror("Gagal", f"Gagal menambahkan file:\n{e}")

def export_file():
    print("Exporting file...")
    selection = at3_listbox.curselection()
    if selection:
        selected = selection[0]
        export_at3(selected)
    else:
        print("Nothing selected.")

def replace_file():
    selection = at3_listbox.curselection()
    if selection:
        selected = selection[0]
        # Tampilkan file dialog untuk memilih file .at3
        at3_path = filedialog.askopenfilename(
        title=f"Ganti AT3 untuk ID {selected}",
        defaultextension=".at3",
        filetypes=[
            ("Audio Files (AT3, ADX)", "*.at3 *.adx"),
            ("All files", "*.*")
        ]
    )


        if not at3_path:
            print("Penggantian dibatalkan.")
            return
        replace_at3(selected, at3_path)
        #setelah perintah spesifik
        try:
            backup_file(yaf_file_path)
            with open(yaf_file_path, "r+b") as yaf_file:
                sort_at3()
                rebuild_yaf(yaf_file)
                rebuild_sfay(yaf_file)
                pass
            finalize_output(yaf_file_path)
            reset_variables()
            read_file()
            messagebox.showinfo("Berhasil", f"File berhasil direplace.")
        except Exception as e:
            print(f"Failed to read file: {e}")
            messagebox.showerror("Gagal", f"Gagal replace file:\n{e}")
            pass
    else:
        print("Nothing selected.")

def remove_file():
    selection = at3_listbox.curselection()
    if selection:
        selected = selection[0]
        confirm = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus AT3 dengan ID {at3_id[selected]}?"
        )
        if confirm:
            remove_at3(selected)
            #setelah perintah spesifik
            try:
                backup_file(yaf_file_path)
                with open(yaf_file_path, "r+b") as yaf_file:
                    sort_at3()
                    rebuild_yaf(yaf_file)
                    rebuild_sfay(yaf_file)
                    pass
                finalize_output(yaf_file_path)
                reset_variables()
                read_file()
                messagebox.showinfo("Berhasil", f"File berhasil dihapus.")
            except Exception as e:
                print(f"Failed to read file: {e}")
                messagebox.showerror("Gagal", f"Gagal menghapus file:\n{e}")
                pass
        else:
            print("Penghapusan dibatalkan.")

    else:
        print("Nothing selected.")

def rebuild_file():
    print("Rebuilding archive...")
    #setelah perintah spesifik
    try:
        backup_file(yaf_file_path)
        with open(yaf_file_path, "r+b") as yaf_file:
            sort_at3()
            rebuild_yaf(yaf_file)
            rebuild_sfay(yaf_file)
            pass
        finalize_output(yaf_file_path)
        reset_variables()
        read_file()
        messagebox.showinfo("Berhasil", f"Rebuild berhasil.")
    except Exception as e:
        print(f"Failed to read file: {e}")
        messagebox.showerror("Gagal", f"Gagal rebuild file:\n{e}")
        pass


def on_listbox_double_click(event):
    selection = at3_listbox.curselection()
    if selection:
        selected = selection[0]
        play_at3(selected)
    else:
        print("Nothing selected.")

# GUI setup
root = tk.Tk()
root.title("Music Files Editor PSP")

file_path_var = tk.StringVar()
at3_path_var = tk.StringVar()

# File browse
tk.Label(root, text="YAF File:").grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, textvariable=file_path_var, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=10)

# Object listbox
tk.Label(root).grid(row=1, column=0, padx=10, pady=10)
at3_listbox = tk.Listbox(root, selectmode=tk.SINGLE, height=10, width=80)
at3_listbox.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
at3_listbox.bind("<Double-Button-1>", on_listbox_double_click)

# Button frame
button_frame = tk.Frame(root)
button_frame.grid(row=2, column=1, padx=10, pady=10)

tk.Button(button_frame, text="Export", command=export_file).pack(side=tk.LEFT, padx=(0, 10))
tk.Button(button_frame, text="Replace", command=replace_file).pack(side=tk.LEFT, padx=(0, 10))
tk.Button(button_frame, text="Remove", command=remove_file).pack(side=tk.LEFT, padx=(0, 10))
tk.Button(button_frame, text="Add New", command=open_add_new_window).pack(side=tk.LEFT, padx=(0, 10))
tk.Button(button_frame, text="Rebuild", command=rebuild_file).pack(side=tk.LEFT)

root.mainloop()
