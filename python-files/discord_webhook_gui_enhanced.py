import customtkinter as ctk
from tkinter import messagebox, scrolledtext, filedialog
import requests
import json
import os
from datetime import datetime
from tkcalendar import DateEntry
import threading

# استيراد الملفات المساعدة
from i18n import i18n, save_preferences, load_preferences, save_template, load_template, delete_template, get_available_templates
from scheduler import scheduler
from history import message_history
from validator import WebhookValidator
from profiles import profile_manager
from animations import AnimationManager, CircularProgress

CONFIG_FILE = 'webhook_config.json'

def save_config(webhook_url, username, avatar_url):
    config = {
        'webhook_url': webhook_url,
        'username': username,
        'avatar_url': avatar_url
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'webhook_url': '', 'username': '', 'avatar_url': ''}

# --- Global lists for dynamic elements ---
embed_frames = []
button_frames = []

def send_webhook(scheduled=False):
    """إرسال الرسالة إلى Discord"""
    webhook_url = url_entry.get()
    message_content = message_content_textbox.get("1.0", "end-1c").strip()
    custom_username = username_entry.get()
    custom_avatar_url = avatar_url_entry.get()

    if not webhook_url:
        AnimationManager.error_animation(root, i18n.get_text('please_enter_webhook_url'))
        return

    # التحقق من صحة الويب هوك
    valid, error_msg = WebhookValidator.validate_url(webhook_url)
    if not valid:
        AnimationManager.error_animation(root, error_msg)
        return

    payload = {}
    if message_content:
        payload["content"] = message_content
    if custom_username:
        payload["username"] = custom_username
    if custom_avatar_url:
        payload["avatar_url"] = custom_avatar_url

    embeds_data = []
    for embed_frame_data in embed_frames:
        embed = {}
        embed_title = embed_frame_data['title_entry'].get()
        embed_description = embed_frame_data['description_textbox'].get("1.0", "end-1c").strip()
        embed_color = embed_frame_data['color_entry'].get()
        embed_thumbnail = embed_frame_data['thumbnail_entry'].get()
        embed_image = embed_frame_data['image_entry'].get()
        embed_footer_text = embed_frame_data['footer_text_entry'].get()
        embed_author_name = embed_frame_data['author_name_entry'].get()
        embed_author_url = embed_frame_data['author_url_entry'].get()

        if embed_title: embed["title"] = embed_title
        if embed_description: embed["description"] = embed_description
        if embed_color:
            try:
                embed["color"] = int(embed_color.replace("#", ""), 16)
            except ValueError:
                AnimationManager.error_animation(root, i18n.get_text('invalid_embed_color'))
        if embed_thumbnail: embed["thumbnail"] = {"url": embed_thumbnail}
        if embed_image: embed["image"] = {"url": embed_image}
        if embed_footer_text: embed["footer"] = {"text": embed_footer_text}
        if embed_author_name:
            author = {"name": embed_author_name}
            if embed_author_url: author["url"] = embed_author_url
            embed["author"] = author

        fields = []
        for field_data in embed_frame_data['fields']:
            field_name = field_data['name_entry'].get()
            field_value = field_data['value_entry'].get()
            field_inline = field_data['inline_var'].get()
            if field_name and field_value:
                fields.append({"name": field_name, "value": field_value, "inline": field_inline})
        if fields: embed["fields"] = fields

        if embed: embeds_data.append(embed)
    
    if embeds_data:
        payload["embeds"] = embeds_data

    # Components (Buttons)
    buttons_data = []
    for btn_data in button_frames:
        button_label = btn_data['label_entry'].get()
        button_url = btn_data['url_entry'].get()
        if button_label and button_url:
            buttons_data.append({"type": 2, "label": button_label, "style": 5, "url": button_url})
    
    if buttons_data:
        payload["components"] = [{
            "type": 1,
            "components": buttons_data
        }]

    if not payload:
        AnimationManager.error_animation(root, i18n.get_text('please_enter_message_or_embed'))
        return

    # التحقق الشامل من الـ payload
    valid, errors = WebhookValidator.validate_complete_payload(payload)
    if not valid:
        error_text = "\n".join(errors)
        AnimationManager.error_animation(root, error_text)
        return

    headers = {"Content-Type": "application/json"}

    # عرض نافذة loading
    if not scheduled:
        loading_window = AnimationManager.loading_animation(root, i18n.get_text('send_message') + "...")
    
    def send_in_thread():
        try:
            response = requests.post(webhook_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # حفظ في السجل
            message_history.add_entry(webhook_url, payload, success=True)
            
            # إغلاق نافذة loading
            if not scheduled:
                loading_window.destroy()
                AnimationManager.success_animation(root, i18n.get_text('message_sent_successfully'))
            
            # حفظ الإعدادات
            save_config(webhook_url, custom_username, custom_avatar_url)
            
        except requests.exceptions.RequestException as e:
            # حفظ في السجل
            message_history.add_entry(webhook_url, payload, success=False, error_message=str(e))
            
            # إغلاق نافذة loading
            if not scheduled:
                loading_window.destroy()
                AnimationManager.error_animation(root, i18n.get_text('error_sending_message', error=e))
    
    # إرسال في thread منفصل
    thread = threading.Thread(target=send_in_thread, daemon=True)
    thread.start()

def validate_webhook_ui():
    """التحقق من صحة الويب هوك وعرض المعلومات"""
    webhook_url = url_entry.get()
    
    if not webhook_url:
        AnimationManager.error_animation(root, i18n.get_text('please_enter_webhook_url'))
        return
    
    # التحقق من صحة الرابط
    valid, error_msg = WebhookValidator.validate_url(webhook_url)
    if not valid:
        AnimationManager.error_animation(root, error_msg)
        return
    
    # عرض نافذة loading
    loading_window = AnimationManager.loading_animation(root, i18n.get_text('validate_webhook') + "...")
    
    def validate_in_thread():
        # التحقق من أن الويب هوك نشط
        valid, data = WebhookValidator.validate_webhook_active(webhook_url)
        
        loading_window.destroy()
        
        if valid:
            # عرض معلومات الويب هوك
            info_window = ctk.CTkToplevel(root)
            info_window.title(i18n.get_text('webhook_info'))
            info_window.geometry("400x300")
            info_window.resizable(False, False)
            info_window.transient(root)
            
            ctk.CTkLabel(
                info_window, 
                text="✓ " + i18n.get_text('webhook_valid'), 
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#00FF00"
            ).pack(pady=20)
            
            info_frame = ctk.CTkFrame(info_window)
            info_frame.pack(pady=10, padx=20, fill="both", expand=True)
            
            ctk.CTkLabel(info_frame, text=f"{i18n.get_text('server_name')} {data.get('name', 'Unknown')}", anchor="w").pack(pady=5, padx=10, fill="x")
            ctk.CTkLabel(info_frame, text=f"{i18n.get_text('channel_id')} {data.get('channel_id', 'Unknown')}", anchor="w").pack(pady=5, padx=10, fill="x")
            
            ctk.CTkButton(info_window, text="OK", command=info_window.destroy).pack(pady=20)
            
            AnimationManager.fade_in(info_window)
        else:
            AnimationManager.error_animation(root, i18n.get_text('webhook_invalid') + "\n" + str(data))
    
    thread = threading.Thread(target=validate_in_thread, daemon=True)
    thread.start()

def preview_message():
    """معاينة الرسالة قبل الإرسال"""
    # سيتم تطويره لاحقاً - عرض نافذة معاينة
    messagebox.showinfo(i18n.get_text('preview_message'), "Feature coming soon!")

def clear_all_fields():
    """مسح جميع الحقول"""
    message_content_textbox.delete("1.0", "end")
    
    # مسح جميع الـ embeds
    while embed_frames:
        remove_embed_ui()
    
    # مسح جميع الأزرار
    while button_frames:
        remove_button_ui()

# --- Theme and Language Management ---
def apply_theme(theme_name):
    ctk.set_appearance_mode(theme_name)
    if theme_name == 'dark':
        ctk.set_default_color_theme("blue")
    elif theme_name == 'light':
        ctk.set_default_color_theme("green")
    elif theme_name == 'blue':
        ctk.set_default_color_theme("blue")
    elif theme_name == 'red':
        ctk.set_default_color_theme("red")
    
    save_preferences(i18n.current_lang, theme_name)

def update_gui_texts():
    """تحديث النصوص في الواجهة"""
    root.title(i18n.get_text('app_title'))
    app_title.configure(text=i18n.get_text('app_title'))
    ims_label.configure(text=i18n.get_text('by_ims'))
    
    # Basic Message Tab
    url_label.configure(text=i18n.get_text('webhook_url'))
    username_label.configure(text=i18n.get_text('username_optional'))
    avatar_url_label.configure(text=i18n.get_text('avatar_url_optional'))
    message_content_label.configure(text=i18n.get_text('message_content'))

    # Embeds Tab
    for embed_frame_data in embed_frames:
        embed_frame_data['title_label'].configure(text=i18n.get_text('embed_title'))
        embed_frame_data['description_label'].configure(text=i18n.get_text('embed_description'))
        embed_frame_data['color_label'].configure(text=i18n.get_text('embed_color_hex'))
        embed_frame_data['thumbnail_label'].configure(text=i18n.get_text('thumbnail_url'))
        embed_frame_data['image_label'].configure(text=i18n.get_text('image_url'))
        embed_frame_data['footer_text_label'].configure(text=i18n.get_text('footer_text'))
        embed_frame_data['author_name_label'].configure(text=i18n.get_text('author_name'))
        embed_frame_data['author_url_label'].configure(text=i18n.get_text('author_url'))
        for field_data in embed_frame_data['fields']:
            field_data['name_label'].configure(text=i18n.get_text('field_name'))
            field_data['value_label'].configure(text=i18n.get_text('field_value'))
            field_data['inline_checkbox'].configure(text=i18n.get_text('inline_field'))
        embed_frame_data['add_field_button'].configure(text=i18n.get_text('add_field'))
        embed_frame_data['remove_field_button'].configure(text=i18n.get_text('remove_field'))

    add_embed_button.configure(text=i18n.get_text('add_embed'))
    remove_embed_button.configure(text=i18n.get_text('remove_embed'))

    # Components Tab
    for btn_data in button_frames:
        btn_data['label_label'].configure(text=i18n.get_text('button_label'))
        btn_data['url_label'].configure(text=i18n.get_text('button_url'))
    add_button_button.configure(text=i18n.get_text('add_button'))
    remove_button_button.configure(text=i18n.get_text('remove_button'))

    send_button.configure(text=i18n.get_text('send_message'))

def set_language_and_update(lang):
    i18n.set_language(lang)
    global tabview
    tabview.destroy()
    tabview = create_tabview(root)
    tabview.pack(pady=10, padx=10, fill="both", expand=True)
    update_gui_texts()
    save_preferences(lang, ctk.get_appearance_mode().lower())
    language_optionmenu.set(lang.upper())

# --- Dynamic Embeds and Fields --- 
def add_embed_ui():
    embed_index = len(embed_frames)
    embed_frame = ctk.CTkFrame(embeds_scroll_frame)
    embed_frame.pack(pady=10, padx=10, fill="x", expand=True)

    ctk.CTkLabel(embed_frame, text=f"Embed {embed_index + 1}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

    # Embed Title
    title_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('embed_title'))
    title_label.pack(anchor="w", padx=5, pady=2)
    title_entry = ctk.CTkEntry(embed_frame, width=400)
    title_entry.pack(fill="x", padx=5, pady=2)

    # Embed Description
    description_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('embed_description'))
    description_label.pack(anchor="w", padx=5, pady=2)
    description_textbox = ctk.CTkTextbox(embed_frame, height=70, width=400)
    description_textbox.pack(fill="x", padx=5, pady=2)

    # Embed Color
    color_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('embed_color_hex'))
    color_label.pack(anchor="w", padx=5, pady=2)
    color_entry = ctk.CTkEntry(embed_frame, width=400)
    color_entry.pack(fill="x", padx=5, pady=2)

    # Thumbnail URL
    thumbnail_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('thumbnail_url'))
    thumbnail_label.pack(anchor="w", padx=5, pady=2)
    thumbnail_entry = ctk.CTkEntry(embed_frame, width=400)
    thumbnail_entry.pack(fill="x", padx=5, pady=2)

    # Image URL
    image_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('image_url'))
    image_label.pack(anchor="w", padx=5, pady=2)
    image_entry = ctk.CTkEntry(embed_frame, width=400)
    image_entry.pack(fill="x", padx=5, pady=2)

    # Footer Text
    footer_text_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('footer_text'))
    footer_text_label.pack(anchor="w", padx=5, pady=2)
    footer_text_entry = ctk.CTkEntry(embed_frame, width=400)
    footer_text_entry.pack(fill="x", padx=5, pady=2)

    # Author Name
    author_name_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('author_name'))
    author_name_label.pack(anchor="w", padx=5, pady=2)
    author_name_entry = ctk.CTkEntry(embed_frame, width=400)
    author_name_entry.pack(fill="x", padx=5, pady=2)

    # Author URL
    author_url_label = ctk.CTkLabel(embed_frame, text=i18n.get_text('author_url'))
    author_url_label.pack(anchor="w", padx=5, pady=2)
    author_url_entry = ctk.CTkEntry(embed_frame, width=400)
    author_url_entry.pack(fill="x", padx=5, pady=2)

    # Fields section
    fields_frame = ctk.CTkFrame(embed_frame)
    fields_frame.pack(pady=5, padx=5, fill="x", expand=True)
    ctk.CTkLabel(fields_frame, text="Fields", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)

    field_widgets = []

    def add_field_ui_for_embed():
        field_row = len(field_widgets)
        field_sub_frame = ctk.CTkFrame(fields_frame)
        field_sub_frame.pack(pady=2, padx=5, fill="x", expand=True)

        name_label = ctk.CTkLabel(field_sub_frame, text=i18n.get_text('field_name'))
        name_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        name_entry = ctk.CTkEntry(field_sub_frame, width=150)
        name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        value_label = ctk.CTkLabel(field_sub_frame, text=i18n.get_text('field_value'))
        value_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        value_entry = ctk.CTkEntry(field_sub_frame, width=150)
        value_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        inline_var = ctk.BooleanVar(value=False)
        inline_checkbox = ctk.CTkCheckBox(field_sub_frame, text=i18n.get_text('inline_field'), variable=inline_var)
        inline_checkbox.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        field_widgets.append({
            'frame': field_sub_frame,
            'name_label': name_label,
            'name_entry': name_entry,
            'value_label': value_label,
            'value_entry': value_entry,
            'inline_var': inline_var,
            'inline_checkbox': inline_checkbox
        })
        fields_frame.grid_columnconfigure(1, weight=1)

    def remove_field_ui_for_embed():
        if field_widgets:
            last_field = field_widgets.pop()
            last_field['frame'].destroy()

    add_field_button = ctk.CTkButton(fields_frame, text=i18n.get_text('add_field'), command=add_field_ui_for_embed)
    add_field_button.pack(pady=5, padx=5)
    remove_field_button = ctk.CTkButton(fields_frame, text=i18n.get_text('remove_field'), command=remove_field_ui_for_embed)
    remove_field_button.pack(pady=2, padx=5)

    embed_frames.append({
        'frame': embed_frame,
        'title_label': title_label,
        'title_entry': title_entry,
        'description_label': description_label,
        'description_textbox': description_textbox,
        'color_label': color_label,
        'color_entry': color_entry,
        'thumbnail_label': thumbnail_label,
        'thumbnail_entry': thumbnail_entry,
        'image_label': image_label,
        'image_entry': image_entry,
        'footer_text_label': footer_text_label,
        'footer_text_entry': footer_text_entry,
        'author_name_label': author_name_label,
        'author_name_entry': author_name_entry,
        'author_url_label': author_url_label,
        'author_url_entry': author_url_entry,
        'fields_frame': fields_frame,
        'fields': field_widgets,
        'add_field_button': add_field_button,
        'remove_field_button': remove_field_button
    })
    update_gui_texts()

def remove_embed_ui():
    if embed_frames:
        last_embed = embed_frames.pop()
        last_embed['frame'].destroy()

# --- Dynamic Buttons --- 
def add_button_ui():
    button_index = len(button_frames)
    button_frame = ctk.CTkFrame(components_scroll_frame)
    button_frame.pack(pady=5, padx=10, fill="x", expand=True)

    ctk.CTkLabel(button_frame, text=f"Button {button_index + 1}", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)

    label_label = ctk.CTkLabel(button_frame, text=i18n.get_text('button_label'))
    label_label.pack(anchor="w", padx=5, pady=2)
    label_entry = ctk.CTkEntry(button_frame, width=300)
    label_entry.pack(fill="x", padx=5, pady=2)

    url_label = ctk.CTkLabel(button_frame, text=i18n.get_text('button_url'))
    url_label.pack(anchor="w", padx=5, pady=2)
    url_entry = ctk.CTkEntry(button_frame, width=300)
    url_entry.pack(fill="x", padx=5, pady=2)

    button_frames.append({
        'frame': button_frame,
        'label_label': label_label,
        'label_entry': label_entry,
        'url_label': url_label,
        'url_entry': url_entry
    })
    update_gui_texts()

def remove_button_ui():
    if button_frames:
        last_button = button_frames.pop()
        last_button['frame'].destroy()


# --- Template Management ---
def save_current_template():
    template_name = template_name_entry.get().strip()
    if not template_name:
        AnimationManager.error_animation(root, i18n.get_text('enter_template_name'))
        return

    template_data = {
        'webhook_url': url_entry.get(),
        'username': username_entry.get(),
        'avatar_url': avatar_url_entry.get(),
        'message_content': message_content_textbox.get("1.0", "end-1c"),
        'embeds': [],
        'buttons': []
    }

    for embed_frame_data in embed_frames:
        embed_data = {
            'title': embed_frame_data['title_entry'].get(),
            'description': embed_frame_data['description_textbox'].get("1.0", "end-1c"),
            'color': embed_frame_data['color_entry'].get(),
            'thumbnail': embed_frame_data['thumbnail_entry'].get(),
            'image': embed_frame_data['image_entry'].get(),
            'footer_text': embed_frame_data['footer_text_entry'].get(),
            'author_name': embed_frame_data['author_name_entry'].get(),
            'author_url': embed_frame_data['author_url_entry'].get(),
            'fields': []
        }
        for field_data in embed_frame_data['fields']:
            field_info = {
                'name': field_data['name_entry'].get(),
                'value': field_data['value_entry'].get(),
                'inline': field_data['inline_var'].get()
            }
            embed_data['fields'].append(field_info)
        template_data['embeds'].append(embed_data)

    for btn_data in button_frames:
        button_info = {
            'label': btn_data['label_entry'].get(),
            'url': btn_data['url_entry'].get()
        }
        template_data['buttons'].append(button_info)

    save_template(template_name, template_data)
    AnimationManager.success_animation(root, i18n.get_text('template_saved_successfully'))
    update_template_list()

def load_selected_template():
    template_name = template_list_combobox.get()
    if not template_name:
        return

    loaded_data = load_template(template_name)
    if loaded_data:
        url_entry.delete(0, 'end')
        url_entry.insert(0, loaded_data.get('webhook_url', ''))
        username_entry.delete(0, 'end')
        username_entry.insert(0, loaded_data.get('username', ''))
        avatar_url_entry.delete(0, 'end')
        avatar_url_entry.insert(0, loaded_data.get('avatar_url', ''))
        message_content_textbox.delete("1.0", "end")
        message_content_textbox.insert("1.0", loaded_data.get('message_content', ''))

        while embed_frames:
            remove_embed_ui()
        
        for embed_data in loaded_data.get('embeds', []):
            add_embed_ui()
            current_embed_frame = embed_frames[-1]
            current_embed_frame['title_entry'].insert(0, embed_data.get('title', ''))
            current_embed_frame['description_textbox'].insert("1.0", embed_data.get('description', ''))
            current_embed_frame['color_entry'].insert(0, embed_data.get('color', ''))
            current_embed_frame['thumbnail_entry'].insert(0, embed_data.get('thumbnail', ''))
            current_embed_frame['image_entry'].insert(0, embed_data.get('image', ''))
            current_embed_frame['footer_text_entry'].insert(0, embed_data.get('footer_text', ''))
            current_embed_frame['author_name_entry'].insert(0, embed_data.get('author_name', ''))
            current_embed_frame['author_url_entry'].insert(0, embed_data.get('author_url', ''))
            
            for field_data in embed_data.get('fields', []):
                current_embed_frame['add_field_button'].invoke()
                current_field_widgets = current_embed_frame['fields'][-1]
                current_field_widgets['name_entry'].insert(0, field_data.get('name', ''))
                current_field_widgets['value_entry'].insert(0, field_data.get('value', ''))
                current_field_widgets['inline_var'].set(field_data.get('inline', False))
        
        while button_frames:
            remove_button_ui()
        
        for button_data in loaded_data.get('buttons', []):
            add_button_ui()
            current_button_frame = button_frames[-1]
            current_button_frame['label_entry'].insert(0, button_data.get('label', ''))
            current_button_frame['url_entry'].insert(0, button_data.get('url', ''))

        AnimationManager.success_animation(root, i18n.get_text('template_loaded_successfully'))
    else:
        AnimationManager.error_animation(root, i18n.get_text('template_not_found'))

def delete_selected_template():
    template_name = template_list_combobox.get()
    if not template_name:
        return
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete template '{template_name}'?"):
        if delete_template(template_name):
            AnimationManager.success_animation(root, i18n.get_text('template_deleted_successfully'))
            update_template_list()
        else:
            AnimationManager.error_animation(root, i18n.get_text('template_not_found'))

def update_template_list():
    templates = get_available_templates()
    template_list_combobox.configure(values=templates)
    if templates:
        template_list_combobox.set(templates[0])
    else:
        template_list_combobox.set("")

# --- Scheduled Messages ---
def schedule_current_message():
    """جدولة الرسالة الحالية"""
    webhook_url = url_entry.get()
    if not webhook_url:
        AnimationManager.error_animation(root, i18n.get_text('please_enter_webhook_url'))
        return
    
    # إنشاء نافذة الجدولة
    schedule_window = ctk.CTkToplevel(root)
    schedule_window.title(i18n.get_text('schedule_message'))
    schedule_window.geometry("500x600")
    schedule_window.resizable(False, False)
    schedule_window.transient(root)
    schedule_window.grab_set()
    
    # اسم الرسالة
    ctk.CTkLabel(schedule_window, text=i18n.get_text('message_name')).pack(pady=5, padx=10, anchor="w")
    message_name_entry = ctk.CTkEntry(schedule_window, width=450)
    message_name_entry.pack(pady=5, padx=10)
    
    # التاريخ والوقت
    ctk.CTkLabel(schedule_window, text=i18n.get_text('scheduled_time')).pack(pady=5, padx=10, anchor="w")
    
    date_frame = ctk.CTkFrame(schedule_window)
    date_frame.pack(pady=5, padx=10, fill="x")
    
    date_picker = DateEntry(date_frame, width=20, background='darkblue', foreground='white', borderwidth=2)
    date_picker.pack(side="left", padx=5)
    
    time_frame = ctk.CTkFrame(date_frame)
    time_frame.pack(side="left", padx=5)
    
    hour_var = ctk.StringVar(value="12")
    minute_var = ctk.StringVar(value="00")
    
    ctk.CTkLabel(time_frame, text="Hour:").pack(side="left", padx=2)
    hour_spinbox = ctk.CTkEntry(time_frame, width=50, textvariable=hour_var)
    hour_spinbox.pack(side="left", padx=2)
    
    ctk.CTkLabel(time_frame, text="Minute:").pack(side="left", padx=2)
    minute_spinbox = ctk.CTkEntry(time_frame, width=50, textvariable=minute_var)
    minute_spinbox.pack(side="left", padx=2)
    
    # نوع التكرار
    ctk.CTkLabel(schedule_window, text=i18n.get_text('repeat_type')).pack(pady=5, padx=10, anchor="w")
    repeat_var = ctk.StringVar(value="none")
    repeat_menu = ctk.CTkOptionMenu(
        schedule_window, 
        values=[
            i18n.get_text('repeat_none'),
            i18n.get_text('repeat_daily'),
            i18n.get_text('repeat_weekly'),
            i18n.get_text('repeat_monthly'),
            i18n.get_text('repeat_custom')
        ],
        variable=repeat_var,
        width=450
    )
    repeat_menu.pack(pady=5, padx=10)
    
    # الفترة المخصصة
    ctk.CTkLabel(schedule_window, text=i18n.get_text('repeat_interval')).pack(pady=5, padx=10, anchor="w")
    interval_entry = ctk.CTkEntry(schedule_window, width=450)
    interval_entry.insert(0, "60")
    interval_entry.pack(pady=5, padx=10)
    
    def save_scheduled():
        message_name = message_name_entry.get().strip()
        if not message_name:
            message_name = f"Scheduled Message {len(scheduler.get_scheduled_messages()) + 1}"
        
        # الحصول على التاريخ والوقت
        selected_date = date_picker.get_date()
        try:
            hour = int(hour_var.get())
            minute = int(minute_var.get())
        except:
            hour = 12
            minute = 0
        
        scheduled_time = datetime(selected_date.year, selected_date.month, selected_date.day, hour, minute)
        
        # تحديد نوع التكرار
        repeat_text = repeat_var.get()
        if repeat_text == i18n.get_text('repeat_none'):
            repeat_type = 'none'
        elif repeat_text == i18n.get_text('repeat_daily'):
            repeat_type = 'daily'
        elif repeat_text == i18n.get_text('repeat_weekly'):
            repeat_type = 'weekly'
        elif repeat_text == i18n.get_text('repeat_monthly'):
            repeat_type = 'monthly'
        else:
            repeat_type = 'custom'
        
        try:
            repeat_interval = int(interval_entry.get())
        except:
            repeat_interval = 60
        
        # إنشاء الـ payload
        message_content = message_content_textbox.get("1.0", "end-1c").strip()
        custom_username = username_entry.get()
        custom_avatar_url = avatar_url_entry.get()
        
        payload = {}
        if message_content:
            payload["content"] = message_content
        if custom_username:
            payload["username"] = custom_username
        if custom_avatar_url:
            payload["avatar_url"] = custom_avatar_url
        
        # إضافة للجدولة
        scheduler.add_scheduled_message(
            webhook_url=webhook_url,
            payload=payload,
            scheduled_time=scheduled_time,
            repeat_type=repeat_type,
            repeat_interval=repeat_interval,
            message_name=message_name
        )
        
        schedule_window.destroy()
        AnimationManager.success_animation(root, i18n.get_text('message_scheduled_successfully'))
        refresh_scheduled_list()
    
    # أزرار
    button_frame = ctk.CTkFrame(schedule_window)
    button_frame.pack(pady=20)
    
    ctk.CTkButton(button_frame, text=i18n.get_text('schedule_message'), command=save_scheduled, width=200).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Cancel", command=schedule_window.destroy, width=100).pack(side="left", padx=5)

def refresh_scheduled_list():
    """تحديث قائمة الرسائل المجدولة"""
    # مسح القائمة الحالية
    for widget in scheduled_list_frame.winfo_children():
        widget.destroy()
    
    # عرض الرسائل المجدولة
    messages = scheduler.get_scheduled_messages()
    
    if not messages:
        ctk.CTkLabel(scheduled_list_frame, text="No scheduled messages", font=ctk.CTkFont(size=14)).pack(pady=20)
        return
    
    for msg in messages:
        msg_frame = ctk.CTkFrame(scheduled_list_frame)
        msg_frame.pack(pady=5, padx=10, fill="x")
        
        # معلومات الرسالة
        info_frame = ctk.CTkFrame(msg_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(info_frame, text=msg['name'], font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{i18n.get_text('next_send')} {msg['next_send']}", font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        if msg['last_sent']:
            ctk.CTkLabel(info_frame, text=f"{i18n.get_text('last_sent')} {msg['last_sent']}", font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        # أزرار التحكم
        control_frame = ctk.CTkFrame(msg_frame)
        control_frame.pack(side="right", padx=5, pady=5)
        
        def toggle_message(msg_id=msg['id'], enabled=not msg['enabled']):
            scheduler.toggle_message(msg_id, enabled)
            refresh_scheduled_list()
        
        def delete_message(msg_id=msg['id']):
            scheduler.remove_scheduled_message(msg_id)
            AnimationManager.success_animation(root, i18n.get_text('message_deleted_successfully'))
            refresh_scheduled_list()
        
        toggle_text = i18n.get_text('disable') if msg['enabled'] else i18n.get_text('enable')
        toggle_color = "#FF0000" if msg['enabled'] else "#00FF00"
        
        ctk.CTkButton(control_frame, text=toggle_text, command=toggle_message, width=80, fg_color=toggle_color).pack(side="left", padx=2)
        ctk.CTkButton(control_frame, text=i18n.get_text('delete'), command=delete_message, width=80, fg_color="#CC0000").pack(side="left", padx=2)

# --- History Management ---
def refresh_history_list():
    """تحديث قائمة سجل الرسائل"""
    # مسح القائمة الحالية
    for widget in history_list_frame.winfo_children():
        widget.destroy()
    
    # عرض الإحصائيات
    stats = message_history.get_statistics()
    stats_frame = ctk.CTkFrame(history_list_frame)
    stats_frame.pack(pady=10, padx=10, fill="x")
    
    ctk.CTkLabel(stats_frame, text=f"{i18n.get_text('total_messages')} {stats['total']}", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
    ctk.CTkLabel(stats_frame, text=f"{i18n.get_text('successful_messages')} {stats['successful']}", font=ctk.CTkFont(size=12), text_color="#00FF00").pack(side="left", padx=10)
    ctk.CTkLabel(stats_frame, text=f"{i18n.get_text('failed_messages')} {stats['failed']}", font=ctk.CTkFont(size=12), text_color="#FF0000").pack(side="left", padx=10)
    ctk.CTkLabel(stats_frame, text=f"{i18n.get_text('success_rate')} {stats['success_rate']:.1f}%", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
    
    # عرض الرسائل
    entries = message_history.get_recent_entries(50)
    
    if not entries:
        ctk.CTkLabel(history_list_frame, text="No messages in history", font=ctk.CTkFont(size=14)).pack(pady=20)
        return
    
    for entry in entries:
        entry_frame = ctk.CTkFrame(history_list_frame)
        entry_frame.pack(pady=5, padx=10, fill="x")
        
        # معلومات الرسالة
        info_frame = ctk.CTkFrame(entry_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        status_icon = "✓" if entry['success'] else "✗"
        status_color = "#00FF00" if entry['success'] else "#FF0000"
        
        ctk.CTkLabel(info_frame, text=f"{status_icon} {entry['timestamp']}", font=ctk.CTkFont(size=12), text_color=status_color).pack(anchor="w")
        
        content_preview = entry['payload'].get('content', '')[:50]
        if content_preview:
            ctk.CTkLabel(info_frame, text=content_preview, font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        # زر إعادة الإرسال
        if entry['success']:
            def resend_message(payload=entry['payload'], webhook=entry['webhook_url']):
                # ملء الحقول بالبيانات
                url_entry.delete(0, 'end')
                url_entry.insert(0, webhook)
                
                if 'content' in payload:
                    message_content_textbox.delete("1.0", "end")
                    message_content_textbox.insert("1.0", payload['content'])
                
                if 'username' in payload:
                    username_entry.delete(0, 'end')
                    username_entry.insert(0, payload['username'])
                
                if 'avatar_url' in payload:
                    avatar_url_entry.delete(0, 'end')
                    avatar_url_entry.insert(0, payload['avatar_url'])
                
                # التبديل إلى تبويب الرسالة الأساسية
                tabview.set(i18n.get_text('basic_message_tab'))
            
            ctk.CTkButton(entry_frame, text=i18n.get_text('resend'), command=resend_message, width=80).pack(side="right", padx=5, pady=5)

def search_history():
    """البحث في السجل"""
    query = history_search_entry.get().strip()
    if not query:
        refresh_history_list()
        return
    
    # مسح القائمة الحالية
    for widget in history_list_frame.winfo_children():
        widget.destroy()
    
    # البحث
    results = message_history.search_entries(query)
    
    if not results:
        ctk.CTkLabel(history_list_frame, text="No results found", font=ctk.CTkFont(size=14)).pack(pady=20)
        return
    
    for entry in results:
        entry_frame = ctk.CTkFrame(history_list_frame)
        entry_frame.pack(pady=5, padx=10, fill="x")
        
        status_icon = "✓" if entry['success'] else "✗"
        status_color = "#00FF00" if entry['success'] else "#FF0000"
        
        ctk.CTkLabel(entry_frame, text=f"{status_icon} {entry['timestamp']}", font=ctk.CTkFont(size=12), text_color=status_color).pack(anchor="w", padx=5)
        
        content_preview = entry['payload'].get('content', '')[:50]
        if content_preview:
            ctk.CTkLabel(entry_frame, text=content_preview, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=5)

# --- Profiles Management ---
def refresh_profiles_list():
    """تحديث قائمة البروفايلات"""
    profiles = profile_manager.get_profile_names()
    profiles_combobox.configure(values=profiles)
    
    current = profile_manager.get_current_profile_name()
    if current:
        profiles_combobox.set(current)
        current_profile_label.configure(text=f"{i18n.get_text('current_profile')} {current}")
    else:
        current_profile_label.configure(text=i18n.get_text('current_profile') + " None")

def create_new_profile():
    """إنشاء بروفايل جديد"""
    name = profile_name_entry.get().strip()
    if not name:
        AnimationManager.error_animation(root, "Please enter a profile name")
        return
    
    webhook_url = url_entry.get()
    username = username_entry.get()
    avatar_url = avatar_url_entry.get()
    description = profile_description_entry.get().strip()
    
    success, message = profile_manager.create_profile(name, webhook_url, username, avatar_url, description)
    
    if success:
        AnimationManager.success_animation(root, i18n.get_text('profile_created_successfully'))
        refresh_profiles_list()
        profile_name_entry.delete(0, 'end')
        profile_description_entry.delete(0, 'end')
    else:
        AnimationManager.error_animation(root, message)

def switch_to_profile():
    """التبديل إلى بروفايل"""
    name = profiles_combobox.get()
    if not name:
        return
    
    success, message = profile_manager.set_current_profile(name)
    
    if success:
        profile = profile_manager.get_profile(name)
        
        # ملء الحقول
        url_entry.delete(0, 'end')
        url_entry.insert(0, profile['webhook_url'])
        
        username_entry.delete(0, 'end')
        username_entry.insert(0, profile['username'])
        
        avatar_url_entry.delete(0, 'end')
        avatar_url_entry.insert(0, profile['avatar_url'])
        
        AnimationManager.success_animation(root, i18n.get_text('profile_switched_successfully'))
        refresh_profiles_list()
    else:
        AnimationManager.error_animation(root, message)

def delete_current_profile():
    """حذف البروفايل الحالي"""
    name = profiles_combobox.get()
    if not name:
        return
    
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{name}'?"):
        success, message = profile_manager.delete_profile(name)
        
        if success:
            AnimationManager.success_animation(root, i18n.get_text('profile_deleted_successfully'))
            refresh_profiles_list()
        else:
            AnimationManager.error_animation(root, message)

# --- Keyboard Shortcuts ---
def setup_keyboard_shortcuts(root_window):
    """إعداد اختصارات لوحة المفاتيح"""
    def on_ctrl_enter(event):
        send_webhook()
    
    def on_ctrl_s(event):
        save_current_template()
    
    def on_ctrl_n(event):
        clear_all_fields()
    
    def on_ctrl_p(event):
        preview_message()
    
    root_window.bind('<Control-Return>', on_ctrl_enter)
    root_window.bind('<Control-s>', on_ctrl_s)
    root_window.bind('<Control-n>', on_ctrl_n)
    root_window.bind('<Control-p>', on_ctrl_p)

# --- Tab Creation Functions ---
def create_tabview(parent):
    new_tabview = ctk.CTkTabview(parent, width=780, height=700)
    
    # Basic Message Tab
    global basic_message_tab
    basic_message_tab = new_tabview.add(i18n.get_text('basic_message_tab'))
    setup_basic_message_tab(basic_message_tab)

    # Embeds Tab
    global embeds_tab, embeds_scroll_frame, embed_buttons_frame, add_embed_button, remove_embed_button
    embeds_tab = new_tabview.add(i18n.get_text('embeds_tab'))
    embeds_scroll_frame = ctk.CTkScrollableFrame(embeds_tab, width=750, height=600)
    embeds_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
    embed_buttons_frame = ctk.CTkFrame(embeds_tab)
    embed_buttons_frame.pack(fill="x", pady=5, padx=5)
    add_embed_button = ctk.CTkButton(embed_buttons_frame, text=i18n.get_text('add_embed'), command=add_embed_ui)
    add_embed_button.pack(side="left", padx=5, pady=5)
    remove_embed_button = ctk.CTkButton(embed_buttons_frame, text=i18n.get_text('remove_embed'), command=remove_embed_ui)
    remove_embed_button.pack(side="left", padx=5, pady=5)

    # Components Tab
    global components_tab, components_scroll_frame, button_controls_frame, add_button_button, remove_button_button
    components_tab = new_tabview.add(i18n.get_text('components_tab'))
    components_scroll_frame = ctk.CTkScrollableFrame(components_tab, width=750, height=600)
    components_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
    button_controls_frame = ctk.CTkFrame(components_tab)
    button_controls_frame.pack(fill="x", pady=5, padx=5)
    add_button_button = ctk.CTkButton(button_controls_frame, text=i18n.get_text('add_button'), command=add_button_ui)
    add_button_button.pack(side="left", padx=5, pady=5)
    remove_button_button = ctk.CTkButton(button_controls_frame, text=i18n.get_text('remove_button'), command=remove_button_ui)
    remove_button_button.pack(side="left", padx=5, pady=5)

    # Scheduled Messages Tab
    global scheduled_tab, scheduled_list_frame
    scheduled_tab = new_tabview.add(i18n.get_text('scheduled_tab'))
    setup_scheduled_tab(scheduled_tab)

    # History Tab
    global history_tab, history_list_frame, history_search_entry
    history_tab = new_tabview.add(i18n.get_text('history_tab'))
    setup_history_tab(history_tab)

    # Profiles Tab
    global profiles_tab, profiles_combobox, profile_name_entry, profile_description_entry, current_profile_label
    profiles_tab = new_tabview.add(i18n.get_text('profiles_tab'))
    setup_profiles_tab(profiles_tab)

    # Settings Tab
    global settings_tab, language_label, language_optionmenu, theme_label, theme_optionmenu, template_frame, template_name_label, template_name_entry, save_template_button, template_list_combobox, load_template_button, delete_template_button
    settings_tab = new_tabview.add(i18n.get_text('settings_tab'))
    setup_settings_tab(settings_tab)

    return new_tabview

def setup_basic_message_tab(parent_tab):
    global url_label, url_entry, username_label, username_entry, avatar_url_label, avatar_url_entry, message_content_label, message_content_textbox
    
    # Webhook URL
    url_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('webhook_url'))
    url_label.pack(anchor="w", padx=10, pady=5)
    
    url_frame = ctk.CTkFrame(parent_tab)
    url_frame.pack(fill="x", padx=10, pady=2)
    
    url_entry = ctk.CTkEntry(url_frame, width=400)
    url_entry.pack(side="left", fill="x", expand=True, padx=5, pady=2)
    
    validate_button = ctk.CTkButton(url_frame, text=i18n.get_text('validate_webhook'), command=validate_webhook_ui, width=150)
    validate_button.pack(side="right", padx=5, pady=2)
    AnimationManager.hover_effect(validate_button, "#1f538d", "#1f6aa5")

    # Username
    username_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('username_optional'))
    username_label.pack(anchor="w", padx=10, pady=5)
    username_entry = ctk.CTkEntry(parent_tab, width=500)
    username_entry.pack(fill="x", padx=10, pady=2)

    # Avatar URL
    avatar_url_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('avatar_url_optional'))
    avatar_url_label.pack(anchor="w", padx=10, pady=5)
    avatar_url_entry = ctk.CTkEntry(parent_tab, width=500)
    avatar_url_entry.pack(fill="x", padx=10, pady=2)

    # Message Content
    message_content_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('message_content'))
    message_content_label.pack(anchor="w", padx=10, pady=5)
    message_content_textbox = ctk.CTkTextbox(parent_tab, height=150, width=500)
    message_content_textbox.pack(fill="both", padx=10, pady=2, expand=True)

def setup_scheduled_tab(parent_tab):
    global scheduled_list_frame
    
    # أزرار التحكم
    control_frame = ctk.CTkFrame(parent_tab)
    control_frame.pack(fill="x", pady=10, padx=10)
    
    schedule_button = ctk.CTkButton(control_frame, text=i18n.get_text('schedule_message'), command=schedule_current_message, width=200)
    schedule_button.pack(side="left", padx=5)
    AnimationManager.hover_effect(schedule_button, "#1f538d", "#1f6aa5")
    
    refresh_button = ctk.CTkButton(control_frame, text="Refresh", command=refresh_scheduled_list, width=100)
    refresh_button.pack(side="left", padx=5)
    
    # قائمة الرسائل المجدولة
    ctk.CTkLabel(parent_tab, text=i18n.get_text('scheduled_messages_list'), font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, padx=10, anchor="w")
    
    scheduled_list_frame = ctk.CTkScrollableFrame(parent_tab, width=750, height=500)
    scheduled_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # تحديث القائمة
    refresh_scheduled_list()

def setup_history_tab(parent_tab):
    global history_list_frame, history_search_entry
    
    # شريط البحث
    search_frame = ctk.CTkFrame(parent_tab)
    search_frame.pack(fill="x", pady=10, padx=10)
    
    ctk.CTkLabel(search_frame, text=i18n.get_text('search')).pack(side="left", padx=5)
    history_search_entry = ctk.CTkEntry(search_frame, width=300)
    history_search_entry.pack(side="left", padx=5)
    
    search_button = ctk.CTkButton(search_frame, text=i18n.get_text('search_history'), command=search_history, width=120)
    search_button.pack(side="left", padx=5)
    
    refresh_button = ctk.CTkButton(search_frame, text="Refresh", command=refresh_history_list, width=100)
    refresh_button.pack(side="left", padx=5)
    
    clear_button = ctk.CTkButton(search_frame, text=i18n.get_text('clear_history'), command=lambda: message_history.clear_history() or refresh_history_list(), width=120, fg_color="#CC0000")
    clear_button.pack(side="left", padx=5)
    
    # قائمة السجل
    history_list_frame = ctk.CTkScrollableFrame(parent_tab, width=750, height=500)
    history_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # تحديث القائمة
    refresh_history_list()

def setup_profiles_tab(parent_tab):
    global profiles_combobox, profile_name_entry, profile_description_entry, current_profile_label
    
    # البروفايل الحالي
    current_profile_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('current_profile') + " None", font=ctk.CTkFont(size=14, weight="bold"))
    current_profile_label.pack(pady=10, padx=10, anchor="w")
    
    # إنشاء بروفايل جديد
    create_frame = ctk.CTkFrame(parent_tab)
    create_frame.pack(fill="x", pady=10, padx=10)
    
    ctk.CTkLabel(create_frame, text=i18n.get_text('profile_name')).pack(anchor="w", padx=5, pady=2)
    profile_name_entry = ctk.CTkEntry(create_frame, width=400)
    profile_name_entry.pack(fill="x", padx=5, pady=2)
    
    ctk.CTkLabel(create_frame, text=i18n.get_text('profile_description')).pack(anchor="w", padx=5, pady=2)
    profile_description_entry = ctk.CTkEntry(create_frame, width=400)
    profile_description_entry.pack(fill="x", padx=5, pady=2)
    
    create_button = ctk.CTkButton(create_frame, text=i18n.get_text('create_profile'), command=create_new_profile, width=200)
    create_button.pack(pady=10)
    AnimationManager.hover_effect(create_button, "#1f538d", "#1f6aa5")
    
    # التبديل بين البروفايلات
    switch_frame = ctk.CTkFrame(parent_tab)
    switch_frame.pack(fill="x", pady=10, padx=10)
    
    ctk.CTkLabel(switch_frame, text="Select Profile:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=5)
    
    profiles_combobox = ctk.CTkComboBox(switch_frame, values=[], width=400)
    profiles_combobox.pack(fill="x", padx=5, pady=5)
    
    button_frame = ctk.CTkFrame(switch_frame)
    button_frame.pack(pady=10)
    
    switch_button = ctk.CTkButton(button_frame, text=i18n.get_text('switch_profile'), command=switch_to_profile, width=150)
    switch_button.pack(side="left", padx=5)
    
    delete_button = ctk.CTkButton(button_frame, text=i18n.get_text('delete_profile'), command=delete_current_profile, width=150, fg_color="#CC0000")
    delete_button.pack(side="left", padx=5)
    
    # تحديث القائمة
    refresh_profiles_list()

def setup_settings_tab(parent_tab):
    global language_label, language_optionmenu, theme_label, theme_optionmenu, template_frame, template_name_label, template_name_entry, save_template_button, template_list_combobox, load_template_button, delete_template_button
    
    # Language Settings
    language_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('language'))
    language_label.pack(anchor="w", padx=10, pady=5)
    language_optionmenu = ctk.CTkOptionMenu(parent_tab, values=["EN", "AR"], command=lambda choice: set_language_and_update(choice.lower()))
    language_optionmenu.set(i18n.current_lang.upper())
    language_optionmenu.pack(anchor="w", padx=10, pady=2)

    # Theme Settings
    theme_label = ctk.CTkLabel(parent_tab, text=i18n.get_text('theme'))
    theme_label.pack(anchor="w", padx=10, pady=5)
    theme_optionmenu = ctk.CTkOptionMenu(parent_tab, values=["Dark", "Light", "Blue", "Red"], command=apply_theme)
    theme_optionmenu.set(preferences.get('theme', 'dark').capitalize())
    theme_optionmenu.pack(anchor="w", padx=10, pady=2)

    # Template Management
    template_frame = ctk.CTkFrame(parent_tab)
    template_frame.pack(fill="x", padx=10, pady=10)

    template_name_label = ctk.CTkLabel(template_frame, text=i18n.get_text('template_name'))
    template_name_label.pack(anchor="w", padx=5, pady=2)
    template_name_entry = ctk.CTkEntry(template_frame, width=300)
    template_name_entry.pack(fill="x", padx=5, pady=2)

    save_template_button = ctk.CTkButton(template_frame, text=i18n.get_text('save_template'), command=save_current_template)
    save_template_button.pack(pady=5, padx=5)

    ctk.CTkLabel(template_frame, text="---").pack(pady=5)

    template_list_combobox = ctk.CTkComboBox(template_frame, values=get_available_templates(), width=300)
    template_list_combobox.pack(fill="x", padx=5, pady=2)
    update_template_list()

    load_template_button = ctk.CTkButton(template_frame, text=i18n.get_text('load_template'), command=load_selected_template)
    load_template_button.pack(pady=5, padx=5)

    delete_template_button = ctk.CTkButton(template_frame, text=i18n.get_text('delete_template'), command=delete_selected_template)
    delete_template_button.pack(pady=5, padx=5)
    
    # Keyboard Shortcuts Info
    ctk.CTkLabel(parent_tab, text="---").pack(pady=10)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('keyboard_shortcuts'), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('shortcut_send'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('shortcut_save'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('shortcut_new'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('shortcut_preview'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=2)
    
    # About
    ctk.CTkLabel(parent_tab, text="---").pack(pady=10)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('about'), font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('version'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=20, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('features'), font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=5)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_scheduled'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_history'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_profiles'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_preview'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_validation'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_animations'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)
    ctk.CTkLabel(parent_tab, text=i18n.get_text('feature_shortcuts'), font=ctk.CTkFont(size=11)).pack(anchor="w", padx=30, pady=2)

# --- Main Window Setup --- 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()

# Load preferences
preferences = load_preferences()
i18n.set_language(preferences.get('language', 'en'))

root.title(i18n.get_text('app_title'))
root.geometry("900x1000")
root.resizable(True, True)

# --- Header --- 
header_frame = ctk.CTkFrame(root, corner_radius=0, fg_color=("#3B8ED0", "#1F6AA5"))
header_frame.pack(fill="x", pady=0, padx=0)

app_title = ctk.CTkLabel(header_frame, text=i18n.get_text('app_title'), font=ctk.CTkFont(size=26, weight="bold"))
app_title.pack(pady=10)

ims_label = ctk.CTkLabel(header_frame, text=i18n.get_text('by_ims'), font=ctk.CTkFont(size=13))
ims_label.pack(pady=5)

# --- Tabview --- 
tabview = create_tabview(root)
tabview.pack(pady=10, padx=10, fill="both", expand=True)

# --- Action Buttons --- 
action_frame = ctk.CTkFrame(root)
action_frame.pack(pady=10, fill="x", padx=10)

send_button = ctk.CTkButton(action_frame, text=i18n.get_text('send_message'), command=send_webhook, font=ctk.CTkFont(size=18, weight="bold"), height=40, width=200)
send_button.pack(side="left", padx=5)
AnimationManager.hover_effect(send_button, "#1f538d", "#1f6aa5")

preview_button = ctk.CTkButton(action_frame, text=i18n.get_text('preview_message'), command=preview_message, height=40, width=150)
preview_button.pack(side="left", padx=5)

clear_button = ctk.CTkButton(action_frame, text="Clear All", command=clear_all_fields, height=40, width=100, fg_color="#CC0000")
clear_button.pack(side="left", padx=5)

# Load initial config
initial_config = load_config()
url_entry.insert(0, initial_config.get('webhook_url', ''))
username_entry.insert(0, initial_config.get('username', ''))
avatar_url_entry.insert(0, initial_config.get('avatar_url', ''))

# Apply initial theme and update texts
apply_theme(preferences.get('theme', 'dark'))
update_gui_texts()

# Setup keyboard shortcuts
setup_keyboard_shortcuts(root)

# Start scheduler
scheduler.start()

# Fade in effect for main window
AnimationManager.fade_in(root)

# Main loop
root.mainloop()

# Stop scheduler on exit
scheduler.stop()
