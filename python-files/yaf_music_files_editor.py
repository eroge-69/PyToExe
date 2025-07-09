import struct
import sys
import os
import tempfile
import subprocess
import platform

yaf_filename=''
yaf_header= b''
yaf_header_new=b''
at3_count=0
at3_id=[]
at3_offset=[]
at3_size=[]
at3_file=[]

def reset_variables():
    global yaf_filename, yaf_header, yaf_header_new, at3_count
    global at3_id, at3_offset, at3_size, at3_file

    yaf_filename = ''
    yaf_header = b''
    yaf_header_new = b''
    at3_count = 0
    at3_id = []
    at3_offset = []
    at3_size = []
    at3_file = []

    print("All variables have been reset.")

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

    # Tentukan nama file dengan ID yang sesuai
    output_file = os.path.join(os.getcwd(), f"{at3_id[selected]}.at3")

    # Simpan data AT3 ke file di lokasi program
    with open(output_file, "wb") as audio_file:
        audio_file.write(at3_file[selected])  # Tulis data AT3 ke file
        audio_file.flush()  # Pastikan data benar-benar ditulis ke disk

    print(f"File {output_file} berhasil diekspor.")
def replace_at3(selected):
    global at3_file, at3_size
    # Minta user input path file AT3
    at3_path = input(f"Masukkan path file AT3 untuk {selected}: ")

    # Pastikan file benar-benar ada
    if not os.path.exists(at3_path):
        print("File tidak ditemukan, pastikan path benar.")
        return

    # Buka file dan baca isinya
    with open(at3_path, "rb") as f:
        at3_file[selected] = f.read()

    # Simpan ukuran file
    at3_size[selected] = os.path.getsize(at3_path)

    print(f"File {selected} berhasil diganti dengan {at3_path} (size: {at3_size[selected]} bytes)")
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
def remove_at3(selected):
    global at3_count, at3_id, at3_offset, at3_size, at3_file
    at3_count=at3_count-1
    del at3_id[selected]
    del at3_offset[selected]
    del at3_file[selected]
    del at3_size[selected]
    pass
def add_new_at3(id):
    global at3_count, at3_id, at3_file, at3_size

    at3_path = input(f"Masukkan path file AT3 untuk {id}: ")

    # Pastikan file benar-benar ada
    if not os.path.exists(at3_path):
        print("File tidak ditemukan, pastikan path benar.")
        return

    # Baca isi file ke dalam variabel
    with open(at3_path, "rb") as f:
        at3_data = f.read()

    # Simpan metadata
    at3_count += 1
    at3_id.append(id)
    at3_size.append(len(at3_data))
    at3_offset.append(0)
    at3_file.append(at3_data)  # Simpan isi file ke dalam list

    print(f"File {id} berhasil dibaca dengan ukuran {len(at3_data)} bytes dan disimpan dalam variabel.")
def sort_at3():
    global at3_id, at3_size, at3_offset, at3_file

    # Gabungkan semua dalam satu list sementara dan sort berdasarkan id
    sorted_data = sorted(zip(at3_id, at3_size, at3_offset, at3_file), key=lambda x: x[0])

    # Pisahkan kembali ke masing-masing list
    at3_id, at3_size, at3_offset, at3_file = map(list, zip(*sorted_data))
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} infile")
        return 1

    try:
        yaf_file = open(sys.argv[1], "r+b")
    except IOError:
        print(f"Cannot open {sys.argv[1]}")
        return 1

    #setelah browse file
    validate_yaf(yaf_file)
    read_header(yaf_file)
    read_at3(yaf_file)

    #perintah spesifik
    replace_at3(selected)

    #setelah perintah spesifik
    sort_at3()
    rebuild_yaf(yaf_file)
    rebuild_sfay(yaf_file)
    yaf_file.close()

    return 0

if __name__ == "__main__":
    main()
