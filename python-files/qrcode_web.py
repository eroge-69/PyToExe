"""
자.. 지금부터 이 코드가 기준이 되는 코드야...
수정하다 오류나거나 잘못된 방향으로 수정되면 항상 이버전으로
다시 시작하는 거야.. 알겠지??

언어 추가시 살펴봐야 하는 줄: 82, 359, 464
패턴 추가시 살펴봐야 하는 줄: 164, 547, 737

QR 코드 생성 웹앱 - Streamlit 버전
휴대폰에서도 사용 가능

실행 방법:
1. pip install streamlit qrcode[pil]
2. streamlit run qrcode_web.py

또는 온라인에서 실행:
- Streamlit Cloud, Heroku, Replit 등에 배포 가능
"""

# qrcode_web.py

import streamlit as st
import qrcode
import io
import re
import math
import hashlib
import base64 # SVG 이미지 표시를 위해 추가
import qrcode.image.svg # SVG 생성을 위해 추가
from datetime import datetime
from zoneinfo import ZoneInfo
from messages import messages
from PIL import Image, ImageDraw


# 기본 설정값을 초기화하는 함수
def reset_language_defaults():
    st.session_state.error_correction_select = messages[st.session_state.lang]['error_correction_low_select']
    st.session_state.pattern_shape_select = messages[st.session_state.lang]['pattern_shape_square']
    st.session_state.finder_pattern_shape_select = messages[st.session_state.lang]['pattern_shape_square']
    st.session_state.pattern_color_select = "black"
    st.session_state.bg_color_select = "white"
    st.session_state.box_size_input = 20
    st.session_state.border_input = 2
    st.session_state.mask_pattern_select = 2
    st.session_state.corner_radius_input = 25
    st.session_state.finder_corner_radius_input = 25
    st.session_state.cell_gap_input = 1
    st.session_state.finder_cell_gap_input = 1
    st.session_state.jpg_quality_input = 50
    st.session_state.strip_option = True
    st.session_state.file_format_select = "PNG"

# 세션 상태 초기화
if 'lang' not in st.session_state:
    st.session_state.lang = "ko"
    reset_language_defaults()
if 'qr_input_area' not in st.session_state:
    st.session_state.qr_input_area = ""
if 'custom_pattern_color_input_key' not in st.session_state:
    st.session_state.custom_pattern_color_input_key = ""
if 'custom_bg_color_input_key' not in st.session_state:
    st.session_state.custom_bg_color_input_key = ""
if 'filename_input_key' not in st.session_state:
    st.session_state.filename_input_key = ""
if 'box_size_input' not in st.session_state:
    st.session_state.box_size_input = 20
if 'border_input' not in st.session_state:
    st.session_state.border_input = 2
if 'mask_pattern_select' not in st.session_state:
    st.session_state.mask_pattern_select = 2
if 'pattern_color_select' not in st.session_state:
    st.session_state.pattern_color_select = "black"
if 'bg_color_select' not in st.session_state:
    st.session_state.bg_color_select = "white"
if 'finder_corner_radius_input' not in st.session_state:
    st.session_state.finder_corner_radius_input = 25
if 'cell_gap_input' not in st.session_state or st.session_state.cell_gap_input < 1:
    st.session_state.cell_gap_input = 1
if 'finder_cell_gap_input' not in st.session_state or st.session_state.finder_cell_gap_input < 1:
    st.session_state.finder_cell_gap_input = 1

# 언어에 따른 페이지 제목 매핑
dynamic_page_titles = {
    "ko": "QR 코드 생성기",
    "en": "QR Code Generator",
    "ja": "QRコードジェネレーター",
    "zh": "二维码生成器",
    "de": "QR-Code-Generator",
    "fr": "Générateur de code QR",
    "es": "Generador de códigos QR",
    "tr": "QR Kod Üretici",
    "ru": "Генератор QR-кода",
    "pt": "Gerador de Código QR",
    "ar": "مولد رمز الاستجابة السريعة",
    "hi": "क्यूआर कोड जनरेटर",
    "bn": "কিউআর কোড জেনারেটর",
}


# 페이지 설정
st.set_page_config(
    page_title=dynamic_page_titles[st.session_state.lang],
    page_icon="🔲",
    layout="wide",
)


# 현재 언어 설정 불러오기
lang_messages = messages[st.session_state.lang]


# 파일명에 특수문자 포함시 '_' 문자로 치환
def sanitize_filename(name: str) -> str:
    invalid_chars = '\\/:*?"<>|[]'
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip()


# 유효한 색상인지 확인하는 함수
def is_valid_color(color_name):
    if not color_name:
        return False
    color_name = color_name.strip()
    hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    return hex_pattern.match(color_name)


# 패턴 간격을 강제로 최소 1값 이상으로 지정
def enforce_min_value():
    if st.session_state.cell_gap_input < 1:
        st.session_state.cell_gap_input = 1
    if st.session_state.finder_cell_gap_input < 1:
        st.session_state.finder_cell_gap_input = 1


# 오류 복원 수준 옵션과 상수 매핑
error_correction_map = {
    'low': qrcode.constants.ERROR_CORRECT_L,
    'medium': qrcode.constants.ERROR_CORRECT_M,
    'quartile': qrcode.constants.ERROR_CORRECT_Q,
    'high': qrcode.constants.ERROR_CORRECT_H,
}


# QR 코드 데이터 생성
def get_qr_data_object(data, box_size, border, error_correction, mask_pattern,):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
            mask_pattern=mask_pattern,
        )
        qr.add_data(data, optimize=0,)
        qr.make(fit=True)
        return qr
    except Exception as e:
        st.error(f"{lang_messages['qr_code_data_error']}: {str(e)}")
        return None
    
# 사용자 정의 모양으로 QR 코드 패턴 이미지 생성 함수 (PNG)
def draw_custom_shape_image(qr_object, box_size, border, fill_color, back_color, pattern_shape, finder_pattern_shape, pattern_corner_radius, finder_corner_radius, pattern_cell_gap, finder_cell_gap,):
    if not qr_object:
        return None

    img_size = (qr_object.modules_count + 2 * border) * box_size
    img = Image.new('RGB', (img_size, img_size), back_color,)
    draw = ImageDraw.Draw(img)

    def draw_shape(draw, xy, shape, fill, corner_radius, cell_gap,):
        x1, y1, x2, y2 = xy
        effective_size = x2 - x1
        
        gap_pixels = int(box_size * (cell_gap / 100))
        new_x = x1 + gap_pixels // 2
        new_y = y1 + gap_pixels // 2
        new_x_end = x2 - (gap_pixels - gap_pixels // 2)
        new_y_end = y2 - (gap_pixels - gap_pixels // 2)
        draw_coords = [new_x, new_y, new_x_end, new_y_end]

        effective_size_after_gap = new_x_end - new_x
        
        if shape == lang_messages['pattern_shape_square']:
            draw.rectangle(draw_coords, fill=fill,)
        elif shape == lang_messages['pattern_shape_rounded']:
            radius = int(effective_size_after_gap * (corner_radius / 100))
            draw.rectangle([new_x + radius, new_y, new_x_end - radius, new_y_end], fill=fill,)
            draw.rectangle([new_x, new_y + radius, new_x_end, new_y_end - radius], fill=fill,)
            draw.pieslice([new_x, new_y, new_x + radius * 2, new_y + radius * 2], 180, 270, fill=fill,)
            draw.pieslice([new_x_end - radius * 2, new_y, new_x_end, new_y + radius * 2], 270, 360, fill=fill,)
            draw.pieslice([new_x, new_y_end - radius * 2, new_x + radius * 2, new_y_end], 90, 180, fill=fill,)
            draw.pieslice([new_x_end - radius * 2, new_y_end - radius * 2, new_x_end, new_y_end], 0, 90, fill=fill,)
        elif shape == lang_messages['pattern_shape_circle']:
            draw.ellipse(draw_coords, fill=fill,)
        elif shape == lang_messages['pattern_shape_diamond']:
            draw.polygon([(new_x + effective_size_after_gap/2, new_y),
                          (new_x + effective_size_after_gap, new_y + effective_size_after_gap/2),
                          (new_x + effective_size_after_gap/2, new_y + effective_size_after_gap),
                          (new_x, new_y + effective_size_after_gap/2)],
                          fill=fill,)
        elif shape == lang_messages['pattern_shape_star']:
            x_center = (new_x + new_x_end) / 2
            y_center = (new_y + new_y_end) / 2
            radius_outer = effective_size_after_gap / 1.5  # 이 갑으로 별 크기 조절
            radius_inner = radius_outer * 0.4
            points = []
            for i in range(5):
                angle_outer = math.radians(i * 72 + 54)
                x_outer = x_center + radius_outer * math.cos(angle_outer)
                y_outer = y_center + radius_outer * math.sin(angle_outer)
                points.append((x_outer, y_outer))
                angle_inner = math.radians(i * 72 + 90)
                x_inner = x_center + radius_inner * math.cos(angle_inner)
                y_inner = y_center + radius_inner * math.sin(angle_inner)
                points.append((x_inner, y_inner))
            draw.polygon(points, fill=fill,)
        elif shape == lang_messages['pattern_shape_cross']:
            x_center = (new_x + new_x_end) / 2
            y_center = (new_y + new_y_end) / 2
            cross_width = effective_size_after_gap * 0.4 # 십자 너비를 조정
            draw.rectangle([new_x, y_center - cross_width/2, new_x_end, y_center + cross_width/2], fill=fill,)
            draw.rectangle([x_center - cross_width/2, new_y, x_center + cross_width/2, new_y_end], fill=fill,)
        elif shape == lang_messages['pattern_shape_x']:
            # 'X'자 모양은 두 개의 겹치는 대각선으로 구현합니다.
            # 간격이 적용된 좌표를 사용
            x_center = (new_x + new_x_end) / 2
            y_center = (new_y + new_y_end) / 2
            effective_size = new_x_end - new_x # 간격이 적용된 유효한 크기
            x_width = effective_size * 0.25 # 엑스 너비 조정
            # 대각선 1: 왼쪽 위에서 오른쪽 아래로
            draw.polygon([(new_x, new_y + x_width), (new_x + x_width, new_y), (new_x_end, new_y_end - x_width), (new_x_end - x_width, new_y_end)], fill=fill,)
            # 대각선 2: 오른쪽 위에서 왼쪽 아래로
            draw.polygon([(new_x_end, new_y + x_width), (new_x_end - x_width, new_y), (new_x, new_y_end - x_width), (new_x + x_width, new_y_end)], fill=fill,)
        elif shape == lang_messages['pattern_shape_donut']:
            # 도넛 모양
            x1, y1, x2, y2 = xy
            effective_size = x2 - x1
            gap_pixels = int(box_size * (cell_gap / 100))
            new_x = x1 + gap_pixels // 2
            new_y = y1 + gap_pixels // 2
            new_x_end = x2 - (gap_pixels - gap_pixels // 2)
            new_y_end = y2 - (gap_pixels - gap_pixels // 2)
            draw_coords = [new_x, new_y, new_x_end, new_y_end]
            # 바깥쪽 원 (패턴 색상)
            draw.ellipse(draw_coords, fill=fill,)
            # 안쪽 원 (배경 색상)
            hole_size_ratio = 0.25 # 구멍 크기 비율을 조정 가능합니다.
            hole_size = effective_size * hole_size_ratio
            hole_x1 = new_x + (new_x_end - new_x) / 2 - hole_size / 2
            hole_y1 = new_y + (new_y_end - new_y) / 2 - hole_size / 2
            hole_x2 = new_x + (new_x_end - new_x) / 2 + hole_size / 2
            hole_y2 = new_y + (new_y_end - new_y) / 2 + hole_size / 2
            draw.ellipse([hole_x1, hole_y1, hole_x2, hole_y2], fill=back_color,) # back_color 변수 사용
        elif shape == lang_messages['pattern_shape_triangle']:
            # 위로 향하는 정삼각형
            x1, y1, x2, y2 = draw_coords
            mid_x = (x1 + x2) / 2
            draw.polygon([(mid_x, y1), (x2, y2), (x1, y2)], fill=fill,)
        elif shape == lang_messages['pattern_shape_pentagon']:
            # 오각
            x_center = (new_x + new_x_end) / 2
            y_center = (new_y + new_y_end) / 2
            radius = effective_size_after_gap / 1.8  # 이 값으로 크기를 조절
            points = []
            for i in range(5):
                angle = math.radians(72 * i - 90)  # 위쪽 꼭짓점부터 시작
                x = x_center + radius * math.cos(angle)
                y = y_center + radius * math.sin(angle)
                points.append((x, y))
            draw.polygon(points, fill=fill)
        elif shape == lang_messages['pattern_shape_hexagon']:
            # 육각
            x_center = (new_x + new_x_end) / 2
            y_center = (new_y + new_y_end) / 2
            radius = effective_size_after_gap / 1.92  # 이 값으로 크기를 조절
            points = []
            for i in range(6):
                angle = math.radians(60 * i)
                x = x_center + radius * math.cos(angle)
                y = y_center + radius * math.sin(angle)
                points.append((x, y))
            draw.polygon(points, fill=fill)
        elif shape == lang_messages['pattern_shape_heart']:
            # 하트
            width = effective_size_after_gap
            height = effective_size_after_gap
            x_center = new_x + width / 2
            y_center = new_y + height / 2
            # 하단 삼각형
            triangle_height = height * 0.4
            triangle_points = [
            (x_center, new_y_end),
            (new_x, new_y_end - triangle_height),
            (new_x_end, new_y_end - triangle_height)
            ]
            draw.polygon(triangle_points, fill=fill)
            # 상단 아치 및 원 부분
            radius_x = width / 2
            radius_y = height * 0.35
            draw.ellipse([x_center - radius_x, new_y, x_center, new_y + 2 * radius_y], fill=fill)
            draw.ellipse([x_center, new_y, x_center + radius_x, new_y + 2 * radius_y], fill=fill)
        elif shape == lang_messages['pattern_shape_spade']:
             # 세로 길이 늘리기
             new_y_end = new_y + (new_y_end - new_y) * 1.5

             # 하트는 원 + 삼각형 조합으로 단순하게 구현 (상하 뒤집힌 버전)
             width = effective_size_after_gap
             height = effective_size_after_gap
             x_center = (new_x + new_x_end) / 2
             y_center = (new_y + new_y_end) / 2

             # 상단 삼각형 (뒤집혀서 위로 향함)
             draw.polygon([(new_x, y_center), (new_x_end, y_center), (x_center, new_y)], fill=fill)

             # 하단 원 두 개
             radius = width / 4
             draw.ellipse([x_center - radius*2, y_center - radius, x_center, y_center + radius], fill=fill)
             draw.ellipse([x_center, y_center - radius, x_center + radius*2, y_center + radius], fill=fill)
        elif shape == lang_messages['pattern_shape_club']:
             # 클로버 모양 (삼각형 배치의 원 3개)
             width = effective_size_after_gap
             height = effective_size_after_gap
             x_center = (new_x + new_x_end) / 2
             y_center = (new_y + new_y_end) / 2
            
             # 클로버 잎 크기를 더 크게
             leaf_radius = width / 4.0  # 원의 크기, 작을수록 커짐
             offset = width / 4.0  # 원들 사이의 간격, 작을수록 넓어짐
            
             # 위쪽에 원 1개
             top_x = x_center
             top_y = y_center - offset
             draw.ellipse([top_x - leaf_radius, top_y - leaf_radius,
                           top_x + leaf_radius, top_y + leaf_radius], fill=fill)
            
             # 아래쪽 왼쪽에 원 1개
             left_x = x_center - offset
             left_y = y_center + offset
             draw.ellipse([left_x - leaf_radius, left_y - leaf_radius,
                           left_x + leaf_radius, left_y + leaf_radius], fill=fill)
            
             # 아래쪽 오른쪽에 원 1개
             right_x = x_center + offset
             right_y = y_center + offset
             draw.ellipse([right_x - leaf_radius, right_y - leaf_radius,
                           right_x + leaf_radius, right_y + leaf_radius], fill=fill)
        elif shape == lang_messages['pattern_shape_snowflake']:
            # 8각 눈꽃
            x_center = (new_x + new_x_end) / 2
            y_center = (new_y + new_y_end) / 2
            radius_outer = effective_size_after_gap / 1.5  # 이 값으로 크기를 조절
            radius_inner = radius_outer * 0.4
            points = []
            for i in range(8):
                angle_outer = math.radians(i * 45)   # 360° / 8 = 45°
                x_outer = x_center + radius_outer * math.cos(angle_outer)
                y_outer = y_center + radius_outer * math.sin(angle_outer)
                points.append((x_outer, y_outer))
                angle_inner = math.radians(i * 45 + 22.5)  # 중간 각도
                x_inner = x_center + radius_inner * math.cos(angle_inner)
                y_inner = y_center + radius_inner * math.sin(angle_inner)
                points.append((x_inner, y_inner))
            draw.polygon(points, fill=fill)

# 이부분에 가로/세로 패턴이 들어와야 함

    for r in range(qr_object.modules_count):
        for c in range(qr_object.modules_count):
            is_finder_pattern = False
            # 세 개의 파인더 패턴 위치에 있는지 확인
            if (r < 7 and c < 7) or (r >= qr_object.modules_count - 7 and c < 7) or (r < 7 and c >= qr_object.modules_count - 7):
                is_finder_pattern = True

            if qr_object.modules[r][c]:
                x = (c + border) * box_size
                y = (r + border) * box_size

                current_shape = finder_pattern_shape if is_finder_pattern else pattern_shape
                current_corner_radius = finder_corner_radius if is_finder_pattern else pattern_corner_radius
                current_cell_gap = finder_cell_gap if is_finder_pattern else pattern_cell_gap

                draw_coords = [x, y, x + box_size, y + box_size]
                draw_shape(draw, draw_coords, current_shape, fill_color, current_corner_radius, current_cell_gap,)

    return img

# QR 코드 SVG 생성 함수
def generate_qr_code_svg(data, box_size, border, error_correction, mask_pattern, fill_color, back_color,):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
            mask_pattern=mask_pattern,
        )
        qr.add_data(data, optimize=0)
        qr.make(fit=True)

        img_svg = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)

        svg_buffer = io.BytesIO()
        img_svg.save(svg_buffer)
        svg_data = svg_buffer.getvalue().decode('utf-8')

        svg_data = svg_data.replace('fill="black"', f'fill="{fill_color}"', 1,)
        svg_data = svg_data.replace('fill="white"', f'fill="{back_color}"', 1,)

        return svg_data, qr
    except Exception as e:
        st.error(f"{lang_messages['qr_code_svg_error']}: {str(e)}")
        return None, None


# QR 내용만 초기화하는 콜백 함수 (파일명은 유지)
def clear_text_input():
    st.session_state.qr_input_area = ""

# 파일명 초기화 콜백 함수
def clear_filename_callback():
    st.session_state.filename_input_key = ""

# 전체 초기화 콜백 함수
def reset_all_settings():
    st.session_state.qr_input_area = ""
    st.session_state.custom_pattern_color_input_key = ""
    st.session_state.custom_bg_color_input_key = ""
    st.session_state.filename_input_key = ""

    st.session_state.box_size_input = 20
    st.session_state.border_input = 2
    st.session_state.error_correction_select = messages[st.session_state.lang]['error_correction_low_select']
    st.session_state.mask_pattern_select = 2
    st.session_state.pattern_color_select = "black"
    st.session_state.bg_color_select = "white"
    st.session_state.strip_option = True
    st.session_state.file_format_select = "PNG"
    st.session_state.pattern_shape_select = lang_messages['pattern_shape_square']
    st.session_state.finder_pattern_shape_select = lang_messages['pattern_shape_square']
    st.session_state.corner_radius_input = 25
    st.session_state.finder_corner_radius_input = 25
    st.session_state.cell_gap_input = 1
    st.session_state.finder_cell_gap_input = 1
    st.session_state.jpg_quality_input = 50

# 언어 변경 콜백 함수
def set_language():
    old_lang = st.session_state.lang

    # 현재 설정값들을 임시 저장
    current_qr_data = st.session_state.get('qr_input_area', "")
    current_box_size = st.session_state.get('box_size_input', 20)
    current_border = st.session_state.get('border_input', 2)
    current_mask_pattern = st.session_state.get('mask_pattern_select', 2)
    current_error_correction_label = st.session_state.get('error_correction_select', messages[old_lang]['error_correction_low_select'])
    current_pattern_color_choice = st.session_state.get('pattern_color_select', "black")
    current_bg_color_choice = st.session_state.get('bg_color_select', "white")
    current_custom_pattern_color = st.session_state.get('custom_pattern_color_input_key', "")
    current_custom_bg_color = st.session_state.get('custom_bg_color_input_key', "")
    current_filename = st.session_state.get('filename_input_key', "")
    current_strip_option = st.session_state.get('strip_option', True)
    current_file_format = st.session_state.get('file_format_select', "PNG")
    current_pattern_shape = st.session_state.get('pattern_shape_select', messages[old_lang]['pattern_shape_square'])
    current_finder_shape = st.session_state.get('finder_pattern_shape_select', messages[old_lang]['pattern_shape_square'])
    current_corner_radius = st.session_state.get('corner_radius_input', 25)
    current_finder_corner_radius = st.session_state.get('finder_corner_radius_input', 25)
    current_cell_gap = st.session_state.get('cell_gap_input', 1)
    current_finder_cell_gap = st.session_state.get('finder_cell_gap_input', 1)
    current_jpg_quality = st.session_state.get('jpg_quality_input', 50)


# 선택된 언어 이름을 언어 코드로 변환
    lang_map = {
        "한국어 (Korean)": "ko",
        "English (US)": "en",
        "日本語 (Japanese)": "ja",
        "中文 (Chinese)": "zh",
        "Deutsch (German)": "de",
        "Français (French)": "fr",
        "Español (Spanish)": "es",
        "Türkçe (Turkish)": "tr",
        "Русский (Russian)": "ru",
        "Português (Portuguese)": "pt",
        "العربية (Arabic)": "ar",
        "हिन्दी (Hindi)": "hi",
        "বাংলা (Bengali)": "bn",
    }

    new_lang = lang_map.get(st.session_state.lang_select, "ko",)

    
    # 언어 변경이 발생했을 때만 상태를 업데이트
    if new_lang != old_lang:
        st.session_state.lang = new_lang
        # 기존 언어의 오류 복원 레벨을 상수값으로 변환
        error_correction_map_old_lang = {
            messages[old_lang]['error_correction_low_select']: qrcode.constants.ERROR_CORRECT_L,
            messages[old_lang]['error_correction_medium_select']: qrcode.constants.ERROR_CORRECT_M,
            messages[old_lang]['error_correction_quartile_select']: qrcode.constants.ERROR_CORRECT_Q,
            messages[old_lang]['error_correction_high_select']: qrcode.constants.ERROR_CORRECT_H,
        }
        current_error_constant = error_correction_map_old_lang.get(current_error_correction_label, qrcode.constants.ERROR_CORRECT_L)

        # 새로운 언어의 텍스트로 변환
        error_correction_map_new_lang = {
            qrcode.constants.ERROR_CORRECT_L: messages[new_lang]['error_correction_low_select'],
            qrcode.constants.ERROR_CORRECT_M: messages[new_lang]['error_correction_medium_select'],
            qrcode.constants.ERROR_CORRECT_Q: messages[new_lang]['error_correction_quartile_select'],
            qrcode.constants.ERROR_CORRECT_H: messages[new_lang]['error_correction_high_select'],
        }
        st.session_state.error_correction_select = error_correction_map_new_lang.get(current_error_constant, messages[new_lang]['error_correction_low_select'])

        # 패턴 모양도 동일하게 변환
        pattern_shape_map_old_lang = {
            messages[old_lang]['pattern_shape_square']: 'square',
            messages[old_lang]['pattern_shape_rounded']: 'rounded',
            messages[old_lang]['pattern_shape_circle']: 'circle',
            messages[old_lang]['pattern_shape_diamond']: 'diamond',
            messages[old_lang]['pattern_shape_triangle']: 'triangle',
            messages[old_lang]['pattern_shape_star']: 'star',
            messages[old_lang]['pattern_shape_cross']: 'cross',
            messages[old_lang]['pattern_shape_x']: 'x',
            messages[old_lang]['pattern_shape_donut']: 'donut',
            messages[old_lang]['pattern_shape_pentagon']: 'pentagon',
            messages[old_lang]['pattern_shape_hexagon']: 'hexagon',
            messages[old_lang]['pattern_shape_heart']: 'heart',
            messages[old_lang]['pattern_shape_spade']: 'spade',
            messages[old_lang]['pattern_shape_club']: 'club',
            messages[old_lang]['pattern_shape_snowflake']: 'snowflake',
            messages[old_lang]['pattern_shape_vertical_line']: 'vertical',
            messages[old_lang]['pattern_shape_horizontal_line']: 'horizontal',
        }
        
        pattern_shape_map_new_lang = {
            'square': messages[new_lang]['pattern_shape_square'],
            'rounded': messages[new_lang]['pattern_shape_rounded'],
            'circle': messages[new_lang]['pattern_shape_circle'],
            'diamond': messages[new_lang]['pattern_shape_diamond'],
            'triangle': messages[new_lang]['pattern_shape_triangle'],
            'star': messages[new_lang]['pattern_shape_star'],
            'cross': messages[new_lang]['pattern_shape_cross'],
            'x': messages[new_lang]['pattern_shape_x'],
            'donut': messages[new_lang]['pattern_shape_donut'],
            'pentagon': messages[new_lang]['pattern_shape_pentagon'],
            'hexagon': messages[new_lang]['pattern_shape_hexagon'],
            'heart': messages[new_lang]['pattern_shape_heart'],
            'spade': messages[new_lang]['pattern_shape_spade'],
            'club': messages[new_lang]['pattern_shape_club'],
            'snowflake': messages[new_lang]['pattern_shape_snowflake'],
            'vertical': messages[new_lang]['pattern_shape_vertical_line'],
            'horizontal': messages[new_lang]['pattern_shape_horizontal_line'],
         }

        # 기존 선택된 값을 새 언어의 값으로 업데이트
        old_pattern_shape_key = pattern_shape_map_old_lang.get(current_pattern_shape, 'square')
        st.session_state.pattern_shape_select = pattern_shape_map_new_lang.get(old_pattern_shape_key, messages[new_lang]['pattern_shape_square'])
        
        old_finder_shape_key = pattern_shape_map_old_lang.get(current_finder_shape, 'square')
        st.session_state.finder_pattern_shape_select = pattern_shape_map_new_lang.get(old_finder_shape_key, messages[new_lang]['pattern_shape_square'])

        # 색상 선택 값도 변환
        if current_pattern_color_choice == messages[old_lang]['custom_color_select']:
            st.session_state.pattern_color_select = messages[new_lang]['custom_color_select']
        else:
            st.session_state.pattern_color_select = current_pattern_color_choice

        if current_bg_color_choice == messages[old_lang]['custom_color_select']:
            st.session_state.bg_color_select = messages[new_lang]['custom_color_select']
        else:
            st.session_state.bg_color_select = current_bg_color_choice


    # 언어 변경 후, 저장했던 값들을 다시 복원
    st.session_state.qr_input_area = current_qr_data
    st.session_state.box_size_input = current_box_size
    st.session_state.border_input = current_border
    st.session_state.mask_pattern_select = current_mask_pattern
    st.session_state.custom_pattern_color_input_key = current_custom_pattern_color
    st.session_state.custom_bg_color_input_key = current_custom_bg_color
    st.session_state.filename_input_key = current_filename
    st.session_state.strip_option = current_strip_option
    st.session_state.file_format_select = current_file_format
    st.session_state.corner_radius_input = current_corner_radius
    st.session_state.finder_corner_radius_input = current_finder_corner_radius
    st.session_state.cell_gap_input = current_cell_gap
    st.session_state.finder_cell_gap_input = current_finder_cell_gap
    st.session_state.jpg_quality_input = current_jpg_quality


#[메인]====================================================================================================================================================================

st.title(lang_messages['title'])
st.markdown("---")

# 언어 선택 드롭다운
lang_options = {
    "한국어 (Korean)": "ko",
    "English (US)": "en",
    "日本語 (Japanese)": "ja",
    "中文 (Chinese)": "zh",
    "Deutsch (German)": "de",
    "Français (French)": "fr",
    "Español (Spanish)": "es",
    "Türkçe (Turkish)": "tr",
    "Русский (Russian)": "ru",
    "Português (Portuguese)": "pt",
    "العربية (Arabic)": "ar",
    "हिन्दी (Hindi)": "hi",
    "বাংলা (Bengali)": "bn",
}

lang_selected_name = st.selectbox(
    "언어 선택(Select Language)" if st.session_state.lang == "ko" else "Select Language",
    options=list(lang_options.keys()),
    on_change=set_language,
    key="lang_select",
    index=list(lang_options.values()).index(st.session_state.lang),
)

st.markdown("---")

# 레이아웃 설정 (2개 컬럼)
col1, col2 = st.columns([1.2, 1])

with col1:
    st.header(lang_messages['main_header'])

    # QR 코드 입력창
    st.subheader(lang_messages['qr_content_subheader'])
    st.info(lang_messages['max_char_info'])

    qr_data = st.text_area(
        lang_messages['text_area_label'],
        height=200,
        placeholder=lang_messages['text_area_placeholder'],
        key="qr_input_area",
    )

    # 문자 수 표시
    char_count = len(qr_data) if qr_data else 0
    if char_count > 0:
        if char_count > 2900:
            st.error(lang_messages['char_count_exceeded'].format(char_count=char_count))
        elif char_count > 2400:
            st.warning(lang_messages['char_count_near_limit'].format(char_count=char_count))
        else:
            st.success(lang_messages['char_count_ok'].format(char_count=char_count))
    else:
        st.caption(lang_messages['char_count_zero'])

    # 공백/줄바꿈 제거 옵션
    strip_option = st.checkbox(
        lang_messages['strip_option'],
        value=st.session_state.strip_option,
        key="strip_option",
        help=lang_messages['strip_option_help'],
    )

    # 입력 내용 삭제 버튼
    col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
    with col_clear2:
        delete_btn_disabled = (char_count == 0)
        st.button(
            lang_messages['delete_button'],
            help=lang_messages['delete_button_help'],
            use_container_width=True,
            type="secondary",
            disabled=delete_btn_disabled,
            on_click=clear_text_input,
        )

    st.markdown("---")

    # 파일 형식 설정
    st.subheader(lang_messages['file_format_subheader'])
    file_format = st.selectbox(
        lang_messages['file_format_select_label'],
        ("PNG", "JPG", "SVG"),
        index=0 if st.session_state.file_format_select == "PNG" else (1 if st.session_state.file_format_select == "JPG" else 2),
        key="file_format_select",
    )

    # JPG 품질 설정 슬라이더 (JPG 선택 시에만 표시)
    if file_format == "JPG":
        st.caption(lang_messages['jpg_quality_info'])
        jpg_quality = st.slider(
            lang_messages['jpg_quality_label'],
            min_value=1,
            max_value=100,
            value=st.session_state.jpg_quality_input,
            key="jpg_quality_input",
            help=lang_messages['jpg_quality_help'],
        )
    else:
        jpg_quality = 50

    # 패턴 모양 설정
    st.markdown("---")
    st.subheader(lang_messages['pattern_shape_subheader'])
    pattern_shape_disabled = (file_format == "SVG")
    st.caption(lang_messages['pattern_shape_warning'])

    # 일반 패턴 모양 선택 옵션
    pattern_options = (
        lang_messages['pattern_shape_square'],
        lang_messages['pattern_shape_rounded'],
        lang_messages['pattern_shape_circle'],
        lang_messages['pattern_shape_diamond'],
        lang_messages['pattern_shape_triangle'],
        lang_messages['pattern_shape_star'],
        lang_messages['pattern_shape_cross'],
        lang_messages['pattern_shape_x'],
        lang_messages['pattern_shape_donut'],
        lang_messages['pattern_shape_pentagon'],
        lang_messages['pattern_shape_hexagon'],
        lang_messages['pattern_shape_heart'],
        lang_messages['pattern_shape_spade'],
        lang_messages['pattern_shape_club'],
        lang_messages['pattern_shape_snowflake'],
#        lang_messages['pattern_shape_vertical_line'],
#        lang_messages['pattern_shape_horizontal_line'],
    )

    pattern_shape = st.selectbox(
        lang_messages['pattern_select_label'],
        pattern_options, # pattern_options 튜플을 재사용
        key="pattern_shape_select",
        disabled=pattern_shape_disabled,
    )

    # 둥근사각 전용 슬라이더 (일반 패턴) - 즉각 반응을 위해 조건문 밖으로 이동
    corner_radius_disabled = (file_format == "SVG") or (pattern_shape != lang_messages['pattern_shape_rounded'])
    if pattern_shape == lang_messages['pattern_shape_rounded']:
        st.caption(lang_messages['corner_radius_warning'])
    corner_radius = st.slider(
        lang_messages['corner_radius_label'],
        min_value=0,
        max_value=50,
        value=st.session_state.corner_radius_input,
        help=lang_messages['corner_radius_help'],
        key="corner_radius_input",
        disabled=corner_radius_disabled,
    )

    # 패턴 간격 슬라이더 (일반 패턴)
    cell_gap_disabled = (file_format == "SVG")
    st.caption(lang_messages['cell_gap_warning'])
    cell_gap = st.slider(
        lang_messages['cell_gap_label'],
        min_value=1,
        max_value=40,
        value=st.session_state.cell_gap_input,
        help=lang_messages['cell_gap_help'],
        disabled=cell_gap_disabled,
        key="cell_gap_input",
        on_change=enforce_min_value,
    )

    # 파인더 패턴 모양 선택 옵션
    st.markdown("---")
    finder_pattern_shape = st.selectbox(
        lang_messages['finder_pattern_select_label'],
        pattern_options, # pattern_options 튜플을 재사용
        key="finder_pattern_shape_select",
        disabled=pattern_shape_disabled,
    )

    # 둥근사각 전용 슬라이더 (파인더 패턴) - 즉각 반응을 위해 조건문 밖으로 이동
    finder_corner_radius_disabled = (file_format == "SVG") or (finder_pattern_shape != lang_messages['pattern_shape_rounded'])
    if finder_pattern_shape == lang_messages['pattern_shape_rounded']:
        st.caption(lang_messages['finder_corner_radius_warning'])
    finder_corner_radius = st.slider(
        lang_messages['finder_corner_radius_label'],
        min_value=0,
        max_value=50,
        value=st.session_state.finder_corner_radius_input,
        help=lang_messages['finder_corner_radius_help'],
        key="finder_corner_radius_input",
        disabled=finder_corner_radius_disabled,
    )

    # 패턴 간격 슬라이더 (파인더 패턴)
    finder_cell_gap_disabled = (file_format == "SVG")
    st.caption(lang_messages['finder_cell_gap_warning'])
    finder_cell_gap = st.slider(
        lang_messages['finder_cell_gap_label'],
        min_value=1,
        max_value=40,
        value=st.session_state.finder_cell_gap_input,
        help=lang_messages['finder_cell_gap_help'],
        disabled=finder_cell_gap_disabled,
        key="finder_cell_gap_input",
        on_change=enforce_min_value,
    )

#========================================================================================================================================================================

    # 색상 설정 (순서 변경)
    st.markdown("---")
    st.subheader(lang_messages['color_subheader'])

    file_format_is_svg = (st.session_state.file_format_select == "SVG")

    if file_format_is_svg:
        st.warning(lang_messages['svg_color_warning'])

    colors = [
        lang_messages['custom_color_select'], "black", "white", "gray", "lightgray", "dimgray",
        "red", "green", "blue", "yellow", "cyan", "magenta", "maroon",
        "purple", "navy", "lime", "olive", "teal", "aqua", "fuchsia",
        "silver", "gold", "orange", "orangered", "crimson", "indigo",
    ]
    col1_3, col1_4 = st.columns(2)
    with col1_3:
        pattern_color_choice = st.selectbox(
            lang_messages['pattern_color_label'], colors,
            index=colors.index(st.session_state.pattern_color_select),
            key="pattern_color_select",
            disabled=file_format_is_svg,
        )
    with col1_4:
        bg_color_choice = st.selectbox(
            lang_messages['bg_color_label'], colors,
            index=colors.index(st.session_state.bg_color_select),
            key="bg_color_select",
            disabled=file_format_is_svg,
        )

    st.markdown(lang_messages['custom_color_info'])
    st.caption(lang_messages['custom_color_example'])
    col1_5, col1_6 = st.columns(2)
    with col1_5:
        st.text_input(
            lang_messages['pattern_hex_label'],
            placeholder=lang_messages['custom_color_placeholder'],
            disabled=(pattern_color_choice != lang_messages['custom_color_select']) or file_format_is_svg,
            key="custom_pattern_color_input_key",
        )
    with col1_6:
        st.text_input(
            lang_messages['bg_hex_label'],
            placeholder=lang_messages['custom_color_placeholder'],
            disabled=(bg_color_choice != lang_messages['custom_color_select']) or file_format_is_svg,
            key="custom_bg_color_input_key",
        )

    pattern_color = st.session_state.get('custom_pattern_color_input_key', '',).strip() if pattern_color_choice == lang_messages['custom_color_select'] else pattern_color_choice
    bg_color = st.session_state.get('custom_bg_color_input_key', '',).strip() if bg_color_choice == lang_messages['custom_color_select'] else bg_color_choice

#========================================================================================================================================================================

    # QR 코드 설정
    st.markdown("---")
    st.subheader(lang_messages['qr_setting_subheader'])

    col1_1, col1_2 = st.columns(2)
    with col1_1:
        # 1cell당 최소 px은 10으로 고정, 그 이하는 이미지 깨짐
        box_size = st.number_input(lang_messages['box_size_label'], min_value=10, max_value=100, key="box_size_input",)
        border = st.number_input(lang_messages['border_label'], min_value=0, max_value=10, key="border_input",)

    with col1_2:
        error_correction_options = {
            lang_messages['error_correction_low_select']: qrcode.constants.ERROR_CORRECT_L,
            lang_messages['error_correction_medium_select']: qrcode.constants.ERROR_CORRECT_M,
            lang_messages['error_correction_quartile_select']: qrcode.constants.ERROR_CORRECT_Q,
            lang_messages['error_correction_high_select']: qrcode.constants.ERROR_CORRECT_H,
        }
        error_correction_options_list = list(error_correction_options.keys())

        try:
            current_error_index = error_correction_options_list.index(st.session_state.error_correction_select)
        except ValueError:
            current_error_index = 0 # 만약 세션 상태 값이 없으면 기본값으로

        error_correction_choice = st.selectbox(
            lang_messages['error_correction_label'],
            options=error_correction_options_list,
            index=current_error_index,
            key="error_correction_select",
        )
        error_correction = error_correction_options[error_correction_choice]
        mask_pattern = st.selectbox(lang_messages['mask_pattern_label'], options=list(range(8)), key="mask_pattern_select",)


#========================================================================================================================================================================

    # 파일명 설정
    st.markdown("---")
    st.subheader(lang_messages['filename_subheader'])

    col_filename_input, col_filename_delete = st.columns([3, 1.1])

    with col_filename_input:
        filename = st.text_input(
            lang_messages['filename_input_label'],
            placeholder=lang_messages['filename_placeholder'],
            key="filename_input_key",
        )

    current_filename = filename.strip()

    with col_filename_delete:
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        filename_delete_disabled = not st.session_state.get("filename_input_key", "")
        st.button(
            lang_messages['filename_delete_button'],
            help=lang_messages['filename_delete_help'],
            use_container_width=True,
            type="secondary",
            disabled=filename_delete_disabled,
            on_click=clear_filename_callback,
        )


#========================================================================================================================================================================

with col2:
    st.header(lang_messages['preview_header'])

    current_data = qr_data.strip() if st.session_state.strip_option else qr_data

    is_pattern_color_valid_preview = (pattern_color_choice != lang_messages['custom_color_select']) or (pattern_color_choice == lang_messages['custom_color_select'] and pattern_color and is_valid_color(pattern_color))
    is_bg_color_valid_preview = (bg_color_choice != lang_messages['custom_color_select']) or (bg_color_choice == lang_messages['custom_color_select'] and bg_color and is_valid_color(bg_color))
    is_colors_same_preview = (is_pattern_color_valid_preview and is_bg_color_valid_preview and pattern_color and bg_color and pattern_color == bg_color)

    preview_image_display = None
    preview_qr_object = None

    can_generate_preview = current_data and (file_format == "SVG" or (is_pattern_color_valid_preview and is_bg_color_valid_preview and not is_colors_same_preview))

    download_data = None
    download_mime = ""
    download_extension = ""
    save_format = ""

    if can_generate_preview:
        try:
            qr = get_qr_data_object(
                current_data, int(st.session_state.box_size_input), int(st.session_state.border_input), error_correction,
                int(st.session_state.mask_pattern_select)
            )
            if qr:
                preview_qr_object = qr
                if file_format in ["PNG", "JPG"]:
                    preview_image_display = draw_custom_shape_image(
                        qr, int(st.session_state.box_size_input), int(st.session_state.border_input),
                        pattern_color, bg_color, st.session_state.pattern_shape_select,
                        st.session_state.finder_pattern_shape_select,
                        st.session_state.corner_radius_input,
                        st.session_state.finder_corner_radius_input,
                        st.session_state.cell_gap_input,
                        st.session_state.finder_cell_gap_input,
                    )
                    img_buffer = io.BytesIO()
                    if file_format == "PNG":
                        preview_image_display.save(img_buffer, format='PNG')
                        download_mime = "image/png"
                        download_extension = ".png"
                    elif file_format == "JPG":
                        # JPG는 투명도를 지원하지 않아, RGB 모드로 변환
                        rgb_image = preview_image_display.convert('RGB')
                        rgb_image.save(img_buffer, format='JPEG', quality=jpg_quality)
                        download_mime = "image/jpeg"
                        download_extension = ".jpg"

                    download_data = img_buffer.getvalue()

                else: # SVG
                    svg_data, _ = generate_qr_code_svg(
                        current_data, int(st.session_state.box_size_input), int(st.session_state.border_input), error_correction,
                        int(st.session_state.mask_pattern_select), "black", "white",
                    )
                    download_data = svg_data.encode('utf-8')
                    download_mime = "image/svg+xml"
                    download_extension = ".svg"

                    # SVG 미리보기를 위한 이미지 생성 (간격 0으로)
                    preview_image_display = draw_custom_shape_image(
                        qr, int(st.session_state.box_size_input), int(st.session_state.border_input),
                        "black", "white", lang_messages['pattern_shape_square'],
                        lang_messages['pattern_shape_square'],
                        st.session_state.corner_radius_input,
                        st.session_state.finder_corner_radius_input,
                        0, # SVG는 간격을 지원하지 않으므로 미리보기에서 간격 0으로 설정
                        0,
                    )
        except Exception as e:
            st.error(f"{lang_messages['error_occurred']}: {str(e)}")

    st.markdown("---")

    if preview_image_display:
        st.success(lang_messages['preview_success'])
        st.subheader(lang_messages['preview_subheader'])
        col_left, col_center, col_right = st.columns([1, 3.2, 1])
        with col_center:
            st.image(preview_image_display, caption=lang_messages['preview_subheader'], width=380)

        if preview_qr_object:
            st.subheader(lang_messages['qr_info_header'])
            st.info(f"""
- **{lang_messages['qr_version'].format(version=preview_qr_object.version)}**
- **{lang_messages['qr_modules_count'].format(modules_count=preview_qr_object.modules_count)}**
- **{lang_messages['qr_border_count'].format(border_count=2 * int(st.session_state.border_input))}**
- **{lang_messages['qr_box_size'].format(box_size=int(st.session_state.box_size_input))}**
- **{lang_messages['qr_image_size'].format(width=(preview_qr_object.modules_count + 2 * int(st.session_state.border_input)) * int(st.session_state.box_size_input), height=(preview_qr_object.modules_count + 2 * int(st.session_state.border_input)) * int(st.session_state.box_size_input))}**
---
- **{lang_messages['qr_size_formula']}**
---
- **{lang_messages['qr_pattern_color'].format(color='black' if file_format == 'SVG' else pattern_color)}**
- **{lang_messages['qr_bg_color'].format(color='white' if file_format == 'SVG' else bg_color)}**
            """)

        # 다운로드 섹션의 위치를 미리보기 아래로 이동
        st.markdown("---")
        st.subheader(lang_messages['download_subheader'])
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        final_filename = sanitize_filename(st.session_state.filename_input_key.strip() if st.session_state.filename_input_key.strip() else now.strftime("QR_%Y-%m-%d_%H-%M-%S"))
        download_filename = f"{final_filename}{download_extension}"

        st.download_button(
            label=lang_messages['download_button'],
            data=download_data,
            file_name=download_filename,
            mime=download_mime,
            use_container_width=True,
            help=lang_messages['download_help'],
        )

        st.markdown(
            f'<p style="font-size:18px;">'
            f'<span style="color:darkorange; font-weight:bold;">{lang_messages["download_filename_display"]} </span> '
            f'<span style="color:dodgerblue;"> {download_filename}</span>'
            f'</p>',
            unsafe_allow_html=True,
        )

    elif current_data:
        st.warning(lang_messages['preview_warning'])

        if file_format != "SVG":
            if pattern_color_choice == lang_messages['custom_color_select'] and not pattern_color:
                st.warning(lang_messages['pattern_hex_empty_warning'])
            if bg_color_choice == lang_messages['custom_color_select'] and not bg_color:
                st.warning(lang_messages['bg_hex_empty_warning'])
            if pattern_color_choice == lang_messages['custom_color_select'] and pattern_color and not is_valid_color(pattern_color):
                st.warning(lang_messages['pattern_hex_invalid_warning'])
            if bg_color_choice == lang_messages['custom_color_select'] and bg_color and not is_valid_color(bg_color):
                st.warning(lang_messages['bg_hex_invalid_warning'])
            if is_colors_same_preview:
                st.warning(lang_messages['same_color_warning'])
    else:
        st.info(lang_messages['no_input_info'])


st.markdown("---")

st.button(
    label=lang_messages['reset_button'],
    use_container_width=True,
    type="secondary",
    on_click=reset_all_settings,
    help=lang_messages['reset_button_help'],
)

with st.sidebar:
    st.header(lang_messages['sidebar_title'])
    st.markdown(f"""
    {lang_messages['how_to_use_step1']}
    {lang_messages['how_to_use_step2']}
    {lang_messages['how_to_use_step3']}
    {lang_messages['how_to_use_step4']}
    {lang_messages['how_to_use_step5']}
    {lang_messages['how_to_use_step6']}
    """)

    st.markdown("---")

    st.header(lang_messages['sidebar_tip_title'])
    st.markdown(f"""
    - {lang_messages['text_example']}
    - {lang_messages['website_example']}
    - {lang_messages['email_example']}
    - {lang_messages['email_full_example']}
    - {lang_messages['phone_example']}
    - {lang_messages['sms_example']}
    - {lang_messages['sms_full_example']}
    - {lang_messages['wifi_example']}
    """)

    st.markdown("---")

    st.header(lang_messages['sidebar_setting_guide_title'])
    st.markdown(f"**{lang_messages['sidebar_file_format']}**")
    st.markdown(f"""
    {lang_messages['file_format_png']}
    {lang_messages['file_format_jpg']}
    {lang_messages['file_format_svg']}
    """)

    st.markdown("---")

    st.markdown(f"**{lang_messages['sidebar_pattern_shape']}**")
    st.markdown(f"""
    - {lang_messages['pattern_shape_square']}, {lang_messages['pattern_shape_rounded']}, {lang_messages['pattern_shape_circle']}, {lang_messages['pattern_shape_diamond']}, {lang_messages['pattern_shape_triangle']}, {lang_messages['pattern_shape_star']}, {lang_messages['pattern_shape_cross']}, ... {lang_messages['pattern_shape_svg_note']}
    """)

    st.markdown(f"**{lang_messages['sidebar_pattern_gap']}**")
    st.markdown(f"""
    {lang_messages['pattern_gap_note1']}
    {lang_messages['pattern_gap_note2']}
    """)

    st.markdown("---")

    st.markdown(f"**{lang_messages['sidebar_color_input']}**")
    st.markdown(f"""
    {lang_messages['color_input_note1']}
    {lang_messages['color_input_note2']}
    {lang_messages['color_input_note3']}
    """)

    st.markdown("---")

    st.markdown(f"**{lang_messages['sidebar_qr_setting']}**")
    st.markdown(f"**{lang_messages['sidebar_error_correction']}**")
    st.markdown(f"""
    {lang_messages['error_correction_low']}
    {lang_messages['error_correction_medium']}
    {lang_messages['error_correction_quartile']}
    {lang_messages['error_correction_high']}
    """)

    st.markdown(f"**{lang_messages['sidebar_mask_pattern']}**")
    st.markdown(f"""
    {lang_messages['mask_pattern_note']}
    """)

# 하단 정보
st.markdown("---")
st.markdown(
    f'<p style="text-align: center; color: mediumslateblue; font-size: 15px;">{lang_messages["author_info"]}</p>',
    unsafe_allow_html=True
)
# 최종버전(다중 언어 지원 통함 파일 버전)
