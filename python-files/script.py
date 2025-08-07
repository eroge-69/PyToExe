from tkinter import ttk

import tkinter as tk 

from tkinterweb import HtmlFrame 

import json


from pathlib import Path

import clipboard


from bs4 import BeautifulSoup as Soup 

from tkinter import font as tkfont

from tkinter import messagebox


from PIL import ImageTk, Image

import urllib.request
import io

import ssl 

list_change="<<list_change>>" 

last_form = {} 

class Form(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)

        # Lock focus on this window
        self.grab_set()
        self.overrideredirect(True)  # Removes default title bar

        # Window size
        window_width = 600
        window_height = 400

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Style variables
        self.bg_color = "#f9f9f9"
        self.title_bg = "#4a90e2"
        self.title_fg = "white"
        self.btn_bg = "#4a90e2"
        self.btn_fg = "white"
        self.entry_bg = "white"
        self.border_color = "#cccccc"

        self.configure(bg=self.bg_color)

        self.create_widgets()


    def create_widgets(self):
        # --- Title Bar ---
        title_bar = tk.Frame(self, bg=self.title_bg, height=40)
        title_bar.pack(fill="x", side="top")

        title_label = tk.Label(
            title_bar, text="Add Person", bg=self.title_bg, fg=self.title_fg,
            font=tkfont.Font(size=12, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=5)

        close_button = tk.Button(
            title_bar, text="✕", command=self.destroy,
            bg=self.title_bg, fg=self.title_fg, border=0,
            font=tkfont.Font(size=12, weight="bold"),
            activebackground="#e74c3c", activeforeground="white"
        )
        close_button.pack(side="right", padx=10, pady=5)

        # --- Main Frame ---
        form_frame = tk.Frame(self, bg=self.bg_color, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        # Helper to add label + entry
        def add_row(label_text, row, widget_type="entry", height=1):
            label = tk.Label(form_frame, text=label_text, bg=self.bg_color, anchor="w")
            label.grid(row=row, column=0, sticky="w", pady=5)

            if widget_type == "entry":
                entry = tk.Entry(form_frame, width=40, bg=self.entry_bg)
                entry.grid(row=row, column=1, sticky="w", pady=5)
                return entry
            elif widget_type == "text":
                text_box = tk.Text(form_frame, width=40, height=height, bg=self.entry_bg)
                text_box.grid(row=row, column=1, sticky="w", pady=5)
                return text_box

        self.name_entry = add_row("Name:", 0)
        self.email_entry = add_row("Email:", 1)  # Insert after Name row
        self.title_entry = add_row("Title:", 2)
        self.responsibility_entry = add_row("Core Responsibility:", 3)
        self.picture_entry = add_row("Profile Picture Link:", 4)
        self.bio_text = add_row("Bio:", 5, widget_type="text", height=5)

        # --- Submit Button ---
        submit_button = tk.Button(
            form_frame, text="Submit", bg=self.btn_bg, fg=self.btn_fg,
            font=tkfont.Font(size=10, weight="bold"),
            activebackground="#357ab7", activeforeground="white",
            padx=15, pady=5, command=self.on_submit
        )
        submit_button.grid(row=6, column=1, sticky="e", pady=(15, 0))

    def on_submit(self):
        # Collect values
        self.data = {
            "name": self.name_entry.get(),
            "title": self.title_entry.get(),
            "responsibility": self.responsibility_entry.get(),
            "img": self.picture_entry.get(),
            "bio": self.bio_text.get("1.0", "end").strip(),
            "email": self.email_entry.get() 
        }


        for v in self.data.values(): 
            if v == None or v == "": 
                messagebox.showerror("Error", "No fields can be left blank.")
                return 


        print("Form Submitted:", self.data)

        global last_form

        last_form = self.data; 

        self.destroy()









class DragDropListbox(tk.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)

    def shiftSelection(self, event):
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i
        self.event_generate(list_change) 

        
        



class App(tk.Tk):
     

    default_db = {"Adrian Pellen" : '''    <!-- Adrian Pellen -->
<div class="profile">
  <div class="image-placeholder">
    <img src="https://connect2storageaccount.blob.core.windows.net/publicimagecontainer/c7d650fc-95b0-4468-bab1-28f7f5eea5fc.jpg">
  </div>
  <div class="info">
    <h3>Adrian Pellen</h3>
    <p class="title">C&I Managing Director</p>
    <p class="responsibility"><em>Brokerage and Service Strategy and Executive Oversight of C&I Resources</em></p>
    <p class="email"><a href="mailto:adrian.pellen@nfp.com">adrian.pellen@nfp.com</a></p>
    <p class="bio">
      As co-leader of NFP's Construction and Infrastructure Group, Adrian oversees strategy, operations, and resource deployment. He previously led Marsh’s Infrastructure segment across the U.S. and Canada. He holds degrees from Concordia, McGill, and the University of Chicago Booth School of Business.
    </p>
  </div>
</div>''', "Mevan Srishan": '''   <!-- Mevan Srishan -->
    <div class="profile">
      <div class="image-placeholder"><img src="https://connect2storageaccount.blob.core.windows.net/publicimagecontainer/501452df-7ce7-4d24-83b8-6e33f55559e6.png"></div>
      <div class="info">
        <h3>Mevan Srishan</h3>
        <p class="title">Strategy & Insights Manager</p>
        <p class="responsibility"><em>Project and Insurance Insights </em></p>
        <p class="email"><a href="mailto:mevan.srishan@nfp.com
">mevan.srishan@nfp.com
</a></p>
        <p class="bio">
           Mevan leads data-driven strategy and insights, helping the organization adapt to industry changes and seize market opportunities. Mevan has worked across sectors including construction, insurance, and mining. Prior to joining NFP, he specialized in metals and mining valuations and has delivered workshops on business interruption and cyber-related losses.
        </p>
      </div>
    </div>''', "Sarah Hanson": '''<!-- Sarah Hanson -->
    <div class="profile">
      <div class="image-placeholder"><img src="https://connect2storageaccount.blob.core.windows.net/publicimagecontainer/b58e3848-b3b2-4d8e-9a1b-350ee0dcd6d7.png"></div>
      <div class="info">
        <h3>Sarah Hanson</h3>
        <p class="title">Senior Account Executive</p>
        <p class="responsibility"><em>Principal Client Contact</em></p
        <p class="email"><a href="mailto:sarah.hanson@nfp.ca">sarah.hanson@nfp.ca</a></p>
        <p class="bio">
           Sarah Hanson brings over 16 years of commercial insurance experience, with deep specialization in construction, infrastructure, and risk advisory. She holds her CAIB (Hons), a Certified Risk Manager designation from GRMI, and a degree in Communications, combining technical acumen with strong stakeholder engagement capabilities.

        </p>
      </div>
    </div>'''}

    root_profile = '''<div class="profile">
      <div class="image-placeholder">
        <img src="{img}">
      </div>
      <div class="info">
        <h3>{name}</h3>
        <p class="title">{title}</p>
        <p class="responsibility"><em>{core_responsibility}</em></p>
        <p class="email"><a href="mailto:{email}">{email}</a></p>
        <p class="bio">
          {bio}
        </p>
      </div>
    </div>
  '''

    root_content = '''
        <div class="team-bios">
          <div class="profiles-grid">



            </div>
        </div>

        <style>

        .profiles-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr); /* 3 columns by default */
          gap: 2rem;
          width: 100%;
          box-sizing: border-box;
        }

        @media (max-width: 1024px) {
          .profiles-grid {
            grid-template-columns: repeat(2, 1fr); /* 2 columns on medium screens */
          }
        }

        @media (max-width: 600px) {
          .profiles-grid {
            grid-template-columns: 1fr; /* 1 column on small screens */
          }
        }
        .responsibility {
          font-style: italic;
          color: #555;
          margin-bottom: 8px;
        }

        .profile {
          display: flex;
          flex-direction: row;
          gap: 1rem;
          background: #fff;
          padding: 1rem;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
          
           width: 100%;
          height: 100%; /* Ensures it fills the grid cell */

          box-sizing: border-box;
        }
        .v-center-container  {
          position: relative;
          z-index: 0;
        }

        .profiles-grid {
          position: relative;
          z-index: 1;
        }


        .v-center-container  {
          max-height: 0;
          overflow: hidden;
        }

        /* For placeholder boxes */
        .image-placeholder {
          width: 100px;
          height: 100px;
          background-color: #ddd;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.9rem;
          color: #666;
          flex-shrink: 0;
        }

        /* For actual images */
        .profile img {
          width: 100px;
          height: 100px;
          object-fit: cover;
          border-radius: 8px;
          flex-shrink: 0;
          display: block; /* Important: don't use flex on images */

          align-items: stretch; /* Ensures all grid items match height */

        }



        @media (max-width: 600px) {
          .profile {
            flex-direction: column;
            align-items: center;
            text-align: center;
          }

          .image-placeholder {
            margin-bottom: 1rem;
          }
        }

        </style>

        '''

    def init_database(self):
        

        db_path = Path("team_profiles.json")

        if db_path.exists(): 
            with db_path.open("r", encoding="utf-8") as file:
                self.default_db = json.load(file)
        
        else: 
            with db_path.open("w", encoding="utf-8") as create_file: 
                json.dump(self.default_db, create_file, indent=2) 

        self.soup = Soup(self.root_content)

        profile = self.soup.find("div", {"class" : "profiles-grid"})

        for key,value in self.default_db.items():
            
            profile.insert_after(Soup(value))

            profile = self.soup.find_all("div", {"class" : "profile"}).pop()



    def checkbox_clicked(self):
        selected = [var.get() for var in self.p_button_states] 

        self.soup = Soup(self.root_content)

        profile = self.soup.find("div", {"class" : "profiles-grid"})

        for i,k in enumerate(self.default_db):
            if selected[i] == 1:
                
                profile.insert_after(Soup(self.default_db[k]))

                profile = self.soup.find_all("div", {"class" : "profile"}).pop()

                if k not in self.listbox_drag.get(0, tk.END):
                    self.listbox_drag.insert(i, k)  

            else:
                for j, item in enumerate(self.listbox_drag.get(0, tk.END)):
                    if item == k:
                        self.listbox_drag.delete(j)
                        break

                   
        self.frame.load_html(str(self.soup))

    def copy_clicked(self):

        clipboard.copy(str(self.soup)) 

    def add_person_clicked(self):
        
        global last_form
      
        prev = last_form
        
        form = Form(self)

        self.wait_window(form) 


        if(last_form.__eq__(prev)):
            return 
    
        print(last_form)

        
        html = self.root_profile.format(
            img=last_form['img'],
            name=last_form['name'],
            title=last_form['title'],
            core_responsibility=last_form['responsibility'],
            email=last_form['email'],
            bio=last_form['bio']
          )


        self.default_db[last_form['name']] = html 

        profile = self.soup.find_all("div", {"class" : "profile"}); 

        if len(profile) == 0: 
            profile = self.soup.find("div", {"class" : "profiles-grid"})
            profile.insert_after(Soup(html))   
        else: 
            new_profile = profile.pop()
            new_profile.insert_after(Soup(html))  
       

        self.frame.load_html(str(self.soup))


        self.listbox_drag.insert(tk.END, last_form['name']) 

        p_button_state = tk.IntVar(value=1)

        self.p_button_states.append(p_button_state) 
            
        p_button = ttk.Checkbutton(self.button_box, text=last_form['name'], command=self.checkbox_clicked, variable=p_button_state)

        p_button.pack(fill="x")

        db_path = Path("team_profiles.json")

        with db_path.open("w", encoding="utf-8") as create_file: 
                json.dump(self.default_db, create_file, indent=2) 
        
      

        



    
    def __init__(self):
        super().__init__()

        self.bind(list_change, self.handle_list_change) 


        self.init_database()
        
        self.title("NFP Connect Tool")

        window_width = 1000
        window_height = 800

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        center_x = int(screen_width/2 - window_width /2)
        center_y = int(screen_height/2 - window_height /2)
        
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.create_widgets()

    def handle_list_change(self, event):
        
        self.soup = Soup(self.root_content)

        profile = self.soup.find("div", {"class" : "profiles-grid"})

        for i,k in enumerate(self.listbox_drag.get(0, tk.END)):
            
            profile.insert_after(Soup(self.default_db[k])); 

            profile = self.soup.find_all("div", {"class" : "profile"}).pop()
            

        self.frame.load_html(str(self.soup))

            


        
    def create_widgets(self):
        self.frame = HtmlFrame(self, width=400)


        self.frame.load_html(str(self.soup))

        
        self.frame.pack(side=tk.RIGHT, fill="both", expand=True)
    
        tools_frame = tk.Frame(self, width=250, height=self.winfo_height())
        tools_frame.pack(side=tk.LEFT, fill=tk.Y)


        self.p_button_states = [] 


        self.button_box = tk.LabelFrame(tools_frame) 

        self.button_box.pack() 


        for person in self.default_db:

            p_button_state = tk.IntVar(value=1)

            self.p_button_states.append(p_button_state) 
            
            p_button = ttk.Checkbutton(self.button_box, text=person, command=self.checkbox_clicked, variable=p_button_state)

            p_button.pack(fill="x")



        self.add_frame = ttk.Frame(tools_frame)

        self.add_frame.pack(fill=tk.Y)  

        url = "https://img.icons8.com/?size=24&id=63650&format=png&color=000000"

        try:
            context = ssl._create_unverified_context() 
            with urllib.request.urlopen(url, context=context) as u:
              raw_data = u.read()
        except Exception as e:
            print(f"Error fetching image: {e}")
          
        try:
            image = Image.open(io.BytesIO(raw_data))
            self.add_img = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error opening image: {e}")
            return



        self.add_button = ttk.Button(self.add_frame, image=self.add_img, text="Add Person", compound="left", command=self.add_person_clicked) 

        self.add_button.pack() 


        self.order_text = ttk.Label(tools_frame, text="Ordering", font=("Arial", 16, "bold"))

        self.order_text.pack()  

        self.list_items = tk.Variable(value=list(self.default_db.keys()))

        self.listbox_drag = DragDropListbox(tools_frame, listvariable=self.list_items)

        self.listbox_drag.pack(fill="both", expand=True) 

        self.copy_button = ttk.Button(tools_frame, text="Copy to Clipboard", command=self.copy_clicked)

        self.copy_button.pack(side=tk.BOTTOM, fill="x")      

if __name__ == "__main__": 
    app = App()
    app.mainloop()
