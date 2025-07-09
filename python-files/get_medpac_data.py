import requests
from pathlib import Path
import json
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import sys
import argparse

# ---- CONFIGURATION ----
API_BASE = 'https://demo.medpacsystems.com/medpac/common/control/'
SESSION_ID = 'your-session-id-here'  # <-- Replace with your valid session id
ANALYZER = 'demo'
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://demo.medpacsystems.com/',
    'Origin': 'https://demo.medpacsystems.com',
    'Cookie': f'PHPSESSID={SESSION_ID};',
}

# ---- UTILITY FUNCTIONS ----
def get_total_images(session):
    url = API_BASE + 'table.php?1751881516386=null'
    data = {
        'CenterName': '',
        'EmergencyFlag': 'false',
        'Analizer': ANALYZER,
        'Currow': 0,
        'Rows': 1
    }
    resp = session.post(url, headers=HEADERS, data=data)
    resp.raise_for_status()
    # Try to extract 'totimages' from the response
    try:
        text = resp.text
        idx = text.find('"totimages":"')
        if idx == -1:
            raise ValueError('totimages not found in response')
        start = idx + len('"totimages":"')
        end = text.find('"', start)
        totimages = int(text[start:end])
        return totimages
    except Exception as e:
        print('Error extracting totimages:', e)
        print('Response:', resp.text)
        sys.exit(1)

def get_all_patients(session, totimages):
    url = API_BASE + 'table.php?1751881516386=null'
    data = {
        'CenterName': '',
        'EmergencyFlag': 'false',
        'Analizer': ANALYZER,
        'Currow': 0,
        'Rows': totimages
    }
    resp = session.post(url, headers=HEADERS, data=data)
    resp.raise_for_status()
    # The response is not a clean JSON, so try to extract the JSON part
    text = resp.text
    try:
        json_start = text.find('{')
        json_data = json.loads(text[json_start:])
        return json_data
    except Exception as e:
        print('Error parsing patient data:', e)
        print('Response:', text)
        sys.exit(1)

def get_patient_images(session, study_uid):
    url = API_BASE + 'viewer.php?1752035032128'
    headers = HEADERS.copy()
    headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
    })
    data = {
        'Study': study_uid
    }
    resp = session.post(url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()

def download_and_save_image(session, image_url, save_path_base):
    extensions = ['.png', '.j2k', '.jpg']
    for ext in extensions:
        full_url = 'https://demo.medpacsystems.com' + image_url + ext
        try:
            resp = session.get(full_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            # Save using the actual extension
            save_path = save_path_base.with_suffix(ext)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return save_path  # Return the correct path
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 404:
                continue  # Try next extension
            else:
                raise
    raise FileNotFoundError(f"Image not found with any extension for path: {image_url}")


def visualize_image(image_path):
    img = Image.open(image_path)
    plt.imshow(img, cmap='gray')
    plt.axis('off')
    plt.show()

# ---- MAIN SCRIPT ----
def main(visualize=False, max_patients=None):
    session = requests.Session()
    print('Fetching total number of patients/images...')
    totimages = get_total_images(session)
    print(f'Total images/patients: {totimages}')
    if max_patients:
        totimages = min(totimages, max_patients)
    print('Fetching all patient data...')
    patients_data = get_all_patients(session, totimages)
    # The patient list is in patients_data['data'] or similar; adjust as needed
    patient_list = patients_data.get('studies')  # or patients_data.get('Data') or []
    if not patient_list:
        # Try to parse as a list
        if isinstance(patients_data, list):
            patient_list = patients_data
        else:
            print('Could not find patient list in response.')
            sys.exit(1)
    print(f'Found {len(patient_list)} patients.')
    for idx, patient in enumerate(patient_list, 1):
        patid = patient.get('PatID') or f'patient_{idx}'
        study_uid = patient.get('StuInsUID')
        if not study_uid:
            print(f'Skipping patient {patid}: no StuInsUID')
            continue
        print(f'[{idx}/{len(patient_list)}] Fetching images for patient {patid} (StudyUID: {study_uid})...')
        try:
            image_data = get_patient_images(session, study_uid)
        except Exception as e:
            print(f'Failed to fetch images for {patid}: {e}')
            continue
        series_list = image_data.get('series', [])
        for series in series_list:
            series_num = series.get('SeriesNum', 'unknown')
            paths = series.get('Path', [])
            for i, img_path in enumerate(paths, 1):
                save_dir = Path('data') / str(patid) / str(series_num)
                save_path = save_dir / f'MR.{i}.png'
                try:
                    download_and_save_image(session, img_path, save_path)
                    print(f'  Saved: {save_path}')
                    if visualize:
                        visualize_image(save_path)
                except Exception as e:
                    print(f'  Failed to download image {img_path}: {e}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch and store Medpac patient images cross-platform.')
    parser.add_argument('--visualize', action='store_true', help='Visualize images as they are downloaded')
    parser.add_argument('--max-patients', type=int, default=None, help='Limit number of patients to fetch')
    args = parser.parse_args()
    main(visualize=args.visualize, max_patients=args.max_patients)

# ---- REQUIREMENTS.TXT SUGGESTION ----
# requests
# pillow
# matplotlib
