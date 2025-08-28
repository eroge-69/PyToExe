from tkinter import *
import ctypes
import re
import os

def execute(event=None):
    with open('run.py', 'w', encoding='utf-8') as f:
        f.write(editArea.get('1.0', END))

    os.system('start cmd /K "python run.py"')

def changes(event=None):
    global previousText

    if editArea.get('1.0', END).strip() == previousText:
        return
    for tag in editArea.tag_names():
        editArea.tag_remove(tag, '1.0', "end")
    i = 0
    for pattern, color in repl:
        for start, end in search_re(pattern, editArea.get('1.0', END)):
            editArea.tag_add(f'{i}', start, end)
            editArea.tag_config(f'{i}', foreground=color)
            i += 1

    previousText = editArea.get('1.0', END)
    update_line_numbers()

def search_re(pattern, text):
    matches = []
    text = text.splitlines()
    for i, line in enumerate(text):
        for match in re.finditer(pattern, line):
            matches.append((f"{i+1}.{match.start()}", f"{i+1}.{match.end()}"))
    return matches

def rgb(rgb):
    return "#%02x%02x%02x" % rgb

def update_line_numbers():
    line_numbers.config(state=NORMAL)
    line_numbers.delete('1.0', END)
    line_count = int(editArea.index('end-1c').split('.')[0])
    line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))
    line_numbers.insert('1.0', line_numbers_text)
    line_numbers.config(state=DISABLED)

def on_scroll(*args):
    editArea.yview(*args)
    line_numbers.yview(*args)

def on_editarea_scroll(*args):
    line_numbers.yview_moveto(args[0])
    scrollbar_y.set(*args)

def auto_close(event):
    pairs = {
        '(': ')',
        '"': '"',
        "'": "'",
        '[': ']',
        '{': '}',
    }
    char = event.char
    if char in pairs:
        pos = editArea.index(INSERT)
        editArea.insert(pos, char + pairs[char])
        editArea.mark_set(INSERT, f"{pos}+1c")
        return "break"

def auto_indent(event):
    line_index = editArea.index("insert").split('.')[0]
    line_text = editArea.get(f"{line_index}.0", f"{line_index}.end")
    indent = re.match(r"[ \t]*", line_text).group(0)
    if line_text.rstrip().endswith(':'):
        indent += '    '
    editArea.insert("insert", f"\n{indent}")
    return "break"
def smart_backspace(event):
    pos = editArea.index("insert")
    start_pos = editArea.index(f"{pos} -4c")
    text_before = editArea.get(start_pos, pos)
    if text_before == "    ":
        editArea.delete(start_pos, pos)
        return "break"

ctypes.windll.shcore.SetProcessDpiAwareness(1)

root = Tk()
root.geometry('700x500')
root.title('Code editor')
previousText = ''

normal = rgb((234, 234, 234))
keywords = rgb((234, 95, 95))
comments = rgb((95, 234, 165))
string = rgb((234, 162, 95))
function = rgb((95, 211, 234))
background = rgb((42, 42, 42))
font = 'Consolas 15'

repl = [
    ['(^| )(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )', keywords],
    ['".*?"', string],
    ['\".*?\"', string],
    ['#.*?$', comments],
]

frame = Frame(root)
frame.pack(fill=BOTH, expand=1)

line_numbers = Text(frame, width=4, padx=4, takefocus=0, border=0,
                    background="#2a2a2a", foreground="#888888", state=DISABLED,
                    font=font)
line_numbers.pack(side=LEFT, fill=Y)

editArea = Text(
    frame, background=background, foreground=normal, insertbackground=normal,
    relief=FLAT, borderwidth=30, font=font, wrap=NONE
)

scrollbar_y = Scrollbar(frame, orient=VERTICAL, command=on_scroll)
scrollbar_x = Scrollbar(frame, orient=HORIZONTAL, command=editArea.xview)
editArea.configure(yscrollcommand=on_editarea_scroll, xscrollcommand=scrollbar_x.set)

scrollbar_y.pack(side=RIGHT, fill=Y)
scrollbar_x.pack(side=BOTTOM, fill=X)
editArea.pack(side=LEFT, fill=BOTH, expand=1)

editArea.insert('1.0', """# Control+R to start program""")

editArea.bind('<KeyRelease>', changes)
editArea.bind('<MouseWheel>', lambda e: (editArea.yview_scroll(int(-1*(e.delta/120)), "units"), line_numbers.yview_scroll(int(-1*(e.delta/120)), "units")))
editArea.bind('<KeyPress>', auto_close)
editArea.bind('<Return>', auto_indent)
editArea.bind('<BackSpace>', smart_backspace)

root.bind('<Control-r>', execute)

changes()

root.mainloop()
