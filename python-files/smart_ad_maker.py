
# Updated Smart Ad Maker + Chrome Extension Integration
import PySimpleGUI as sg
import os
import shutil
import json
from PIL import Image

# Set GUI theme
try:
    sg.theme('LightGreen')
except:
    pass  # fallback in case theme method is unavailable

layout = [
    [sg.Text('🖼️ اشتہار کی تصویر اپ لوڈ کریں | Upload Ad Image')],
    [sg.Input(key='-FILE-', enable_events=True), sg.FileBrowse(file_types=(('Image Files', '*.png *.jpg *.jpeg'),))],
    [sg.Image(key='-IMAGE-')],

    [sg.Text('📝 اشتہار کا عنوان | Ad Title')],
    [sg.Multiline(size=(60, 2), key='-TITLE-')],

    [sg.Text('📄 اشتہار کی تفصیل | Ad Description')],
    [sg.Multiline(size=(60, 6), key='-DESC-')],

    [sg.Text('💰 قیمت | Price')],
    [sg.Input(key='-PRICE-')],

    [sg.Button('📥 فیس بک اشتہار درآمد کریں | Import FB Ad'), sg.Button('✨ ٹیکسٹ صاف کریں | AI Text Cleanup'), sg.Button('💾 اشتہار محفوظ کریں | Save Final Ad')],
    [sg.StatusBar('', size=(60, 1), key='-STATUS-')]
]

window = sg.Window('اسمارٹ ایڈ میکر | Smart Ad Maker', layout, finalize=True)

image_path = None

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    if event == '-FILE-':
        image_path = values['-FILE-']
        if os.path.exists(image_path):
            window['-IMAGE-'].update(filename=image_path, size=(400, 300))

    if event == '📥 فیس بک اشتہار درآمد کریں | Import FB Ad':
        json_file = sg.popup_get_file('Import Facebook Ad JSON', file_types=(('JSON Files', '*.json'),))
        if json_file and os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                ad_data = json.load(f)
                window['-TITLE-'].update(ad_data.get('title', ''))
                window['-DESC-'].update(ad_data.get('description', ''))
                window['-PRICE-'].update(ad_data.get('price', ''))
                img_path = ad_data.get('image_path')
                if img_path and os.path.exists(img_path):
                    image_path = img_path
                    window['-IMAGE-'].update(filename=image_path, size=(400, 300))
            window['-STATUS-'].update('✔️ Facebook ad imported')

    if event == '✨ ٹیکسٹ صاف کریں | AI Text Cleanup':
        title = values['-TITLE-'].strip().title()
        desc = values['-DESC-'].strip().replace('!!', '!').replace('  ', ' ').capitalize()
        price = values['-PRICE-'].strip()
        window['-TITLE-'].update(value=title)
        window['-DESC-'].update(value=desc)
        window['-PRICE-'].update(value=price)
        window['-STATUS-'].update('✔️ Text cleaned')

    if event == '💾 اشتہار محفوظ کریں | Save Final Ad':
        if not image_path or not os.path.exists(image_path):
            sg.popup_error('⚠️ براہ کرم تصویر منتخب کریں | Please select an image file')
            continue

        folder = sg.popup_get_folder('💾 محفوظ کرنے کے لیے فولڈر منتخب کریں | Select Save Folder')
        if folder:
            img_name = os.path.basename(image_path)
            final_img_path = os.path.join(folder, img_name)
            shutil.copy(image_path, final_img_path)

            data = {
                'title': values['-TITLE-'].strip(),
                'description': values['-DESC-'].strip(),
                'price': values['-PRICE-'].strip(),
                'image_path': final_img_path
            }

            with open(os.path.join(folder, 'final_ad.json'), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            sg.popup('✅ اشتہار محفوظ ہو گیا | Ad Saved', f'✔️ All ad data saved to: {folder}')
            window['-STATUS-'].update('✔️ Ad saved successfully')

window.close()
