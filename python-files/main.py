import os
import requests
import gradio as gr
from datetime import datetime
from pathlib import Path
from gradio.themes.utils import fonts

# Global cancel flag
cancel_flag = {"stop": False}

# Province and crop lists
province_list = [
    "Aceh",
    "Sumatera Utara",
    "Sumatera Barat",
    "Riau",
    "Jambi",
    "Sumatera Selatan",
    "Bengkulu",
    "Lampung",
    "Kepulauan Bangka Belitung",
    "Kepulauan Riau",
    "DKI Jakarta",
    "Jawa Barat",
    "Jawa Tengah",
    "DI Yogyakarta",
    "Jawa Timur",
    "Banten",
    "Bali",
    "Nusa Tenggara Barat",
    "Nusa Tenggara Timur",
    "Kalimantan Barat",
    "Kalimantan Tengah",
    "Kalimantan Selatan",
    "Kalimantan Timur",
    "Kalimantan Utara",
    "Sulawesi Utara",
    "Sulawesi Tengah",
    "Sulawesi Selatan",
    "Sulawesi Tenggara",
    "Gorontalo",
    "Sulawesi Barat",
    "Maluku",
    "Maluku Utara",
    "Papua Barat",
    "Papua Barat Daya",
    "Papua",
    "Papua Selatan",
    "Papua Tengah",
    "Papua Pegunungan",
]

crop_list = [
    "Kacang Tanah",
    "Kacang Hijau",
    "Sorgum",
    "Ubi Jalar",
    "Ubi Kayu",
    "Kedelai",
    "Jagung",
    "Padi",
]

BASE_FOLDER = Path.home() / "Downloads"


def download_data(
    cookie,
    data_type,
    crop,
    download_national,
    year_str,
    select_province,
    selected_provinces,
):
    cancel_flag["stop"] = False  # Reset cancel flag

    try:
        year = int(year_str)
        if year < 2000 or year > datetime.now().year + 1:
            yield "❌ Year must be between 2000 and next year."
            return
    except ValueError:
        yield "❌ Invalid year format. Please enter a number."
        return

    folder_path = BASE_FOLDER / crop / data_type
    yield f"📂 Looking for download folder: `{folder_path}`"
    if not folder_path.exists():
        yield "📁 Folder not found."
        folder_path.mkdir(parents=True, exist_ok=True)
        yield "✅ Folder created."
    else:
        yield "✅ Folder exists."

    folder = str(folder_path)

    display_name = f"Rekap SP - {crop}"
    crop_query = crop.replace(" ", "+")
    cookies = {"sipdps_session": cookie}
    headers = {"User-Agent": "Mozilla/5.0"}

    # Download national data
    if cancel_flag["stop"]:
        yield "⛔ Cancelation requested. Waiting for download to stop..."
        import time

        time.sleep(0.3)
        yield "⛔ Download canceled by user."
        return

    if download_national:
        national_filename = f"National - {display_name}.xlsx"
        national_filepath = os.path.join(folder, national_filename)
        yield f"🌍 Downloading national data: `{national_filename}`..."
        national_url = f"https://sitampan.pertanian.go.id/sipdps/admin/form-sp/rekap?selectedType={data_type}&y={year}&id_cms_pangans={crop_query}&download=true"

        try:
            r = requests.get(national_url, headers=headers, cookies=cookies)
            if r.ok and r.headers.get("Content-Type", "").startswith("application"):
                with open(national_filepath, "wb") as f:
                    f.write(r.content)
                yield f"✅ National data saved: `{national_filename}`"
            else:
                yield "⚠️ Failed to download national data!"
        except Exception as e:
            yield f"❌ Error downloading {national_filename}: {e}"

    # Download provincial data
    targets = (
        selected_provinces if select_province and selected_provinces else province_list
    )

    for i, province in enumerate(province_list, start=1):
        if province not in targets:
            continue

        if cancel_flag["stop"]:
            yield "⛔ Cancelation requested. Waiting for download to stop..."
            import time

            time.sleep(0.3)
            yield "⛔ Download canceled by user."
            return

        filename = f"{i}. {province} - {display_name}.xlsx"
        filepath = os.path.join(folder, filename)
        yield f"📥 Downloading: `{province}`..."

        try:
            url = f"https://sitampan.pertanian.go.id/sipdps/admin/form-sp/rekap?selectedType={data_type}&y={year}&id_cms_provinsis={i}&id_cms_pangans={crop_query}&download=true"
            r = requests.get(url, headers=headers, cookies=cookies)
            if r.ok and r.headers.get("Content-Type", "").startswith("application"):
                with open(filepath, "wb") as f:
                    f.write(r.content)
                yield f"✅ Completed: `{filename}`"
            else:
                yield f"⚠️ Failed: `{province}`"
        except Exception as e:
            yield f"❌ Error `{province}`: {e}"

    yield "🎉 All downloads completed!"
    yield f"📁 Saved to: `{folder}`"


def cancel_download():
    cancel_flag["stop"] = True
    return "⛔ Cancelation requested. Waiting for download to stop..."


# Custom dark theme and scrollbar CSS
custom_theme = gr.themes.Base(primary_hue="blue", font=fonts.GoogleFont("Inter")).set(
    body_background_fill_dark="#1a1a1a",
    body_text_color_dark="#ffffff",
    button_primary_background_fill_dark="#4f46e5",
    button_primary_text_color_dark="#ffffff",
)

custom_css = """
body::-webkit-scrollbar {
    width: 10px;
}
body::-webkit-scrollbar-track {
    background: #1a1a1a;
}
body::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 10px;
}
"""

with gr.Blocks(title="PDPS Downloader", theme=custom_theme, css=custom_css) as app:
    gr.HTML(
    """
    <script>
        var link = document.createElement('link');
        link.rel = 'icon';
        link.type = 'image/png';
        link.href = 'https://i.postimg.cc/4dLwdWkf/favico-Photoroom.png';
        document.head.appendChild(link);
    </script>
    """
)

    gr.Markdown("## 💾 Rekap SP Downloader - SITAMPAN")

    with gr.Row():
        cookie = gr.Textbox(
            label="Cookie Token",
            placeholder="Paste your Cookie Token from Cookie Editor",
        )
        year = gr.Textbox(label="Data Tahun", placeholder="e.g., 2024")

    with gr.Row():
        data_type = gr.Dropdown(
            ["tanam", "panen", "puso"], label="Jenis Data", value="tanam"
        )
        crop = gr.Dropdown(crop_list, label="Jenis Tanaman", value="Kacang Tanah")

    download_national = gr.Checkbox(label="Sertakan Rekap Data Nasional", value=True)

    select_province = gr.Checkbox(label="Download Rekap Provinsi Tertentu")
    gr.Markdown(
        "🛈 Tidak perlu di checklist jika ingin mendownload seluruh Rekap Data Provinsi"
    )

    selected_provinces = gr.Dropdown(
        choices=province_list, label="Select Provinces", multiselect=True, visible=False
    )
    select_province.change(
        lambda x: gr.update(visible=x),
        inputs=select_province,
        outputs=selected_provinces,
    )

    with gr.Row():
        start_button = gr.Button("📥 Start Download")
        cancel_button = gr.Button("❌ Cancel Download")

    log_area = gr.Textbox(label="💻 Realtime Process", lines=20, interactive=False)

    def log_collector(*args):
        logs = ""
        for log in download_data(*args):
            logs += log + "\n"
            yield logs

    start_button.click(
        fn=log_collector,
        inputs=[
            cookie,
            data_type,
            crop,
            download_national,
            year,
            select_province,
            selected_provinces,
        ],
        outputs=log_area,
    )

    cancel_button.click(fn=cancel_download, outputs=log_area)

app.launch(inbrowser=True)
