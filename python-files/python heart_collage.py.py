import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import numpy as np
from math import sin, cos, pi

# Convert RGB to HSV
def rgb_to_hsv(rgb):
    r,g,b=[x/255.0 for x in rgb]
    mx=max(r,g,b)
    mn=min(r,g,b)
    diff=mx-mn
    h=s=v=0
    v=mx
    s=0 if mx==0 else diff/mx
    if diff==0:h=0
    elif mx==r:h=(60*((g-b)/diff)+360)%360
    elif mx==g:h=(60*((b-r)/diff)+120)%360
    elif mx==b:h=(60*((r-g)/diff)+240)%360
    return (h,s,v)

# Add drop shadow to an image
def add_shadow(img, offset=(5,5), background_color=(255,255,255)):
    shadow = Image.new("RGBA",(img.width+offset[0]*2,img.height+offset[1]*2),(0,0,0,0))
    shadow_img = Image.new("RGBA",(img.width,img.height),(0,0,0,128))
    shadow.paste(shadow_img,(offset[0],offset[1]))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    combined = Image.new("RGBA", shadow.size, background_color+(255,))
    combined.paste(shadow,(0,0),shadow)
    combined.paste(img,(offset[0],offset[1]),img.convert("RGBA"))
    return combined

# Generate heart shape mask
def generate_heart_mask(width, height, scale=15):
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    for t in np.linspace(0, 2*pi, 2000):
        x = 16 * sin(t)**3
        y = 13*cos(t) -5*cos(2*t)-2*cos(3*t)-cos(4*t)
        px = int(width/2 + x*scale)
        py = int(height/2 - y*scale)
        draw.point((px, py), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=2))
    return mask

# Check if a point is inside heart shape (mask)
def point_in_mask(mask, x, y):
    if x<0 or y<0 or x>=mask.width or y>=mask.height: return False
    return mask.getpixel((x,y))>0

class HeartCollageApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Heart Shaped Collage")
        self.master.geometry("950x750")

        self.images=[]
        self.image_hues=[]
        self.prominent_images=[]
        self.central_image=None
        self.collage_image=None
        self.positions=[]
        self.img_size=80
        self.mask=None

        self.drag_data={"x":0,"y":0,"item":None}
        self.setup_ui()

    def setup_ui(self):
        frame=tk.Frame(self.master)
        frame.pack(side="top", pady=5)

        tk.Button(frame,text="Select Image Folder",command=self.select_folder).pack(side="left", padx=5)
        tk.Button(frame,text="Select Central Image",command=self.select_central_image).pack(side="left", padx=5)
        tk.Button(frame,text="Select Prominent Images",command=self.select_prominent_images).pack(side="left", padx=5)
        tk.Button(frame,text="Generate Collage",command=self.generate_collage).pack(side="left", padx=5)
        tk.Button(frame,text="Save Collage",command=self.save_collage).pack(side="left", padx=5)

        tk.Label(frame,text="Base Image Size:").pack(side="left", padx=5)
        self.img_size_var=tk.IntVar(value=80)
        tk.Entry(frame,textvariable=self.img_size_var,width=5).pack(side="left")

        self.canvas=tk.Canvas(self.master,width=900,height=650,bg="white")
        self.canvas.pack(pady=10)
        self.canvas.bind("<ButtonPress-1>",self.start_drag)
        self.canvas.bind("<B1-Motion>",self.do_drag)
        self.canvas.bind("<ButtonRelease-1>",self.end_drag)

    def select_folder(self):
        folder=filedialog.askdirectory()
        if folder:
            self.images=[]
            self.image_hues=[]
            for file in os.listdir(folder):
                if file.lower().endswith(("jpg","jpeg","png")):
                    img=Image.open(os.path.join(folder,file))
                    self.images.append(img)
                    self.image_hues.append(rgb_to_hsv(np.array(img.resize((50,50))).mean(axis=(0,1)))[0])
            messagebox.showinfo("Loaded",f"{len(self.images)} images loaded")

    def select_central_image(self):
        file=filedialog.askopenfilename(filetypes=[("Images","*.jpg *.png *.jpeg")])
        if file:
            self.central_image=Image.open(file)
            messagebox.showinfo("Central Image","Selected central image")

    def select_prominent_images(self):
        files=filedialog.askopenfilenames(filetypes=[("Images","*.jpg *.png *.jpeg")])
        if files:
            self.prominent_images=[Image.open(f) for f in files[:5]]
            messagebox.showinfo("Prominent Images",f"{len(self.prominent_images)} images selected")

    def is_overlapping(self,x,y,w,h):
        for px,py,pw,ph in self.positions:
            if x < px+pw and x+w>px and y<py+ph and y+h>py:
                return True
        return False

    def generate_collage(self):
        if not self.images:
            messagebox.showerror("Error","Load images first"); return

        self.img_size=self.img_size_var.get()
        width, height = 900, 650
        self.mask = generate_heart_mask(width, height, scale=15)
        collage = Image.new("RGB",(width,height),"white")

        all_images=self.prominent_images + [img for img in self.images if img not in self.prominent_images]
        all_hues=[rgb_to_hsv(np.array(img.resize((50,50))).mean(axis=(0,1)))[0] for img in all_images]
        sorted_imgs=[x for _,x in sorted(zip(all_hues,all_images),key=lambda pair:pair[0])]

        self.positions=[]
        # Central image
        if self.central_image:
            c_img=self.central_image.resize((int(self.img_size*2),int(self.img_size*2)))
            c_img_shadow=add_shadow(c_img)
            x=width//2 - c_img.width//2
            y=height//2 - c_img.height//2
            collage.paste(c_img_shadow,(x,y),c_img_shadow)
            self.positions.append([x,y,c_img.width,c_img.height])

        for img in sorted_imgs:
            size=self.img_size*1.5 if img in self.prominent_images else self.img_size
            placed=False
            attempts=0
            while not placed and attempts<5000:
                x=random.randint(0,width-int(size))
                y=random.randint(0,height-int(size))
                cx=x+int(size/2)
                cy=y+int(size/2)
                if point_in_mask(self.mask,cx,cy) and not self.is_overlapping(x,y,size,size):
                    img_resized=img.resize((int(size),int(size)))
                    img_rot=img_resized.rotate(random.randint(0,359),expand=True)
                    img_shadow=add_shadow(img_rot)
                    collage.paste(img_shadow,(x,y),img_shadow)
                    self.positions.append([x,y,size,size])
                    placed=True
                attempts+=1

        self.collage_image=collage
        self.display_collage()
        messagebox.showinfo("Done",f"Heart-shaped collage generated with {len(sorted_imgs)} images")

    def display_collage(self):
        if self.collage_image:
            self.tk_image=ImageTk.PhotoImage(self.collage_image)
            self.canvas.delete("all")
            self.canvas.create_image(0,0,anchor="nw",image=self.tk_image)

    def save_collage(self):
        if not self.collage_image:
            messagebox.showerror("Error","Generate collage first"); return
        file_path=filedialog.asksaveasfilename(defaultextension=".png",
                                              filetypes=[("PNG files","*.png"),("JPEG files","*.jpg")])
        if file_path: self.collage_image.save(file_path); messagebox.showinfo("Saved","Collage saved")

    def start_drag(self,event):
        x,y=event.x,event.y
        items=self.canvas.find_overlapping(x,y,x,y)
        if items: self.drag_data["item"]=items[0]; self.drag_data["x"]=x; self.drag_data["y"]=y

    def do_drag(self,event):
        dx=event.x-self.drag_data["x"]
        dy=event.y-self.drag_data["y"]
        if self.drag_data["item"]: self.canvas.move(self.drag_data["item"],dx,dy); self.drag_data["x"]=event.x; self.drag_data["y"]=event.y

    def end_drag(self,event): self.drag_data["item"]=None

if __name__=="__main__":
    root=tk.Tk()
    app=HeartCollageApp(root)
    root.mainloop()
