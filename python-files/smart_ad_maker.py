# Smart Ad Maker + Chrome Extension Integration
import PySimpleGUI as sg
import os
import shutil
import json
from PIL import Image, ImageTk
import sys

# Set GUI theme
try:
    sg.theme('LightGreen')
except:
    pass  # fallback in case theme method is unavailable

# Function to resize image while maintaining aspect ratio
def resize_image(image_path, max_size=(400, 300)):
    try:
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        sg.popup_error(f"Error loading image: {e}")
        return None

layout = [
    [sg.Text('🖼 اشتہار کی تصویر اپ لوڈ کریں | Upload Ad Image')],
    [sg.Input(key='-FILE-', enable_events=True), 
     sg.FileBrowse(file_types=(('Image Files', '*.png *.jpg *.jpeg *.webp'),)],
    [sg.Image(key='-IMAGE-', size=(400, 300))],

    [sg.Text('📝 اشتہار کا عنوان | Ad Title')],
    [sg.Multiline(size=(60, 2), key='-TITLE-', expand_x=True)],

    [sg.Text('📄 اشتہار کی تفصیل | Ad Description')],
    [sg.Multiline(size=(60, 6), key='-DESC-', expand_x=True)],

    [sg.Text('💰 قیمت | Price')],
    [sg.Input(key='-PRICE-', expand_x=True)],

    [sg.Button('📥 فیس بک اشتہار درآمد کریں | Import FB Ad'), 
     sg.Button('✨ ٹیکسٹ صاف کریں | AI Text Cleanup'), 
     sg.Button('💾 اشتہار محفوظ کریں | Save Final Ad')],
    [sg.StatusBar('تیار | Ready', size=(60, 1), key='-STATUS-', expand_x=True)]
]

window = sg.Window('اسمارٹ ایڈ میکر | Smart Ad Maker', layout, resizable=True)

# Variables to hold image references
current_image = None
image_path = None

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    if event == '-FILE-':
        image_path = values['-FILE-']
        if os.path.exists(image_path):
            try:
                # Update image display with resized version
                current_image = resize_image(image_path)
                if current_image:
                    window['-IMAGE-'].update(data=current_image)
                    window['-STATUS-'].update('✔ تصویر اپ لوڈ ہو گئی | Image uploaded')
            except Exception as e:
                window['-STATUS-'].update(f'✖ تصویر اپ لوڈ میں خرابی | Error: {str(e)}')

    elif event == '📥 فیس بک اشتہار درآمد کریں | Import FB Ad':
        json_file = sg.popup_get_file('Import Facebook Ad JSON', file_types=(('JSON Files', '*.json'),))
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    ad_data = json.load(f)
                    window['-TITLE-'].update(ad_data.get('title', ''))
                    window['-DESC-'].update(ad_data.get('description', ''))
                    window['-PRICE-'].update(ad_data.get('price', ''))
                    img_path = ad_data.get('image_path', '')
                    
                    if img_path and os.path.exists(img_path):
                        image_path = img_path
                        current_image = resize_image(image_path)
                        if current_image:
                            window['-IMAGE-'].update(data=current_image)
                
                window['-STATUS-'].update('✔ Facebook ad imported successfully')
            except Exception as e:
                window['-STATUS-'].update(f'✖ Error importing ad: {str(e)}')

    elif event == '✨ ٹیکسٹ صاف کریں | AI Text Cleanup':
        try:
            title = values['-TITLE-'].strip()
            if title:
                title = title[0].upper() + title[1:]
            
            desc = values['-DESC-'].strip()
            if desc:
                desc = desc.replace('!!', '!').replace('  ', ' ')
                desc = desc[0].upper() + desc[1:]
            
            price = values['-PRICE-'].strip()
            
            window['-TITLE-'].update(value=title)
            window['-DESC-'].update(value=desc)
            window['-PRICE-'].update(value=price)
            window['-STATUS-'].update('✔ Text cleaned and formatted')
        except Exception as e:
            window['-STATUS-'].update(f'✖ Error cleaning text: {str(e)}')

    elif event == '💾 اشتہار محفوظ کریں | Save Final Ad':
        if not image_path or not os.path.exists(image_path):
            sg.popup_error('⚠ براہ کرم تصویر منتخب کریں | Please select an image file')
            continue

        folder = sg.popup_get_folder('💾 محفوظ کرنے کے لیے فولڈر منتخب کریں | Select Save Folder')
        if folder:
            try:
                # Create folder if it doesn't exist
                os.makedirs(folder, exist_ok=True)
                
                # Copy image
                img_name = os.path.basename(image_path)
                final_img_path = os.path.join(folder, img_name)
                shutil.copy2(image_path, final_img_path)

                # Save JSON data
                data = {
                    'title': values['-TITLE-'].strip(),
                    'description': values['-DESC-'].strip(),
                    'price': values['-PRICE-'].strip(),
                    'image_path': final_img_path
                }

                with open(os.path.join(folder, 'final_ad.json'), 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                sg.popup('✅ اشتہار محفوظ ہو گیا | Ad Saved', 
                        f'✔ All ad data saved to: {folder}')
                window['-STATUS-'].update('✔ Ad saved successfully')
            except Exception as e:
                window['-STATUS-'].update(f'✖ Error saving ad: {str(e)}')
                sg.popup_error(f'Error saving ad: {str(e)}')

window.close()