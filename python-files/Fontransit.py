import tkinter as tk
from tkinter import filedialog, messagebox
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import GlyphCoordinates
import os

def adjust_font(input_path, output_path, spacing, scale_x):
    font = TTFont(input_path)
    hmtx = font["hmtx"]

    if "glyf" in font:
        glyf = font["glyf"]
    else:
        glyf = None

    for glyph_name in font.getGlyphOrder():
        try:
            width, lsb = hmtx[glyph_name]
            new_width = int(width * scale_x) + spacing
            new_width = max(0, min(new_width, 65535))
            hmtx[glyph_name] = (new_width, lsb)

            if glyf:
                glyph = glyf[glyph_name]
                if glyph.isComposite():
                    continue
                if not hasattr(glyph, "coordinates") or glyph.coordinates is None:
                    continue
                coords = glyph.coordinates
                for i in range(len(coords)):
                    x, y = coords[i]
                    coords[i] = (int(x * scale_x), y)
                glyph.coordinates = GlyphCoordinates(coords)
                glyph.recalcBounds(font.getGlyphSet())
        except Exception as e:
            print(f"스킵됨: {glyph_name}, 오류: {e}")
            continue

    font.save(output_path)

def browse_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Font files", "*.ttf *.otf")])
    if file_paths:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, ';'.join(file_paths[:15]))

def choose_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)

def run_adjustment():
    input_paths = input_entry.get().split(";")
    output_dir = output_entry.get()

    try:
        spacing = int(spacing_entry.get())
        scale = float(scale_entry.get()) / 100.0
    except ValueError:
        messagebox.showerror("오류", "자간 또는 장평 값을 숫자로 입력해 주세요.")
        return

    if not input_paths or not output_dir:
        messagebox.showerror("오류", "입력 폰트와 출력 경로를 모두 지정해 주세요.")
        return

    success_count = 0
    for font_path in input_paths[:15]:
        if not os.path.exists(font_path):
            continue
        font_name = os.path.basename(font_path)
        out_path = os.path.join(output_dir, f"adj_{font_name}")
        try:
            adjust_font(font_path, out_path, spacing, scale)
            success_count += 1
        except Exception as e:
            print(f"처리 실패: {font_path}, 오류: {e}")
            continue

    messagebox.showinfo("완료", f"{success_count}개 폰트 수정 완료!")

# GUI 구성
root = tk.Tk()
root.title("Fontransit")
root.geometry("450x400")

tk.Label(root, text="입력 폰트 파일 (최대 15개)").pack()
input_entry = tk.Entry(root, width=60)
input_entry.pack()
tk.Button(root, text="찾아보기", command=browse_files).pack(pady=5)

tk.Label(root, text="출력 폴더").pack()
output_entry = tk.Entry(root, width=60)
output_entry.pack()
tk.Button(root, text="폴더 선택", command=choose_output_folder).pack(pady=5)

tk.Label(root, text="자간 값 (예: -20 ~ 50)").pack()
spacing_entry = tk.Entry(root)
spacing_entry.insert(0, "0")
spacing_entry.pack()

tk.Label(root, text="장평 비율 % (예: 80 ~ 120)").pack()
scale_entry = tk.Entry(root)
scale_entry.insert(0, "100")
scale_entry.pack()

tk.Button(root, text="일괄 변환 실행", command=run_adjustment, bg="#4CAF50", fg="white", height=2).pack(pady=20)

root.mainloop()
