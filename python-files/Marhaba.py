import tkinter as tk
import time

# نافذة رئيسية
root = tk.Tk()
root.title("Welcome Screen")
root.geometry("900x500")
root.configure(bg="#1e1e2f")
root.resizable(False, False)

# ألوان وخطوط
bg_color = "#1e1e2f"
frame_color = "#2a2a3f"
accent1 = "#7aa6a1"
accent2 = "#9fbfcb"
muted = "#a0a0b0"
font_title = ("Cairo", 36, "bold")
font_sub = ("Cairo", 20)
font_note = ("Cairo", 16, "italic")

# الإطار الرئيسي مع تدرج خفيف
frame = tk.Frame(root, bg=frame_color, bd=0, relief=tk.RIDGE)
frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=400)

# Canvas لتدرج خلفي بسيط
canvas = tk.Canvas(frame, width=800, height=400, highlightthickness=0)
canvas.place(x=0, y=0)
canvas.create_rectangle(0, 0, 800, 400, fill=frame_color, outline="")
for i in range(400):
    color_val = 42 + int(i*0.05)
    color_hex = f'#{color_val:02x}{color_val:02x}{color_val+20:02x}'
    canvas.create_line(0, i, 800, i, fill=color_hex)

# الرسائل
title = tk.Label(frame, text="اهلا وسهلا بالاستاذة اسماء", font=font_title, bg=frame_color, fg=accent1)
title.pack(pady=(40,15))

sub = tk.Label(frame, text="تم فحص الفلاشة ولا يوجد اي فيروسات", font=font_sub, bg=frame_color, fg=muted)
sub.pack(pady=(0,15))

note = tk.Label(frame, text="ملاحظة: بتقدري تحذفي الملف وتستخدمي الفلاشة بالشكل الطبيعي",
                font=font_note, bg=frame_color, fg=muted, wraplength=750, justify="center")
note.pack(pady=(0,5))  # أقل مسافة للربط مع التحية

# أيقونة بسيطة
icon = tk.Label(frame, text="🌿", font=("Segoe UI Emoji", 64), bg=frame_color, fg=accent2)
icon.place(relx=0.9, rely=0.25, anchor="center")

# تحياتي محمد في آخر الشاشة، قريبة من الملاحظة
signature = tk.Label(frame, text="تحياتي محمد", font=font_sub, bg=frame_color, fg=accent1)
signature.pack(pady=(0,15))

# تأثير fade-in عند الظهور
root.attributes("-alpha", 0)
for i in range(0, 101, 5):
    root.attributes("-alpha", i/100)
    root.update()
    time.sleep(0.01)

root.mainloop()
