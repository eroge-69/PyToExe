
import tkinter as tk

from tkinterdnd2 import TkinterDnD, DND_FILES

# Function to handle the file drop event
def on_drop(event):
    # Get the file path dropped onto the window
    global file_path
    file_path = event.data.replace("{", "").replace("}", "")
    label.config(text=f"File Dropped: {file_path}")
    root.quit()

# Initialize the Tkinter window with drag-and-drop support
root = TkinterDnD.Tk()

# Set the window title
root.title("Drag and Drop File Location")

# Create a label to display the file path
label = tk.Label(root, text="Drag and drop a file here", padx=20, pady=20, width=40, height=5)
label.pack(padx=10, pady=10)

# Register the window to accept file drops
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# Set the window size
root.geometry("400x200")

# Start the Tkinter event loop
root.mainloop()



def main():
    f = open(file_path, 'r')
    content = f.read()
    content_str = str(content)
    # print(content)

    content_lines = content_str.split('\n')
    modified_content_lines = [""]

    prev_X_element = 0
    prev_Y_element = 0

    for line in content_lines:
        parts = line.strip().split()
        G_element = X_element = Y_element = I_element = J_element = None

        # Extract values
        for part in parts[1:]:
            if part.startswith("G"):
                G_element = int(part[1:])
            elif part.startswith("X"):
                X_element = float(part[1:])
            elif part.startswith("Y"):
                Y_element = float(part[1:])
            elif part.startswith("I"):
                I_element = float(part[1:])
            elif part.startswith("J"):
                J_element = float(part[1:])

        # Use previous X and Y if missing
        if X_element is None:
            X_element = prev_X_element
        if Y_element is None:
            Y_element = prev_Y_element


        # Update previous X and Y if they're now known
        if X_element is not None:
            prev_X_element = X_element
        if Y_element is not None:
            prev_Y_element = Y_element

        # Build new line
        new_line = [f"G{G_element}"]
        if X_element is not None:
            new_line.append(f"X{X_element}")
        if Y_element is not None:
            new_line.append(f"Y{Y_element}")
        if I_element is not None:
            new_line.append(f"I{I_element}")
        if J_element is not None:
            new_line.append(f"J{J_element}")

        if "GNone" in new_line:
            new_line = ""

        if (new_line != "") and (I_element is None):
            new_line = (" ".join(new_line))
            parts = new_line.strip().split()
            G_element = 1
            new_line = [f"G{G_element}"]
            for element in parts[1:]:
                new_line.append(" " + element)

        print(new_line)
        modified_content_lines.append(" ".join(new_line))

    modified_content_lines = list(filter(None, modified_content_lines))

    with open(file_path[:-4] + '_modified.txt', 'w') as f:
        for line in modified_content_lines[:-1]:
            f.write(f"{line}\n")


if __name__ == '__main__':
    main()