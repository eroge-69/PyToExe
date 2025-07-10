import tkinter as tk
from tkinter import filedialog, messagebox

def select_file():
	filePath = filedialog.askopenfilename(title='Select raw text file')
	if not filePath:
		return

	with open(filePath, 'r', encoding='utf-8') as inputFile:
		lines = inputFile.read().splitlines()

	process_lines(lines)

def process_lines(lines):
	markers = {'f': 'F:', 'm': '2.6M:'}
	outputFile = open('output.txt', 'w', encoding='utf-8')

	def update_line():
		nonlocal lineIndex
		if lineIndex >= len(lines):
			messagebox.showinfo("Done", "All lines processed and saved to output.txt")
			outputFile.close()
			root.destroy()
			return
		lineVar.set(f'Current line: {lines[lineIndex]}')

	def mark_line(choice):
		marker = markers.get(choice)
		if marker:
			outputFile.write(marker + lines[lineIndex][14:] + '\n')
		advance()

	def advance():
		nonlocal lineIndex
		lineIndex += 1
		update_line()

	lineIndex = 0
	lineVar = tk.StringVar()
	update_line()

	lineLabel = tk.Label(root, textvariable=lineVar, wraplength=600, justify="left")
	lineLabel.pack(pady=20)

	buttonFrame = tk.Frame(root)
	buttonFrame.pack()

	tk.Button(buttonFrame, text='F:', command=lambda: mark_line('f'), width=10).pack(side='left', padx=10)
	tk.Button(buttonFrame, text='2.6M:', command=lambda: mark_line('m'), width=10).pack(side='right', padx=10)

# GUI setup
root = tk.Tk()
root.title("Marker Replacer")
root.geometry("700x200")

tk.Button(root, text="Select File", command=select_file, height=2, width=20).pack(pady=40)

root.mainloop()
