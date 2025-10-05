r"""Organelle Guessing Game

Image support:
- The game will look for images in: C:\Users\Remy\Pictures\MSPaint Organelles
- Filenames are normalized and matched against organelle names and aliases. Example:
    "Chloroplasts.png" matches organelle name "chloroplast".
- PIL (Pillow) is used for resizing if available; without PIL Tk's PhotoImage is used as a fallback.
"""

import os
import glob
import tkinter as tk
from tkinter import messagebox
import random
try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False

organelles = [
    {
        "name": "nucleus",
        "aliases": ["nucleus", "cell nucleus"],
        "cell_type": "both",
        "membrane": "double",
        "function": "Acts as the control center of the cell, housing genetic material (DNA)."
    },
    {
        "name": "chloroplast",
        "aliases": ["chloroplast", "chloroplasts"],
        "cell_type": "plant",
        "membrane": "double",
        "function": "Site of photosynthesis, converting light energy into chemical energy (glucose) using carbon dioxide and water. Contains chlorophyll, which captures light energy."
    },
    {
        "name": "ribosomes",
        "aliases": ["ribosome", "ribosomes"],
        "cell_type": "both",
        "membrane": "none",
        "function": "Responsible for protein synthesis by translating messenger RNA (mRNA) into polypeptide chains, which fold into functional proteins."
    },
    {
        "name": "lysosomes",
        "aliases": ["lysosome", "lysosomes"],
        "cell_type": "both",
        "membrane": "single",
        "function": "Contains digestive enzymes that break down waste materials, cellular debris, and foreign substances."
    },
    {
        "name": "endoplasmic reticulum (smooth)",
        "aliases": ["smooth endoplasmic reticulum", "smooth er", "er (smooth)", "er smooth", "endoplasmic reticulum smooth"],
        "cell_type": "both",
        "membrane": "single",
        "function": "Involved in lipid synthesis, and detoxification. Not studded with ribosomes."
    },
    {
        "name": "endoplasmic reticulum (rough)",
        "aliases": ["rough endoplasmic reticulum", "rough er", "er (rough)", "er rough", "endoplasmic reticulum rough"],
        "cell_type": "both",
        "membrane": "single",
        "function": "Studded with ribosomes, it is involved in protein synthesis and modification."
    },
    {
        "name": "golgi apparatus",
        "aliases": ["golgi apparatus", "golgi", "golgi complex"],
        "cell_type": "both",
        "membrane": "single",
        "function": "Modifies, sorts, and packages proteins and lipids for storage or transport out of the cell."
    },
    {
        "name": "vacuole",
        "aliases": ["vacuole", "vacuoles"],
        "cell_type": "both",
        "membrane": "single",
        "function": "Stores nutrients, water, and waste products."
    }
]


class OrganelleGuessGame:
    def __init__(self, master):
        self.master = master
        master.title("Organelle Guessing Game")
        master.resizable(True, True)

        # Styling
        self.bg_color = '#f5f7fb'
        self.frame_bg = '#ffffff'
        self.accent = '#2b7a78'
        self.master.configure(bg=self.bg_color)

        # center the window with larger default
        self._center_window(900, 640)
        self.master.minsize(700, 480)

        self.target = None
        self.hint_index = 0
        self.max_hints = 3

        # Container frame for styling
        self.container = tk.Frame(self.master, bg=self.frame_bg, bd=1, relief='flat', padx=16, pady=16)
        self.container.grid(row=0, column=0, padx=12, pady=12)

        # UI
        self.prompt = tk.Label(self.container, text="Guess the organelle:", font=(None, 14, 'bold'), bg=self.frame_bg, fg=self.accent)
        self.prompt.grid(row=0, column=0, columnspan=2, pady=(0, 8))

        # Dropdown select for organelles
        self.choice_var = tk.StringVar()
        display_names = [o['name'] for o in organelles]
        if display_names:
            self.choice_var.set(display_names[0])

        self.dropdown = tk.OptionMenu(self.container, self.choice_var, *display_names)
        self.dropdown.config(width=48)
        self.dropdown.grid(row=1, column=0, padx=(0, 8), pady=(0, 8))

        self.submit_btn = tk.Button(self.container, text="Submit", command=self.check_guess, bg=self.accent, fg='white', activebackground='#196F6F')
        self.submit_btn.grid(row=1, column=1, padx=(0, 0), pady=(0, 8))

        self.hint_label = tk.Label(self.container, text="Hints will appear here after wrong guesses.", wraplength=760, justify='left', bg=self.frame_bg)
        self.hint_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 8))

        self.status_label = tk.Label(self.container, text="Tries: 0", fg=self.accent, bg=self.frame_bg)
        self.status_label.grid(row=3, column=0, sticky='w')

        self.restart_btn = tk.Button(self.container, text="New Game", command=self.new_game)
        self.restart_btn.grid(row=3, column=1, sticky='e')

        self.guesses_label = tk.Label(self.container, text="Previous guesses: None", wraplength=760, justify='left', fg='darkgreen', bg=self.frame_bg)
        self.guesses_label.grid(row=4, column=0, columnspan=2, sticky='w', pady=(8,0))

        # Explanation box (updated when a guess is submitted)
        self.explain_label = tk.Label(self.container, text="", wraplength=760, justify='left', bg=self.frame_bg, fg='#222222')
        self.explain_label.grid(row=5, column=0, columnspan=2, sticky='w', pady=(8,0))
        # Image display for the selected organelle/guess
        self.image_label = tk.Label(self.container, bg=self.frame_bg)
        self.image_label.grid(row=1, column=2, rowspan=5, padx=(12,0), sticky='n')

        # Keep references to PhotoImage objects to avoid garbage collection
        self._images = {}

        # Load images from user's MSPaint Organelles folder
        self.images_map = self._load_images_from_folder(r"C:\Users\Remy\Pictures\MSPaint Organelles")
        # End-screen (hidden by default) used for Correct / Out-of-hints messages
        self.end_frame = tk.Frame(self.master, bg=self.frame_bg, bd=1, relief='flat', padx=16, pady=16)
        # End screen layout: title at top, optional subtitle, image at left, description+hints at right, Play Again at bottom
        self.end_title_label = tk.Label(self.end_frame, text="", font=(None, 16, 'bold'), bg=self.frame_bg, fg=self.accent)
        self.end_title_label.grid(row=0, column=0, columnspan=2, pady=(0, 8))
        self.end_sub_label = tk.Label(self.end_frame, text="", bg=self.frame_bg, fg='#333333')
        self.end_sub_label.grid(row=1, column=0, columnspan=2, pady=(0, 8))

        # Image on left
        self.end_image_label = tk.Label(self.end_frame, bg=self.frame_bg)
        self.end_image_label.grid(row=2, column=0, padx=(0, 12), sticky='n')

        # Description and hints on right
        self.end_text_frame = tk.Frame(self.end_frame, bg=self.frame_bg)
        self.end_text_frame.grid(row=2, column=1, sticky='nw')
        self.end_desc_label = tk.Label(self.end_text_frame, text="", wraplength=520, justify='left', bg=self.frame_bg, fg='#222222')
        self.end_desc_label.grid(row=0, column=0, sticky='w')
        self.end_hints_label = tk.Label(self.end_text_frame, text="", wraplength=520, justify='left', bg=self.frame_bg, fg='darkgreen')
        self.end_hints_label.grid(row=1, column=0, sticky='w', pady=(8,0))

        self.play_again_btn = tk.Button(self.end_frame, text="Play Again", command=self._on_play_again, bg=self.accent, fg='white')
        self.play_again_btn.grid(row=3, column=0, columnspan=2, pady=(12, 0))

        self.new_game()

    def new_game(self):
        self.target = random.choice(organelles)
        self.hint_index = 0
        self.tries = 0
        self.previous_guesses = []
        # reset dropdown selection to blank
        self.choice_var.set('')
        # focus the main window so keyboard interaction works
        self.master.focus_force()
        self.hint_label.config(text="Hints will appear here after wrong guesses.")
        self.guesses_label.config(text="Previous guesses: None")
        self.explain_label.config(text="")
        self.status_label.config(text=f"Tries: {self.tries}")
        # clear image
        self._set_image(None)

    def check_guess(self):
        raw_guess = self.choice_var.get().strip()
        guess = self._normalize(raw_guess)
        if not raw_guess:
            # nothing selected
            messagebox.showwarning("No selection", "Please select an organelle from the dropdown.")
            return

        self.tries += 1
        self.status_label.config(text=f"Tries: {self.tries}")

        self.master.configure(bg=self.bg_color)
        # Find the organelle object corresponding to the selected value (for explanation)
        selected_organelle = None
        for o in organelles:
            names = [self._normalize(o['name'])] + [self._normalize(a) for a in o.get('aliases', [])]
            if guess in names:
                selected_organelle = o
                break

        # Update explanation box with details of selected organelle (if found)
        if selected_organelle:
            explain_text = f"{selected_organelle['name'].title()}\n\n{selected_organelle['function']}\n\nCell type: {selected_organelle['cell_type']}\nMembrane: {selected_organelle['membrane']}"
            self.explain_label.config(text=explain_text)
            # show image for the selected organelle if available
            img = self._get_image_for_organelle(selected_organelle)
            self._set_image(img)
        else:
            self.explain_label.config(text="")
            self._set_image(None)

        # Check against canonical name and aliases for correctness
        target_aliases = [self._normalize(self.target['name'])] + [self._normalize(a) for a in self.target.get('aliases', [])]
        if guess in target_aliases:
            # Show in-window win screen instead of a modal; include organelle details
            self._show_end_screen("Correct!", f"You guessed it in {self.tries} tries! It was '{self.target['name']}'.", organelle=self.target)
            return

        # Wrong guess -> give next hint
        # record previous guess (show original user input for clarity)
        if raw_guess:
            self.previous_guesses.append(raw_guess)
            self.guesses_label.config(text=f"Previous guesses: {', '.join(self.previous_guesses)}")

        self.give_hint()

    def _normalize(self, s: str) -> str:
        """Lowercase, remove punctuation like parentheses and commas, and collapse spaces."""
        import re
        s = s.lower()
        # remove parentheses, commas, periods
        s = re.sub(r"[\(\)\.,]", "", s)
        # collapse multiple spaces
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _center_window(self, width: int, height: int) -> None:
        # center the tkinter window on screen
        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def _show_end_screen(self, title: str, message: str, organelle: dict = None) -> None:
        """Display the end screen in the same window and hide the main container.

        If an organelle is provided, display its image, full description, and all hints.
        """
        # hide main container
        try:
            self.container.grid_remove()
        except Exception:
            pass

        # set title/subtitle
        self.end_title_label.config(text=title)
        self.end_sub_label.config(text=message)

        # populate organelle-specific info if available
        if organelle is not None:
            # description
            desc = organelle.get('function', '')
            self.end_desc_label.config(text=desc)

            # hints: show all three canonical hints
            hints = [f"Cell type: {organelle.get('cell_type')}", f"Membrane: {organelle.get('membrane')}", f"Function: {organelle.get('function')}"]
            self.end_hints_label.config(text='\n'.join(hints))

            # image
            img = self._get_image_for_organelle(organelle)
            if img:
                self.end_image_label.config(image=img)
                self.end_image_label.image = img
            else:
                self.end_image_label.config(image='', text='')
        else:
            # no organelle: clear fields
            self.end_desc_label.config(text='')
            self.end_hints_label.config(text='')
            self.end_image_label.config(image='', text='')

        # show end frame
        self.end_frame.grid(row=0, column=0, padx=12, pady=12)

    def _on_play_again(self) -> None:
        """Hide end screen and start a new game (restore the main UI)."""
        try:
            self.end_frame.grid_remove()
        except Exception:
            pass
        # restore main container
        try:
            self.container.grid()
        except Exception:
            pass
        # clear end-screen image reference to avoid retaining PhotoImage
        try:
            self.end_image_label.image = None
        except Exception:
            pass
        self.new_game()

    def _load_images_from_folder(self, folder_path: str) -> dict:
        """Scan folder for image files and return a mapping of normalized filename -> absolute path."""
        images = {}
        try:
            if not os.path.isdir(folder_path):
                return images
            # match common image extensions
            patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"]
            files = []
            for p in patterns:
                files.extend(glob.glob(os.path.join(folder_path, p)))

            for f in files:
                name = os.path.splitext(os.path.basename(f))[0]
                norm = self._normalize(name)
                images[norm] = f
        except Exception:
            # ignore any problems reading images
            pass
        return images

    def _get_image_for_organelle(self, organelle: dict):
        """Return a PhotoImage (or PIL ImageTk) for the organelle if a matching file exists, else None.

        Matching strategy: try exact canonical name, then aliases, then simple substring matches against filenames.
        """
        candidates = [organelle['name']] + organelle.get('aliases', [])
        norm_candidates = [self._normalize(c) for c in candidates]

        # 1) exact match
        for nc in norm_candidates:
            if nc in self.images_map:
                return self._load_image(self.images_map[nc])

        # 2) substring/contains match
        for fname_norm, path in self.images_map.items():
            for nc in norm_candidates:
                if nc in fname_norm or fname_norm in nc:
                    return self._load_image(path)

        return None

    def _load_image(self, path: str, max_size=(200, 200)):
        """Load image at path and return a Tk-compatible PhotoImage. Resize with PIL if available."""
        try:
            if _HAS_PIL:
                img = Image.open(path)
                img.thumbnail(max_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                # store to prevent GC
                self._images[path] = photo
                return photo
            else:
                # Fallback: use tkinter.PhotoImage (may not support all formats or resizing)
                photo = tk.PhotoImage(file=path)
                self._images[path] = photo
                return photo
        except Exception:
            return None

    def _set_image(self, photo):
        """Set the image_label to show the given PhotoImage (or clear it if None)."""
        if photo is None:
            self.image_label.config(image='', text='')
        else:
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def give_hint(self):
        hints = [
            f"Cell type: {self.target['cell_type']}",
            f"Membrane: {self.target['membrane']}",
            f"Function: {self.target['function']}"
        ]

        if self.hint_index < len(hints):
            prev = self.hint_label.cget('text')
            if "Hints will appear" in prev:
                new_text = hints[self.hint_index]
            else:
                new_text = prev + "\n" + hints[self.hint_index]

            self.hint_label.config(text=new_text)
            self.hint_index += 1
        else:
            # No more hints: reveal answer in the in-window end screen (include organelle info)
            self._show_end_screen("Out of hints", f"No more hints.", organelle=self.target)


if __name__ == '__main__':
    root = tk.Tk()
    app = OrganelleGuessGame(root)
    root.mainloop()
    app = OrganelleGuessGame(root)
    root.mainloop()