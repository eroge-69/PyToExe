from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager

import os
import sys

# Get the absolute path to the project root (two levels up from current file)
ROOT_FOLDER= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_FOLDER)

from Resources.ModuleSet1 import *   
from Resources.ModuleSet2 import *         # Import All Nessery Modules

ROOT_FOLDER= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 

SKIN = os.path.join(ROOT_FOLDER, 'Resources', 'Skins', 'Aadhaar.Kv')

ZIP_FILE = os.path.join(ROOT_FOLDER, 'Resources', 'Documents', 'E_Aadhaar.zip')


# Construct the absolute font path
# Construct the absolute font path
Label_font1 = os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'NotoSerifDevanagari-Bold.ttf')


fontE1 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'Times New Roman.ttf'), 32)
fontE2 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'Times New Roman Bold.ttf'), 40)
fontE3 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'Arial Medium.ttf'), 24)
fontE4 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'Times New Roman Bold.ttf'), 60)
fontE5 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'Times New Roman.ttf'), 30)


fontH1 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'NotoSerifDevanagari-Medium.ttf'), 32)
fontH2 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'NotoSerifDevanagari-Bold.ttf'), 40)
fontH3 = ImageFont.truetype(os.path.join(ROOT_FOLDER, 'Resources', 'Fonts', 'NotoSerifDevanagari-Regular.ttf'), 30)

# Register the font properly (name should be a valid string)
LabelBase.register(name="Hindi1", fn_regular=Label_font1)

from PIL import Image, ImageDraw, ImageFont
def draw_hindi_text_pillow(img: Image.Image, text: str, font_path: str, size: int, position=(0, 0)) -> Image.Image:
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, size)
    draw.text(position, text, fill=(0, 0, 0), font=font)
    return img


class AadhaarScreen(Screen):
    pass

class MainApp(MDApp):

    image_path = StringProperty("")
    Final_E = StringProperty("")

    def build(self):
        return Builder.load_file(SKIN)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.debounce_events = {}   # always exists from start
    
         
    def update_combined_Eng(self):  
        screen = self.root.get_screen("AadhaarScreen")

        AL01 = screen.ids.AL01.text
        AL02 = screen.ids.AL02.text
        AL03 = screen.ids.AL03.text
        AL04 = screen.ids.AL04.text
        AL05 = screen.ids.AL05.text
        AL06 = screen.ids.AL06.text
        AL07 = screen.ids.AL07.text
        #AL08 = screen.ids.AL08.text
        AL09 = screen.ids.AL09.text
        AL10 = screen.ids.AL10.text
        AL11 = screen.ids.AL11.text
        #AL12 = screen.ids.AL12.text

        # Build Final_E string
        self.Final_E = f"C/O: {AL01}, {AL02}, {AL03}, {AL04}, {AL05}, {AL06}, PO: {AL07}, DIST: {AL09}, {AL10}- {AL11}"

        # Update ALE text box
        screen.ids.ALE.text = self.Final_E

    def _do_translate(self, input_text, dst_id):

            screen = self.root.get_screen("AadhaarScreen")
            try:
                translated = GoogleTranslator(source="en", target="hi").translate(input_text)

                Clock.schedule_once(lambda dt: setattr(screen.ids[dst_id], "text", translated))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(screen.ids[dst_id], "text", f"Error: {e}"))

    def translate_Name(self):
        screen = self.root.get_screen("AadhaarScreen")
        name_input = screen.ids["NameE"].text.strip()

        if name_input:
            self.executor.submit(self._do_translate, name_input, "NameH")
        else:
            screen.ids["NameH"].text = ""

    def translate_Address(self):
        screen = self.root.get_screen("AadhaarScreen")
        name_input = screen.ids["ALE"].text.strip()

        if name_input:
            self.executor.submit(self._do_translate, name_input, "ALH")
        else:
            screen.ids["ALH"].text = ""

    def on_gender_select(self, gender):
            self.Gender = gender

    def select_path(self, path):
        self.image_path = path
        filename = os.path.basename(path)

        # Close manager first to avoid UI overlap
        self.exit_manager()

        # Show feedback after closing
        snackbar = MDSnackbar(
            MDSnackbarText(text=f"Selected Image: {filename}"),
            duration=2,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8
        )
        snackbar.open()

    def init_file_manager(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,  # now this exists
            preview=True,
        )
            
    def file_manager_open(self):
        if not hasattr(self, 'file_manager'):
            self.init_file_manager()

        if platform == 'android':
            try:
                from plyer import storagepath
                storage_path = storagepath.get_external_storage_dir()
                self.file_manager.show(storage_path)  # Open file manager in external storage
            except ImportError:
                self.file_manager.show(self.user_data_dir)  # Fallback to internal storage
        else:
            from plyer import filechooser
            paths = filechooser.open_file(
                title="Select File",
                filters=[("Image files Only", "*.jpg;*.jpeg;*.png")],
                multiple=False
            )
            if paths:
                self.image_path = paths[0]  # ✅ Store the selected path
                filename = os.path.basename(paths[0])
                snackbar = MDSnackbar(
                    MDSnackbarText(text=f"Selected Image: {filename}")
                )
            else:
                snackbar = MDSnackbar(
                    MDSnackbarText(text="No image selected or operation cancelled.")
                )
            snackbar.open()

    def exit_manager(self, *args):
        if platform == 'android':
            if hasattr(self, 'file_manager') and self.file_manager:
                self.file_manager.close()
        else:
            if hasattr(self, 'file_popup') and self.file_popup:
                self.file_popup.dismiss()
                self.file_popup = None  # Optional: clear reference

    def save_image(self):

        # Get text field values
        screen = self.root.get_screen('AadhaarScreen')
        NameE = screen.ids.NameE.text
        NameH = screen.ids.NameH.text
        
        DOB = screen.ids.DOB.text
        AID = screen.ids.AID.text
        Gender = self.Gender
        Aadhaar= screen.ids.Aadhaar.text
        VID=    screen.ids.VID.text
        ENO= screen.ids.ENO.text

        AL01 = screen.ids.AL01.text
        AL02 = screen.ids.AL02.text
        AL03 = screen.ids.AL03.text
        AL04 = screen.ids.AL04.text
        AL05 = screen.ids.AL05.text
        AL06 = screen.ids.AL06.text
        AL07 = screen.ids.AL07.text
        AL08 = screen.ids.AL08.text
        AL09 = screen.ids.AL09.text
        AL10 = screen.ids.AL10.text
        AL11 = screen.ids.AL11.text
        AL12 = screen.ids.AL12.text

        ALE= screen.ids.ALE.text
        ALH = screen.ids.ALH.text

        DOD = screen.ids.DOD.text
        dt = datetime.strptime(DOD, "%d/%m/%Y")
        XDOD2 = dt.strftime("%Y.%m.%d")
        DOD2= f"{XDOD2} 10:50:10"
    
        if not self.image_path:
            snackbar = MDSnackbar(
                MDSnackbarText(text="Please select an image first"),
                duration=2,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8
            )
            snackbar.open()
            return

        try:


            # Image files inside ZIP
            image_filename = 'E_Aadhaar.jpg'  # Base image

            # Open images from ZIP
            with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
                with zip_ref.open(image_filename) as image_file:
                    img = PILImage.open(io.BytesIO(image_file.read())).convert("RGBA")  # ✅ Base image

#...............browsed Phot Paste........................................
 
            self_browsed = PILImage.open(self.image_path).resize((240, 285)).convert("RGBA")  # ✅ Browsed image
            img.paste(self_browsed, (280,2350), self_browsed)  

#...............Adhaar No Issued part........................................
            draw = ImageDraw.Draw(img)

            # Create a transparent image for the rotated text
            temp_img = PILImage.new('RGBA', (500, 100), (255, 255, 255, 0)) 
            temp_draw = ImageDraw.Draw(temp_img)

            temp_draw.text((40, 40), f"Aadhaar no. issued: {AID}", font=fontE5, fill="black")

            rotated_text = temp_img.rotate(90, expand=True) 
    
            img.paste(rotated_text, (175,2260), rotated_text)    

#...............Date of Issue Part........................................

            draw = ImageDraw.Draw(img)

            # Create a transparent image for the rotated text
            temp_img = PILImage.new('RGBA', (500, 100), (255, 255, 255, 0)) 
            temp_draw = ImageDraw.Draw(temp_img)

            temp_draw.text((40, 40), f"Details as on: {DOD}", font=fontE5, fill="black")

            rotated_text = temp_img.rotate(90, expand=True) 
    
            img.paste(rotated_text, (1230,2260), rotated_text)    

# ......................Front Part..............................

            x, y = 375, 980
            # First draw Hindi text
            hindi_text = "नामांकन क्रम/ "
            draw.text((x, y), hindi_text, font=fontH2, fill="black")

            # Measure Hindi text width to place English part after it
            hindi_width = draw.textlength(hindi_text, font=fontH2)

            # Now draw English text
            english_text = "Enrollment No.: " + ENO
            draw.text((x + hindi_width, y), english_text, font=fontE2, fill="black")

            draw.text((410,1802), DOD2, font=fontE3, fill="black")

            draw.text((500,2030), Aadhaar, font=fontE4, fill="black")
            draw.text((500,2090), "VID: "+VID, font=fontE2, fill="black")

            draw.text((1630,2690), Aadhaar, font=fontE4, fill="black")
            draw.text((1630,2755), "VID: "+VID, font=fontE2, fill="black")

            draw.text((500,2740), Aadhaar, font=fontE4, fill="black")

            x = 553
            y = 2346

            values = [NameH, NameE, "जन्म तिथि/DOB: " + DOB, Gender]

            # Auto-select font based on text language
            def pick_font(text):
                for ch in text:
                    if '\u0900' <= ch <= '\u097F':  # Hindi (Devanagari Unicode block)
                        return fontH1
                return fontE1  # Default to English

            # Create mapping with y incremented by 15 for each value
            text_data = {(x, y + i * 40): val for i, val in enumerate(values)}

            for (tx, ty), val in text_data.items():
                if val:  # skip empty values
                    font = pick_font(str(val))
                    draw.text((tx, ty), str(val), font=font, fill="black")


            values = [
                "To",
                NameH,
                NameE,
                "C/O: " + AL01 if AL01 else "",
                AL02,
                AL03,
                AL04,
                AL05,
                "VTC: " + AL06 if AL06 else "",
                "PO: " + AL07 if AL07 else "",
                "Sub District: " + AL08 if AL08 else "",
                "District: " + AL09 if AL09 else "",
                "State: " + AL10 if AL10 else "",
                "PIN CODE: " + AL11 if AL11 else "",
                "Mobile: " + AL12 if AL12 else ""
            ]
            x = 375
            y = 1060
            line_y = y  # track actual Y position

            for val in values:
                if val:  # only print if not empty
                    # Use fontH1 only for NameH
                    if val == NameH:
                        draw.text((x, line_y), str(val), font=fontH1, fill="black")
                    else:
                        draw.text((x, line_y), str(val), font=fontE1, fill="black")

                    line_y += 40  # increase Y only if something was drawn

#...................... Adress Part...................................             
            
            def draw_justified_block(draw, text, font, x_start, y_start, max_width, line_spacing=36):
                """Draws justified paragraph (multi-line) and returns new y position."""
                def get_text_width(word):
                    bbox = font.getbbox(word)
                    return bbox[2] - bbox[0]

                words = text.split()
                current_line = []
                current_width = 0
                space_width = get_text_width(" ")
                y = y_start

                for word in words:
                    word_width = get_text_width(word)
                    if current_line and (current_width + word_width + space_width) > max_width:
                        # Justify line
                        draw_line(current_line, draw, font, x_start, y, max_width)
                        y += line_spacing
                        current_line = [word]
                        current_width = word_width
                    else:
                        current_line.append(word)
                        if current_width > 0:
                            current_width += space_width
                        current_width += word_width

                # Last line left aligned
                if current_line:
                    draw_line(current_line, draw, font, x_start, y, max_width, justify=False)
                    y += line_spacing

                return y


            def draw_line(words, draw, font, x_start, y_start, max_width, justify=True):
                def get_text_width(word):
                    bbox = font.getbbox(word)
                    return bbox[2] - bbox[0]

                if len(words) == 1 or not justify:
                    # Always left align single-word lines
                    text = " ".join(words)
                    draw.text((x_start, y_start), text, font=font, fill=(0, 0, 0))
                    return

                word_widths = [get_text_width(w) for w in words]
                total_word_width = sum(word_widths)
                total_spaces = len(words) - 1
                remaining_space = max_width - total_word_width

                # Normal space width
                base_space = get_text_width(" ")

                # ✅ Mild justification: only add up to +1px per space, no big gaps
                extra_per_space = min(remaining_space / total_spaces, 1)

                x = x_start
                for i, word in enumerate(words):
                    draw.text((x, y_start), word, font=font, fill=(0, 0, 0))
                    x += word_widths[i]
                    if i < total_spaces:
                        x += base_space + extra_per_space

            x, y = 1320, 2340

            # Step 1: "पता:"
            draw.text((x, y), "पता:", font=fontH3, fill="black")

            # Step 2: Move down 30
            y += 30

            # Step 3: Hindi address justified
            y = draw_justified_block(draw, ALH, fontH3, x_start=x, y_start=y, max_width=585, line_spacing=36)

            # Step 4: Gap after last Hindi line
            y += 10

            # Step 5: "Address:"
            draw.text((x, y), "Address:", font=fontE5, fill="black")

            # Step 6: Move down 30
            y += 36

            # Step 7: English address justified
            draw_justified_block(draw, ALE.strip(), fontE5, x_start=x, y_start=y, max_width=585, line_spacing=36)



            draw = ImageDraw.Draw(img)
                
            img = img.convert("RGB")
        
            if platform == 'android':
            
    # Get the Environment class from Android
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
    # Access the primary external storage directory
                external_storage = Environment.getExternalStorageDirectory()
    # Convert the Java path to a string and then to a Python string
                external_storage_path = external_storage.getAbsolutePath()
    # Define the save path
                save_path = os.path.join(external_storage_path, 'Documents', NameE +' E_Adhaar.Pdf')
    
            else:
                save_path = os.path.join('C:/Documents/', NameE + ' E_Adhaar.Pdf')

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # Save as PDF
            img.save(save_path, "PDF", dpi=(300, 300))

# Success message
            snackbar = MDSnackbar(
                MDSnackbarText(text=f"PDF saved at {save_path}"),
                duration=2,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8
            )
            snackbar.open()

            # Error message (inside except block)
        except Exception as e:
            snackbar = MDSnackbar(
                MDSnackbarText(text=f"Error: {str(e)}"),
                duration=2,
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8
            )
            snackbar.open()

if __name__ == '__main__':
    MainApp().run()