
import tkinter as tk
from tkinter import ttk, scrolledtext
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

def run_lua_code():
    code = lua_input.get("1.0", tk.END)
    try:
        result = lua.execute(code)
        lua_output.config(state='normal')
        lua_output.delete("1.0", tk.END)
        lua_output.insert(tk.END, f"Tulos:\n{result}")
        lua_output.config(state='disabled')
    except Exception as e:
        lua_output.config(state='normal')
        lua_output.delete("1.0", tk.END)
        lua_output.insert(tk.END, f"Virhe:\n{str(e)}")
        lua_output.config(state='disabled')

root = tk.Tk()
root.title("Eulen | Mod Menu (Mock)")
root.geometry("900x600")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")
style.configure("TNotebook.Tab", background="#2c2c2c", foreground="white", padding=[10, 5])
style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("TCheckbutton", background="#1e1e1e", foreground="white")
style.configure("TButton", background="#444", foreground="white")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Tabit
tabs = {}
for name in ["Myself", "Online", "Weapon", "Vehicle", "Visuals", "Lua", "Resources", "Config"]:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)
    tabs[name] = frame

# "Myself"-välilehti (mock checkboxit)
myself_frame = tabs["Myself"]
left = tk.Frame(myself_frame, bg="#1e1e1e")
left.pack(side="left", padx=20, pady=20, anchor="n")

for text in ["Refill Health in Cover", "God Mode", "Semi God Mode", "Infinite Stamina", "Invisibility",
             "No Ragdoll", "Seatbelt", "No HS", "AntiStun", "Infinite Combat Roll"]:
    chk = ttk.Checkbutton(left, text=text)
    chk.pack(anchor="w", pady=2)

# Info oikealle
info_right = tk.Frame(myself_frame, bg="#1e1e1e")
info_right.pack(side="right", padx=20, pady=20, anchor="n")
for label in ["Health: 0", "Max Health: 0", "Armor: 0", "Server ID: 0", "Server IP: (null)"]:
    lbl = ttk.Label(info_right, text=label)
    lbl.pack(anchor="w", pady=2)

# "Lua"-välilehti
lua_frame = tabs["Lua"]

lua_input = scrolledtext.ScrolledText(lua_frame, width=100, height=15, bg="#2c2c2c", fg="white", insertbackground="white")
lua_input.pack(padx=20, pady=(20,10))

tk.Button(lua_frame, text="Execute", command=run_lua_code, bg="#4CAF50", fg="white").pack(pady=5)

lua_output = scrolledtext.ScrolledText(lua_frame, width=100, height=10, state='disabled', bg="#1e1e1e", fg="lightgreen")
lua_output.pack(padx=20, pady=(10, 20))

root.mainloop()
