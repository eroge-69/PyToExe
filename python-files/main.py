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
    "Papua",
    "Papua Barat Daya",
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

# Kabupaten/Kota mapping based on provided data
kabupaten_mapping = {
    "Aceh": {
        "range": "1-23",
        "kabupaten": ["SIMEULUE", "ACEH SINGKIL", "ACEH SELATAN", "ACEH TENGGARA", "ACEH TIMUR", "ACEH TENGAH", "ACEH BARAT", "ACEH BESAR", "PIDIE", "BIREUEN", "ACEH UTARA", "ACEH BARAT DAYA", "GAYO LUES", "ACEH TAMIANG", "NAGAN RAYA", "ACEH JAYA", "BENER MERIAH", "PIDIE JAYA", "KOTA BANDA ACEH", "KOTA SABANG", "KOTA LANGSA", "KOTA LHOKSEUMAWE", "KOTA SUBULUSSALAM"]
    },
    "Sumatera Utara": {
        "range": "24-56",
        "kabupaten": ["NIAS", "MANDAILING NATAL", "TAPANULI SELATAN", "TAPANULI TENGAH", "TAPANULI UTARA", "TOBA SAMOSIR", "LABUHAN BATU", "ASAHAN", "SIMALUNGUN", "DAIRI", "KARO", "DELI SERDANG", "LANGKAT", "NIAS SELATAN", "HUMBANG HASUNDUTAN", "PAKPAK BHARAT", "SAMOSIR", "SERDANG BEDAGAI", "BATU BARA", "PADANG LAWAS UTARA", "PADANG LAWAS", "LABUHAN BATU SELATAN", "LABUHAN BATU UTARA", "NIAS UTARA", "NIAS BARAT", "KOTA SIBOLGA", "KOTA TANJUNG BALAI", "KOTA PEMATANGSIANTAR", "KOTA TEBING TINGGI", "KOTA MEDAN", "KOTA BINJAI", "KOTA PADANG SIDEMPUAN", "KOTA GUNUNGSITOLI"]
    },
    "Sumatera Barat": {
        "range": "57-75",
        "kabupaten": ["KEPULAUAN MENTAWAI", "PESISIR SELATAN", "SOLOK", "SIJUNJUNG", "TANAH DATAR", "PADANG PARIAMAN", "AGAM", "LIMA PULUH KOTA", "PASAMAN", "SOLOK SELATAN", "DHARMASRAYA", "PASAMAN BARAT", "KOTA PADANG", "KOTA SOLOK", "KOTA SAWAH LUNTO", "KOTA PADANG PANJANG", "KOTA BUKITTINGGI", "KOTA PAYAKUMBUH", "KOTA PARIAMAN"]
    },
    "Riau": {
        "range": "76-87",
        "kabupaten": ["KUANTAN SINGINGI", "INDRAGIRI HULU", "INDRAGIRI HILIR", "PELALAWAN", "SIAK", "KAMPAR", "ROKAN HULU", "BENGKALIS", "ROKAN HILIR", "KEPULAUAN MERANTI", "KOTA PEKANBARU", "KOTA DUMAI"]
    },
    "Jambi": {
        "range": "88-98",
        "kabupaten": ["KERINCI", "MERANGIN", "SAROLANGUN", "BATANG HARI", "MUARO JAMBI", "TANJUNG JABUNG TIMUR", "TANJUNG JABUNG BARAT", "TEBO", "BUNGO", "KOTA JAMBI", "KOTA SUNGAI PENUH"]
    },
    "Sumatera Selatan": {
        "range": "99-115",
        "kabupaten": ["OGAN KOMERING ULU", "OGAN KOMERING ILIR", "MUARA ENIM", "LAHAT", "MUSI RAWAS", "MUSI BANYUASIN", "BANYU ASIN", "OGAN KOMERING ULU SELATAN", "OGAN KOMERING ULU TIMUR", "OGAN ILIR", "EMPAT LAWANG", "PENUKAL ABAB LEMATANG ILIR", "MUSI RAWAS UTARA", "KOTA PALEMBANG", "KOTA PRABUMULIH", "KOTA PAGAR ALAM", "KOTA LUBUKLINGGAU"]
    },
    "Bengkulu": {
        "range": "116-125",
        "kabupaten": ["BENGKULU SELATAN", "REJANG LEBONG", "BENGKULU UTARA", "KAUR", "SELUMA", "MUKOMUKO", "LEBONG", "KEPAHIANG", "BENGKULU TENGAH", "KOTA BENGKULU"]
    },
    "Lampung": {
        "range": "126-140",
        "kabupaten": ["LAMPUNG BARAT", "TANGGAMUS", "LAMPUNG SELATAN", "LAMPUNG TIMUR", "LAMPUNG TENGAH", "LAMPUNG UTARA", "WAY KANAN", "TULANGBAWANG", "PESAWARAN", "PRINGSEWU", "MESUJI", "TULANG BAWANG BARAT", "PESISIR BARAT", "KOTA BANDAR LAMPUNG", "KOTA METRO"]
    },
    "Kepulauan Bangka Belitung": {
        "range": "141-147",
        "kabupaten": ["BANGKA", "BELITUNG", "BANGKA BARAT", "BANGKA TENGAH", "BANGKA SELATAN", "BELITUNG TIMUR", "KOTA PANGKALPINANG"]
    },
    "Kepulauan Riau": {
        "range": "148-154",
        "kabupaten": ["KARIMUN", "BINTAN", "NATUNA", "LINGGA", "KEPULAUAN ANAMBAS", "KOTA BATAM", "KOTA TANJUNG PINANG"]
    },
    "DKI Jakarta": {
        "range": "155-160",
        "kabupaten": ["KEPULAUAN SERIBU", "KOTA JAKARTA SELATAN", "KOTA JAKARTA TIMUR", "KOTA JAKARTA PUSAT", "KOTA JAKARTA BARAT", "KOTA JAKARTA UTARA"]
    },
    "Jawa Barat": {
        "range": "161-187",
        "kabupaten": ["BOGOR", "SUKABUMI", "CIANJUR", "BANDUNG", "GARUT", "TASIKMALAYA", "CIAMIS", "KUNINGAN", "CIREBON", "MAJALENGKA", "SUMEDANG", "INDRAMAYU", "SUBANG", "PURWAKARTA", "KARAWANG", "BEKASI", "BANDUNG BARAT", "PANGANDARAN", "KOTA BOGOR", "KOTA SUKABUMI", "KOTA BANDUNG", "KOTA CIREBON", "KOTA BEKASI", "KOTA DEPOK", "KOTA CIMAHI", "KOTA TASIKMALAYA", "KOTA BANJAR"]
    },
    "Jawa Tengah": {
        "range": "188-222",
        "kabupaten": ["CILACAP", "BANYUMAS", "PURBALINGGA", "BANJARNEGARA", "KEBUMEN", "PURWOREJO", "WONOSOBO", "MAGELANG", "BOYOLALI", "KLATEN", "SUKOHARJO", "WONOGIRI", "KARANGANYAR", "SRAGEN", "GROBOGAN", "BLORA", "REMBANG", "PATI", "KUDUS", "JEPARA", "DEMAK", "SEMARANG", "TEMANGGUNG", "KENDAL", "BATANG", "PEKALONGAN", "PEMALANG", "TEGAL", "BREBES", "KOTA MAGELANG", "KOTA SURAKARTA", "KOTA SALATIGA", "KOTA SEMARANG", "KOTA PEKALONGAN", "KOTA TEGAL"]
    },
    "DI Yogyakarta": {
        "range": "223-227",
        "kabupaten": ["KULON PROGO", "BANTUL", "GUNUNG KIDUL", "SLEMAN", "KOTA YOGYAKARTA"]
    },
    "Jawa Timur": {
        "range": "228-265",
        "kabupaten": ["PACITAN", "PONOROGO", "TRENGGALEK", "TULUNGAGUNG", "BLITAR", "KEDIRI", "MALANG", "LUMAJANG", "JEMBER", "BANYUWANGI", "BONDOWOSO", "SITUBONDO", "PROBOLINGGO", "PASURUAN", "SIDOARJO", "MOJOKERTO", "JOMBANG", "NGANJUK", "MADIUN", "MAGETAN", "NGAWI", "BOJONEGORO", "TUBAN", "LAMONGAN", "GRESIK", "BANGKALAN", "SAMPANG", "PAMEKASAN", "SUMENEP", "KOTA KEDIRI", "KOTA BLITAR", "KOTA MALANG", "KOTA PROBOLINGGO", "KOTA PASURUAN", "KOTA MOJOKERTO", "KOTA MADIUN", "KOTA SURABAYA", "KOTA BATU"]
    },
    "Banten": {
        "range": "266-273",
        "kabupaten": ["PANDEGLANG", "LEBAK", "TANGERANG", "SERANG", "KOTA TANGERANG", "KOTA CILEGON", "KOTA SERANG", "KOTA TANGERANG SELATAN"]
    },
    "Bali": {
        "range": "274-282",
        "kabupaten": ["JEMBRANA", "TABANAN", "BADUNG", "GIANYAR", "KLUNGKUNG", "BANGLI", "KARANGASEM", "BULELENG", "KOTA DENPASAR"]
    },
    "Nusa Tenggara Barat": {
        "range": "283-292",
        "kabupaten": ["LOMBOK BARAT", "LOMBOK TENGAH", "LOMBOK TIMUR", "SUMBAWA", "DOMPU", "BIMA", "SUMBAWA BARAT", "LOMBOK UTARA", "KOTA MATARAM", "KOTA BIMA"]
    },
    "Nusa Tenggara Timur": {
        "range": "293-314",
        "kabupaten": ["SUMBA BARAT", "SUMBA TIMUR", "KUPANG", "TIMOR TENGAH SELATAN", "TIMOR TENGAH UTARA", "BELU", "ALOR", "LEMBATA", "FLORES TIMUR", "SIKKA", "ENDE", "NGADA", "MANGGARAI", "ROTE NDAO", "MANGGARAI BARAT", "SUMBA TENGAH", "SUMBA BARAT DAYA", "NAGEKEO", "MANGGARAI TIMUR", "SABU RAIJUA", "MALAKA", "KOTA KUPANG"]
    },
    "Kalimantan Barat": {
        "range": "315-328",
        "kabupaten": ["SAMBAS", "BENGKAYANG", "LANDAK", "MEMPAWAH", "SANGGAU", "KETAPANG", "SINTANG", "KAPUAS HULU", "SEKADAU", "MELAWI", "KAYONG UTARA", "KUBU RAYA", "KOTA PONTIANAK", "KOTA SINGKAWANG"]
    },
    "Kalimantan Tengah": {
        "range": "329-342",
        "kabupaten": ["KOTAWARINGIN BARAT", "KOTAWARINGIN TIMUR", "KAPUAS", "BARITO SELATAN", "BARITO UTARA", "SUKAMARA", "LAMANDAU", "SERUYAN", "KATINGAN", "PULANG PISAU", "GUNUNG MAS", "BARITO TIMUR", "MURUNG RAYA", "KOTA PALANGKA RAYA"]
    },
    "Kalimantan Selatan": {
        "range": "343-355",
        "kabupaten": ["TANAH LAUT", "KOTABARU", "BANJAR", "BARITO KUALA", "TAPIN", "HULU SUNGAI SELATAN", "HULU SUNGAI TENGAH", "HULU SUNGAI UTARA", "TABALONG", "TANAH BUMBU", "BALANGAN", "KOTA BANJARMASIN", "KOTA BANJAR BARU"]
    },
    "Kalimantan Timur": {
        "range": "356-365",
        "kabupaten": ["PASER", "KUTAI BARAT", "KUTAI KARTANEGARA", "KUTAI TIMUR", "BERAU", "PENAJAM PASER UTARA", "MAHAKAM HULU", "KOTA BALIKPAPAN", "KOTA SAMARINDA", "KOTA BONTANG"]
    },
    "Kalimantan Utara": {
        "range": "366-370",
        "kabupaten": ["MALINAU", "BULUNGAN", "TANA TIDUNG", "NUNUKAN", "KOTA TARAKAN"]
    },
    "Sulawesi Utara": {
        "range": "371-385",
        "kabupaten": ["BOLAANG MONGONDOW", "MINAHASA", "KEPULAUAN SANGIHE", "KEPULAUAN TALAUD", "MINAHASA SELATAN", "MINAHASA UTARA", "BOLAANG MONGONDOW UTARA", "SIAU TAGULANDANG BIARO", "MINAHASA TENGGARA", "BOLAANG MONGONDOW SELATAN", "BOLAANG MONGONDOW TIMUR", "KOTA MANADO", "KOTA BITUNG", "KOTA TOMOHON", "KOTA KOTAMOBAGU"]
    },
    "Sulawesi Tengah": {
        "range": "386-398",
        "kabupaten": ["BANGGAI KEPULAUAN", "BANGGAI", "MOROWALI", "POSO", "DONGGALA", "TOLI-TOLI", "BUOL", "PARIGI MOUTONG", "TOJO UNA-UNA", "SIGI", "BANGGAI LAUT", "MOROWALI UTARA", "KOTA PALU"]
    },
    "Sulawesi Selatan": {
        "range": "399-422",
        "kabupaten": ["KEPULAUAN SELAYAR", "BULUKUMBA", "BANTAENG", "JENEPONTO", "TAKALAR", "GOWA", "SINJAI", "MAROS", "PANGKAJENE DAN KEPULAUAN", "BARRU", "BONE", "SOPPENG", "WAJO", "SIDENRENG RAPPANG", "PINRANG", "ENREKANG", "LUWU", "TANA TORAJA", "LUWU UTARA", "LUWU TIMUR", "TORAJA UTARA", "KOTA MAKASSAR", "KOTA PAREPARE", "KOTA PALOPO"]
    },
    "Sulawesi Tenggara": {
        "range": "423-439",
        "kabupaten": ["BUTON", "MUNA", "KONAWE", "KOLAKA", "KONAWE SELATAN", "BOMBANA", "WAKATOBI", "KOLAKA UTARA", "BUTON UTARA", "KONAWE UTARA", "KOLAKA TIMUR", "KONAWE KEPULAUAN", "MUNA BARAT", "BUTON TENGAH", "BUTON SELATAN", "KOTA KENDARI", "KOTA BAUBAU"]
    },
    "Gorontalo": {
        "range": "440-445",
        "kabupaten": ["BOALEMO", "GORONTALO", "POHUWATO", "BONE BOLANGO", "GORONTALO UTARA", "KOTA GORONTALO"]
    },
    "Sulawesi Barat": {
        "range": "446-451",
        "kabupaten": ["MAJENE", "POLEWALI MANDAR", "MAMASA", "MAMUJU", "PASANGKAYU", "MAMUJU TENGAH"]
    },
    "Maluku": {
        "range": "452-462",
        "kabupaten": ["KEPULAUAN TANIMBAR", "MALUKU TENGGARA", "MALUKU TENGAH", "BURU", "KEPULAUAN ARU", "SERAM BAGIAN BARAT", "SERAM BAGIAN TIMUR", "MALUKU BARAT DAYA", "BURU SELATAN", "KOTA AMBON", "KOTA TUAL"]
    },
    "Maluku Utara": {
        "range": "463-472",
        "kabupaten": ["HALMAHERA BARAT", "HALMAHERA TENGAH", "KEPULAUAN SULA", "HALMAHERA SELATAN", "HALMAHERA UTARA", "HALMAHERA TIMUR", "PULAU MOROTAI", "PULAU TALIABU", "KOTA TERNATE", "KOTA TIDORE KEPULAUAN"]
    },
    "Papua Barat": {
        "range": "473, 474, 475, 476, 477, 483, 484",
        "kabupaten": ["FAKFAK", "KAIMANA", "TELUK WONDAMA", "TELUK BINTUNI", "MANOKWARI", "MANOKWARI SELATAN", "PEGUNUNGAN ARFAK"]
    },
    "Papua": {
        "range": "488, 490, 491, 501, 502, 503, 504, 505, 514",
        "kabupaten": ["JAYAPURA", "KEPULAUAN YAPEN", "BIAK NUMFOR", "SARMI", "KEEROM", "WAROPEN", "SUPIORI", "MAMBERAMO RAYA", "KOTA JAYAPURA"]
    },
    "Papua Barat Daya": {
        "range": "480, 479, 478, 482, 481, 485",
        "kabupaten": ["RAJA AMPAT", "SORONG", "SORONG SELATAN", "MAYBRAT", "TAMBRAUW", "KOTA SORONG"]
    },
    "Papua Selatan": {
        "range": "486, 495, 496, 497",
        "kabupaten": ["MERAUKE", "BOVEN DIGOEL", "MAPPI", "ASMAT"]
    },
    "Papua Tengah": {
        "range": "494, 511, 513, 489, 492, 512, 510, 493",
        "kabupaten": ["MIMIKA", "DOGIYAI", "DEIYAI", "NABIRE", "PANIAI", "INTAN JAYA", "PUNCAK", "PUNCAK JAYA"]
    },
    "Papua Pegunungan": {
        "range": "506, 487, 507, 500, 508, 509, 498, 499",
        "kabupaten": ["NDUGA", "JAYAWIJAYA", "LANNY JAYA", "TOLIKARA", "MAMBERAMO TENGAH", "YALIMO", "YAHUKIMO", "PEGUNUNGAN BINTANG"]
    }
}

def get_kabupaten_ids(province_name):
    """Get kabupaten IDs for a specific province"""
    if province_name not in kabupaten_mapping:
        return []
    
    range_str = kabupaten_mapping[province_name]["range"]
    ids = []
    
    # Parse range string (e.g., "1-23", "473-477, 483-484", "488, 490-491, 501-505, 514")
    parts = range_str.split(', ')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ids.extend(range(start, end + 1))
        else:
            ids.append(int(part))
    
    return ids

# Base folder now includes "PDPS Downloader"
BASE_FOLDER = Path.home() / "Downloads" / "PDPS Downloader"


def download_data(
    cookie,
    data_type,
    crop,
    download_national,
    year_str,
    select_province,
    selected_provinces,
    download_kabupaten,
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

    # Check and create main PDPS Downloader folder first
    yield f"📂 Looking for main PDPS Downloader folder: `{BASE_FOLDER}`"
    if not BASE_FOLDER.exists():
        yield "📁 PDPS Downloader folder not found."
        BASE_FOLDER.mkdir(parents=True, exist_ok=True)
        yield "✅ PDPS Downloader folder created."
    else:
        yield "✅ PDPS Downloader folder exists."

    # Create crop/data_type folder structure inside PDPS Downloader
    folder_path = BASE_FOLDER / crop / data_type
    yield f"📂 Looking for download folder: `{folder_path}`"
    if not folder_path.exists():
        yield "📁 Crop/Data type folder not found."
        folder_path.mkdir(parents=True, exist_ok=True)
        yield "✅ Crop/Data type folder created."
    else:
        yield "✅ Crop/Data type folder exists."

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
        national_filename = f"National_Data.xlsx"
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

        # Create province folder with number prefix
        province_folder_name = f"{i}. {province}"
        province_folder = folder_path / province_folder_name
        province_folder.mkdir(exist_ok=True)
        
        filename = f"Province_Data.xlsx"
        filepath = province_folder / filename
        yield f"📥 Downloading province: `{province}`..."

        try:
            url = f"https://sitampan.pertanian.go.id/sipdps/admin/form-sp/rekap?selectedType={data_type}&y={year}&id_cms_provinsis={i}&id_cms_pangans={crop_query}&download=true"
            r = requests.get(url, headers=headers, cookies=cookies)
            if r.ok and r.headers.get("Content-Type", "").startswith("application"):
                with open(filepath, "wb") as f:
                    f.write(r.content)
                yield f"✅ Province completed: `{filename}`"
            else:
                yield f"⚠️ Failed: `{province}`"
        except Exception as e:
            yield f"❌ Error `{province}`: {e}"

        # Download kabupaten data if enabled
        if download_kabupaten and province in kabupaten_mapping:
            kabupaten_ids = get_kabupaten_ids(province)
            kabupaten_names = kabupaten_mapping[province]["kabupaten"]
            
            # Create kabupaten folder
            kabupaten_folder = province_folder / "Kabupaten"
            kabupaten_folder.mkdir(exist_ok=True)
            
            yield f"📍 Downloading kabupaten data for {province}..."
            
            for idx, (kab_id, kab_name) in enumerate(zip(kabupaten_ids, kabupaten_names)):
                if cancel_flag["stop"]:
                    yield "⛔ Cancelation requested. Waiting for download to stop..."
                    import time
                    time.sleep(0.3)
                    yield "⛔ Download canceled by user."
                    return
                
                # Add kabupaten ID number prefix to filename
                kab_filename = f"{kab_id}. {kab_name}.xlsx"
                kab_filepath = kabupaten_folder / kab_filename
                
                try:
                    kab_url = f"https://sitampan.pertanian.go.id/sipdps/admin/form-sp/rekap?selectedType={data_type}&y={year}&id_cms_provinsis={i}&id_cms_kabupatens={kab_id}&id_cms_pangans={crop_query}&download=true"
                    r = requests.get(kab_url, headers=headers, cookies=cookies)
                    if r.ok and r.headers.get("Content-Type", "").startswith("application"):
                        with open(kab_filepath, "wb") as f:
                            f.write(r.content)
                        yield f"✅ Kabupaten completed: `{kab_name}`"
                    else:
                        yield f"⚠️ Failed kabupaten: `{kab_name}`"
                except Exception as e:
                    yield f"❌ Error kabupaten `{kab_name}`: {e}"

    yield "🎉 All downloads completed!"
    yield f"📁 Saved to: `{folder_path}`"


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

/* Hide default Gradio footer */
footer {
    display: none !important;
}

/* Custom footer styling */
.custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%);
    color: #ffffff;
    text-align: center;
    padding: 8px 16px;
    font-size: 12px;
    border-top: 1px solid #444;
    z-index: 1000;
    box-shadow:
    0 -2px 10px rgba(0,0,0,0.3);
}

.custom-footer a {
    color: #4f46e5;
    text-decoration: none;
    margin: 0 5px;
}

.custom-footer a:hover {
    color: #6366f1;
    text-decoration: underline;
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

    # Custom footer
    gr.HTML(
    """
    <div class="custom-footer">
        💾 PDPS Downloader | 
        Built with ❤️ for <a href="" target="_blank">Neneng Nur Aida</a>
    </div>
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
    
    # New feature: Download Kabupaten checkbox
    download_kabupaten = gr.Checkbox(label="Sertakan data Kabupaten/Kota", value=False)
    gr.Markdown(
        "🏘️ Centang untuk mendownload data kabupaten/kota berdasarkan data yang sudah disediakan (452+ kabupaten/kota)"
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
            download_kabupaten,
        ],
        outputs=log_area,
    )

    cancel_button.click(fn=cancel_download, outputs=log_area)

app.launch(inbrowser=True)