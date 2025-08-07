from nicegui import ui
import pandas as pd
import threading
import time
from io import BytesIO
import pywhatkit

results = []
sending = False
paused = False
uploaded_excel_content = None
uploaded_contacts_df = None
current_idx = -1

progress = None
wait_time_input = None
delay_input = None
uploader = None
processed_count_label = None
current_status_label = None
table = None
country_code = None

def normalize_phone(phone, country_code='+20'):
    phone = str(phone or '').strip().replace(' ', '').replace('-', '')
    if not phone.startswith('+'):
        phone = country_code + phone.lstrip('0')
    return phone

def send_all_pywhatkit(country_code_val: str, excel_bytes, wait_time_seconds, delay_seconds):
    global results, sending, uploaded_contacts_df, paused, current_idx
    results.clear()
    sending = True
    processed = 0

    try:
        df = pd.read_excel(BytesIO(excel_bytes))
        uploaded_contacts_df = df
    except Exception as e:
        ui.notify(f"❌ Failed to read Excel: {e}", type="negative")
        sending = False
        progress.value = 0
        processed_count_label.text = "Processed: 0"
        current_status_label.text = ""
        current_idx = -1
        refresh_table()
        return

    total = len(df)
    if total == 0:
        ui.notify("Excel is empty!", type="warning")
        sending = False
        progress.value = 0
        processed_count_label.text = "Processed: 0"
        current_status_label.text = ""
        current_idx = -1
        refresh_table()
        return

    for idx, row in df.iterrows():
        if not sending:
            current_idx = -1
            current_status_label.text = ""
            refresh_table()
            break

        current_idx = idx
        refresh_status_panel(idx+1, row)
        refresh_table()
        if table:
            table.update()

        phone_column = None
        for col in df.columns:
            if col.lower().strip() in {"phone", "phonenumber", "number"}:
                phone_column = col
                break
        if phone_column is None:
            ui.notify('No column named Phone/Number found!', type='negative')
            sending = False
            current_idx = -1
            current_status_label.text = ""
            refresh_table()
            break
        phone_number = normalize_phone(row[phone_column], country_code_val)
        message_column = None
        for col in df.columns:
            if col.lower().strip() == "message":
                message_column = col
                break
        message = str(row[message_column]) if message_column else ""

        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message,
                wait_time=wait_time_seconds,
                tab_close=True
            )
        except Exception:
            pass

        processed += 1
        progress.value = processed / total
        processed_count_label.text = f"Processed: {processed} / {total}"

        refresh_status_panel(-1, None)
        refresh_table()
        if table:
            table.update()

        time.sleep(delay_seconds)

        while paused and sending:
            time.sleep(0.2)
            refresh_status_panel(-1, None)
            refresh_table()
            if table:
                table.update()

    sending = False
    current_idx = -1
    progress.value = 1.0
    processed_count_label.text = f"Processed: {processed} / {total}"
    current_status_label.text = "✅ All done!"
    ui.notify(f"Finished processing {processed} numbers.", type="info")
    refresh_status_panel(-1, None)
    refresh_table()
    if table:
        table.update()

def refresh_status_panel(seq, row):
    if seq == -1 or row is None:
        current_status_label.text = ""
    else:
        phone = ''
        if uploaded_contacts_df is not None:
            phone_column = None
            for col in uploaded_contacts_df.columns:
                if col.lower().strip() in {"phone", "phonenumber", "number"}:
                    phone_column = col
                    break
            if phone_column:
                phone = str(row[phone_column])
        snippet = ""
        message_column = None
        for col in uploaded_contacts_df.columns:
            if col.lower().strip() == "message":
                message_column = col
                break
        if message_column:
            snippet = str(row[message_column])[:26]
        current_status_label.text = (
            f'▶️ <b>Now:</b> Seq {seq} <span style="color:#808080">({phone}) {snippet}{"..." if len(snippet)==26 else ""}</span>'
        )

def refresh_table():
    global table, current_idx
    if table is None:
        return
    if uploaded_contacts_df is not None:
        columns = [{'name': 'Seq', 'label': 'Seq', 'field': 'Seq'}] + [
            {'name': col, 'label': col, 'field': col} for col in uploaded_contacts_df.columns
        ]
        table.columns = columns
        display_rows = []
        for i, row in uploaded_contacts_df.iterrows():
            new_row = {'Seq': i + 1}
            for col in uploaded_contacts_df.columns:
                new_row[col] = row[col]
            display_rows.append(new_row)
        table.rows = display_rows

        def row_bg(row):
            if current_idx != -1 and row.get('Seq') == current_idx + 1:
                return 'bg-yellow-3'
            return None
        table.row_background = row_bg
        table.visible = True
        table.update()
    else:
        table.rows = []
        table.visible = False
        table.update()

def poll_results():
    while True:
        refresh_table()
        time.sleep(1)

def start_sending():
    global sending, paused
    if not uploaded_excel_content:
        ui.notify('Please upload an Excel file first.', type='negative')
        return
    if sending:
        ui.notify('Already sending!', type='warning')
        return
    try:
        wait_time_seconds = int(wait_time_input.value)
    except Exception:
        wait_time_seconds = 10
    try:
        delay_seconds = int(delay_input.value)
    except Exception:
        delay_seconds = 10
    progress.value = 0
    processed_count_label.text = "Processed: 0"
    sending = True
    paused = False
    current_status_label.text = ""
    threading.Thread(
        target=send_all_pywhatkit,
        args=(country_code.value, uploaded_excel_content, wait_time_seconds, delay_seconds),
        daemon=True
    ).start()

def pause_sending():
    global paused
    if sending and not paused:
        paused = True
        ui.notify("Paused.", type="warning")

def resume_sending():
    global paused
    if sending and paused:
        paused = False
        ui.notify("Resumed.", type="positive")

def refresh_session():
    global results, uploaded_excel_content, uploaded_contacts_df, sending, paused, current_idx
    results.clear()
    uploaded_excel_content = None
    uploaded_contacts_df = None
    sending = False
    paused = False
    current_idx = -1
    if progress is not None:
        progress.value = 0
    if processed_count_label is not None:
        processed_count_label.text = "Processed: 0"
    if current_status_label is not None:
        current_status_label.text = ""
    if table is not None:
        table.rows = []
        table.visible = False
        table.update()
    if uploader is not None:
        uploader.reset()
        uploader.value = None
        uploader.update()
    ui.notify("Session cleared. Ready for new upload.", type="info")

def file_uploaded(files):
    global uploaded_excel_content, uploaded_contacts_df, results
    f = files[0] if isinstance(files, list) else files
    if hasattr(f, "content"):
        content = f.content.read() if hasattr(f.content, "read") else f.content
        uploaded_excel_content = content
    else:
        uploaded_excel_content = f.read() if hasattr(f, "read") else f
    results.clear()
    uploaded_contacts_df = None
    if uploaded_excel_content:
        try:
            df = pd.read_excel(BytesIO(uploaded_excel_content))
            phone_column = None
            for col in df.columns:
                if col.lower().strip() in {"phone", "phonenumber", "number"}:
                    phone_column = col
                    break
            if phone_column:
                code = country_code.value if country_code else '+20'
                df[phone_column] = df[phone_column].apply(lambda v: normalize_phone(v, code))
            uploaded_contacts_df = df.copy()
            n_contacts = len(df)
            ui.notify(
                f"✅ Uploaded: {n_contacts} contact{'s' if n_contacts != 1 else ''}.",
                type='positive', position='top'
            )
            refresh_table()
        except Exception as e:
            uploaded_contacts_df = None
            refresh_table()
            ui.notify(f"File uploaded, but could not preview: {e}", type='warning')
    else:
        uploaded_contacts_df = None
        refresh_table()
        ui.notify("Upload failed -- no file content.", type='negative')

# --- UI LAYOUT ---

with ui.card().tight().classes('shadow-4 q-pa-lg q-mb-lg'):
    ui.label('🤖 WhatsApp Broadcast Automation').classes('text-h4')
    ui.label('Send WhatsApp messages in bulk. Do not touch browser during sending.').classes('text-body1 text-grey-7')
ui.space()

with ui.row().classes('q-gutter-md'):
    with ui.card().tight().classes('shadow-2 q-pa-md').style('min-width:320px;max-width:360px;flex:1'):
        ui.label('⬆️ Upload & Settings').classes('text-h6')
        uploader = ui.upload(label='Upload contacts.xlsx').classes('q-mb-md w-full')
        uploader.on_upload(file_uploaded)
        country_code = ui.input('Country Code', value='+20').props('outlined dense').classes('q-mb-md w-full')
        wait_time_input = ui.input(
            'Delay after open (sec)', value='10'
        ).props('outlined dense type=number min=1').classes('q-mb-md w-full')
        delay_input = ui.input(
            'Delay between messages (sec)', value='10'
        ).props('outlined dense type=number min=0').classes('w-full')
    with ui.card().tight().classes('shadow-2 q-pa-md').style('flex:1;min-width:260px;max-width:320px'):
        ui.label('🪄 Actions & Progress').classes('text-h6')
        with ui.row().classes('q-gutter-sm q-mb-md'):
            ui.button('▶️ Start', on_click=start_sending).classes('bg-primary text-white')
            ui.button('🔄 Reset', on_click=refresh_session).classes('bg-grey-4 text-black q-ml-md')
            ui.button('⏸ Pause', on_click=pause_sending).classes('bg-grey-2 text-black q-ml-md')
            ui.button('⏯ Resume', on_click=resume_sending).classes('bg-green text-white q-ml-sm')
        with ui.column().classes('q-gutter-xs'):
            processed_count_label = ui.label("Processed: 0").classes('text-body1 text-blue-grey-8')
            progress = ui.linear_progress().classes('q-mb-xs q-mt-xs').style('min-width:140px')
            progress.value = 0
            current_status_label = ui.html("").classes('q-mb-xs text-body2')

ui.space()

with ui.card().tight().classes('shadow-3 q-pa-lg q-mt-lg').style('max-width:98vw;overflow-x:auto'):
    ui.label('🗂️ Contacts List').classes('text-h6 q-mb-xs')
    table = ui.table(
        columns=[{'name': 'Seq', 'label': 'Seq', 'field': 'Seq'}],
        rows=[],
        row_key='Seq'
    ).classes('q-mt-md bg-blue-grey-1 q-table--dense').props('wrap-cells')
    table.visible = False  # Hidden until Excel uploaded

ui.label(
    'ℹ️ Your Excel must include a “Phone” (or “Number”) column and a “Message” column. Any extra columns will also be shown.'
).classes('text-caption text-grey q-mt-md q-mb-sm')

threading.Thread(target=poll_results, daemon=True).start()

if __name__ in {"__main__", "__mp_main__"}:
    print("\n✔ You may now open your browser and go to http://127.0.0.1:8080 and use your WhatsApp automation tool!")
    ui.run(host='127.0.0.1', port=8080)
