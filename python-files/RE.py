
global _cpu_serial_cache  # inserted
import os
import tempfile
import sys
import re
import psutil
import shutil
import tempfile
import time
import json
import hashlib
import datetime
import uuid
import random
import platform
import locale
import subprocess
import numpy as np
from pathlib import Path
from shutil import rmtree
import io
import cv2
import colour
import torch
import dlib
from imutils import face_utils
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.functional import normalize
from torchvision.transforms.functional import normalize as torch_normalize
from basicsr.utils import imwrite, img2tensor, tensor2img
from basicsr.utils.download_util import load_file_from_url
from facelib.utils.face_restoration_helper import FaceRestoreHelper
from facelib.utils.misc import is_gray
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.realesrgan_utils import RealESRGANer
from basicsr.utils.registry import ARCH_REGISTRY
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSharedMemory
from PyQt5.QtWidgets import QFileDialog, QProgressBar, QLabel, QStatusBar, QMessageBox, QSplashScreen, QColorDialog, QFontComboBox, QSpinBox, QHBoxLayout
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, QObject, QTimer, Qt
from cryptography.fernet import Fernet
from PIL import ImageCms, Image, ExifTags, ImageFont, ImageDraw, ImageColor
import wmi
import configparser
HARD_CODED_KEY = b'B9x9-WSt4lzKmce9B9tCJTi-R7qGTxTfL3ZG5RMez5g='
hard_coded_fernet = Fernet(HARD_CODED_KEY)
if platform.system()!= 'Windows':
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()

class ThumbnailWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.label = ClickableLabel(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

class CustomWarningDialog(QtWidgets.QMessageBox):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.ok_button = self.button(QtWidgets.QMessageBox.Ok)
        self.mouse_timer = QtCore.QTimer(self)
        self.mouse_timer.timeout.connect(self.check_mouse_position)
        self.mouse_timer.setSingleShot(True)
        self.ok_button.installEventFilter(self)
        self.ok_button.setMouseTracking(True)
        self.mouse_in_ok_button = False

    def eventFilter(self, obj, event):
        if obj == self.ok_button:
            if event.type() == QtCore.QEvent.Enter:
                self.mouse_in_ok_button = True
                self.mouse_timer.start(10000)
            else:  # inserted
                if event.type() == QtCore.QEvent.Leave:
                    self.mouse_in_ok_button = False
                    self.mouse_timer.stop()
        return super().eventFilter(obj, event)

    def check_mouse_position(self):
        if self.mouse_in_ok_button:
            self.show_password_dialog()

    def show_password_dialog(self):
        password_dialog = QtWidgets.QInputDialog(self)
        password_dialog.setWindowTitle('Nhập mật khẩu')
        password_dialog.setLabelText('Nhập mật khẩu:')
        password_dialog.setTextEchoMode(QtWidgets.QLineEdit.Password)
        if password_dialog.exec_() == QtWidgets.QDialog.Accepted:
            entered_password = password_dialog.textValue()
            current_time = QtCore.QTime.currentTime()
            correct_password = f"91062{current_time.minute():02d}4"
            if entered_password == correct_password:
                self.update_serial_and_usage()
            else:  # inserted
                self.show_again()

    def update_serial_and_usage(self):
        parent = self.parentWidget()
        if parent:
            parent.usage_data['cpu_serial'] = parent.cpu_serial
            save_usage_data(parent.usage_data)
            usage_dialog = QtWidgets.QInputDialog(self)
            usage_dialog.setWindowTitle('Cập nhật giờ sử dụng')
            usage_dialog.setLabelText('Nhập số giờ sử dụng:')
            usage_dialog.setInputMode(QtWidgets.QInputDialog.IntInput)
            usage_dialog.setIntRange(0, 99999)
            usage_dialog.setIntStep(1)
            if usage_dialog.exec_() == QtWidgets.QDialog.Accepted:
                new_usage_hours = usage_dialog.intValue()
                parent.usage_data['max_usage_hours'] = new_usage_hours
                save_usage_data(parent.usage_data)
                parent.max_usage_hours = new_usage_hours
                parent.update_usage_time()

    def show_again(self):
        self.exec_()

def add_watermark(image, text='BUY NOW'):
    height, width = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = min(width, height) / 500
    font_thickness = int(font_scale * 2)
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_x_center = (width - text_size[0]) // 2
    text_y_center = (height + text_size[1]) // 2
    text_x_top = text_x_center
    text_y_top = (height // 4 + text_size[1]) // 2
    overlay = image.copy().astype(np.float32)
    cv2.putText(overlay, text, (text_x_center, text_y_center), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
    cv2.putText(overlay, text, (text_x_top, text_y_top), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    def add_noise_to_text_area(overlay, x, y, text_size):
        noise = np.random.randint(0, 50, (text_size[1], text_size[0], 3), dtype=np.uint8)
        noise = noise.astype(np.float32)
        noise_x, noise_y = (x, y - text_size[1])
        if noise_x + text_size[0] <= width and noise_y + text_size[1] <= height:
            overlay[noise_y:noise_y + text_size[1], noise_x:noise_x + text_size[0]] = cv2.addWeighted(overlay[noise_y:noise_y + text_size[1], noise_x:noise_x + text_size[0]].astype(np.float32), 0.7, noise, 0.3, 0)
    add_noise_to_text_area(overlay, text_x_center, text_y_center, text_size)
    add_noise_to_text_area(overlay, text_x_top, text_y_top, text_size)
    alpha = 0.4
    result = cv2.addWeighted(overlay.astype(np.float32), alpha, image.astype(np.float32), 1 - alpha, 0)
    result = np.clip(result, 0, 255).astype(np.uint8)
    return result

def add_watermark_custom(image, text='Watermark', positions=[], font_family='Arial', text_color='#FFFFFF', size_ratio=100, offset_x=0, offset_y=0):
    Logger.log(f'Adding watermark with text: \'{text}0\' at positions: {positions}0')
    height, width = image.shape[:2]
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    font_size = int(min(width, height) * (size_ratio / 100) / 10)
    Logger.log(f'Size Ratio: {size_ratio}0, Calculated Font Size: {font_size}0')
    try:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_directory, 'fonts', f'{font_family}0{'.ttf')
        if not os.path.exists(font_path):
            if platform.system() == 'Windows':
                font_path = f'C:/Windows/Fonts/{font_family}0.ttf'
            else:  # inserted
                if platform.system() == 'Darwin':
                    font_path = f'/Library/Fonts/{font_family}0.ttf'
                else:  # inserted
                    font_path = f'/usr/share/fonts/truetype/{font_family.lower()}/{font_family}.ttf'
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        Logger.log(f'Font \'{font_family}0\' not found. Using default font.')
        font = ImageFont.load_default()
    text_color_rgb = ImageColor.getrgb(text_color)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_size = (text_width, text_height)
    Logger.log(f'Calculated Text Size: {text_size}0')
    positions_dict = {'Top-Left': (offset_x, offset_y), 'Top-Right': (width - text_width - offset_x, offset_y), 'Bottom-Left': (offset_x, height - text_height - offset_y), 'Bottom-Right': (width - text_width - offset_x, height - text_height - offset_y), 'Center': ((width - text_width) // 2 + offset_x, (height - text_height) // 2 + offset_y)}
    for pos in positions:
        if pos in positions_dict:
            x, y = positions_dict[pos]
            Logger.log(f'Drawing watermark at position {pos}0: ({x}0, {y}0)')
            draw.text((x, y), text, font=font, fill=text_color_rgb)
    result = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return result

def safe_write(file_path, data):
    dir_name = os.path.dirname(file_path) or '.'
    os.makedirs(dir_name, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=dir_name)
    try:
        with os.fdopen(fd, 'wb') as temp_file:
            temp_file.write(data)
        os.replace(temp_path, file_path)
    except Exception as e:
        os.remove(temp_path)
        raise e

class Logger:
    @staticmethod
    def log(message):
        try:
            with open('event_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(message + '\n')
            print(message)
        except Exception as e:
            print(f'Failed to log event: {e}0')

def load_key():
    key_path = 'encrypted_secret.key'
    if not os.path.exists(key_path):
        if os.path.exists('usage_time.enc'):
            Logger.log(f'Key file {key_path}0 is missing.')
            QtWidgets.QMessageBox.critical(None, 'Error', f'Key file {key_path}0 is missing. Please restore it from backup.')
            sys.exit(1)
        else:  # inserted
            secret_key = Fernet.generate_key()
            encrypted_secret_key = hard_coded_fernet.encrypt(secret_key)
            safe_write(key_path, encrypted_secret_key)
    else:  # inserted
        with open(key_path, 'rb') as enc_key_file:
            encrypted_secret_key = enc_key_file.read()
    secret_key = hard_coded_fernet.decrypt(encrypted_secret_key)
    return secret_key

def save_encrypted_data(data, file_path, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    safe_write(file_path, encrypted_data)

def load_encrypted_data(file_path, key):
    fernet = Fernet(key)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return decrypted_data
    return None

def is_virtual_interface(interface_name):
    """\n    A simple check to determine if an interface is virtual.\n    This function can be expanded with more complex checks if necessary.\n    """  # inserted
    virtual_keywords = ['virtual', 'vmware', 'docker', 'hyper-v', 'loopback']
    return any((keyword.lower() in interface_name.lower() for keyword in virtual_keywords))
_cpu_serial_cache = None

def get_cpu_serial():
    global _cpu_serial_cache  # inserted
    if _cpu_serial_cache is not None:
        return _cpu_serial_cache
    try:
        c = wmi.WMI()
        for cpu in c.Win32_Processor():
            if cpu.ProcessorId:
                print(f'CPU Serial từ WMI: {cpu.ProcessorId}0')
                _cpu_serial_cache = cpu.ProcessorId
                return _cpu_serial_cache
            print('WMI trả về CPU serial là None.')
    except Exception as e:
        print(f'Không lấy được CPU serial từ WMI: {e}0')
    try:
        result = subprocess.check_output('wmic cpu get ProcessorId', shell=True)
        serial = result.decode().split('\n')[1].strip()
        if serial:
            print(f'UUID của hệ thống: {serial}0')
            _cpu_serial_cache = serial
            return _cpu_serial_cache
        print('Serial-2 của hệ thống là None hoặc không hợp lệ.')
    except Exception as e:
        print(f'Không lấy được Serial-2 của hệ thống: {e}0')
    try:
        mac_uuid = uuid.UUID(int=uuid.getnode()).hex[(-13):]
        if mac_uuid:
            print(f'UUID từ địa chỉ MAC: {mac_uuid}0')
            _cpu_serial_cache = mac_uuid
            return _cpu_serial_cache
        print('Không lấy được UUID từ địa chỉ MAC.')
    except Exception as e:
        print(f'Lỗi khi tạo UUID từ địa chỉ MAC: {e}0')
    try:
        cpu_info = platform.processor()
        if cpu_info:
            print(f'CPU thông qua platform: {cpu_info}0')
            _cpu_serial_cache = cpu_info
            return _cpu_serial_cache
        print('Platform processor trả về None.')
    except Exception as e:
        print(f'Lỗi khi lấy thông tin CPU với platform: {e}0')
    print('All attempts failed. Returning \'unknown\'.')
    _cpu_serial_cache = 'unknown'
    return _cpu_serial_cache

def merge_usage_data(file_data, registry_data):
    if not file_data:
        return {'total_seconds': registry_data.get('total_seconds', 0), 'cpu_serial': get_cpu_serial(), 'max_usage_hours': 3, 'activation_history': registry_data.get('activation_history', [])}
    merged_data = {}
    merged_data['total_seconds'] = max(file_data.get('total_seconds', 0), registry_data.get('total_seconds', 0))
    merged_data['cpu_serial'] = file_data.get('cpu_serial', get_cpu_serial())
    merged_data['max_usage_hours'] = max(file_data.get('max_usage_hours', 0), 0)
    merged_data['activation_history'] = list(set(file_data.get('activation_history', []) + registry_data.get('activation_history', [])))
    return merged_data

def load_usage_data():
    key = load_key()
    usage_data = load_encrypted_data('usage_time.enc', key)
    settings = QSettings('sys_config_1289', 'srv_manager_323')
    if usage_data:
        usage_data = json.loads(usage_data)
    else:  # inserted
        usage_data = {}
    registry_data = {'total_seconds': settings.value('total_seconds', 0, type=int), 'activation_history': settings.value('activation_history', [], type=list)}
    merged_data = merge_usage_data(usage_data, registry_data)
    current_cpu_serial = get_cpu_serial()
    if 'cpu_serial' in merged_data and merged_data['cpu_serial']!= current_cpu_serial:
        merged_data['max_usage_hours'] = 3
        Logger.log('Unauthorized use detected: CPU serial mismatch.')
        QtWidgets.QMessageBox.warning(None, 'Unauthorized Use', 'Phát hiện sử dụng không đúng key bản quyền.')
    return merged_data

def save_usage_data(usage_data):
    key = load_key()
    save_encrypted_data(json.dumps(usage_data), 'usage_time.enc', key)
    settings = QSettings('sys_config_1289', 'srv_manager_323')
    settings.setValue('total_seconds', usage_data.get('total_seconds', 0))
    settings.setValue('activation_history', usage_data.get('activation_history', []))

def format_time(total_seconds):
    hours = total_seconds // 3600
    minutes = total_seconds % 3600 // 60
    seconds = total_seconds % 60
    return f'{hours}h {minutes}m {seconds}s'

def generate_user_code():
    cpu_serial = get_cpu_serial()
    sha256_hash = hashlib.sha256(cpu_serial.encode()).hexdigest()
    int_dig = int(sha256_hash, 16)
    user_code_prefix = str(int_dig)[:39]
    start_date = datetime.datetime(2020, 1, 1, 0, 0)
    current_date = datetime.datetime.now()
    current_hours = int((current_date - start_date).total_seconds() // 3600)
    combined_value = str(int(user_code_prefix) + current_hours)[:39]
    final_user_code = user_code_prefix + combined_value
    return final_user_code

def imread(img_path):
    try:
        Logger.log(f'Reading image from path: {img_path}0')
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f'Failed to read image from path: {img_path}0')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    except Exception as e:
        Logger.log(f'Exception occurred while reading image: {e}0')
        raise

def save_image(restored_img, output_dir, filename, format, quality, avoid_overwrite=True):
    Logger.log(f'Saving image to {output_dir}0/{filename}0 with format {format} and quality {quality}0')
    try:
        os.makedirs(output_dir, exist_ok=True)
        extension_map = {'JPEG': '.jpg', 'PNG': '.png', 'BMP': '.bmp', 'TIFF': '.tiff'}
        if format not in extension_map:
            raise ValueError(f'Unsupported format: {format}0')
        file_ext = extension_map[format]
        base_filename = os.path.splitext(filename)[0]
        save_path = os.path.join(output_dir, base_filename + file_ext)
        if avoid_overwrite:
            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(output_dir, f'{base_filename}_{counter}0{file_ext}')
                counter += 1
        else:  # inserted
            save_path = os.path.join(output_dir, base_filename + file_ext)
        if format == 'JPEG':
            quality_map = {'Low': 50, 'Medium': 75, 'High': 90, 'Very High': 100}
            _, encoded_img = cv2.imencode('.jpg', restored_img, [int(cv2.IMWRITE_JPEG_QUALITY), quality_map[quality]])
        else:  # inserted
            if format == 'PNG':
                _, encoded_img = cv2.imencode('.png', restored_img)
            else:  # inserted
                if format == 'BMP':
                    _, encoded_img = cv2.imencode('.bmp', restored_img)
                else:  # inserted
                    if format == 'TIFF':
                        _, encoded_img = cv2.imencode('.tiff', restored_img)
        with open(save_path, 'wb') as f:
            f.write(encoded_img.tobytes())
        Logger.log(f'Image saved as {save_path}0')
        return save_path
    except Exception as e:
        Logger.log(f'Error saving image: {e}0')
        raise

def generate_facial_mask(image, predictor, expand_size=20, mask_mode='lông mày + mắt + mũi + miệng'):
    Logger.log(f'expand_size received in generate_facial_mask: {expand_size}0')
    Logger.log(f'mask_mode received in generate_facial_mask: {mask_mode}0')
    pass
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    detector = dlib.get_frontal_face_detector()
    rects = detector(gray, 1)
    if not rects:
        Logger.log('No faces detected. Returning empty mask.')
        return mask
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        features = {'mouth': shape[48:68], 'right_eye': shape[36:42], 'left_eye': shape[42:48], 'right_eyebrow': shape[17:22], 'left_eyebrow': shape[22:27], 'nose': shape[27:36]}
        mask_mode_to_features = {'lông mày': ['left_eyebrow', 'right_eyebrow'], 'mắt': ['left_eye', 'right_eye'], 'mũi': ['nose'], 'miệng': ['mouth'], 'lông mày + mắt': ['left_eyebrow', 'right_eyebrow', 'left_eye', 'right_eye'], 'lông mày + mắt + mũi': ['left_eyebrow', 'right_eyebrow', 'left_eye', 'right_eye', 'nose'], 'lông mày + mắt + mũi + miệng': ['left_eyebrow', 'right_eyebrow', 'left_eye', 'right_eye', 'nose', 'mouth']}
        selected_features = mask_mode_to_features.get(mask_mode, [])
        for key, feature in features.items():
            if key in selected_features:
                hull = cv2.convexHull(feature)
                cv2.drawContours(mask, [hull], (-1), 255, (-1))
        if expand_size > 0:
            kernel_size = 2 * expand_size + 1
            kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
    Logger.log('Facial mask generation completed.')
    return mask

def set_realesrgan(device, option='normal', run_skin=False):
    try:
        if option == 'super_fine':
            Logger.log('Setting RealESRGAN_x4plus (SIÊU MỊN)')
            model_path = 'CodeFormer/weights/realesrgan/RealESRGAN_x4plus.pth'
            scale = 4
        else:  # inserted
            if option == 'super_sharp':
                Logger.log('Setting RealESRNet (SIÊU GIỮ NÉT)')
                model_path = 'CodeFormer/weights/realesrgan/RealESRNet_x4plus.pth'
                scale = 4
            else:  # inserted
                Logger.log('Setting RealESRGAN_x2plus (MỊN BÌNH THƯỜNG)')
                model_path = 'CodeFormer/weights/realesrgan/RealESRGAN_x2plus.pth'
                scale = 2
        use_half = False
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale).to(device)
        tile_size = 100
        tile_pad = 20
        if run_skin:
            tile_size = 200
            tile_pad = 20
        upsampler = RealESRGANer(scale=scale, model_path=model_path, model=model, tile=tile_size, tile_pad=tile_pad, pre_pad=0, half=use_half, device=device)
        return upsampler
    except Exception as e:
        Logger.log(f'Error setting RealESRGAN with option {option}0: {e}0')
        raise

def resize_to_thumbnail(image, max_size=384):
    original_height, original_width = image.shape[:2]
    max_dimension = max(original_height, original_width)
    if max_dimension <= max_size:
        return image
    scale_factor = max_size / max_dimension
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

def load_codeformer(device):
    try:
        Logger.log('Loading CodeFormer model')
        codeformer_net = ARCH_REGISTRY.get('CodeFormer')(dim_embd=512, codebook_size=1024, n_head=8, n_layers=9, connect_list=['32', '64', '128', '256']).to(device)
        ckpt_path = 'CodeFormer/weights/CodeFormer/codeformer.pth'
        checkpoint = torch.load(ckpt_path, map_location=device)['params_ema']
        codeformer_net.load_state_dict(checkpoint)
        codeformer_net.eval()
        return codeformer_net
    except Exception as e:
        Logger.log(f'Error loading CodeFormer model: {e}0')
        raise

def load_restoreformer(device):
    try:
        Logger.log('Loading RestoreFormer++ model')
        model_path = 'CodeFormer/weights/RestoreFormerPlusPlus/last.ckpt'
        restoreformer_net = RestoreFormer(model_path=model_path, upscale=1, arch='RestoreFormer++', bg_upsampler=None, device=device, head_size=4, ex_multi_scale_num=1, beta=0.25)
        return restoreformer_net
    except Exception as e:
        Logger.log(f'Error loading RestoreFormer++ model: {e}0')
        raise

def blend_faces(restored_face, original_face, threshold1, threshold2, kernel_size):
    if kernel_size % 2 == 0:
        kernel_size += 1
    edges = cv2.Canny(cv2.cvtColor(original_face, cv2.COLOR_BGR2GRAY), threshold1, threshold2)
    edges = cv2.dilate(edges, None)
    mask = cv2.GaussianBlur(edges, (kernel_size, kernel_size), 0)
    mask = mask.astype(np.float32) / 255.0
    mask = 1 / (1 + np.exp((-10) * (mask - 0.5)))
    if mask.ndim == 2:
        mask = mask[:, :, np.newaxis]
    mask = np.repeat(mask, 3, axis=2)
    blended_face = restored_face * (1 - mask) + original_face * mask
    blended_face = blended_face.astype(np.uint8)
    return blended_face

def compare_histograms(img1, img2, step_name):
    hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()
    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    Logger.log(f'Histogram correlation after {step_name}0: {correlation}0')
    if correlation < 0.99:
        Logger.log(f'Warning: Significant color distortion detected after {step_name}0')

def assemble_frames_to_video(frames_input_dir, output_video_path, original_video_path):
    try:
        command = ['ffprobe', '-v', '0', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', original_video_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        fps_info = result.stdout.strip()
        try:
            if '/' in fps_info:
                numerator, denominator = map(float, fps_info.split('/'))
                fps = numerator / denominator
            else:  # inserted
                fps = float(fps_info)
            Logger.log(f'Original video FPS: {fps}0')
        except ValueError as e:
            Logger.log(f'Error parsing frame rate: {fps_info}0')
            raise ValueError(f'Could not parse frame rate from ffprobe output: {fps_info}0') from e
        frame_files = [f for f in os.listdir(frames_input_dir) if f.startswith('frame_') and os.path.isfile(os.path.join(frames_input_dir, f))]
        if not frame_files:
            raise FileNotFoundError(f'No frame files found in {frames_input_dir}0')
        first_frame_file = frame_files[0]
        frame_extension = os.path.splitext(first_frame_file)[1]
        Logger.log(f'Detected frame extension: {frame_extension}0')
        command = ['ffmpeg', '-y', '-framerate', str(fps), '-i', os.path.join(frames_input_dir, f'frame_%06d{frame_extension}0'), '-i', original_video_path, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-c:a', 'copy', '-shortest', output_video_path]
        subprocess.run(command, check=True)
        Logger.log(f'Video reassembled and saved to {output_video_path}0')
    except Exception as e:
        Logger.log(f'Error assembling video from frames: {e}0')
        raise

def extract_frames_from_video(video_path, frames_output_dir):
    try:
        os.makedirs(frames_output_dir, exist_ok=True)
        command = ['ffmpeg', '-y', '-i', video_path, '-q:v', '1', os.path.join(frames_output_dir, 'frame_%06d.png')]
        subprocess.run(command, check=True)
        Logger.log(f'Frames extracted to {frames_output_dir}0')
    except Exception as e:
        Logger.log(f'Error extracting frames from video: {e}0')
        raise

def extract_first_frame(video_path, thumbnail_path):
    try:
        command = ['ffmpeg', '-y', '-i', video_path, '-frames:v', '1', thumbnail_path]
        subprocess.run(command, check=True)
        Logger.log(f'Thumbnail extracted to {thumbnail_path}0')
    except Exception as e:
        Logger.log(f'Error extracting first frame from video: {e}0')
        raise

class VectorQuantizer(nn.Module):
    def __init__(self, n_e, e_dim, beta):
        super(VectorQuantizer, self).__init__()
        self.n_e = n_e
        self.e_dim = e_dim
        self.beta = beta
        self.embedding = nn.Embedding(self.n_e, self.e_dim)
        self.embedding.weight.data.uniform_((-1.0) / self.n_e, 1.0 / self.n_e)

    def forward(self, z):
        z = z.permute(0, 2, 3, 1).contiguous()
        z_flattened = z.view((-1), self.e_dim)
        d = torch.sum(z_flattened ** 2, dim=1, keepdim=True) + torch.sum(self.embedding.weight ** 2, dim=1) - 2 * torch.matmul(z_flattened, self.embedding.weight.t())
        min_encoding_indices = torch.argmin(d, dim=1).unsqueeze(1)
        min_encodings = torch.zeros(min_encoding_indices.shape[0], self.n_e).to(z)
        min_encodings.scatter_(1, min_encoding_indices, 1)
        z_q = torch.matmul(min_encodings, self.embedding.weight).view(z.shape)
        loss = torch.mean((z_q.detach() - z) ** 2) + self.beta * torch.mean((z_q - z.detach()) ** 2)
        z_q = z + (z_q - z).detach()
        e_mean = torch.mean(min_encodings, dim=0)
        perplexity = torch.exp(-torch.sum(e_mean * torch.log(e_mean + 1e-10)))
        z_q = z_q.permute(0, 3, 1, 2).contiguous()
        return (z_q, loss, (perplexity, min_encodings, min_encoding_indices, d))

    def get_codebook_entry(self, indices, shape):
        min_encodings = torch.zeros(indices.shape[0], self.n_e).to(indices)
        min_encodings.scatter_(1, indices[:, None], 1)
        z_q = torch.matmul(min_encodings.float(), self.embedding.weight)
        if shape is not None:
            z_q = z_q.view(shape)
            z_q = z_q.permute(0, 3, 1, 2).contiguous()
        return z_q

def nonlinearity(x):
    return x * torch.sigmoid(x)

def Normalize(in_channels):
    return nn.GroupNorm(num_groups=32, num_channels=in_channels, eps=1e-06, affine=True)

class Upsample(nn.Module):
    def __init__(self, in_channels, with_conv):
        super().__init__()
        self.with_conv = with_conv
        if self.with_conv:
            self.conv = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        x = nn.functional.interpolate(x, scale_factor=2.0, mode='nearest')
        if self.with_conv:
            x = self.conv(x)
        return x

class Downsample(nn.Module):
    def __init__(self, in_channels, with_conv):
        super().__init__()
        self.with_conv = with_conv
        if self.with_conv:
            self.conv = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=2, padding=0)

    def forward(self, x):
        if self.with_conv:
            pad = (0, 1, 0, 1)
            x = nn.functional.pad(x, pad, mode='constant', value=0)
            x = self.conv(x)
            return x
        x = nn.functional.avg_pool2d(x, kernel_size=2, stride=2)
        return x

class ResnetBlock(nn.Module):
    def __init__(self, *, in_channels, out_channels=None, conv_shortcut=False, dropout=0.0, temb_channels=512):
        super().__init__()
        self.in_channels = in_channels
        out_channels = in_channels if out_channels is None else out_channels
        self.out_channels = out_channels
        self.use_conv_shortcut = conv_shortcut
        self.norm1 = Normalize(in_channels)
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        if temb_channels > 0:
            self.temb_proj = nn.Linear(temb_channels, out_channels)
        else:  # inserted
            self.temb_proj = None
        self.norm2 = Normalize(out_channels)
        self.dropout = nn.Dropout(dropout)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        if self.in_channels!= self.out_channels:
            if self.use_conv_shortcut:
                self.conv_shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
            else:  # inserted
                self.nin_shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        else:  # inserted
            self.conv_shortcut = None
            self.nin_shortcut = None

    def forward(self, x, temb):
        h = x
        h = self.norm1(h)
        h = nonlinearity(h)
        h = self.conv1(h)
        if self.temb_proj is not None and temb is not None:
            h = h + self.temb_proj(nonlinearity(temb))[:, :, None, None]
        h = self.norm2(h)
        h = nonlinearity(h)
        h = self.dropout(h)
        h = self.conv2(h)
        if self.in_channels!= self.out_channels:
            if self.use_conv_shortcut and self.conv_shortcut is not None:
                x = self.conv_shortcut(x)
                return x + h
            if self.nin_shortcut is not None:
                x = self.nin_shortcut(x)
        return x + h

class MultiHeadAttnBlock(nn.Module):
    def __init__(self, in_channels, head_size=1):
        super().__init__()
        self.in_channels = in_channels
        self.head_size = head_size
        self.att_size = in_channels // head_size
        assert in_channels % head_size == 0, 'The size of head should be divided by the number of channels.'
        self.norm1 = Normalize(in_channels)
        self.norm2 = Normalize(in_channels)
        self.q = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, padding=0)
        self.k = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, padding=0)
        self.v = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, padding=0)
        self.proj_out = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, padding=0)

    def forward(self, x, y=None):
        h_ = x
        h_ = self.norm1(h_)
        if y is None:
            y = h_
        else:  # inserted
            y = self.norm2(y)
        q = self.q(y)
        k = self.k(h_)
        v = self.v(h_)
        b, c, h, w = q.shape
        q = q.reshape(b, self.head_size, self.att_size, h * w)
        q = q.permute(0, 3, 1, 2)
        k = k.reshape(b, self.head_size, self.att_size, h * w)
        k = k.permute(0, 3, 1, 2)
        v = v.reshape(b, self.head_size, self.att_size, h * w)
        v = v.permute(0, 3, 1, 2)
        q = q.transpose(1, 2)
        v = v.transpose(1, 2)
        k = k.transpose(1, 2).transpose(2, 3)
        scale = int(self.att_size) ** (-0.5)
        q.mul_(scale)
        w_ = torch.matmul(q, k)
        w_ = F.softmax(w_, dim=3)
        w_ = w_.matmul(v)
        w_ = w_.transpose(1, 2).contiguous()
        w_ = w_.view(b, h, w, (-1))
        w_ = w_.permute(0, 3, 1, 2)
        w_ = self.proj_out(w_)
        return x + w_

class MultiHeadEncoder(nn.Module):
    def __init__(self, ch, out_ch, ch_mult=(1, 2, 4, 8), num_res_blocks=2, attn_resolutions=[16], dropout=0.0, resamp_with_conv=True, in_channels=3, resolution=512, z_channels=256, double_z=True, enable_mid=True, head_size=1, **ignore_kwargs):
        super().__init__()
        self.ch = ch
        self.temb_ch = 0
        self.num_resolutions = len(ch_mult)
        self.num_res_blocks = num_res_blocks
        self.resolution = resolution
        self.in_channels = in_channels
        self.enable_mid = enable_mid
        self.conv_in = nn.Conv2d(in_channels, self.ch, kernel_size=3, stride=1, padding=1)
        curr_res = resolution
        in_ch_mult = (1,) + tuple(ch_mult)
        self.down = nn.ModuleList()
        for i_level in range(self.num_resolutions):
            block = nn.ModuleList()
            attn = nn.ModuleList()
            block_in = ch * in_ch_mult[i_level]
            block_out = ch * ch_mult[i_level]
            for i_block in range(self.num_res_blocks):
                block.append(ResnetBlock(in_channels=block_in, out_channels=block_out, temb_channels=self.temb_ch, dropout=dropout))
                block_in = block_out
                if curr_res in attn_resolutions:
                    attn.append(MultiHeadAttnBlock(block_in, head_size))
            down = nn.Module()
            down.block = block
            down.attn = attn
            if i_level!= self.num_resolutions - 1:
                down.downsample = Downsample(block_in, resamp_with_conv)
                curr_res = curr_res // 2
            self.down.append(down)
        if self.enable_mid:
            self.mid = nn.Module()
            self.mid.block_1 = ResnetBlock(in_channels=block_in, out_channels=block_in, temb_channels=self.temb_ch, dropout=dropout)
            self.mid.attn_1 = MultiHeadAttnBlock(block_in, head_size)
            self.mid.block_2 = ResnetBlock(in_channels=block_in, out_channels=block_in, temb_channels=self.temb_ch, dropout=dropout)
        self.norm_out = Normalize(block_in)
        self.conv_out = nn.Conv2d(block_in, 2 * z_channels if double_z else z_channels, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        hs = {}
        temb = None
        h = self.conv_in(x)
        hs['in'] = h
        for i_level in range(self.num_resolutions):
            for i_block in range(self.num_res_blocks):
                h = self.down[i_level].block[i_block](h, temb)
                if len(self.down[i_level].attn) > 0:
                    h = self.down[i_level].attn[i_block](h)
            if i_level!= self.num_resolutions - 1:
                hs['block_' + str(i_level)] = h
                h = self.down[i_level].downsample(h)
        if self.enable_mid:
            h = self.mid.block_1(h, temb)
            hs['block_' + str(i_level) + '_atten'] = h
            h = self.mid.attn_1(h)
            h = self.mid.block_2(h, temb)
            hs['mid_atten'] = h
        h = self.norm_out(h)
        h = nonlinearity(h)
        h = self.conv_out(h)
        hs['out'] = h
        return hs

class MultiHeadDecoderTransformer(nn.Module):
    pass
    pass
    pass
    pass
    def __init__(self, ch, out_ch, ch_mult=(1, 2, 4, 8), num_res_blocks=2, attn_resolutions=16, dropout=0.0, resamp_with_conv=True, in_channels=3, resolution=512, z_channels=256, give_pre_end=False, enable_mid=True, head_size=1, ex_multi_scale_num=0, **ignorekwargs):
        super().__init__()
        self.ch = ch
        self.temb_ch = 0
        self.num_resolutions = len(ch_mult)
        self.num_res_blocks = num_res_blocks
        self.resolution = resolution
        self.in_channels = in_channels
        self.give_pre_end = give_pre_end
        self.enable_mid = enable_mid
        in_ch_mult = (1,) + tuple(ch_mult)
        block_in = ch * ch_mult[self.num_resolutions - 1]
        curr_res = resolution // 2 ** (self.num_resolutions - 1)
        self.z_shape = (1, z_channels, curr_res, curr_res)
        print('Working with z of shape {} = {} dimensions.'.format(self.z_shape, np.prod(self.z_shape)))
        self.conv_in = nn.Conv2d(z_channels, block_in, kernel_size=3, stride=1, padding=1)
        if self.enable_mid:
            self.mid = nn.Module()
            self.mid.block_1 = ResnetBlock(in_channels=block_in, out_channels=block_in, temb_channels=self.temb_ch, dropout=dropout)
            self.mid.attn_1 = MultiHeadAttnBlock(block_in, head_size)
            self.mid.block_2 = ResnetBlock(in_channels=block_in, out_channels=block_in, temb_channels=self.temb_ch, dropout=dropout)
        self.up = nn.ModuleList()
        for i_level in reversed(range(self.num_resolutions)):
            block = nn.ModuleList()
            attn = nn.ModuleList()
            block_out = ch * ch_mult[i_level]
            for i_block in range(self.num_res_blocks + 1):
                block.append(ResnetBlock(in_channels=block_in, out_channels=block_out, temb_channels=self.temb_ch, dropout=dropout))
                block_in = block_out
                if curr_res in attn_resolutions:
                    attn.append(MultiHeadAttnBlock(block_in, head_size))
            up = nn.Module()
            up.block = block
            up.attn = attn
            if i_level!= 0:
                up.upsample = Upsample(block_in, resamp_with_conv)
                curr_res = curr_res * 2
            self.up.insert(0, up)
        self.norm_out = Normalize(block_in)
        self.conv_out = nn.Conv2d(block_in, out_ch, kernel_size=3, stride=1, padding=1)

    def forward(self, z, hs):
        temb = None
        h = self.conv_in(z)
        if self.enable_mid:
            h = self.mid.block_1(h, temb)
            h = self.mid.attn_1(h, hs['mid_atten'])
            h = self.mid.block_2(h, temb)
        for i_level in reversed(range(self.num_resolutions)):
            for i_block in range(self.num_res_blocks + 1):
                h = self.up[i_level].block[i_block](h, temb)
                if len(self.up[i_level].attn) > 0:
                    if 'block_' + str(i_level) + '_atten' in hs:
                        h = self.up[i_level].attn[i_block](h, hs['block_' + str(i_level) + '_atten'])
                    else:  # inserted
                        h = self.up[i_level].attn[i_block](h, hs['block_' + str(i_level)])
            if i_level!= 0:
                h = self.up[i_level].upsample(h)
        if self.give_pre_end:
            return h
        h = self.norm_out(h)
        h = nonlinearity(h)
        h = self.conv_out(h)
        return h

class VQVAEGANMultiHeadTransformer(nn.Module):
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    pass
    def __init__(self, n_embed=1024, embed_dim=256, ch=64, out_ch=3, ch_mult=(1, 2, 2, 4, 4, 8), num_res_blocks=2, attn_resolutions=(16,), dropout=0.0, in_channels=3, resolution=512, z_channels=256, double_z=False, enable_mid=True, fix_decoder=False, fix_codebook=True, fix_encoder=False, head_size=4, ex_multi_scale_num=0, beta=0.25):
        super(VQVAEGANMultiHeadTransformer, self).__init__()
        self.encoder = MultiHeadEncoder(ch=ch, out_ch=out_ch, ch_mult=ch_mult, num_res_blocks=num_res_blocks, attn_resolutions=attn_resolutions, dropout=dropout, in_channels=in_channels, resolution=resolution, z_channels=z_channels, double_z=double_z, enable_mid=enable_mid, head_size=head_size)
        for i in range(ex_multi_scale_num):
            attn_resolutions = [attn_resolutions[0], attn_resolutions[(-1)] * 2]
        self.decoder = MultiHeadDecoderTransformer(ch=ch, out_ch=out_ch, ch_mult=ch_mult, num_res_blocks=num_res_blocks, attn_resolutions=attn_resolutions, dropout=dropout, in_channels=in_channels, resolution=resolution, z_channels=z_channels, enable_mid=enable_mid, head_size=head_size)
        self.quantize = VectorQuantizer(n_embed, embed_dim, beta=beta)
        self.quant_conv = nn.Conv2d(z_channels, embed_dim, 1)
        self.post_quant_conv = nn.Conv2d(embed_dim, z_channels, 1)
        if fix_decoder:
            for _, param in self.decoder.named_parameters():
                param.requires_grad = False
            for _, param in self.post_quant_conv.named_parameters():
                param.requires_grad = False
            for _, param in self.quantize.named_parameters():
                param.requires_grad = False
        else:  # inserted
            if fix_codebook:
                for _, param in self.quantize.named_parameters():
                    param.requires_grad = False
        if fix_encoder:
            for _, param in self.encoder.named_parameters():
                param.requires_grad = False
            for _, param in self.quant_conv.named_parameters():
                param.requires_grad = False

    def encode(self, x):
        hs = self.encoder(x)
        h = self.quant_conv(hs['out'])
        quant, emb_loss, info = self.quantize(h)
        return (quant, emb_loss, info, hs)

    def decode(self, quant, hs):
        quant = self.post_quant_conv(quant)
        dec = self.decoder(quant, hs)
        return dec

    def forward(self, input):
        quant, diff, info, hs = self.encode(input)
        dec = self.decode(quant, hs)
        return (dec, diff, info, hs)

class RestoreFormer:
    pass
    pass
    def __init__(self, model_path, upscale=2, arch='RestoreFormer++', bg_upsampler=None, device=None, head_size=4, ex_multi_scale_num=1, beta=0.25):
        self.upscale = upscale
        self.bg_upsampler = bg_upsampler
        self.arch = arch
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None else device
        if arch == 'RestoreFormer':
            self.RF = VQVAEGANMultiHeadTransformer(head_size=head_size, ex_multi_scale_num=ex_multi_scale_num, beta=beta)
        else:  # inserted
            if arch == 'RestoreFormer++':
                self.RF = VQVAEGANMultiHeadTransformer(head_size=head_size, ex_multi_scale_num=ex_multi_scale_num, beta=beta)
            else:  # inserted
                raise NotImplementedError(f'Not supported arch: {arch}.')
        self.face_helper = FaceRestoreHelper(upscale, face_size=512, crop_ratio=(1, 1), det_model='retinaface_resnet50', save_ext='png', use_parse=True, device=self.device)
        loadnet = torch.load(model_path, map_location=lambda storage, loc: storage)
        weights = loadnet['state_dict']
        new_weights = {}
        for k, v in weights.items():
            if k.startswith('vqvae.'):
                k = k.replace('vqvae.', '')
            new_weights[k] = v
        self.RF.load_state_dict(new_weights, strict=False)
        self.RF.eval()
        self.RF = self.RF.to(self.device)

def color_transfer(source, target, alpha=1):
    """\n    Thực hiện color transfer từ ảnh \'source\' sang ảnh \'target\' dựa trên thuật toán Reinhard,\n    nhưng thêm tham số alpha để pha trộn (0 < alpha <= 1).\n\n    alpha = 1:  Áp dụng chuyển màu hoàn toàn như công thức Reinhard.\n    alpha = 0.5: Mềm hơn, chỉ chuyển 50% màu.\n    alpha = 0:   Bằng ảnh gốc (không đổi màu).\n    """  # inserted
    source_rgb = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
    target_rgb = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
    source_rgb_01 = source_rgb.astype(np.float32) / 255.0
    target_rgb_01 = target_rgb.astype(np.float32) / 255.0
    source_xyz = colour.sRGB_to_XYZ(source_rgb_01)
    target_xyz = colour.sRGB_to_XYZ(target_rgb_01)
    source_lab = colour.XYZ_to_Lab(source_xyz)
    target_lab = colour.XYZ_to_Lab(target_xyz)
    l_s, a_s, b_s = (source_lab[..., 0], source_lab[..., 1], source_lab[..., 2])
    l_t, a_t, b_t = (target_lab[..., 0], target_lab[..., 1], target_lab[..., 2])
    l_mean_s, l_std_s = (l_s.mean(), l_s.std() + 1e-08)
    a_mean_s, a_std_s = (a_s.mean(), a_s.std() + 1e-08)
    b_mean_s, b_std_s = (b_s.mean(), b_s.std() + 1e-08)
    l_mean_t, l_std_t = (l_t.mean(), l_t.std() + 1e-08)
    a_mean_t, a_std_t = (a_t.mean(), a_t.std() + 1e-08)
    b_mean_t, b_std_t = (b_t.mean(), b_t.std() + 1e-08)
    l_t_reinhard = (l_t - l_mean_t) / l_std_t * l_std_s + l_mean_s
    a_t_reinhard = (a_t - a_mean_t) / a_std_t * a_std_s + a_mean_s
    b_t_reinhard = (b_t - b_mean_t) / b_std_t * b_std_s + b_mean_s
    l_t_norm = alpha * l_t_reinhard + (1.0 - alpha) * l_t
    a_t_norm = alpha * a_t_reinhard + (1.0 - alpha) * a_t
    b_t_norm = alpha * b_t_reinhard + (1.0 - alpha) * b_t
    transfer_lab = np.stack([l_t_norm, a_t_norm, b_t_norm], axis=(-1))
    transfer_xyz = colour.Lab_to_XYZ(transfer_lab)
    transfer_rgb_01 = colour.XYZ_to_sRGB(transfer_xyz)
    transfer_rgb_01 = np.clip(transfer_rgb_01, 0.0, 1.0)
    transfer_rgb = (transfer_rgb_01 * 255.0).astype(np.uint8)
    transfer_bgr = cv2.cvtColor(transfer_rgb, cv2.COLOR_RGB2BGR)
    return transfer_bgr

def inference(image, upscale, codeformer_fidelity, codeformer_fidelity_mask, resize_value, output_dir, filename, format, quality, device, progress_callback=False, background_enhance=None, face_upsample=None, batch='RestoreFormer', restoreformer_net=None, codeformer_net=True, selected_model=100, mask=100, check_colorspace=200, max_usage_hours=100, blend_visibility=200, blend_visibility_mask=False, blend_visibility_face035=31, blend_visibility_mask_face035=10, run_skin=False, skin_run_value='', eye_dist_threshold=[], user_watermark_enabled='Arial', user_watermark_text='#FFFFFF', user_watermark_positions=100, font_family=0, text_color=0, size_ratio=True, offset_x=1, offset_y=1, avoid_overwrite=None, current_image_index=None, total_images='lông mày + mắt + mũi + miệng', predictor=None, upsampler=None, mask_mode='lông mày + mắt + mũi + miệng'):
    if not run_skin:
        upsampler = None
        upsamplerface = set_realesrgan(device, option='normal', run_skin=run_skin)
    else:  # inserted
        upsampler = set_realesrgan(device, option='normal', run_skin=run_skin)
        upsamplerface = set_realesrgan(device, option='normal', run_skin=run_skin)
    try:
        Logger.log(f'Starting inference on {image}0 using {device}0')
        if batch:
            progress_callback.emit(0, f'Processing image {current_image_index}0/{total_images}0: Starting inference on {image} using {device}0', 'green')
        else:  # inserted
            progress_callback.emit(0, f'Starting inference on {image}0 using {device}0', 'green')
        face_align = True
        only_center_face = False
        draw_box = False
        detection_model = 'retinaface_resnet50'
        has_aligned = not face_align
        upscale = 1 if has_aligned else upscale
        Logger.log('Reading the image')
        if batch:
            progress_callback.emit(1, f'Processing image {current_image_index}/{total_images}0: Reading the image...', 'green')
        else:  # inserted
            progress_callback.emit(1, 'Reading the image...', 'green')
        img = cv2.imdecode(np.fromfile(image, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            Logger.log(f'Failed to read image: {image}0')
            if batch:
                progress_callback.emit(1, f'Processing image {current_image_index}/{total_images}0: Failed to read image: {image}', 'red')
                return (None, None, None, None, None, None)
            progress_callback.emit(1, f'Failed to read image: {image}0', 'red')
            return (None, None, None, None, None, None)
        original_img_copy = img.copy()
        upscale = int(upscale)
        original_width, original_height = (img.shape[1], img.shape[0])
        Logger.log(f'Original image size: {original_width}0x{original_height}0')
        if batch:
            progress_callback.emit(2, f'Processing image {current_image_index}/{total_images}0: Original image size: {original_width}0x{original_height}0', 'green')
        else:  # inserted
            progress_callback.emit(2, f'Original image size: {original_width}x{original_height}0', 'green')
        target_size = resize_value * upscale
        original_max_size = max(original_width, original_height)
        if target_size < original_max_size and resize_value not in (1024, 2560, 4096):
            Logger.log('Product of resize_value and upscale is less than original image size. Keeping original size and setting upscale to 1.')
            if batch:
                progress_callback.emit(2.5, f'Processing image {current_image_index}/{total_images}0: Product of resize_value and upscale is less than original image size. Keeping original size and setting upscale to 1.', 'green')
            else:  # inserted
                progress_callback.emit(2.5, 'Product of resize_value and upscale is less than original image size. Keeping original size and setting upscale to 1.', 'green')
            upscale = 1
            skip_resizing = True
        else:  # inserted
            skip_resizing = False
        Logger.log('Checking if resizing is needed based on resize_value and maximum size')
        if batch:
            progress_callback.emit(3, f'Processing image {current_image_index}/{total_images}0: Checking if resizing is needed...', 'green')
        else:  # inserted
            progress_callback.emit(3, 'Checking if resizing is needed...', 'green')
        max_size = max(img.shape[0], img.shape[1])
        if not skip_resizing and resize_value > 0 and (max_size > resize_value):
            Logger.log(f'Resizing image based on resize_value {resize_value}0')
            if batch:
                progress_callback.emit(4, f'Processing image {current_image_index}/{total_images}0: Resizing image to {resize_value}px...', 'green')
            else:  # inserted
                progress_callback.emit(4, f'Resizing image to {resize_value}px...', 'green')
            scale_factor = resize_value / max_size
            new_size = (int(img.shape[1] * scale_factor), int(img.shape[0] * scale_factor))
            img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
            Logger.log(f'Resized image to {new_size}0')
            if batch:
                progress_callback.emit(5, f'Processing image {current_image_index}/{total_images}0: Resized image to {new_size}', 'green')
            else:  # inserted
                progress_callback.emit(5, f'Resized image to {new_size}0', 'green')
            compare_histograms(original_img_copy, img, 'resizing')
            if mask is not None:
                Logger.log('Resizing mask to match new image size')
                if batch:
                    progress_callback.emit(6, f'Processing image {current_image_index}/{total_images}0: Resizing mask...', 'green')
                else:  # inserted
                    progress_callback.emit(6, 'Resizing mask...', 'green')
                mask = cv2.resize(mask, new_size, interpolation=cv2.INTER_NEAREST)
                Logger.log(f'Resized mask to {new_size}0')
                if batch:
                    progress_callback.emit(7, f'Processing image {current_image_index}/{total_images}0: Resized mask to {new_size}', 'green')
                else:  # inserted
                    progress_callback.emit(7, f'Resized mask to {new_size}0', 'green')
        Logger.log('Checking if resizing is needed based on minimum dimension')
        if batch:
            progress_callback.emit(8, f'Processing image {current_image_index}/{total_images}0: Checking minimum dimension...', 'green')
        else:  # inserted
            progress_callback.emit(8, 'Checking minimum dimension...', 'green')
        min_size = min(img.shape[0], img.shape[1])
        if min_size < 512:
            Logger.log('Resizing image to meet minimum dimension requirement of 512px')
            if batch:
                progress_callback.emit(9, f'Processing image {current_image_index}/{total_images}0: Resizing image to meet minimum dimension...', 'green')
            else:  # inserted
                progress_callback.emit(9, 'Resizing image to meet minimum dimension...', 'green')
            scale_factor = 512 / min_size
            new_size = (int(img.shape[1] * scale_factor), int(img.shape[0] * scale_factor))
            img = cv2.resize(img, new_size, interpolation=cv2.INTER_CUBIC)
            Logger.log(f'Resized image to meet minimum dimension requirement: {new_size}0')
            if batch:
                progress_callback.emit(10, f'Processing image {current_image_index}/{total_images}0: Resized image to {new_size}', 'green')
            else:  # inserted
                progress_callback.emit(10, f'Resized image to {new_size}0', 'green')
            if mask is not None:
                Logger.log('Resizing mask to match new image size')
                if batch:
                    progress_callback.emit(11, f'Processing image {current_image_index}/{total_images}0: Resizing mask...', 'green')
                else:  # inserted
                    progress_callback.emit(11, 'Resizing mask...', 'green')
                mask = cv2.resize(mask, new_size, interpolation=cv2.INTER_NEAREST)
                Logger.log(f'Resized mask to {new_size}0')
                if batch:
                    progress_callback.emit(12, f'Processing image {current_image_index}/{total_images}0: Resized mask to {new_size}', 'green')
                else:  # inserted
                    progress_callback.emit(12, f'Resized mask to {new_size}0', 'green')
        progress_message = 'Resizing image completed.'
        Logger.log(progress_message)
        if batch:
            progress_callback.emit(20, f'Processing image {current_image_index}/{total_images}0: {progress_message}', 'green')
        else:  # inserted
            progress_callback.emit(20, progress_message, 'green')
        Logger.log('Initializing upsamplers for background and face')
        if batch:
            progress_callback.emit(21, f'Processing image {current_image_index}/{total_images}0: Initializing upsamplers...', 'green')
        else:  # inserted
            progress_callback.emit(21, 'Initializing upsamplers...', 'green')
        bg_upsampler = upsampler if background_enhance else None
        face_upsampler = upsamplerface if face_upsample else None
        Logger.log('Upscaling background image if applicable')
        if batch:
            progress_callback.emit(22, f'Processing image {current_image_index}/{total_images}0: Upscaling background image...', 'green')
        else:  # inserted
            progress_callback.emit(22, 'Upscaling background image...', 'green')
        bg_img = bg_upsampler.enhance(img, outscale=upscale)[0] if bg_upsampler is not None else None
        if bg_img is not None:
            compare_histograms(img, bg_img, 'background upsampling')
        Logger.log('Initializing FaceRestoreHelper')
        if batch:
            progress_callback.emit(23, f'Processing image {current_image_index}/{total_images}0: Initializing FaceRestoreHelper...', 'green')
        else:  # inserted
            progress_callback.emit(23, 'Initializing FaceRestoreHelper...', 'green')
        face_helper = FaceRestoreHelper(upscale, face_size=512, crop_ratio=(1, 1), det_model=detection_model, save_ext='png', use_parse=True, device=device)
        face_helper.read_image(img)
        Logger.log('Detecting faces...')
        if batch:
            progress_callback.emit(25, f'Processing image {current_image_index}/{total_images}0: Detecting faces...', 'green')
        else:  # inserted
            progress_callback.emit(25, 'Detecting faces...', 'green')
        num_det_faces = face_helper.get_face_landmarks_5(only_center_face=only_center_face, resize=640, eye_dist_threshold=eye_dist_threshold)
        Logger.log(f'Detected {num_det_faces}0 faces')
        if batch:
            progress_callback.emit(30, f'Processing image {current_image_index}/{total_images}0: Detected {num_det_faces} faces', 'green')
        else:  # inserted
            progress_callback.emit(30, f'Detected {num_det_faces} faces', 'green')
        Logger.log('Aligning and warping faces...')
        if batch:
            progress_callback.emit(35, f'Processing image {current_image_index}/{total_images}0: Aligning and warping faces...', 'green')
        else:  # inserted
            progress_callback.emit(35, 'Aligning and warping faces...', 'green')
        face_helper.align_warp_face()
        Logger.log('Face alignment completed')
        if batch:
            progress_callback.emit(40, f'Processing image {current_image_index}/{total_images}0: Face alignment completed', 'green')
        else:  # inserted
            progress_callback.emit(40, 'Face alignment completed', 'green')
        last_restored_face = None
        last_cropped_face = None
        face_helper.restored_faces = []
        for idx, cropped_face in enumerate(face_helper.cropped_faces):
            Logger.log(f'Processing face {idx + 1}/{num_det_faces}0')
            if batch:
                progress_callback.emit(45, f'Processing image {current_image_index}0/{total_images}0: Processing face {idx + 1}0/{num_det_faces}', 'green')
            else:  # inserted
                progress_callback.emit(45, f'Processing face {idx + 1}0{'/':0}', 'green')
            cropped_face_t = img2tensor(cropped_face / 255.0, bgr2rgb=True, float32=True).to(torch.float32)
            torch_normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
            cropped_face_t = cropped_face_t.unsqueeze(0).to(device)
            if selected_model == 'CodeFormer' and codeformer_net is not None:
                Logger.log('Using CodeFormer model for face restoration')
                if codeformer_fidelity > 1.8:
                    restored_face = cropped_face.copy()
                    Logger.log('Skipping CodeFormer processing as fidelity is above threshold')
                    if batch:
                        progress_callback.emit(50, f'Processing image {current_image_index}/{total_images}0: Skipping CodeFormer processing as fidelity is above threshold', 'green')
                    else:  # inserted
                        progress_callback.emit(50, 'Skipping CodeFormer processing as fidelity is above threshold', 'green')
                else:  # inserted
                    with torch.no_grad():
                        Logger.log('Running CodeFormer model for face restoration')
                        if batch:
                            progress_callback.emit(50, f'Processing image {current_image_index}/{total_images}0: Running CodeFormer model...', 'green')
                        else:  # inserted
                            progress_callback.emit(50, 'Running CodeFormer model...', 'green')
                        output = codeformer_net(cropped_face_t, w=codeformer_fidelity, adain=True)[0]
                        restored_face = tensor2img(output, rgb2bgr=True, min_max=((-1), 1))
                    Logger.log('Face restoration completed')
                    if batch:
                        progress_callback.emit(55, f'Processing image {current_image_index}/{total_images}0: Face restoration completed', 'green')
                    else:  # inserted
                        progress_callback.emit(55, 'Face restoration completed', 'green')
            else:  # inserted
                if selected_model == 'RestoreFormer' and restoreformer_net is not None:
                    Logger.log('Using RestoreFormer model for face restoration')
                    if codeformer_fidelity > 1.8:
                        restored_face = cropped_face.copy()
                        Logger.log('Skipping RestoreFormer processing as fidelity is above threshold')
                        if batch:
                            progress_callback.emit(50, f'Processing image {current_image_index}/{total_images}0: Skipping RestoreFormer processing as fidelity is above threshold', 'green')
                        else:  # inserted
                            progress_callback.emit(50, 'Skipping RestoreFormer processing as fidelity is above threshold', 'green')
                    else:  # inserted
                        with torch.no_grad():
                            Logger.log('Running RestoreFormer model for face restoration')
                            if batch:
                                progress_callback.emit(50, f'Processing image {current_image_index}/{total_images}0: Running RestoreFormer model...', 'green')
                            else:  # inserted
                                progress_callback.emit(50, 'Running RestoreFormer model...', 'green')
                            output, _, _, _ = restoreformer_net.RF(cropped_face_t)
                            restored_face = tensor2img(output.squeeze(0), rgb2bgr=True, min_max=((-1), 1))
                        Logger.log('Face restoration completed')
                        if batch:
                            progress_callback.emit(55, f'Processing image {current_image_index}/{total_images}0: Face restoration completed', 'green')
                        else:  # inserted
                            progress_callback.emit(55, 'Face restoration completed', 'green')
                else:  # inserted
                    Logger.log('No valid model selected or model not loaded')
                    if batch:
                        progress_callback.emit(50, f'Processing image {current_image_index}/{total_images}0: No valid model selected or model not loaded', 'red')
                    else:  # inserted
                        progress_callback.emit(50, 'No valid model selected or model not loaded', 'red')
                    restored_face = cropped_face.copy()
            compare_histograms(cropped_face, restored_face, f'face restoration {idx + 1}0')
            blended_face_user = blend_faces(restored_face, cropped_face, threshold1=blend_visibility, threshold2=blend_visibility_mask, kernel_size=skin_run_value)
            if codeformer_fidelity == 0:
                blended_face_user = restored_face
            print(f'Current mask_mode: {mask_mode}0')
            if mask_mode == 'miệng' or mask_mode == 'lông mày + mắt + mũi + miệng':
                gray = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
                rects = [dlib.rectangle(0, 0, cropped_face.shape[1], cropped_face.shape[0])]
                for rect in rects:
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    teeth_landmarks = shape[60:68]
                    teeth_mask = np.zeros(cropped_face.shape[:2], dtype=np.uint8)
                    cv2.fillPoly(teeth_mask, [teeth_landmarks], 255)
                    teeth_mask = cv2.GaussianBlur(teeth_mask, (15, 15), 0)
                    alpha_mask = teeth_mask.astype(np.float32) / 255.0
                    alpha_mask = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
                    blended_face_user = alpha_mask * cropped_face + (1 - alpha_mask) * blended_face_user
                    blended_face_user = blended_face_user.astype(np.uint8)
            blended_face_user = color_transfer(cropped_face, blended_face_user)
            face_helper.restored_faces.append(blended_face_user)
            last_restored_face = restored_face
            last_cropped_face = cropped_face
            Logger.log('Blending restored face with original face')
            if batch:
                progress_callback.emit(65, f'Processing image {current_image_index}/{total_images}0: Blending faces...', 'green')
            else:  # inserted
                progress_callback.emit(65, 'Blending faces...', 'green')
        face_helper.get_inverse_affine(None)
        if face_upsample and face_upsampler is not None:
            Logger.log('Pasting faces onto upsampled background image')
            if batch:
                progress_callback.emit(75, f'Processing image {current_image_index}/{total_images}0: Pasting faces onto background...', 'green')
            else:  # inserted
                progress_callback.emit(75, 'Pasting faces onto background...', 'green')
            if codeformer_fidelity > 1.8:
                if bg_img is not None:
                    restored_img = bg_img
                else:  # inserted
                    restored_img = img
            else:  # inserted
                restored_img = face_helper.paste_faces_to_input_image(upsample_img=bg_img, draw_box=draw_box, face_upsampler=face_upsampler)
        else:  # inserted
            Logger.log('Pasting faces onto original image')
            if batch:
                progress_callback.emit(75, f'Processing image {current_image_index}/{total_images}0: Pasting faces onto original image...', 'green')
            else:  # inserted
                progress_callback.emit(75, 'Pasting faces onto original image...', 'green')
            if codeformer_fidelity > 1.8:
                if bg_img is not None:
                    restored_img = bg_img
                else:  # inserted
                    restored_img = img
            else:  # inserted
                restored_img = face_helper.paste_faces_to_input_image(upsample_img=bg_img, draw_box=draw_box)
                Logger.log(f'restored_img dimensions: {restored_img.shape}0')
        if batch:
            progress_callback.emit(80, f'Processing image {current_image_index}/{total_images}0: Face restoration and pasting completed', 'green')
        else:  # inserted
            progress_callback.emit(80, 'Face restoration and pasting completed', 'green')
        compare_histograms(img, restored_img, 'face blending')
        if mask is not None:
            Logger.log('Processing mask provided')
            if batch:
                progress_callback.emit(81, f'Processing image {current_image_index}/{total_images}0: Processing mask...', 'green')
            else:  # inserted
                progress_callback.emit(81, 'Processing mask...', 'green')
            face_helper_vis035 = FaceRestoreHelper(upscale, face_size=512, crop_ratio=(1, 1), det_model=detection_model, save_ext='png', use_parse=True, device=device)
            face_helper_vis035.read_image(img)
            Logger.log('Detecting faces for mask processing')
            if batch:
                progress_callback.emit(82, f'Processing image {current_image_index}/{total_images}0: Detecting faces for mask...', 'green')
            else:  # inserted
                progress_callback.emit(82, 'Detecting faces for mask...', 'green')
            num_det_faces = face_helper_vis035.get_face_landmarks_5(only_center_face=only_center_face, resize=640, eye_dist_threshold=eye_dist_threshold)
            Logger.log(f'Detected {num_det_faces}0 faces for mask processing')
            if batch:
                progress_callback.emit(83, f'Processing image {current_image_index}/{total_images}0: Detected {num_det_faces} faces for mask', 'green')
            else:  # inserted
                progress_callback.emit(83, f'Detected {num_det_faces} faces for mask', 'green')
            face_helper_vis035.align_warp_face()
            face_helper_vis035.restored_faces = []
            for idx, cropped_face in enumerate(face_helper_vis035.cropped_faces):
                Logger.log(f'Processing face {idx + 1}/{num_det_faces}0 for mask blending')
                if batch:
                    progress_callback.emit(84, f'Processing image {current_image_index}0/{total_images}0: Processing face {idx + 1}0/{num_det_faces}0 for mask blending', 'green')
                else:  # inserted
                    progress_callback.emit(84, f'Processing face {idx + 1}0/{num_det_faces} for mask blending', 'green')
                cropped_face_t = img2tensor(cropped_face / 255.0, bgr2rgb=True, float32=True).to(torch.float32)
                torch_normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
                cropped_face_t = cropped_face_t.unsqueeze(0).to(device)
                if selected_model == 'CodeFormer' and codeformer_net is not None:
                    Logger.log('Using CodeFormer model for mask face restoration')
                    if codeformer_fidelity_mask > 1.8:
                        restored_face = cropped_face.copy()
                        Logger.log('Skipping CodeFormer Mask processing as fidelity Mask is above threshold')
                        if batch:
                            progress_callback.emit(87, f'Processing image {current_image_index}/{total_images}0: Skipping CodeFormer Mask processing as fidelity Mask is above threshold', 'green')
                        else:  # inserted
                            progress_callback.emit(87, 'Skipping CodeFormer Mask processing as fidelity Mask is above threshold', 'green')
                    else:  # inserted
                        with torch.no_grad():
                            Logger.log('Running CodeFormer model for mask face restoration')
                            if batch:
                                progress_callback.emit(85, f'Processing image {current_image_index}/{total_images}0: Running CodeFormer Mask model...', 'green')
                            else:  # inserted
                                progress_callback.emit(85, 'Running CodeFormer Mask model...', 'green')
                            output = codeformer_net(cropped_face_t, w=codeformer_fidelity_mask, adain=True)[0]
                            restored_face = tensor2img(output, rgb2bgr=True, min_max=((-1), 1))
                        Logger.log('Face restoration completed')
                        if batch:
                            progress_callback.emit(86, f'Processing image {current_image_index}/{total_images}0: Face Mask restoration completed', 'green')
                        else:  # inserted
                            progress_callback.emit(86, 'Face Mask restoration completed', 'green')
                else:  # inserted
                    if selected_model == 'RestoreFormer' and restoreformer_net is not None:
                        Logger.log('Using RestoreFormer model for mask face restoration')
                        if codeformer_fidelity_mask > 1.8:
                            restored_face = cropped_face.copy()
                            Logger.log('Skipping RestoreFormer Mask processing as fidelity Mask is above threshold')
                            if batch:
                                progress_callback.emit(87, f'Processing image {current_image_index}/{total_images}0: Skipping RestoreFormer Mask processing as fidelity Mask is above threshold', 'green')
                            else:  # inserted
                                progress_callback.emit(87, 'Skipping RestoreFormer Mask processing as fidelity Mask is above threshold', 'green')
                        else:  # inserted
                            with torch.no_grad():
                                Logger.log('Running RestoreFormer model for mask face restoration')
                                if batch:
                                    progress_callback.emit(85, f'Processing image {current_image_index}/{total_images}0: Running RestoreFormer Mask model...', 'green')
                                else:  # inserted
                                    progress_callback.emit(85, 'Running RestoreFormer Mask model...', 'green')
                                output, _, _, _ = restoreformer_net.RF(cropped_face_t)
                                restored_face = tensor2img(output.squeeze(0), rgb2bgr=True, min_max=((-1), 1))
                            Logger.log('Face restoration completed')
                            if batch:
                                progress_callback.emit(86, f'Processing image {current_image_index}/{total_images}0: Face Mask restoration completed', 'green')
                            else:  # inserted
                                progress_callback.emit(86, 'Face Mask restoration completed', 'green')
                    else:  # inserted
                        Logger.log('No valid model selected or model not loaded for mask processing')
                        if batch:
                            progress_callback.emit(87, f'Processing image {current_image_index}/{total_images}0: No valid model selected or model not loaded for mask processing', 'red')
                        else:  # inserted
                            progress_callback.emit(87, 'No valid model selected or model not loaded for mask processing', 'red')
                        restored_face = cropped_face.copy()
                if codeformer_fidelity_mask > 1.8:
                    blended_face_035 = cropped_face.copy()
                    face_helper_vis035.restored_faces.append(blended_face_035)
                    Logger.log('Skipping mask face blending as fidelity Mask is above threshold')
                else:  # inserted
                    blended_face_035 = blend_faces(restored_face, cropped_face, threshold1=blend_visibility_face035, threshold2=blend_visibility_mask_face035, kernel_size=skin_run_value)
                    gray = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
                    rects = [dlib.rectangle(0, 0, cropped_face.shape[1], cropped_face.shape[0])]
                    for rect in rects:
                        shape = predictor(gray, rect)
                        shape = face_utils.shape_to_np(shape)
                        teeth_landmarks = shape[60:68]
                        teeth_mask = np.zeros(cropped_face.shape[:2], dtype=np.uint8)
                        cv2.fillPoly(teeth_mask, [teeth_landmarks], 255)
                        teeth_mask_expanded = cv2.merge([teeth_mask, teeth_mask, teeth_mask])
                        blended_teeth = restored_face
                        blended_face_035 = np.where(teeth_mask_expanded == 255, blended_teeth, blended_face_035)
                    face_helper_vis035.restored_faces.append(blended_face_035)
                    Logger.log('Blending face with visibility mask')
                    if batch:
                        progress_callback.emit(87, f'Processing image {current_image_index}/{total_images}0: Blending face with visibility mask...', 'green')
                    else:  # inserted
                        progress_callback.emit(87, 'Blending face with visibility mask...', 'green')
            face_helper_vis035.get_inverse_affine(None)
            if face_upsample and face_upsampler is not None:
                Logger.log('Pasting faces onto upsampled background image')
                if batch:
                    progress_callback.emit(88, f'Processing image {current_image_index}/{total_images}0: Pasting faces onto background...', 'green')
                else:  # inserted
                    progress_callback.emit(88, 'Pasting faces onto background...', 'green')
                if codeformer_fidelity_mask > 1.8:
                    if bg_img is not None:
                        restored_img_vis035 = bg_img
                    else:  # inserted
                        restored_img_vis035 = img
                else:  # inserted
                    restored_img_vis035 = face_helper_vis035.paste_faces_to_input_image(upsample_img=bg_img, draw_box=draw_box, face_upsampler=face_upsampler)
            else:  # inserted
                Logger.log('Pasting faces onto original image')
                if batch:
                    progress_callback.emit(88, f'Processing image {current_image_index}/{total_images}0: Pasting faces onto original image...', 'green')
                else:  # inserted
                    progress_callback.emit(88, 'Pasting faces onto original image...', 'green')
                if codeformer_fidelity_mask > 1.8:
                    if bg_img is not None:
                        restored_img_vis035 = bg_img
                    else:  # inserted
                        restored_img_vis035 = img
                else:  # inserted
                    restored_img_vis035 = face_helper_vis035.paste_faces_to_input_image(upsample_img=bg_img, draw_box=draw_box)
            Logger.log(f'restored_img_vis035 dimensions: {restored_img_vis035.shape}0')
            if batch:
                progress_callback.emit(89, f'Processing image {current_image_index}/{total_images}0: Mask processing completed', 'green')
            else:  # inserted
                progress_callback.emit(89, 'Mask processing completed', 'green')
            Logger.log('Applying mask to combine images')
            if batch:
                progress_callback.emit(90, f'Processing image {current_image_index}/{total_images}0: Applying mask...', 'green')
            else:  # inserted
                progress_callback.emit(90, 'Applying mask...', 'green')
            max_height = max(restored_img.shape[0], restored_img_vis035.shape[0], mask.shape[0], img.shape[0])
            max_width = max(restored_img.shape[1], restored_img_vis035.shape[1], mask.shape[1], img.shape[1])
            Logger.log('Resizing images and mask to maximum dimensions')
            if batch:
                progress_callback.emit(91, f'Processing image {current_image_index}/{total_images}0: Resizing images and mask...', 'green')
            else:  # inserted
                progress_callback.emit(91, 'Resizing images and mask...', 'green')
            mask = cv2.resize(mask, (max_width, max_height), interpolation=cv2.INTER_NEAREST)
            mask = mask.astype(np.float32) / 255.0
            if mask.ndim == 2:
                mask = mask[:, :, np.newaxis]
            Logger.log(f'restored_img dimensions: {restored_img.shape}0')
            Logger.log(f'restored_img_vis035 dimensions: {restored_img_vis035.shape}0')
            Logger.log(f'Mask dimensions: {mask.shape}0')
            if batch:
                progress_callback.emit(92, f'Processing image {current_image_index}/{total_images}0: Images and mask prepared for blending', 'green')
            else:  # inserted
                progress_callback.emit(92, 'Images and mask prepared for blending', 'green')
            Logger.log('Feathering the mask')
            if batch:
                progress_callback.emit(93, f'Processing image {current_image_index}/{total_images}0: Feathering the mask...', 'green')
            else:  # inserted
                progress_callback.emit(93, 'Feathering the mask...', 'green')
            kernel_size = (31, 31)
            mask_blurred = cv2.GaussianBlur(mask, kernel_size, 0)
            if mask_blurred.ndim == 2:
                mask_blurred = mask_blurred[:, :, np.newaxis]
            mask_blurred = np.repeat(mask_blurred, 3, axis=2)
            Logger.log('Adjusting color and brightness of images for seamless blending')
            if batch:
                progress_callback.emit(94, f'Processing image {current_image_index}/{total_images}0: Adjusting color and brightness...', 'green')
            else:  # inserted
                progress_callback.emit(94, 'Adjusting color and brightness...', 'green')
            restored_img_vis035_lab = cv2.cvtColor(restored_img_vis035, cv2.COLOR_BGR2LAB).astype(np.float32)
            restored_img_lab = cv2.cvtColor(restored_img, cv2.COLOR_BGR2LAB).astype(np.float32)
            restored_img_vis035_lab[..., 1:] -= 128
            restored_img_lab[..., 1:] -= 128
            l_mean_vis035, l_std_vis035 = cv2.meanStdDev(restored_img_vis035_lab[..., 0])
            a_mean_vis035, a_std_vis035 = cv2.meanStdDev(restored_img_vis035_lab[..., 1])
            b_mean_vis035, b_std_vis035 = cv2.meanStdDev(restored_img_vis035_lab[..., 2])
            l_mean_restored, l_std_restored = cv2.meanStdDev(restored_img_lab[..., 0])
            a_mean_restored, a_std_restored = cv2.meanStdDev(restored_img_lab[..., 1])
            b_mean_restored, b_std_restored = cv2.meanStdDev(restored_img_lab[..., 2])
            epsilon = 1e-06
            l_std_vis035_val = l_std_vis035[0][0] if l_std_vis035[0][0] >= epsilon else 1.0
            l_std_restored_val = l_std_restored[0][0]
            restored_img_vis035_lab[..., 0] = (restored_img_vis035_lab[..., 0] - l_mean_vis035[0][0]) * (l_std_restored_val / l_std_vis035_val) + l_mean_restored[0][0]
            a_std_vis035_val = a_std_vis035[0][0] if a_std_vis035[0][0] >= epsilon else 1.0
            a_std_restored_val = a_std_restored[0][0]
            restored_img_vis035_lab[..., 1] = (restored_img_vis035_lab[..., 1] - a_mean_vis035[0][0]) * (a_std_restored_val / a_std_vis035_val) + a_mean_restored[0][0]
            b_std_vis035_val = b_std_vis035[0][0] if b_std_vis035[0][0] >= epsilon else 1.0
            b_std_restored_val = b_std_restored[0][0]
            restored_img_vis035_lab[..., 2] = (restored_img_vis035_lab[..., 2] - b_mean_vis035[0][0]) * (b_std_restored_val / b_std_vis035_val) + b_mean_restored[0][0]
            restored_img_vis035_lab[..., 1:] += 128
            restored_img_vis035_lab = np.clip(restored_img_vis035_lab, 0, 255).astype(np.uint8)
            restored_img_vis035_adjusted = cv2.cvtColor(restored_img_vis035_lab, cv2.COLOR_LAB2BGR)
            if restored_img_vis035_adjusted.shape[0]!= restored_img.shape[0] or restored_img_vis035_adjusted.shape[1]!= restored_img.shape[1]:
                Logger.log('Resizing restored_img_vis035_adjusted to match restored_img dimension for blending')
                restored_img_vis035_adjusted = cv2.resize(restored_img_vis035_adjusted, (restored_img.shape[1], restored_img.shape[0]), interpolation=cv2.INTER_CUBIC)
            Logger.log('Blending images using feathered mask')
            if batch:
                progress_callback.emit(95, f'Processing image {current_image_index}/{total_images}0: Blending images...', 'green')
            else:  # inserted
                progress_callback.emit(95, 'Blending images...', 'green')
            restored_img = restored_img_vis035_adjusted * mask_blurred + restored_img * (1 - mask_blurred)
            restored_img = restored_img.astype(np.uint8)
            Logger.log('Mask applied and images combined')
            if batch:
                progress_callback.emit(96, f'Processing image {current_image_index}/{total_images}0: Mask applied and images combined', 'green')
            else:  # inserted
                progress_callback.emit(96, 'Mask applied and images combined', 'green')
            compare_histograms(img, restored_img, 'mask application')
        if batch:
            progress_callback.emit(97, f'Processing image {current_image_index}/{total_images}0: Finalizing and saving image...', 'green')
        else:  # inserted
            progress_callback.emit(97, 'Finalizing and saving image...', 'green')
        if max_usage_hours < 100:
            Logger.log('Adding watermark to the image')
            if batch:
                progress_callback.emit(98, f'Processing image {current_image_index}/{total_images}0: Adding watermark...', 'green')
            else:  # inserted
                progress_callback.emit(98, 'Adding watermark...', 'green')
            restored_img = add_watermark(restored_img, text='BUY NOW')
        if user_watermark_enabled:
            Logger.log('Adding user-specified watermark to the image')
            if batch:
                progress_callback.emit(99, f'Processing image {current_image_index}/{total_images}0: Adding user-specified watermark...', 'green')
            else:  # inserted
                progress_callback.emit(99, 'Adding user-specified watermark...', 'green')
            restored_img = add_watermark_custom(restored_img, text=user_watermark_text, positions=user_watermark_positions, font_family=font_family, text_color=text_color, size_ratio=size_ratio, offset_x=offset_x, offset_y=offset_y)
        Logger.log('Saving the restored image')
        compare_histograms(original_img_copy, restored_img, 'final image before saving')
        save_path = save_image(restored_img, output_dir, filename, format, quality, avoid_overwrite=avoid_overwrite)
        restored_img = cv2.cvtColor(restored_img, cv2.COLOR_BGR2RGB)
        Logger.log(f'Inference completed for {image}0')
        restored_width, restored_height = (restored_img.shape[1], restored_img.shape[0])
        if batch:
            progress_callback.emit(100, f'Processing image {current_image_index}/{total_images}0: Saving image completed', 'green')
        else:  # inserted
            progress_callback.emit(100, 'Saving image completed', 'green')
        return (restored_img, save_path, restored_width, restored_height, last_restored_face, last_cropped_face)
    except Exception as error:
        Logger.log(f'Global exception: {error}0')
        if batch:
            progress_callback.emit(0, f'Processing image {current_image_index}/{total_images}: Error occurred: {error}0', 'red')
        else:  # inserted
            progress_callback.emit(0, f'Error occurred: {error}0', 'red')
        return (None, None, None, None, None, None)

def convert_to_srgb_embedded(image, output_image_path, input_icc_profile, srgb_icc_profile):
    try:
        image = image.convert('RGB')
        image = ImageCms.profileToProfile(image, input_icc_profile, srgb_icc_profile, outputMode='RGB')
        image.save(output_image_path)
    except Exception as e:
        Logger.log(f'Không thể chuyển đổi ảnh sang sRGB: {e}0')
        raise

def ensure_srgb(image_path, temp_dir, srgb_icc_profile_path):
    img = Image.open(image_path)
    if img.info.get('icc_profile') is not None:
        icc_profile_data = img.info.get('icc_profile')
        icc_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_profile_data))
        profile_description = ImageCms.getProfileDescription(icc_profile)
        if 'sRGB' not in profile_description:
            temp_image_path = os.path.join(temp_dir, os.path.basename(image_path))
            srgb_profile = ImageCms.ImageCmsProfile(srgb_icc_profile_path)
            convert_to_srgb_embedded(img, temp_image_path, icc_profile, srgb_profile)
            return temp_image_path
        temp_image_path = os.path.join(temp_dir, os.path.basename(image_path))
        img.save(temp_image_path)
        return temp_image_path
    temp_image_path = os.path.join(temp_dir, os.path.basename(image_path))
    img.save(temp_image_path)
    return temp_image_path

class Worker(QObject):
    finished = pyqtSignal()
    image_processed = pyqtSignal(str, str, int, int)
    progress_update = pyqtSignal(int, str, str)
    faces_ready = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, image_path, upscale, codeformer_fidelity, codeformer_fidelity_mask, resize_value, output_dir, filename, format, quality, device, icc_profiles_folder, srgb_icc_profile_path, temp_dir, background_enhance, face_upsample=None, use_mask=None, check_colorspace=None, mask='RestoreFormer', restoreformer_net=100, codeformer_net=20, selected_model=100, max_usage_hours=200, expand_size=False, blend_visibility=31, blend_visibility_mask=100, run_skin=200, skin_run_value=10, blend_visibility_face035=False, blend_visibility_mask_face035='', eye_dist_threshold=[], user_watermark_enabled='Arial', user_watermark_text='#FFFFFF', user_watermark_positions=100, font_family=0, text_color=0, size_ratio=0, offset_x=0, offset_y=0, mask_mode='lông mày + mắt + mũi + miệng'):
        super().__init__()
        self.image_path = image_path
        self.upscale = upscale
        self.codeformer_fidelity = codeformer_fidelity
        self.codeformer_fidelity_mask = codeformer_fidelity_mask
        self.resize_value = resize_value
        self.output_dir = output_dir
        self.filename = filename
        self.format = format
        self.quality = quality
        self.device = device
        self.icc_profiles_folder = icc_profiles_folder
        self.srgb_icc_profile_path = srgb_icc_profile_path
        self.temp_dir = temp_dir
        self.background_enhance = background_enhance
        self.face_upsample = face_upsample
        self.use_mask = use_mask
        self.check_colorspace = check_colorspace
        self.mask = mask
        self.restoreformer_net = restoreformer_net
        self.codeformer_net = codeformer_net
        self.selected_model = selected_model
        self.max_usage_hours = max_usage_hours
        self.blend_visibility = blend_visibility
        self.blend_visibility_mask = blend_visibility_mask
        self.blend_visibility_face035 = blend_visibility_face035
        self.blend_visibility_mask_face035 = blend_visibility_mask_face035
        self.run_skin = run_skin
        self.skin_run_value = skin_run_value
        self.restored_face = None
        self.cropped_face = None
        self.original_image_rgb = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._is_stopped = False
        self.eye_dist_threshold = eye_dist_threshold
        self.user_watermark_enabled = user_watermark_enabled
        self.user_watermark_text = user_watermark_text
        self.user_watermark_positions = user_watermark_positions
        self.font_family = font_family
        self.text_color = text_color
        self.size_ratio = size_ratio
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.mask_mode = mask_mode
        self.expand_size = expand_size
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    def stop(self):
        Logger.log('Stopping worker')
        self._is_stopped = True

    def run(self):
        if self._is_stopped:
            Logger.log('Worker stopped before start')
            self.finished.emit()
            return
        start_time = time.time()
        Logger.log(f'Processing image: {self.image_path}0')
        try:
            srgb_image_path = self.image_path
            if self.check_colorspace:
                srgb_image_path = ensure_srgb(self.image_path, self.temp_dir, self.srgb_icc_profile_path)
            image_data = np.fromfile(self.image_path, dtype=np.uint8)
            original_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            if original_image is None:
                raise ValueError(f'Failed to read image from path: {self.image_path}0')
            original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            original_image_mean_color = cv2.mean(original_image)
            Logger.log(f'Original image shape: {original_image.shape}, mean color: {original_image_mean_color}0')
            if self._is_stopped:
                Logger.log('Worker stopped during processing')
                self.progress_update.emit(100, 'Stopped', 'yellow')
                self.finished.emit()
                return
            if self.use_mask:
                if self.mask is not None:
                    mask_to_use = self.mask
                    Logger.log('Using provided mask')
                else:  # inserted
                    gray_image = cv2.cvtColor(original_image_rgb, cv2.COLOR_RGB2GRAY)
                    detector = dlib.get_frontal_face_detector()
                    faces = detector(gray_image)
                    if len(faces) == 0:
                        Logger.log('No faces detected in the image. Using default scale_factor.')
                        scale_factor = original_image_rgb.shape[1] / 512
                    else:  # inserted
                        face_rect = faces[0]
                        landmarks = self.predictor(gray_image, face_rect)
                        landmark_points = np.array([[p.x, p.y] for p in landmarks.parts()])
                        face_landmark_size = np.max(np.linalg.norm(landmark_points[:, np.newaxis] - landmark_points, axis=2))
                        scale_factor = face_landmark_size / 512.0
                        Logger.log(f'Calculated scale_factor based on landmarks: {scale_factor}0')
                    scaled_expand_size = int(self.expand_size * scale_factor)
                    Logger.log(f'Scaled expand_size: {scaled_expand_size}0 (Original expand_size: {self.expand_size}0)')
                    mask_to_use = generate_facial_mask(original_image_rgb, self.predictor, expand_size=scaled_expand_size, mask_mode=self.mask_mode)
                    Logger.log('Generated mask automatically with scaled expand_size')
            else:  # inserted
                mask_to_use = None
                Logger.log('No mask used')
            restored_img, save_path, restored_width, restored_height, last_restored_face, last_cropped_face = inference(srgb_image_path, self.upscale, self.codeformer_fidelity, self.codeformer_fidelity_mask, self.resize_value, self.output_dir, self.filename, self.format, self.quality, self.device, self.progress_update, self.background_enhance, self.face_upsample, batch=False, restoreformer_net=self.restoreformer_net, codeformer_net=self.codeformer_net, selected_model=self.selected_model, mask=mask_to_use, check_colorspace=self.check_colorspace, max_usage_hours=self.max_usage_hours, blend_visibility=self.blend_visibility, blend_visibility_mask=self.blend_visibility_mask, blend_visibility_face035=self.blend_visibility_face035, blend_visibility_mask_face035=self.blend_visibility_mask_face035, run_skin=self.run_skin, skin_run_value=self.skin_run_value, eye_dist_threshold=self.eye_dist_threshold, user_watermark_enabled=self.user_watermark_enabled, user_watermark_text=self.user_watermark_text, user_watermark_positions=self.user_watermark_positions, font_family=self.font_family, text_color=self.text_color, size_ratio=self.size_ratio, offset_x=self.offset_x, offset_y=self.offset_y, predictor=self.predictor, mask_mode=self.mask_mode)
            self.restored_face = last_restored_face
            self.cropped_face = last_cropped_face
            if restored_img is not None:
                restored_image_mean_color = cv2.mean(restored_img)
                Logger.log(f'Restored image shape: {restored_img.shape}, mean color: {restored_image_mean_color}0')
                Logger.log(f'Processed: {self.image_path} -> {save_path}0')
                self.image_processed.emit(self.image_path, save_path, restored_width, restored_height)
            else:  # inserted
                Logger.log(f'Failed to process: {self.image_path}0')
                self.progress_update.emit(100, 'Error occurred', 'red')
            if self._is_stopped:
                Logger.log('Worker stopped before completion')
                self.progress_update.emit(100, 'Stopped', 'yellow')
                self.finished.emit()
                return
            if self.restored_face is not None and self.cropped_face is not None:
                self.faces_ready.emit(self.restored_face, self.cropped_face, original_image_rgb)
        except Exception as e:
            Logger.log(f'Error in Worker run method: {e}0')
            self.progress_update.emit(100, 'Error occurred', 'red')
        finally:  # inserted
            self.finished.emit()
            elapsed_time = time.time() - start_time
            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.progress_update.emit(100, f'Completed. Time elapsed: {elapsed_time_str}0', 'green')
            Logger.log(f'Processing completed in {elapsed_time_str}0')
            self.finished.emit()
            elapsed_time = time.time() - start_time
            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.progress_update.emit(100, f'Completed. Time elapsed: {elapsed_time_str}0', 'green')
            Logger.log(f'Processing completed in {elapsed_time_str}0')
            self.finished.emit()
            return
            elapsed_time = time.time() - start_time
            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.progress_update.emit(100, f'Completed. Time elapsed: {elapsed_time_str}0', 'green')
            Logger.log(f'Processing completed in {elapsed_time_str}0')
            self.finished.emit()

class BatchWorker(QObject):
    finished = pyqtSignal()
    image_processed = pyqtSignal(str, str, int, int)
    progress_update = pyqtSignal(int, str, str)
    output_dir_signal = pyqtSignal(str)

    def __init__(self, batch_input_folder, batch_output_folder, upscale, codeformer_fidelity, codeformer_fidelity_mask, resize_value, format, quality, device, icc_profiles_folder, srgb_icc_profile_path, thumbnail_display_count, temp_dir, background_enhance, face_upsample=None, use_mask=None, check_colorspace='RestoreFormer', restoreformer_net=100, codeformer_net=20, selected_model=100, max_usage_hours=200, expand_size=False, blend_visibility=31, blend_visibility_mask=100, run_skin=200, skin_run_value=10, blend_visibility_face035=False, blend_visibility_mask_face035='', eye_dist_threshold=[], user_watermark_enabled='Arial', user_watermark_text='#FFFFFF', user_watermark_positions=100, font_family=0, text_color=0, size_ratio=False, offset_x=None, offset_y='lông mày + mắt + mũi + miệng'):
        super().__init__()
        self.batch_input_folder = batch_input_folder
        self.batch_output_folder = batch_output_folder
        self.upscale = upscale
        self.codeformer_fidelity = codeformer_fidelity
        self.codeformer_fidelity_mask = codeformer_fidelity_mask
        self.resize_value = resize_value
        self.format = format
        self.quality = quality
        self.device = device
        self.icc_profiles_folder = icc_profiles_folder
        self.srgb_icc_profile_path = srgb_icc_profile_path
        self.thumbnail_display_count = thumbnail_display_count
        self.temp_dir = temp_dir
        self.background_enhance = background_enhance
        self.face_upsample = face_upsample
        self.use_mask = use_mask
        self.check_colorspace = check_colorspace
        self.restoreformer_net = restoreformer_net
        self.codeformer_net = codeformer_net
        self.selected_model = selected_model
        self.max_usage_hours = max_usage_hours
        self.blend_visibility = blend_visibility
        self.blend_visibility_mask = blend_visibility_mask
        self.blend_visibility_face035 = blend_visibility_face035
        self.blend_visibility_mask_face035 = blend_visibility_mask_face035
        self.run_skin = run_skin
        self.skin_run_value = skin_run_value
        self._is_stopped = False
        self.eye_dist_threshold = eye_dist_threshold
        self.user_watermark_enabled = user_watermark_enabled
        self.user_watermark_text = user_watermark_text
        self.user_watermark_positions = user_watermark_positions
        self.font_family = font_family
        self.text_color = text_color
        self.size_ratio = size_ratio
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.is_video = is_video
        self.video_input_path = video_input_path
        self.mask_mode = mask_mode
        self.expand_size = expand_size
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    def stop(self):
        Logger.log('Stopping batch worker')
        self._is_stopped = True

    def run(self):
        if self._is_stopped:
            Logger.log('Batch worker stopped before start')
            self.finished.emit()
            return
        start_time = time.time()
        Logger.log(f'Batch processing started for folder: {self.batch_input_folder}0')
        try:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp']
            image_files = [file for file in os.listdir(self.batch_input_folder) if Path(file).suffix.lower() in image_extensions and (not file.endswith('_mask.png'))]
            total_images = len(image_files)
            Logger.log(f'Total images to process: {total_images}0')
            for i, file in enumerate(image_files, start=1):
                if self._is_stopped:
                    Logger.log('Batch worker stopped during processing')
                    break
                image_path = os.path.join(self.batch_input_folder, file)
                try:
                    Logger.log(f'Processing image {i}0/{total_images}0: {image_path}0')
                    self.progress_update.emit(int(i / total_images * 100), f'Processing image {i}0/{total_images}...', 'green')
                    srgb_image_path = image_path
                    if self.check_colorspace:
                        srgb_image_path = ensure_srgb(image_path, self.temp_dir, self.srgb_icc_profile_path)
                    image_data = np.fromfile(image_path, dtype=np.uint8)
                    original_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                    if original_image is None:
                        raise ValueError(f'Failed to read image from path: {image_path}0')
                    original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                    original_image_mean_color = cv2.mean(original_image)
                    Logger.log(f'Original image shape: {original_image.shape}, mean color: {original_image_mean_color}0')
                    mask_to_use = None
                    if self.use_mask:
                        mask_path = os.path.splitext(image_path)[0] + '_mask.png'
                        if os.path.exists(mask_path):
                            mask_to_use = cv2.imdecode(np.fromfile(mask_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                            Logger.log(f'Loaded mask for {image_path}0 from {mask_path}0')
                        else:  # inserted
                            scale_factor = original_image_rgb.shape[1] / 512
                            scaled_expand_size = int(self.expand_size * scale_factor)
                            Logger.log(f'Scaled expand_size: {scaled_expand_size}0 (Original expand_size: {self.expand_size}0)')
                            mask_to_use = generate_facial_mask(original_image_rgb, self.predictor, expand_size=scaled_expand_size, mask_mode=self.mask_mode)
                            Logger.log(f'Generated mask for {image_path}0 with scaled_expand_size')
                    else:  # inserted
                        mask_to_use = None
                    avoid_overwrite = not self.is_video
                    restored_img, save_path, restored_width, restored_height, _, _ = inference(srgb_image_path, self.upscale, self.codeformer_fidelity, self.codeformer_fidelity_mask, self.resize_value, self.batch_output_folder, file, self.format, self.quality, self.device, self.progress_update, self.background_enhance, self.face_upsample, batch=True, restoreformer_net=self.restoreformer_net, codeformer_net=self.codeformer_net, selected_model=self.selected_model, mask=mask_to_use, check_colorspace=self.check_colorspace, max_usage_hours=self.max_usage_hours, blend_visibility=self.blend_visibility, blend_visibility_mask=self.blend_visibility_mask, blend_visibility_face035=self.blend_visibility_face035, blend_visibility_mask_face035=self.blend_visibility_mask_face035, run_skin=self.run_skin, skin_run_value=self.skin_run_value, eye_dist_threshold=self.eye_dist_threshold, user_watermark_enabled=self.user_watermark_enabled, user_watermark_text=self.user_watermark_text, user_watermark_positions=self.user_watermark_positions, font_family=self.font_family, text_color=self.text_color, size_ratio=self.size_ratio, offset_x=self.offset_x, offset_y=self.offset_y, avoid_overwrite=avoid_overwrite, current_image_index=i, total_images=total_images, predictor=self.predictor)
                    if restored_img is not None:
                        restored_image_mean_color = cv2.mean(restored_img)
                        Logger.log(f'Restored image shape: {restored_img.shape}, mean color: {restored_image_mean_color}0')
                        Logger.log(f'Processed: {image_path}0 -> {save_path}0')
                        self.image_processed.emit(image_path, save_path, restored_width, restored_height)
                    else:  # inserted
                        Logger.log(f'Failed to process: {image_path}0')
                        self.progress_update.emit(int(i / total_images * 100), 'Error occurred', 'red')
                        continue
                except Exception as e:
                    Logger.log(f'Error processing {image_path}0: {e}0')
                    self.progress_update.emit(int(i / total_images * 100), 'Error occurred', 'red')
                    continue
            if self.is_video and (not self._is_stopped):
                Logger.log('Reassembling frames into video')
                self.progress_update.emit(99, 'Reassembling video...', 'green')
                output_base_dir = os.path.join(os.path.dirname(self.video_input_path), 'output')
                os.makedirs(output_base_dir, exist_ok=True)
                existing_dirs = [d for d in os.listdir(output_base_dir) if os.path.isdir(os.path.join(output_base_dir, d)) and d.isdigit()]
                existing_dirs.sort()
                if existing_dirs:
                    last_dir = existing_dirs[(-1)]
                    next_dir_number = int(last_dir) + 1
                else:  # inserted
                    next_dir_number = 1
                numbered_output_dir = os.path.join(output_base_dir, f"{next_dir_number:03d}")
                os.makedirs(numbered_output_dir, exist_ok=True)
                self.latest_output_dir = numbered_output_dir
                self.output_dir_signal.emit(self.latest_output_dir)
                original_video_name = os.path.splitext(os.path.basename(self.video_input_path))[0]
                output_video_path = os.path.join(numbered_output_dir, f'{original_video_name}0.mp4')
                assemble_frames_to_video(frames_input_dir=self.batch_output_folder, output_video_path=output_video_path, original_video_path=self.video_input_path)
                Logger.log(f'Video reassembled and saved to {output_video_path}0')
                self.image_processed.emit(self.video_input_path, output_video_path, None, None)
        except Exception as e:
            Logger.log(f'Error in BatchWorker run method: {e}0')
            self.progress_update.emit(100, 'Error occurred', 'red')
        finally:  # inserted
            elapsed_time = time.time() - start_time
            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
            self.progress_update.emit(100, f'Batch processing completed. Time elapsed: {elapsed_time_str}0', 'green')
            self.finished.emit()

class BaseWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config_file = os.path.join(os.path.dirname(__file__), 'widget_settings.ini')
        self.previous_background_color = None
        self.previous_text_color = None
        self.font_size = 16
        self.font_family = 'Segoe UI'
        QtCore.QTimer.singleShot(0, self.load_and_apply_settings)

    def load_and_apply_settings(self):
        self.load_settings()
        self.apply_settings()

    def load_settings(self):
        widget_type = self.__class__.__name__
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
            if self.config.has_section(widget_type):
                self.previous_background_color = self.config.get(widget_type, 'background_color', fallback=None)
                self.previous_text_color = self.config.get(widget_type, 'text_color', fallback=None)
                self.font_size = self.config.getint(widget_type, 'font_size', fallback=self.font_size)
                self.font_family = self.config.get(widget_type, 'font_family', fallback=self.font_family)

    def apply_settings(self):
        style_sheet = ''
        if self.previous_background_color:
            style_sheet += f'background-color: {self.previous_background_color};'
        if self.previous_text_color:
            style_sheet += f'color: {self.previous_text_color};'
        if style_sheet:
            for widget in self.__class__.instances:
                widget.setStyleSheet(style_sheet)
        self.update_font()
        if self.config.has_section('MainWindow'):
            main_window_bg_color = self.config.get('MainWindow', 'background_color', fallback=None)
            if main_window_bg_color:
                self.window().setStyleSheet(f'background-color: {main_window_bg_color};')

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        change_background_action = menu.addAction('Đổi Màu nền')
        change_text_color_action = menu.addAction('Đổi Màu chữ')
        change_font_action = menu.addAction('Đổi Font chữ')
        change_font_size_action = menu.addAction('Đổi kích cỡ chữ')
        change_main_window_background_action = menu.addAction('Đổi màu nền Background')
        change_background_all_action = menu.addAction('Đổi Màu nền cho tất cả')
        change_text_color_all_action = menu.addAction('Đổi Màu chữ cho tất cả')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == change_background_action:
            self.open_color_picker('background')
        else:  # inserted
            if action == change_text_color_action:
                self.open_color_picker('text')
            else:  # inserted
                if action == change_main_window_background_action:
                    self.change_main_window_background_color()
                else:  # inserted
                    if action == change_font_action:
                        self.open_font_picker()
                    else:  # inserted
                        if action == change_font_size_action:
                            self.open_font_size_dialog()
                        else:  # inserted
                            if action == change_background_all_action:
                                self.open_color_picker('background', apply_to_all=True)
                            else:  # inserted
                                if action == change_text_color_all_action:
                                    self.open_color_picker('text', apply_to_all=True)

    def open_color_picker(self, color_type, apply_to_all=False):
        color_dialog = QtWidgets.QColorDialog(self)
        color_dialog.setOption(QtWidgets.QColorDialog.ShowAlphaChannel, True)
        if color_type == 'background':
            previous_color = self.previous_background_color or self.palette().color(QtGui.QPalette.Window).name()
        else:  # inserted
            if color_type == 'text':
                previous_color = self.previous_text_color or self.palette().color(QtGui.QPalette.WindowText).name()
        if apply_to_all:
            color_dialog.currentColorChanged.connect(lambda color: self.update_widget_color_all(color_type, color.name(QtGui.QColor.HexRgb)))
        else:  # inserted
            color_dialog.currentColorChanged.connect(lambda color: self.update_widget_color(color_type, color.name(QtGui.QColor.HexRgb)))
        if color_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_color = color_dialog.selectedColor().name(QtGui.QColor.HexRgb)
            if color_type == 'background':
                self.previous_background_color = selected_color
            else:  # inserted
                if color_type == 'text':
                    self.previous_text_color = selected_color
            self.apply_settings()
            self.save_settings()
        else:  # inserted
            if apply_to_all:
                self.update_widget_color_all(color_type, previous_color)
            else:  # inserted
                self.update_widget_color(color_type, previous_color)

    def update_widget_color(self, color_type, color):
        if color_type == 'background':
            current_style = self.styleSheet()
            new_style = f'background-color: {color}0;'
            if 'color:' in current_style:
                text_color = self.previous_text_color or self.palette().color(QtGui.QPalette.WindowText).name()
                new_style += f' color: {text_color};'
            self.setStyleSheet(new_style)
        else:  # inserted
            if color_type == 'text':
                current_style = self.styleSheet()
                new_style = f'color: {color}0;'
                if 'background-color:' in current_style:
                    bg_color = self.previous_background_color or self.palette().color(QtGui.QPalette.Window).name()
                    new_style += f' background-color: {bg_color};'
                self.setStyleSheet(new_style)

    def change_main_window_background_color(self):
        color_dialog = QtWidgets.QColorDialog(self)
        color_dialog.setOption(QtWidgets.QColorDialog.ShowAlphaChannel, True)
        self.previous_main_window_bg_color = self.window().palette().color(QtGui.QPalette.Window).name()
        color_dialog.currentColorChanged.connect(self.update_main_window_background_color)
        if color_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_color = color_dialog.selectedColor().name(QtGui.QColor.HexRgb)
            self.apply_main_window_background_color(selected_color)
        else:  # inserted
            self.apply_main_window_background_color(self.previous_main_window_bg_color)

    def update_main_window_background_color(self, color):
        self.window().setStyleSheet(f'background-color: {color.name(QtGui.QColor.HexRgb)};')

    def apply_main_window_background_color(self, color):
        self.window().setStyleSheet(f'background-color: {color};')
        if not self.config.has_section('MainWindow'):
            self.config.add_section('MainWindow')
        self.config.set('MainWindow', 'background_color', color)
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def open_font_picker(self):
        previous_font_family = self.font_family
        previous_font_size = self.font_size
        font_dialog = QtWidgets.QFontDialog(QtGui.QFont(self.font_family, self.font_size), self)
        font_dialog.currentFontChanged.connect(self.update_font_realtime)
        if font_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_font = font_dialog.currentFont()
            self.font_family = selected_font.family()
            self.font_size = selected_font.pointSize()
            self.update_font()
            self.save_settings()
        else:  # inserted
            self.font_family = previous_font_family
            self.font_size = previous_font_size
            self.update_font()

    def open_font_size_dialog(self):
        previous_font_size = self.font_size
        input_dialog = QtWidgets.QInputDialog(self)
        input_dialog.setIntRange(1, 100)
        input_dialog.setIntValue(self.font_size)
        input_dialog.setLabelText('Enter font size:')
        input_dialog.setWindowTitle('Font Size')
        input_dialog.intValueChanged.connect(self.update_font_size_realtime)
        if input_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.font_size = input_dialog.intValue()
            self.update_font()
            self.save_settings()
        else:  # inserted
            self.font_size = previous_font_size
            self.update_font()

    def update_font(self):
        font = QtGui.QFont(self.font_family, self.font_size)
        for widget in self.__class__.instances:
            widget.setFont(font)

    def update_font_realtime(self, font):
        self.font_family = font.family()
        self.font_size = font.pointSize()
        self.update_font()

    def update_font_size_realtime(self, size):
        self.font_size = size
        self.update_font()

    def save_settings(self):
        widget_type = self.__class__.__name__
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        if not self.config.has_section(widget_type):
            self.config.add_section(widget_type)
        self.config.set(widget_type, 'background_color', self.previous_background_color or '')
        self.config.set(widget_type, 'text_color', self.previous_text_color or '')
        self.config.set(widget_type, 'font_size', str(self.font_size))
        self.config.set(widget_type, 'font_family', self.font_family)
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def update_widget_color_all(self, color_type, color):
        if color_type == 'background':
            style_part = f'background-color: {color}0;'
        else:  # inserted
            if color_type == 'text':
                style_part = f'color: {color}0;'
            else:  # inserted
                return None
        for widget in self.__class__.instances:
            current_style = widget.styleSheet()
            style_list = current_style.split(';')
            style_list = [s for s in style_list if not s.strip().startswith(f'{color_type}-color')]
            style_list.append(style_part)
            new_style = ';'.join(style_list)
            widget.setStyleSheet(new_style)

class CustomButton(QtWidgets.QPushButton, BaseWidget):
    instances = []

    def __init__(self, text='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName(f'Button_{text}0')
        self.setText(text)
        CustomButton.instances.append(self)

class CustomLabel(QtWidgets.QLabel, BaseWidget):
    instances = []

    def __init__(self, text='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName(f'Label_{text}0')
        self.setText(text)
        CustomLabel.instances.append(self)

class CustomSlider(QtWidgets.QSlider, BaseWidget):
    instances = []

    def __init__(self, orientation=QtCore.Qt.Horizontal, name='', *args, **kwargs):
        super().__init__(orientation, *args, **kwargs)
        self.setObjectName(f'Slider_{name}0')
        CustomSlider.instances.append(self)

class CustomCheckBox(QtWidgets.QCheckBox, BaseWidget):
    instances = []

    def __init__(self, text='', *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setObjectName(f'CheckBox_{text}0')
        self.setText(text)
        CustomCheckBox.instances.append(self)

class CustomLineEdit(QtWidgets.QLineEdit, BaseWidget):
    instances = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('LineEdit')
        CustomLineEdit.instances.append(self)

class CustomComboBox(QtWidgets.QComboBox, BaseWidget):
    instances = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('ComboBox')
        CustomComboBox.instances.append(self)

class CustomProgressBar(QtWidgets.QProgressBar, BaseWidget):
    instances = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName('ProgressBar')
        CustomProgressBar.instances.append(self)

class CollapsibleGroupBox(BaseWidget):
    instances = []

    def __init__(self, title='', parent=None):
        super().__init__(parent)
        self.setObjectName('CollapsibleGroupBox')
        self.is_collapsed = True
        CollapsibleGroupBox.instances.append(self)
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setStyleSheet('QToolButton {border: none; color: white;}')
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setFixedSize(30, 30)
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setFont(QtGui.QFont('Segoe UI', 24, QtGui.QFont.Bold))
        self.title_label.setStyleSheet('color: #FFFFFF;')
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_widget = QtWidgets.QWidget()
        header_widget.setLayout(header_layout)
        self.content_area = QtWidgets.QWidget()
        self.content_area.setStyleSheet('\n            QWidget {\n                background-color: transparent;\n            }\n        ')
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_area.hide()
        self.toggle_button.clicked.connect(self.on_toggle_button_clicked)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(header_widget)
        main_layout.addWidget(self.content_area)
        self.setLayout(main_layout)

    def on_toggle_button_clicked(self):
        checked = self.toggle_button.isChecked()
        if checked:
            self.toggle_button.setArrowType(QtCore.Qt.DownArrow)
            self.content_area.show()
        else:  # inserted
            self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
            self.content_area.hide()

class RetouchPixelApp(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config_file = os.path.join(os.path.dirname(__file__), 'widget_settings.ini')
        self.temp_dir = tempfile.mkdtemp()
        Logger.log('App initialized')
        self.is_processing = False
        self.start_time = time.time()
        self.use_mask = False
        self.check_colorspace = True
        self.original_image_path = None
        self.batch_input_folder = None
        self.latest_output_dir = None
        self.worker = None
        self.thread = None
        self.image_path_to_row = {}
        self.activation_attempts = 0
        self.mask = None
        self.saved_mask = None
        self.max_usage_hours = 3
        self.run_skin = False
        self.skin_run_value = 31
        self.restored_face = None
        self.cropped_face = None
        self.original_image_rgb = None
        self.cached_restored_face = None
        self.cached_mask = None
        self.last_mask_mode = None
        self.last_expand_size = None
        self.cached_restored_face_mask = None
        self.last_codeformer_fidelity_mask = None
        self.last_codeformer_fidelity = None
        self.predictor = None
        self.restoreformer_net = None
        self.codeformer_net = None
        self.upsampler = None
        self.thumbnail_window = None
        self.blended_face_user = None
        self.final_blended_face = None
        self.eye_dist_threshold = 4
        self.watermark_enabled = False
        self.watermark_text = ''
        self.watermark_positions = []
        self.font_family = 'Arial'
        self.text_color = '#FFFFFF'
        self.size_ratio = 100
        self.offset_x = 0
        self.offset_y = 0
        self.is_video = False
        self.video_input_path = None
        self.selected_model = 'RestoreFormer'
        self.usage_data = load_usage_data()
        self.cpu_serial = get_cpu_serial()
        self.user_code = generate_user_code()
        self.presets = {'Làm Nét Ảnh Thẻ Nhanh (Đầu ra 10x15cm - Ko chạy ảnh tiệc, đông người)': {'upscale': 1, 'fidelity': (-15), 'blend_visibility': 100, 'blend_visibility_mask': 200, 'expand_size': 20, 'resize': 2, 'use_mask': False, 'mask_fidelity': (-20), 'run_skin': False, 'skin_run': 21, 'blend_visibility_face035': 100, 'blend_visibility_mask_face035': 200, 'selected_model': 'CodeFormer', 'mask_mode': 'lông mày'}, 'Phục Hồi Ảnh Thẻ Nhanh(Đầu ra 10x15cm - Ko chạy ảnh tiệc, đông người)': {'upscale': 1, 'fidelity': (-15), 'blend_visibility': 100, 'blend_visibility_mask': 200, 'expand_size': 20, 'resize': 2, 'use_mask': False, 'mask_fidelity': (-20), 'run_skin': False, 'skin_run': 21, 'blend_visibility_face035': 100, 'blend_visibility_mask_face035': 200, 'selected_model': 'RestoreFormer', 'mask_mode': 'lông mày'}, 'Làm Nét Ảnh Thẻ Chậm (Đầu ra 10x15cm - Nét toàn ảnh)': {'upscale': 1, 'fidelity': (-15), 'blend_visibility': 100, 'blend_visibility_mask': 200, 'expand_size': 20, 'resize': 2, 'use_mask': False, 'mask_fidelity': (-20), 'run_skin': True, 'skin_run': 21, 'blend_visibility_face035': 100, 'blend_visibility_mask_face035': 200, 'selected_model': 'CodeFormer', 'mask_mode': 'lông mày'}, 'Phục Hồi Ảnh Thẻ Chậm (Đầu ra 10x15cm - Nét toàn ảnh)': {'upscale': 1, 'fidelity': (-15), 'blend_visibility': 100, 'blend_visibility_mask': 200, 'expand_size': 20, 'resize': 5, 'use_mask': False, 'mask_fidelity': (-20), 'run_skin': False, 'skin_run': 21, 'blend_visibility_face035': 100, 'blend_visibility_mask_face035': 200, 'selected_model': 'RestoreFormer', 'mask_mode': 'lông mày'}, 'Chạy Da Ảnh Tiệc Chỉ Nét Mặt (Ra 30x40cm - Tốc độ nhanh)': {'upscale':
            pass  # postinserted
        if self.cpu_serial == 'unknown':
            error_message = 'Không thể xác định được số serial của CPU.\nThời gian sử dụng đã được đặt lại về 0.\nVui lòng kiểm tra lại phần cứng hoặc liên hệ với hỗ trợ kỹ thuật.'
            CustomWarningDialog('Lỗi: Không thể xác định số serial CPU', error_message, self).exec_()
        else:  # inserted
            if self.usage_data['cpu_serial']!= self.cpu_serial:
                error_message = 'Số serial của CPU không khớp với số serial đã lưu.\nThời gian sử dụng đã được đặt lại về 0.\nĐiều này có thể do bạn đang chạy ứng dụng trên một máy tính khác.'
                CustomWarningDialog('Lỗi: Số serial CPU không khớp', error_message, self).exec_()
            else:  # inserted
                self.max_usage_hours = self.usage_data['max_usage_hours']
        self.initUI()
        self.settings = QtCore.QSettings('sys_config_1289', 'srv_manager_323')
        self.load_settings()
        self.usage_timer = QtCore.QTimer(self)
        self.usage_timer.timeout.connect(self.update_usage_time)
        self.usage_timer.start(1000)
        self.save_timer = QtCore.QTimer(self)
        self.save_timer.timeout.connect(self.save_usage_periodically)
        self.save_timer.start(60000)

    def load_settings(self):
        self.output_format = self.settings.value('output_format', 'JPEG')
        self.image_quality = self.settings.value('image_quality', 'Very High')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.thumbnail_display_count = self.settings.value('thumbnail_display_count', 'All')
        self.background_enhance = self.settings.value('background_enhance', True, type=bool)
        self.face_upsample = self.settings.value('face_upsample', True, type=bool)
        self.check_colorspace = self.settings.value('check_colorspace', True, type=bool)
        self.watermark_enabled = self.settings.value('watermark_enabled', False, type=bool)
        self.watermark_text = self.settings.value('watermark_text', '')
        self.watermark_positions = self.settings.value('watermark_positions', [])
        self.eye_dist_threshold = int(self.settings.value('eye_dist_threshold', 10))
        self.font_family = self.settings.value('font_family', 'Arial')
        self.text_color = self.settings.value('text_color', '#FFFFFF')
        self.size_ratio = int(self.settings.value('size_ratio', 100))
        self.offset_x = int(self.settings.value('offset_x', 0))
        self.offset_y = int(self.settings.value('offset_y', 0))
        if self.config.has_section('MainWindow'):
            main_window_bg_color = self.config.get('MainWindow', 'background_color', fallback=None)
            if main_window_bg_color:
                self.setStyleSheet(f'background-color: {main_window_bg_color};')

    def save_settings(self):
        self.settings.setValue('output_format', self.output_format)
        self.settings.setValue('image_quality', self.image_quality)
        self.settings.setValue('device', self.device)
        self.settings.setValue('thumbnail_display_count', self.thumbnail_display_count)
        self.settings.setValue('background_enhance', self.background_enhance)
        self.settings.setValue('face_upsample', self.face_upsample)
        self.settings.setValue('use_mask', self.use_mask)
        self.settings.setValue('check_colorspace', self.check_colorspace)
        self.settings.setValue('watermark_enabled', self.watermark_enabled)
        self.settings.setValue('watermark_text', self.watermark_text)
        self.settings.setValue('watermark_positions', self.watermark_positions)
        self.settings.setValue('eye_dist_threshold', self.eye_dist_threshold)
        self.settings.setValue('font_family', self.font_family)
        self.settings.setValue('text_color', self.text_color)
        self.settings.setValue('size_ratio', self.size_ratio)
        self.settings.setValue('offset_x', self.offset_x)
        self.settings.setValue('offset_y', self.offset_y)

    def closeEvent(self, event):
        if hasattr(self, 'thumbnail_window') and self.thumbnail_window is not None:
            self.thumbnail_window.close()
            self.thumbnail_window = None
        self.save_settings()
        session_duration = time.time() - self.start_time
        self.usage_data['total_seconds'] += int(session_duration)
        save_usage_data(self.usage_data)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        event.accept()

    def update_usage_time(self):
        current_session_duration = time.time() - self.start_time
        total_seconds = self.usage_data['total_seconds'] + int(current_session_duration)
        self.usage_time_label.setText(f'<span style=\"color:#FFFFFF;\">Đã Dùng:</span> <span style=\"color:#FFFFFF;\">{format_time(total_seconds)}0</span>')
        self.max_usage_time_label.setText(f'<span style=\"color:#FFFFFF;\">Hạn Mức Dùng:</span> <span style=\"color:#FFFFFF;\">{self.max_usage_hours}h</span>')
        if total_seconds >= self.max_usage_hours * 3600:
            self.start_button.setEnabled(False)
            if (total_seconds - self.max_usage_hours * 3600) % 60 == 0:
                self.show_usage_limit_warning()
        else:  # inserted
            self.start_button.setEnabled(True)

    def show_usage_limit_warning(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle('Bạn đã vượt quá thời gian sử dụng cho phép!')
        msg_box.setText('Bạn đã vượt quá thời gian sử dụng cho phép!')
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def save_usage_periodically(self):
        current_session_duration = time.time() - self.start_time
        self.usage_data['total_seconds'] += int(current_session_duration)
        save_usage_data(self.usage_data)
        self.start_time = time.time()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:  # inserted
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp')):
                Logger.log(f'File dropped: {file_path}0')
                self.original_image_path = file_path
                temp_dir = tempfile.mkdtemp()
                temp_image_path = os.path.join(temp_dir, os.path.basename(file_path))
                try:
                    image = Image.open(file_path)
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    exif = image._getexif()
                    if exif is not None:
                        exif = dict(exif.items())
                        if exif.get(orientation) == 3:
                            image = image.rotate(180, expand=True)
                        else:  # inserted
                            if exif.get(orientation) == 6:
                                image = image.rotate(270, expand=True)
                            else:  # inserted
                                if exif.get(orientation) == 8:
                                    image = image.rotate(90, expand=True)
                    image.save(temp_image_path, quality=95, icc_profile=image.info.get('icc_profile'))
                except (AttributeError, KeyError, IndexError):
                    shutil.copy(file_path, temp_image_path)
                self.process_image_path = temp_image_path
                self.batch_input_folder = None
                self.clear_images(keep_labels=False)
                self.original_image_label = QtWidgets.QLabel('Ảnh đầu vào')
                self.original_image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.original_image_label.setFont(QtGui.QFont('Segoe UI', 24, QtGui.QFont.Bold))
                self.original_image_label.setStyleSheet('color: #FFFFFF;')
                self.images_layout.addWidget(self.original_image_label, 0, 0)
                self.restored_image_label = QtWidgets.QLabel('Ảnh đã xử lý')
                self.restored_image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.restored_image_label.setFont(QtGui.QFont('Segoe UI', 24, QtGui.QFont.Bold))
                self.restored_image_label.setStyleSheet('color: #FFFFFF;')
                self.images_layout.addWidget(self.restored_image_label, 0, 1)
                self.display_image(self.process_image_path, self.original_image_label)
                self.restored_image_label.clear()
                Logger.log('Dropped image displayed')
                self.draw_mask_button = QtWidgets.QPushButton('Vẽ Mask')
                self.draw_mask_button.clicked.connect(self.open_mask_drawer)
                self.draw_mask_button.setStyleSheet('\n                    QPushButton {\n                        background-color: #FFFFFF;\n                        color: black;\n                        font: bold 18px;\n                        padding: 10px;\n                        border-radius: 5px;\n                    }\n                    QPushButton:hover {\n                        background-color: #FFC300;\n                    }\n                ')
                self.images_layout.addWidget(self.draw_mask_button, 1, 0)

    def initUI(self):
        Logger.log('UI initialized')
        self.setWindowTitle('Wedding Beauty Studio')
        self.load_user_presets()
        self.resize(1200, 900)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet('background-color: #1A1A1A;')
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(15)
        self.setAcceptDrops(True)
        grouped_layout = QtWidgets.QHBoxLayout()
        grouped_layout.setSpacing(15)
        self.usage_time_label = CustomLabel(f"Tổng Thời Gian Sử Dụng: <span style=\"color:#FFFFFF;\">{format_time(self.usage_data['total_seconds'])}0</span>")
        self.usage_time_label.setObjectName('Label_UsageTime')
        self.usage_time_label.setFont(QtGui.QFont('Segoe UI', 18, QtGui.QFont.Bold))
        self.usage_time_label.setStyleSheet('color: #FFFFFF;')
        self.usage_time_label.setAlignment(QtCore.Qt.AlignLeft)
        grouped_layout.addWidget(self.usage_time_label)
        self.max_usage_time_label = CustomLabel(f'Hạn Mức Dùng: <span style=\"color:#FFFFFF;\">{self.max_usage_hours}h</span>')
        self.max_usage_time_label.setObjectName('Label_MaxUsageTime')
        self.max_usage_time_label.setFont(QtGui.QFont('Segoe UI', 18, QtGui.QFont.Bold))
        self.max_usage_time_label.setStyleSheet('color: #FFFFFF;')
        self.max_usage_time_label.setAlignment(QtCore.Qt.AlignLeft)
        grouped_layout.addWidget(self.max_usage_time_label)
        display_user_code = f'{self.user_code[:10]}0...{self.user_code[(-4):]}'
        self.user_code_label = CustomLabel(f'USER CODE: <span style=\"color:#FFFFFF;\">{display_user_code}</span>')
        self.user_code_label.setObjectName('Label_UserCode')
        self.user_code_label.setFont(QtGui.QFont('Segoe UI', 18, QtGui.QFont.Bold))
        self.user_code_label.setStyleSheet('color: #FFFFFF;')
        self.user_code_label.setAlignment(QtCore.Qt.AlignLeft)
        grouped_layout.addWidget(self.user_code_label)
        self.copy_code_button = CustomButton('Copy Mã Này')
        self.copy_code_button.setObjectName('Button_CopyCode')
        self.copy_code_button.setFont(QtGui.QFont('Segoe UI', 16))
        self.copy_code_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 16px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #444444;\n            }\n        ')
        self.copy_code_button.clicked.connect(self.copy_user_code)
        grouped_layout.addWidget(self.copy_code_button)
        self.activation_code_input = CustomLineEdit()
        self.activation_code_input.setObjectName('LineEdit_ActivationCode')
        self.activation_code_input.setPlaceholderText('Nhập mã kích hoạt vào đây')
        self.activation_code_input.setFont(QtGui.QFont('Segoe UI', 16))
        self.activation_code_input.setStyleSheet('\n            QLineEdit {\n                color: #FFFFFF;\n                background-color: #333333;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QLineEdit::placeholderText {\n                color: #FFFFFF; /* Màu placeholder */\n            }\n        ')
        grouped_layout.addWidget(self.activation_code_input)
        self.activation_confirm_button = CustomButton('Xác Nhận')
        self.activation_confirm_button.setObjectName('Button_ConfirmActivation')
        self.activation_confirm_button.setFont(QtGui.QFont('Segoe UI', 16))
        self.activation_confirm_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 16px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #444444;\n            }\n        ')
        self.activation_confirm_button.clicked.connect(self.on_confirm_activation_code)
        grouped_layout.addWidget(self.activation_confirm_button)
        settings_group = CollapsibleGroupBox('Beauty Studio CPU Máy Yếu Version 9.5')
        settings_group.setFont(QtGui.QFont('Segoe UI', 24, QtGui.QFont.Bold))
        settings_group.setStyleSheet('\n            QGroupBox {\n                color: #B0B0B0;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n                margin-top: 30px;\n            }\n            QGroupBox::title {\n                subcontrol-origin: margin;\n                subcontrol-position: top center;\n                padding: 0 10px;\n            }\n        ')
        form_layout = QtWidgets.QFormLayout()
        form_layout.setHorizontalSpacing(40)
        form_layout.setVerticalSpacing(15)
        row1_layout = QtWidgets.QHBoxLayout()
        upscale_layout = QtWidgets.QHBoxLayout()
        upscale_label = CustomLabel('Phóng To Ảnh:', self)
        upscale_label.setObjectName('Label_Upscale')
        upscale_label.setFont(QtGui.QFont('Segoe UI', 18))
        upscale_label.setStyleSheet('color: #FFFFFF;')
        upscale_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.upscale_var = CustomSlider(QtCore.Qt.Horizontal, name='Upscale')
        self.upscale_var.setObjectName('Slider_Upscale')
        self.upscale_var.setRange(0, 15)
        self.upscale_var.setValue(1)
        self.upscale_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.upscale_var.setToolTip('<span style=\'font-size:14pt;\'>Phóng to ảnh đầu ra lớn hơn ảnh gốc x lần: Nên dùng 2, chỉ dùng 4 nếu máy mạnh và ảnh cần phóng rất rõ</span>')
        self.upscale_display = CustomLabel('2.0')
        self.upscale_display.setObjectName('Label_UpscaleDisplay')
        self.upscale_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.upscale_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.upscale_display.setStyleSheet('color: #FFFFFF;')
        upscale_layout.addWidget(upscale_label)
        upscale_layout.addWidget(self.upscale_var)
        upscale_layout.addWidget(self.upscale_display)
        resize_layout = QtWidgets.QHBoxLayout()
        resize_label = CustomLabel('Giảm Kích Cỡ Ảnh Gốc:', self)
        resize_label.setObjectName('Label_Resize')
        resize_label.setFont(QtGui.QFont('Segoe UI', 18))
        resize_label.setStyleSheet('color: #FFFFFF;')
        resize_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.resize_var = CustomSlider(QtCore.Qt.Horizontal, name='Resize')
        self.resize_var.setObjectName('Slider_Resize')
        self.resize_var.setRange(0, 16)
        self.resize_var.setValue(2)
        self.resize_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.resize_var.setToolTip('<span style=\'font-size:14pt;\'>Giảm size ảnh gốc để xử lý cho nhẹ, sau khi xử lý xong sẽ phóng to ảnh để tăng size: Ảnh thẻ: 1024 - Ảnh Tiệc: 2560 và 4096</span>')
        self.resize_display = CustomLabel('1024')
        self.resize_display.setObjectName('Label_ResizeDisplay')
        self.resize_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.resize_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.resize_display.setStyleSheet('color: #FFFFFF;')
        resize_layout.addWidget(resize_label)
        resize_layout.addWidget(self.resize_var)
        resize_layout.addWidget(self.resize_display)
        row1_layout.addLayout(upscale_layout)
        row1_layout.addSpacing(30)
        row1_layout.addLayout(resize_layout)
        form_layout.addRow(row1_layout)
        self.upscale_var.valueChanged.connect(self.update_upscale_display)
        self.resize_var.valueChanged.connect(self.update_resize_display)
        row2_layout = QtWidgets.QHBoxLayout()
        fidelity_layout = QtWidgets.QHBoxLayout()
        fidelity_label = CustomLabel('Mịn Da - Làm Nét:', self)
        fidelity_label.setObjectName('Label_Fidelity')
        fidelity_label.setFont(QtGui.QFont('Segoe UI', 18))
        fidelity_label.setStyleSheet('color: #FFFFFF;')
        fidelity_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.fidelity_var = CustomSlider(QtCore.Qt.Horizontal, name='Fidelity')
        self.fidelity_var.setObjectName('Slider_Fidelity')
        self.fidelity_var.setRange((-37), 0)
        self.fidelity_var.setValue((-16))
        self.fidelity_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.fidelity_var.setToolTip('<span style=\'font-size:14pt;\'> Tăng giảm mức độ Làm mịn và nét toàn bộ gương mặt, chỉ số càng bé thì mức độ thay đổi càng lớn, nên dùng 0.75 cho ảnh tiệc, 1.2 cho ảnh phục hồi người già</span>')
        self.fidelity_display = CustomLabel('0.8')
        self.fidelity_display.setObjectName('Label_FidelityDisplay')
        self.fidelity_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.fidelity_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.fidelity_display.setStyleSheet('color: #FFFFFF;')
        fidelity_layout.addWidget(fidelity_label)
        fidelity_layout.addWidget(self.fidelity_var)
        fidelity_layout.addWidget(self.fidelity_display)
        mask_fidelity_layout = QtWidgets.QHBoxLayout()
        mask_fidelity_label = CustomLabel('Giữ Nét Gốc Mặt Nạ:', self)
        mask_fidelity_label.setFont(QtGui.QFont('Segoe UI', 18))
        mask_fidelity_label.setStyleSheet('color: #FFFFFF;')
        mask_fidelity_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.mask_fidelity_var = CustomSlider(QtCore.Qt.Horizontal, name='MaskFidelity')
        self.mask_fidelity_var.setRange((-37), 0)
        self.mask_fidelity_var.setValue((-20))
        self.mask_fidelity_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.mask_fidelity_var.setToolTip('<span style=\'font-size:14pt;\'>Giữ nét gốc cho phần mặt nạ được chọn: 1.85 là giữ nguyên y như bản gốc</span>')
        self.mask_fidelity_display = CustomLabel('1.0')
        self.mask_fidelity_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mask_fidelity_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.mask_fidelity_display.setStyleSheet('color: #FFFFFF;')
        mask_fidelity_layout.addWidget(mask_fidelity_label)
        mask_fidelity_layout.addWidget(self.mask_fidelity_var)
        mask_fidelity_layout.addWidget(self.mask_fidelity_display)
        row2_layout.addLayout(fidelity_layout)
        row2_layout.addSpacing(30)
        row2_layout.addLayout(mask_fidelity_layout)
        form_layout.addRow(row2_layout)
        self.fidelity_var.valueChanged.connect(self.update_fidelity_display)
        self.mask_fidelity_var.valueChanged.connect(self.update_mask_fidelity_display)
        row3_layout = QtWidgets.QHBoxLayout()
        blend_visibility_layout = QtWidgets.QHBoxLayout()
        blend_visibility_label = CustomLabel('Giữ Nét Ngưỡng Dưới:', self)
        blend_visibility_label.setObjectName('Label_BlendVisibility')
        blend_visibility_label.setFont(QtGui.QFont('Segoe UI', 18))
        blend_visibility_label.setStyleSheet('color: #FFFFFF;')
        blend_visibility_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.blend_visibility_var = CustomSlider(QtCore.Qt.Horizontal, name='BlendVisibility')
        self.blend_visibility_var.setObjectName('Slider_BlendVisibility')
        self.blend_visibility_var.setRange(0, 500)
        self.blend_visibility_var.setValue(100)
        self.blend_visibility_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.blend_visibility_var.setToolTip('\n            <span style=\'font-size:14pt;\'>\n            <b>Giữ lại các chi tiết nhỏ từ ảnh gốc cho cả khuôn mặt</b>...\n            </span>\n            ')
        self.blend_visibility_display = CustomLabel('100')
        self.blend_visibility_display.setObjectName('Label_BlendVisibilityDisplay')
        self.blend_visibility_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.blend_visibility_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.blend_visibility_display.setStyleSheet('color: #FFFFFF;')
        blend_visibility_layout.addWidget(blend_visibility_label)
        blend_visibility_layout.addWidget(self.blend_visibility_var)
        blend_visibility_layout.addWidget(self.blend_visibility_display)
        blend_visibility_mask_layout = QtWidgets.QHBoxLayout()
        blend_visibility_mask_label = CustomLabel('Giữ Nét Ngưỡng Trên:', self)
        blend_visibility_mask_label.setFont(QtGui.QFont('Segoe UI', 18))
        blend_visibility_mask_label.setStyleSheet('color: #FFFFFF;')
        blend_visibility_mask_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.blend_visibility_mask_var = CustomSlider(QtCore.Qt.Horizontal)
        self.blend_visibility_mask_var.setRange(0, 500)
        self.blend_visibility_mask_var.setValue(200)
        self.blend_visibility_mask_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.blend_visibility_mask_var.setToolTip('\n            <span style=\'font-size:14pt;\'>\n            <b>Xác định và giữ lại các đường nét lớn và quan trọng...</b>\n            </span>\n            ')
        self.blend_visibility_mask_display = CustomLabel('200')
        self.blend_visibility_mask_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.blend_visibility_mask_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.blend_visibility_mask_display.setStyleSheet('color: #FFFFFF;')
        blend_visibility_mask_layout.addWidget(blend_visibility_mask_label)
        blend_visibility_mask_layout.addWidget(self.blend_visibility_mask_var)
        blend_visibility_mask_layout.addWidget(self.blend_visibility_mask_display)
        row3_layout.addLayout(blend_visibility_layout)
        row3_layout.addSpacing(30)
        row3_layout.addLayout(blend_visibility_mask_layout)
        form_layout.addRow(row3_layout)
        self.blend_visibility_var.valueChanged.connect(self.update_blend_visibility_display)
        self.blend_visibility_mask_var.valueChanged.connect(self.update_blend_visibility_mask_display)
        row4_layout = QtWidgets.QHBoxLayout()
        skin_run_layout = QtWidgets.QHBoxLayout()
        skin_run_label = CustomLabel('Mức Độ Hòa Trộn Giữ Nét:', self)
        skin_run_label.setFont(QtGui.QFont('Segoe UI', 18))
        skin_run_label.setStyleSheet('color: #FFFFFF;')
        skin_run_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.skin_run_var = CustomSlider(QtCore.Qt.Horizontal, name='SkinRun')
        self.skin_run_var.setRange(0, 100)
        self.skin_run_var.setValue(21)
        self.skin_run_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.skin_run_var.setToolTip('\n            <span style=\'font-size:14pt;\'>\n            <b>Ảnh hưởng đến nét gốc</b>\n            </span>\n            ')
        self.skin_run_display = CustomLabel('21')
        self.skin_run_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.skin_run_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.skin_run_display.setStyleSheet('color: #FFFFFF;')
        skin_run_layout.addWidget(skin_run_label)
        skin_run_layout.addWidget(self.skin_run_var)
        skin_run_layout.addWidget(self.skin_run_display)
        expand_size_layout = QtWidgets.QHBoxLayout()
        expand_size_label = CustomLabel('Tăng Kích Cỡ Mặt Nạ:', self)
        expand_size_label.setFont(QtGui.QFont('Segoe UI', 18))
        expand_size_label.setStyleSheet('color: #FFFFFF;')
        expand_size_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.expand_size_var = CustomSlider(QtCore.Qt.Horizontal, name='ExpandSize')
        self.expand_size_var.setRange(0, 50)
        self.expand_size_var.setValue(20)
        self.expand_size_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.expand_size_var.setToolTip('<span style=\'font-size:14pt;\'>Mở rộng vùng gần mắt và bao phủ toàn bộ mi, mí mắt để giữ nét...</span>')
        self.expand_size_display = CustomLabel('20')
        self.expand_size_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.expand_size_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.expand_size_display.setStyleSheet('color: #FFFFFF;')
        expand_size_layout.addWidget(expand_size_label)
        expand_size_layout.addWidget(self.expand_size_var)
        expand_size_layout.addWidget(self.expand_size_display)
        row4_layout.addLayout(skin_run_layout)
        row4_layout.addSpacing(30)
        row4_layout.addLayout(expand_size_layout)
        form_layout.addRow(row4_layout)
        self.skin_run_var.valueChanged.connect(self.update_skin_run_display)
        self.expand_size_var.valueChanged.connect(self.update_expand_size_display)
        row5_layout = QtWidgets.QHBoxLayout()
        blend_visibility_face035_layout = QtWidgets.QHBoxLayout()
        blend_visibility_face035_label = CustomLabel('Giữ Nét Mặt Nạ Ngưỡng Dưới:', self)
        blend_visibility_face035_label.setFont(QtGui.QFont('Segoe UI', 18))
        blend_visibility_face035_label.setStyleSheet('color: #FFFFFF;')
        blend_visibility_face035_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.blend_visibility_face035_var = CustomSlider(QtCore.Qt.Horizontal)
        self.blend_visibility_face035_var.setRange(0, 500)
        self.blend_visibility_face035_var.setValue(100)
        self.blend_visibility_face035_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.blend_visibility_face035_var.setToolTip('\n            <span style=\'font-size:14pt;\'>\n            <b>Giữ lại các chi tiết nhỏ từ ảnh gốc cho mặt nạ</b>...\n            </span>\n            ')
        self.blend_visibility_face035_display = CustomLabel('100')
        self.blend_visibility_face035_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.blend_visibility_face035_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.blend_visibility_face035_display.setStyleSheet('color: #FFFFFF;')
        blend_visibility_face035_layout.addWidget(blend_visibility_face035_label)
        blend_visibility_face035_layout.addWidget(self.blend_visibility_face035_var)
        blend_visibility_face035_layout.addWidget(self.blend_visibility_face035_display)
        blend_visibility_mask_face035_layout = QtWidgets.QHBoxLayout()
        blend_visibility_mask_face035_label = CustomLabel('Giữ Nét Mặt Nạ Ngưỡng Trên:', self)
        blend_visibility_mask_face035_label.setFont(QtGui.QFont('Segoe UI', 18))
        blend_visibility_mask_face035_label.setStyleSheet('color: #FFFFFF;')
        blend_visibility_mask_face035_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.blend_visibility_mask_face035_var = CustomSlider(QtCore.Qt.Horizontal)
        self.blend_visibility_mask_face035_var.setRange(0, 500)
        self.blend_visibility_mask_face035_var.setValue(200)
        self.blend_visibility_mask_face035_var.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.blend_visibility_mask_face035_var.setToolTip('\n            <span style=\'font-size:14pt;\'>\n            <b>Xác định và giữ lại các đường nét lớn từ ảnh gốc cho mặt nạ</b>\n            </span>\n            ')
        self.blend_visibility_mask_face035_display = CustomLabel('200')
        self.blend_visibility_mask_face035_display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.blend_visibility_mask_face035_display.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.blend_visibility_mask_face035_display.setStyleSheet('color: #FFFFFF;')
        blend_visibility_mask_face035_layout.addWidget(blend_visibility_mask_face035_label)
        blend_visibility_mask_face035_layout.addWidget(self.blend_visibility_mask_face035_var)
        blend_visibility_mask_face035_layout.addWidget(self.blend_visibility_mask_face035_display)
        row5_layout.addLayout(blend_visibility_face035_layout)
        row5_layout.addSpacing(30)
        row5_layout.addLayout(blend_visibility_mask_face035_layout)
        form_layout.addRow(row5_layout)
        self.blend_visibility_face035_var.valueChanged.connect(self.update_blend_visibility_face035_display)
        self.blend_visibility_mask_face035_var.valueChanged.connect(self.update_blend_visibility_mask_face035_display)
        settings_group.content_area.setLayout(form_layout)
        layout.addWidget(settings_group)
        mask_mode_label = CustomLabel('Đánh Dấu Mặt Nạ:')
        mask_mode_label.setObjectName('Label_MaskMode')
        mask_mode_label.setFont(QtGui.QFont('Segoe UI', 18, QtGui.QFont.Bold))
        mask_mode_label.setStyleSheet('color: #FFFFFF;')
        mask_mode_label.setAlignment(QtCore.Qt.AlignLeft)
        self.mask_mode_combo = CustomComboBox(self)
        self.mask_mode_combo.setObjectName('ComboBox_MaskMode')
        self.mask_mode_combo.addItems(['lông mày', 'mắt', 'mũi', 'miệng', 'lông mày + mắt + mũi + miệng', 'lông mày + mắt + mũi', 'lông mày + mắt'])
        self.mask_mode_combo.setCurrentIndex(0)
        self.mask_mode_combo.setFont(QtGui.QFont('Segoe UI', 16))
        self.mask_mode_combo.setStyleSheet('\n            QComboBox {\n                color: #FFFFFF;\n                background-color: #333333;\n                padding: 10px;\n                border: none;\n                border-radius: 5px;\n            }\n            QComboBox QAbstractItemView {\n                background-color: #333333;\n                selection-background-color: #444444;\n                color: #FFFFFF;\n            }\n        ')
        self.presets_options_combo = QtWidgets.QComboBox(self)
        self.presets_options_combo.setObjectName('ComboBox_PresetsOptions')
        self.update_presets_combo()
        self.presets_options_combo.setCurrentIndex(0)
        self.presets_options_combo.setFont(QtGui.QFont('Segoe UI', 16))
        self.presets_options_combo.setStyleSheet('\n            QComboBox {\n                color: #FFD700; /* Vd: chữ vàng */\n                background-color: #444444; /* Vd: nền xám đậm */\n                padding: 10px;\n                border: 2px solid #FFD700; /* Viền vàng */\n                border-radius: 5px;\n            }\n            QComboBox QAbstractItemView {\n                background-color: #333333;\n                selection-background-color: #FF8C00; /* Vd: cam đậm khi hover */\n                color: #FFFFFF;\n            }\n        ')
        self.presets_options_combo.currentIndexChanged.connect(self.apply_preset_parameters)
        self.save_preset_button = CustomButton('Lưu Kiểu Ảnh')
        self.save_preset_button.setFont(QtGui.QFont('Segoe UI', 16))
        self.save_preset_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 16px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #FFB800;\n            }\n        ')
        self.save_preset_button.clicked.connect(self.save_user_preset)
        self.delete_preset_button = CustomButton('Xóa Kiểu Ảnh')
        self.delete_preset_button.setFont(QtGui.QFont('Segoe UI', 16))
        self.delete_preset_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 16px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #FF6347;\n            }\n        ')
        self.delete_preset_button.clicked.connect(self.delete_user_preset)
        self.mask_checkbox = CustomCheckBox('Dùng Mặt Nạ')
        self.mask_checkbox.setObjectName('CheckBox_Mask')
        self.mask_checkbox.setChecked(self.use_mask)
        self.mask_checkbox.stateChanged.connect(self.toggle_mask_usage)
        self.mask_checkbox.setFont(QtGui.QFont('Segoe UI', 16, QtGui.QFont.Bold))
        self.mask_checkbox.setStyleSheet('color: #FFFFFF;')
        self.run_skin_checkbox = CustomCheckBox('Nét Toàn Ảnh')
        self.run_skin_checkbox.setObjectName('CheckBox_RunSkin')
        self.run_skin_checkbox.setChecked(self.run_skin)
        self.run_skin_checkbox.setFont(QtGui.QFont('Segoe UI', 16, QtGui.QFont.Bold))
        self.run_skin_checkbox.setStyleSheet('color: #FFFFFF;')
        self.run_skin_checkbox.stateChanged.connect(self.on_run_skin_checkbox_changed)
        self.on_run_skin_checkbox_changed(self.run_skin_checkbox.checkState())
        preset_options_layout = QtWidgets.QHBoxLayout()
        preset_options_layout.setSpacing(20)
        label_width = 150
        mask_mode_label.setMinimumWidth(label_width)
        preset_options_layout.addWidget(mask_mode_label)
        preset_options_layout.addWidget(self.mask_mode_combo)
        preset_options_layout.addWidget(self.presets_options_combo)
        preset_options_layout.addWidget(self.save_preset_button)
        preset_options_layout.addWidget(self.delete_preset_button)
        preset_options_layout.addWidget(self.mask_checkbox)
        preset_options_layout.addWidget(self.run_skin_checkbox)
        layout.addLayout(preset_options_layout)
        button_layout1 = QtWidgets.QHBoxLayout()
        button_layout1.setSpacing(10)
        self.browse_photo_button = CustomButton('Chọn 1 Ảnh')
        self.browse_photo_button.setObjectName('Button_BrowsePhoto')
        self.browse_photo_button.setFont(QtGui.QFont('Segoe UI', 18))
        self.browse_photo_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 18px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #444444;\n            }\n        ')
        self.browse_photo_button.clicked.connect(self.on_browse_photo)
        button_layout1.addWidget(self.browse_photo_button)
        self.browse_folder_button = CustomButton('Chọn Thư Mục Ảnh')
        self.browse_folder_button.setObjectName('Button_BrowseFolder')
        self.browse_folder_button.setFont(QtGui.QFont('Segoe UI', 18))
        self.browse_folder_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 18px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #444444;\n            }\n        ')
        self.browse_folder_button.clicked.connect(self.on_browse_folder)
        button_layout1.addWidget(self.browse_folder_button)
        self.model_selection_combo = CustomComboBox(self)
        self.model_selection_combo.setObjectName('ComboBox_ModelSelection')
        self.model_selection_combo.addItem('Dùng Mô Hình Phục Hồi', 'RestoreFormer')
        self.model_selection_combo.addItem('Dùng Mô Hình Làm Nét', 'CodeFormer')
        self.model_selection_combo.setCurrentIndex(1)
        self.model_selection_combo.setFont(QtGui.QFont('Segoe UI', 16))
        self.model_selection_combo.setStyleSheet('\n            QComboBox {\n                color: #FFFFFF;\n                background-color: #333333;\n                padding: 10px;\n                border: none;\n                border-radius: 5px;\n            }\n            QComboBox QAbstractItemView {\n                background-color: #333333;\n                selection-background-color: #444444;\n                color: #FFFFFF;\n            }\n        ')
        self.model_selection_combo.currentIndexChanged.connect(self.on_model_selection_changed)
        button_layout1.addWidget(self.model_selection_combo)
        self.start_button = CustomButton('Bắt Đầu')
        self.start_button.setObjectName('Button_Start')
        self.start_button.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.start_button.setStyleSheet('\n            QPushButton {\n                background-color: #FFFFFF;\n                color: #333333;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n                padding: 10px;\n            }\n            QPushButton:hover {\n                background-color: #FFC300;\n            }\n        ')
        self.start_button.clicked.connect(self.on_start)
        button_layout1.addWidget(self.start_button)
        self.stop_button = CustomButton('Dừng Chạy Hàng Loạt')
        self.stop_button.setObjectName('Button_Stop')
        self.stop_button.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.stop_button.setStyleSheet('\n            QPushButton {\n                background-color: #444444;\n                color: #FFFFFF;\n                font-size: 20px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #DC143C;\n            }\n        ')
        self.stop_button.clicked.connect(self.on_stop)
        button_layout1.addWidget(self.stop_button)
        self.option_button = CustomButton('Cài Đặt')
        self.option_button.setObjectName('Button_Option')
        self.option_button.setFont(QtGui.QFont('Segoe UI', 18))
        self.option_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 18px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #444444;\n            }\n        ')
        self.option_button.clicked.connect(self.on_option)
        button_layout1.addWidget(self.option_button)
        self.output_button = CustomButton('Mở Ảnh Đã Lưu')
        self.output_button.setObjectName('Button_Output')
        self.output_button.setFont(QtGui.QFont('Segoe UI', 18))
        self.output_button.setStyleSheet('\n            QPushButton {\n                background-color: #333333;\n                color: #FFFFFF;\n                font-size: 18px;\n                padding: 10px;\n                border: 2px solid #FFFFFF;\n                border-radius: 10px;\n            }\n            QPushButton:hover {\n                background-color: #444444;\n            }\n        ')
        self.output_button.clicked.connect(self.open_outputs_folder)
        button_layout1.addWidget(self.output_button)
        layout.addLayout(button_layout1)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setObjectName('ScrollArea')
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_content.setObjectName('ScrollContent')
        self.images_layout = QtWidgets.QGridLayout(scroll_content)
        self.original_image_label = CustomLabel('Ảnh Gốc')
        self.original_image_label.setObjectName('Label_OriginalImage')
        self.original_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.original_image_label.setFont(QtGui.QFont('Segoe UI', 24, QtGui.QFont.Bold))
        self.original_image_label.setStyleSheet('color: #FFFFFF;')
        self.images_layout.addWidget(self.original_image_label, 0, 0)
        self.restored_image_label = CustomLabel('Kết Quả')
        self.restored_image_label.setObjectName('Label_RestoredImage')
        self.restored_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.restored_image_label.setFont(QtGui.QFont('Segoe UI', 24, QtGui.QFont.Bold))
        self.restored_image_label.setStyleSheet('color: #FFFFFF;')
        self.images_layout.addWidget(self.restored_image_label, 0, 1)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        self.progress_bar = CustomProgressBar(self)
        self.progress_bar.setObjectName('ProgressBar_Main')
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFont(QtGui.QFont('Segoe UI', 16))
        self.progress_bar.setStyleSheet('\n            QProgressBar {\n                border: 2px solid #FFFFFF;\n                border-radius: 5px;\n                text-align: center;\n                font-size: 16px;\n                color: white;\n            }\n            QProgressBar::chunk {\n                background-color: green;\n                width: 10px;\n            }\n        ')
        layout.addWidget(self.progress_bar)
        layout.addLayout(grouped_layout)
        self.contact_label = CustomLabel('')
        self.contact_label.setObjectName('Label_Contact')
        self.contact_label.setFont(QtGui.QFont('Segoe UI', 20, QtGui.QFont.Bold))
        self.contact_label.setAlignment(QtCore.Qt.AlignCenter)
        self.contact_label.setStyleSheet('\n            color: #FFFFFF;\n            background-color: #333333;\n            padding: 5px;\n            border-radius: 10px;\n        ')
        layout.addWidget(self.contact_label)
        self.setLayout(layout)

    def disable_ui_elements(self):
        self.upscale_var.setEnabled(False)
        self.resize_var.setEnabled(False)
        self.fidelity_var.setEnabled(False)
        self.mask_fidelity_var.setEnabled(False)
        self.blend_visibility_var.setEnabled(False)
        self.blend_visibility_mask_var.setEnabled(False)
        self.skin_run_var.setEnabled(False)
        self.expand_size_var.setEnabled(False)
        self.blend_visibility_face035_var.setEnabled(False)
        self.blend_visibility_mask_face035_var.setEnabled(False)
        self.mask_checkbox.setEnabled(False)
        self.run_skin_checkbox.setEnabled(False)
        self.browse_photo_button.setEnabled(False)
        self.browse_folder_button.setEnabled(False)
        self.option_button.setEnabled(False)
        self.save_preset_button.setEnabled(False)
        self.delete_preset_button.setEnabled(False)
        self.mask_mode_combo.setEnabled(False)
        self.presets_options_combo.setEnabled(False)

    def enable_ui_elements(self):
        self.upscale_var.setEnabled(True)
        self.resize_var.setEnabled(True)
        self.fidelity_var.setEnabled(True)
        self.mask_fidelity_var.setEnabled(True)
        self.blend_visibility_var.setEnabled(True)
        self.blend_visibility_mask_var.setEnabled(True)
        self.skin_run_var.setEnabled(True)
        self.expand_size_var.setEnabled(True)
        self.blend_visibility_face035_var.setEnabled(True)
        self.blend_visibility_mask_face035_var.setEnabled(True)
        self.mask_checkbox.setEnabled(True)
        self.run_skin_checkbox.setEnabled(True)
        self.browse_photo_button.setEnabled(True)
        self.browse_folder_button.setEnabled(True)
        self.option_button.setEnabled(True)
        self.save_preset_button.setEnabled(True)
        self.delete_preset_button.setEnabled(True)
        self.mask_mode_combo.setEnabled(True)
        self.presets_options_combo.setEnabled(True)

    def load_user_presets(self):
        try:
            with open('user_presets.json', 'r') as f:
                self.user_presets = json.load(f)
        except FileNotFoundError:
            self.user_presets = {}

    def update_presets_combo(self):
        self.presets_options_combo.blockSignals(True)
        self.presets_options_combo.clear()
        for preset_name in self.presets.keys():
            self.presets_options_combo.addItem(preset_name)
        for preset_name in self.user_presets.keys():
            self.presets_options_combo.addItem(preset_name)
        self.presets_options_combo.blockSignals(False)

    def save_user_preset(self):
        preset_name, ok = QtWidgets.QInputDialog.getText(self, 'Lưu Tùy Chỉnh', 'Nhập tên cho tùy chỉnh mới:')
        if ok:
            if preset_name:
                @self.upscale_var.value()
                preset_values = {'upscale': self.fidelity_var.value(), 'fidelity': self.blend_visibility_var.value(), 'blend_visibility': self.blend_visibility_mask_var.value(), 'blend_visibility_mask': self.expand_size_var.value(), 'expand_size': self.resize_var.value(), 'resize': self.use_mask, 'use_mask': self.mask_fidelity_var.value(), 'mask_fidelity': self.run_skin_checkbox.isChecked(), 'run_skin': self.skin_run_var.value(), 'skin_run': self.blend_visibility_face035_var.value(), 'blend_visibility_face035': self.blend_visibility_mask_face035_var.value(), 'blend_visibility_mask_face035': self.selected_model, 'selected_model': self.mask_mode_combo.currentText()}
                try:
                    with open('user_presets.json', 'r') as f:
                        user_presets = json.load(f)
                except FileNotFoundError:
                    user_presets = {}
                user_presets[preset_name] = preset_values
                with open('user_presets.json', 'w') as f:
                    json.dump(user_presets, f)
                self.user_presets = user_presets
                self.update_presets_combo()

    def delete_user_preset(self):
        preset_name = self.presets_options_combo.currentText()
        if preset_name in self.user_presets:
            reply = QtWidgets.QMessageBox.question(self, 'Xác nhận', f'Bạn có chắc muốn xóa tùy chỉnh \"{preset_name}\"?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                del self.user_presets[preset_name]
                with open('user_presets.json', 'w') as f:
                    json.dump(self.user_presets, f)
                self.update_presets_combo()
        else:  # inserted
            QtWidgets.QMessageBox.warning(self, 'Không thể xóa', 'Bạn chỉ có thể xóa các tùy chỉnh mà bạn đã tạo.')

    def apply_preset_parameters(self, index):
        preset_name = self.presets_options_combo.itemText(index)
        if preset_name in self.presets:
            preset_values = self.presets.get(preset_name)
        else:  # inserted
            if preset_name in self.user_presets:
                preset_values = self.user_presets.get(preset_name)
            else:  # inserted
                pass
                return
        self.upscale_var.blockSignals(True)
        self.fidelity_var.blockSignals(True)
        self.blend_visibility_var.blockSignals(True)
        self.blend_visibility_mask_var.blockSignals(True)
        self.expand_size_var.blockSignals(True)
        self.resize_var.blockSignals(True)
        self.mask_fidelity_var.blockSignals(True)
        self.skin_run_var.blockSignals(True)
        self.blend_visibility_face035_var.blockSignals(True)
        self.blend_visibility_mask_face035_var.blockSignals(True)
        self.model_selection_combo.blockSignals(True)
        self.mask_mode_combo.blockSignals(True)
        self.upscale_var.setValue(preset_values['upscale'])
        self.fidelity_var.setValue(preset_values['fidelity'])
        self.blend_visibility_var.setValue(preset_values['blend_visibility'])
        self.blend_visibility_mask_var.setValue(preset_values['blend_visibility_mask'])
        self.expand_size_var.setValue(preset_values['expand_size'])
        self.resize_var.setValue(preset_values['resize'])
        self.mask_fidelity_var.setValue(preset_values['mask_fidelity'])
        self.skin_run_var.setValue(preset_values['skin_run'])
        self.blend_visibility_face035_var.setValue(preset_values.get('blend_visibility_face035', 100))
        self.blend_visibility_mask_face035_var.setValue(preset_values.get('blend_visibility_mask_face035', 200))
        self.use_mask = preset_values.get('use_mask', False)
        self.mask_checkbox.blockSignals(True)
        self.mask_checkbox.setChecked(self.use_mask)
        self.mask_checkbox.blockSignals(False)
        self.run_skin = preset_values.get('run_skin', False)
        self.run_skin_checkbox.blockSignals(True)
        self.run_skin_checkbox.setChecked(self.run_skin)
        self.run_skin_checkbox.blockSignals(False)
        self.on_run_skin_checkbox_changed(self.run_skin_checkbox.checkState())
        selected_model = preset_values.get('selected_model', 'RestoreFormer')
        index = self.model_selection_combo.findData(selected_model)
        if index >= 0:
            self.model_selection_combo.setCurrentIndex(index)
        self.selected_model = selected_model
        mask_mode = preset_values.get('mask_mode', 'lông mày + mắt + mũi + miệng')
        index = self.mask_mode_combo.findText(mask_mode)
        if index >= 0:
            self.mask_mode_combo.setCurrentIndex(index)
        self.upscale_var.blockSignals(False)
        self.fidelity_var.blockSignals(False)
        self.blend_visibility_var.blockSignals(False)
        self.blend_visibility_mask_var.blockSignals(False)
        self.expand_size_var.blockSignals(False)
        self.resize_var.blockSignals(False)
        self.mask_fidelity_var.blockSignals(False)
        self.skin_run_var.blockSignals(False)
        self.blend_visibility_face035_var.blockSignals(False)
        self.blend_visibility_mask_face035_var.blockSignals(False)
        self.model_selection_combo.blockSignals(False)
        self.mask_mode_combo.blockSignals(False)
        self.update_upscale_display(self.upscale_var.value())
        self.update_fidelity_display(self.fidelity_var.value())
        self.update_blend_visibility_display(self.blend_visibility_var.value())
        self.update_blend_visibility_mask_display(self.blend_visibility_mask_var.value())
        self.update_expand_size_display(self.expand_size_var.value())
        self.update_resize_display(self.resize_var.value())
        self.update_mask_fidelity_display(self.mask_fidelity_var.value())
        self.update_skin_run_display(self.skin_run_var.value())
        self.update_blend_visibility_face035_display(self.blend_visibility_face035_var.value())
        self.update_blend_visibility_mask_face035_display(self.blend_visibility_mask_face035_var.value())

    def on_model_selection_changed(self, index):
        self.selected_model = self.model_selection_combo.currentData()
        Logger.log(f'Model selected: {self.selected_model}0')

    def update_skin_run_display(self, value):
        skin_run_value = value * 1
        self.skin_run_display.setText(f'{skin_run_value}')

    def update_fidelity_display(self, value):
        fidelity_value = value * (-0.05)
        self.fidelity_display.setText(f"{fidelity_value:.2f}")

    def update_mask_fidelity_display(self, value):
        fidelity_value = value * (-0.05)
        self.mask_fidelity_display.setText(f"{fidelity_value:.2f}")

    def update_blend_visibility_display(self, value):
        blend_visibility_value = value * 1
        self.blend_visibility_display.setText(f'{blend_visibility_value}')

    def update_blend_visibility_mask_display(self, value):
        blend_visibility_mask_value = value * 1
        self.blend_visibility_mask_display.setText(f'{blend_visibility_mask_value}')

    def update_blend_visibility_face035_display(self, value):
        blend_visibility_value = value * 1
        self.blend_visibility_face035_display.setText(f'{blend_visibility_value}')

    def update_blend_visibility_mask_face035_display(self, value):
        blend_visibility_mask_value = value * 1
        self.blend_visibility_mask_face035_display.setText(f'{blend_visibility_mask_value}')

    def update_expand_size_display(self, value):
        expand_size_value = value * 1
        self.expand_size_display.setText(str(expand_size_value))

    def update_resize_display(self, value):
        resize_values = [512, 768, 1024, 1536, 2048, 2560, 3072, 3584, 4096, 4608, 5120, 5632, 6144, 6656, 7168, 7680, 11264]
        self.resize_display.setText(str(resize_values[value]))

    def update_upscale_display(self, value):
        self.upscale_display.setText(f'{value + 1:.1f}')

    def toggle_mask_usage(self, state):
        self.use_mask = state == QtCore.Qt.Checked
        Logger.log(f'Mask usage toggled: {self.use_mask}0')

    def on_run_skin_checkbox_changed(self, state):
        self.run_skin = state == QtCore.Qt.Checked
        Logger.log(f'run_skin toggled: {self.run_skin}0')
        if self.run_skin:
            self.connect_realtime_signals()
        else:  # inserted
            self.disconnect_realtime_signals()

    def connect_realtime_signals(self):
        self.blend_visibility_var.valueChanged.connect(self.reblend_and_update_image)
        self.blend_visibility_mask_var.valueChanged.connect(self.reblend_and_update_image)
        self.skin_run_var.valueChanged.connect(self.reblend_and_update_image)
        self.expand_size_var.valueChanged.connect(self.reblend_and_update_image)
        self.mask_fidelity_var.valueChanged.connect(self.reblend_and_update_image)
        self.blend_visibility_face035_var.valueChanged.connect(self.reblend_and_update_image)
        self.blend_visibility_mask_face035_var.valueChanged.connect(self.reblend_and_update_image)
        self.fidelity_var.valueChanged.connect(self.reblend_and_update_image)

    def disconnect_realtime_signals(self):
        try:
            self.blend_visibility_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.blend_visibility_mask_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.skin_run_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.expand_size_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.mask_fidelity_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.blend_visibility_face035_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.blend_visibility_mask_face035_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            pass
        try:
            self.fidelity_var.valueChanged.disconnect(self.reblend_and_update_image)
        except TypeError:
            return None

    def toggle_colorspace_check(self, state):
        self.check_colorspace = state == QtCore.Qt.Checked
        Logger.log(f'Colorspace check toggled: {self.check_colorspace}0')

    def reblend_and_update_image(self):
        if not self.run_skin:
            return
        if self.restored_face is not None and self.cropped_face is not None:
            blend_visibility = self.blend_visibility_var.value() * 1
            blend_visibility_mask = self.blend_visibility_mask_var.value() * 1
            blend_visibility_face035 = self.blend_visibility_face035_var.value() * 1
            blend_visibility_mask_face035 = self.blend_visibility_mask_face035_var.value() * 1
            skin_run_value = self.skin_run_var.value()
            codeformer_fidelity = self.fidelity_var.value() * (-0.05)
            mask_mode = self.mask_mode_combo.currentText()
            self.selected_model = self.model_selection_combo.currentData()
            if self.last_codeformer_fidelity is None or codeformer_fidelity!= self.last_codeformer_fidelity:
                cropped_face_t = img2tensor(self.cropped_face / 255.0, bgr2rgb=True, float32=True).to(torch.float32)
                cropped_face_t = torch_normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
                cropped_face_t = cropped_face_t.unsqueeze(0).to(self.device)
                if self.selected_model == 'RestoreFormer':
                    with torch.no_grad():
                        output, _, _, _ = self.restoreformer_net.RF(cropped_face_t)
                        restored_face = tensor2img(output.squeeze(0), rgb2bgr=True, min_max=((-1), 1))
                    self.restored_face = restored_face
                else:  # inserted
                    if self.selected_model == 'CodeFormer':
                        with torch.no_grad():
                            if codeformer_fidelity > 1.8:
                                self.restored_face = self.cropped_face
                                Logger.log('Skipping CodeFormer processing as fidelity exceeds 1.8')
                            else:  # inserted
                                output = self.codeformer_net(cropped_face_t, w=codeformer_fidelity, adain=True)[0]
                                restored_face = tensor2img(output, rgb2bgr=True, min_max=((-1), 1))
                                self.restored_face = restored_face
                    else:  # inserted
                        raise ValueError(f'Unknown model selected: {self.selected_model}0')
                self.last_codeformer_fidelity = codeformer_fidelity
            blended_face_user = blend_faces(self.restored_face, self.cropped_face, threshold1=blend_visibility, threshold2=blend_visibility_mask, kernel_size=skin_run_value)
            mask_mode = self.mask_mode_combo.currentText()
            if mask_mode in ['miệng', 'lông mày + mắt + mũi + miệng']:
                gray = cv2.cvtColor(self.cropped_face, cv2.COLOR_BGR2GRAY)
                rects = [dlib.rectangle(0, 0, self.cropped_face.shape[1], self.cropped_face.shape[0])]
                for rect in rects:
                    shape = self.predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    teeth_landmarks = shape[60:68]
                    teeth_mask = np.zeros(self.cropped_face.shape[:2], dtype=np.uint8)
                    cv2.fillPoly(teeth_mask, [teeth_landmarks], 255)
                    teeth_mask = cv2.GaussianBlur(teeth_mask, (15, 15), 0)
                    alpha_mask = teeth_mask.astype(np.float32) / 255.0
                    alpha_mask = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
                    blended_face_user = alpha_mask * self.cropped_face + (1 - alpha_mask) * blended_face_user
                    blended_face_user = blended_face_user.astype(np.uint8)
            if self.use_mask:
                expand_size_value = self.expand_size_var.value() * 1
                mask_mode = self.mask_mode_combo.currentText()
                if self.cached_mask is None or self.last_expand_size!= expand_size_value or self.last_mask_mode!= mask_mode:
                    mask_to_use = generate_facial_mask(self.cropped_face, self.predictor, expand_size=expand_size_value, mask_mode=mask_mode)
                    self.cached_mask = mask_to_use
                    self.last_expand_size = expand_size_value
                    self.last_mask_mode = mask_mode
                else:  # inserted
                    mask_to_use = self.cached_mask
                codeformer_fidelity_mask = self.mask_fidelity_var.value() * (-0.05)
                blended_face_035 = self.process_masked_region(codeformer_fidelity_mask, blend_visibility_face035, blend_visibility_mask_face035, skin_run_value)
                final_blended_face = self.combine_images_with_mask(blended_face_user, blended_face_035, mask_to_use)
                if self.max_usage_hours < 100:
                    final_blended_face = add_watermark(final_blended_face)
                blended_face_qpixmap = self.numpy_to_qpixmap(final_blended_face)
            else:  # inserted
                if self.max_usage_hours < 100:
                    blended_face_user = add_watermark(blended_face_user)
                blended_face_qpixmap = self.numpy_to_qpixmap(blended_face_user)
            screen = QtWidgets.QApplication.primaryScreen()
            screen_size = screen.size()
            screen_height = screen_size.height()
            max_height = screen_height * 1090 // 1440
            blended_face_qpixmap = blended_face_qpixmap.scaledToHeight(max_height, QtCore.Qt.SmoothTransformation)
            self.blended_face_user = blended_face_user
            if self.use_mask:
                self.final_blended_face = final_blended_face
            else:  # inserted
                self.final_blended_face = None
            if self.thumbnail_window is None:
                self.thumbnail_window = ThumbnailWindow()
                self.thumbnail_window.setWindowTitle('Kết Quả')
                self.thumbnail_window.label.clicked.connect(self.thumbnail_clicked)
                screen = QtWidgets.QApplication.primaryScreen()
                screen_size = screen.size()
                screen_width = screen_size.width()
                screen_height = screen_size.height()
                x = (screen_width - self.thumbnail_window.width()) // 2
                y = screen_height * 350 // 1440
                self.thumbnail_window.move(x, y)
            self.thumbnail_window.label.setPixmap(blended_face_qpixmap)
            self.thumbnail_window.resize(blended_face_qpixmap.width(), blended_face_qpixmap.height())
            self.thumbnail_window.show()

    def thumbnail_clicked(self):
        if self.use_mask and self.final_blended_face is not None:
            blended_image = self.final_blended_face
        else:  # inserted
            blended_image = self.blended_face_user
        original_image_path = os.path.join(self.temp_dir, 'cropped_face.jpg')
        restored_image_path = os.path.join(self.temp_dir, 'blended_image.jpg')
        cv2.imwrite(original_image_path, self.cropped_face)
        cv2.imwrite(restored_image_path, blended_image)
        self.fullscreen_comparison = FullScreenComparison(original_image_path, restored_image_path)
        self.fullscreen_comparison.showFullScreen()
        self.thumbnail_window.close()
        self.thumbnail_window = None

    def numpy_to_qpixmap(self, img_array):
        img = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QtGui.QImage(img.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QtGui.QPixmap.fromImage(q_img)

    def update_restored_image_display(self, qpixmap):
        self.restored_image_label.setPixmap(qpixmap.scaled(512, 512, QtCore.Qt.KeepAspectRatio))

    def store_faces(self, restored_face, cropped_face, original_image_rgb):
        self.restored_face = restored_face
        self.cropped_face = cropped_face
        self.original_image_rgb = original_image_rgb
        self.cached_mask = None
        self.last_expand_size = None
        self.cached_restored_face_mask = None
        self.last_codeformer_fidelity_mask = None
        self.last_codeformer_fidelity = None
        self.blend_visibility_var.setEnabled(True)
        self.blend_visibility_mask_var.setEnabled(True)
        self.skin_run_var.setEnabled(True)
        self.expand_size_var.setEnabled(True)

    def process_masked_region(self, codeformer_fidelity_mask, blend_visibility_face035, blend_visibility_mask_face035, skin_run_value):
        if self.selected_model == 'RestoreFormer':
            model_net = self.restoreformer_net
        else:  # inserted
            if self.selected_model == 'CodeFormer':
                model_net = self.codeformer_net
            else:  # inserted
                raise ValueError(f'Unknown model selected: {self.selected_model}0')
        if self.cached_restored_face_mask is None or self.last_codeformer_fidelity_mask!= codeformer_fidelity_mask:
            cropped_face_t = img2tensor(self.cropped_face / 255.0, bgr2rgb=True, float32=True).to(torch.float32)
            cropped_face_t = torch_normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            cropped_face_t = cropped_face_t.unsqueeze(0).to(self.device)
            with torch.no_grad():
                Logger.log(f'Running {self.selected_model} model for mask region processing')
                if self.selected_model == 'RestoreFormer':
                    output, _, _, _ = model_net.RF(cropped_face_t)
                    restored_face = tensor2img(output.squeeze(0), rgb2bgr=True, min_max=((-1), 1))
                else:  # inserted
                    if self.selected_model == 'CodeFormer':
                        w = codeformer_fidelity_mask
                        output = model_net(cropped_face_t, w=w, adain=True)[0]
                        restored_face = tensor2img(output, rgb2bgr=True, min_max=((-1), 1))
            self.cached_restored_face_mask = restored_face
            self.last_codeformer_fidelity_mask = codeformer_fidelity_mask
        else:  # inserted
            restored_face = self.cached_restored_face_mask
        if codeformer_fidelity_mask > 1.8:
            blended_face_035 = self.cropped_face.copy()
            Logger.log(f'Skipping {self.selected_model} processing for mask region as fidelity is above threshold')
            return blended_face_035
        blended_face_035 = blend_faces(restored_face, self.cropped_face, threshold1=blend_visibility_face035, threshold2=blend_visibility_mask_face035, kernel_size=skin_run_value)
        mask_mode = self.mask_mode_combo.currentText()
        if mask_mode in ['miệng', 'lông mày + mắt + mũi + miệng']:
            gray = cv2.cvtColor(self.cropped_face, cv2.COLOR_BGR2GRAY)
            rects = [dlib.rectangle(0, 0, self.cropped_face.shape[1], self.cropped_face.shape[0])]
            for rect in rects:
                shape = self.predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                teeth_landmarks = shape[60:68]
                teeth_mask = np.zeros(self.cropped_face.shape[:2], dtype=np.uint8)
                cv2.fillPoly(teeth_mask, [teeth_landmarks], 255)
                teeth_mask = cv2.GaussianBlur(teeth_mask, (15, 15), 0)
                alpha_mask = teeth_mask.astype(np.float32) / 255.0
                alpha_mask = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
                blended_teeth = blend_faces(restored_face, self.cropped_face, threshold1=500, threshold2=500, kernel_size=100)
                blended_face_035 = np.where(alpha_mask == 1, blended_teeth, blended_face_035)
        gray = cv2.cvtColor(self.cropped_face, cv2.COLOR_BGR2GRAY)
        rects = [dlib.rectangle(0, 0, self.cropped_face.shape[1], self.cropped_face.shape[0])]
        for rect in rects:
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            teeth_landmarks = shape[60:68]
            teeth_mask = np.zeros(self.cropped_face.shape[:2], dtype=np.uint8)
            cv2.fillPoly(teeth_mask, [teeth_landmarks], 255)
            blended_teeth = blend_faces(restored_face, self.cropped_face, threshold1=500, threshold2=500, kernel_size=100)
            teeth_mask_expanded = cv2.merge([teeth_mask, teeth_mask, teeth_mask])
            blended_face_035 = np.where(teeth_mask_expanded == 255, blended_teeth, blended_face_035)
        return blended_face_035

    def combine_images_with_mask(self, blended_face_user, blended_face_035, mask):
        mask_resized = cv2.resize(mask, (blended_face_user.shape[1], blended_face_user.shape[0]), interpolation=cv2.INTER_NEAREST)
        mask_resized = mask_resized.astype(np.float32) / 255.0
        if mask_resized.ndim == 2:
            mask_resized = mask_resized[:, :, np.newaxis]
        kernel_size = (31, 31)
        mask_blurred = cv2.GaussianBlur(mask_resized, kernel_size, 0)
        if mask_blurred.ndim == 2:
            mask_blurred = mask_blurred[:, :, np.newaxis]
        mask_blurred = np.repeat(mask_blurred, 3, axis=2)
        blended_face_035_adjusted = self.adjust_color_brightness(blended_face_035, blended_face_user)
        final_blended_face = blended_face_035_adjusted * mask_blurred + blended_face_user * (1 - mask_blurred)
        final_blended_face = final_blended_face.astype(np.uint8)
        return final_blended_face

    def adjust_color_brightness(self, image_to_adjust, reference_image):
        image_to_adjust_lab = cv2.cvtColor(image_to_adjust, cv2.COLOR_BGR2LAB).astype(np.float32)
        reference_image_lab = cv2.cvtColor(reference_image, cv2.COLOR_BGR2LAB).astype(np.float32)
        image_to_adjust_lab[..., 1:] -= 128
        reference_image_lab[..., 1:] -= 128
        l_mean_adj, l_std_adj = cv2.meanStdDev(image_to_adjust_lab[..., 0])
        a_mean_adj, a_std_adj = cv2.meanStdDev(image_to_adjust_lab[..., 1])
        b_mean_adj, b_std_adj = cv2.meanStdDev(image_to_adjust_lab[..., 2])
        l_mean_ref, l_std_ref = cv2.meanStdDev(reference_image_lab[..., 0])
        a_mean_ref, a_std_ref = cv2.meanStdDev(reference_image_lab[..., 1])
        b_mean_ref, b_std_ref = cv2.meanStdDev(reference_image_lab[..., 2])
        epsilon = 1e-06
        l_std_adj_val = l_std_adj[0][0]
        l_std_ref_val = l_std_ref[0][0]
        if l_std_adj_val < epsilon:
            l_std_adj_val = 1.0
        image_to_adjust_lab[..., 0] = (image_to_adjust_lab[..., 0] - l_mean_adj[0][0]) * (l_std_ref_val / l_std_adj_val) + l_mean_ref[0][0]
        a_std_adj_val = a_std_adj[0][0]
        a_std_ref_val = a_std_ref[0][0]
        if a_std_adj_val < epsilon:
            a_std_adj_val = 1.0
        image_to_adjust_lab[..., 1] = (image_to_adjust_lab[..., 1] - a_mean_adj[0][0]) * (a_std_ref_val / a_std_adj_val) + a_mean_ref[0][0]
        b_std_adj_val = b_std_adj[0][0]
        b_std_ref_val = b_std_ref[0][0]
        if b_std_adj_val < epsilon:
            b_std_adj_val = 1.0
        image_to_adjust_lab[..., 2] = (image_to_adjust_lab[..., 2] - b_mean_adj[0][0]) * (b_std_ref_val / b_std_adj_val) + b_mean_ref[0][0]
        image_to_adjust_lab[..., 1:] += 128
        image_to_adjust_lab = np.clip(image_to_adjust_lab, 0, 255).astype(np.uint8)
        adjusted_image = cv2.cvtColor(image_to_adjust_lab, cv2.COLOR_LAB2BGR)
        return adjusted_image

    def on_browse_photo(self):
        Logger.log('Browsing photo or video')
        options = QFileDialog.Options()
        selected_file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image or Video File', '', 'Image/Video Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp *.mp4 *.avi *.mov *.mkv *.flv)', options=options)
        if selected_file_path:
            selected_extension = os.path.splitext(selected_file_path)[1].lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
            if selected_extension in video_extensions:
                Logger.log(f'Video selected: {selected_file_path}0')
                self.is_video = True
                self.video_input_path = selected_file_path
                self.original_image_path = None
                self.video_frames_dir = tempfile.mkdtemp()
                try:
                    extract_frames_from_video(self.video_input_path, self.video_frames_dir)
                except Exception as e:
                    Logger.log(f'Error extracting frames from video: {e}0')
                    QtWidgets.QMessageBox.warning(self, 'Error', f'Failed to process video: {e}')
                    return None
                self.batch_input_folder = self.video_frames_dir
                thumbnail_path = os.path.join(self.temp_dir, 'video_thumbnail.jpg')
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                extract_first_frame(self.video_input_path, thumbnail_path)
                self.clear_images(keep_labels=False)
                self.original_image_label = QtWidgets.QLabel('Original Video')
                self.original_image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.original_image_label.setFont(QtGui.QFont('Times New Roman', 36, QtGui.QFont.Bold))
                self.original_image_label.setStyleSheet('color: #FFFFFF;')
                self.images_layout.addWidget(self.original_image_label, 0, 0)
                self.display_image(thumbnail_path, self.original_image_label)
                self.restored_image_label = QtWidgets.QLabel('Restored Video')
                self.restored_image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.restored_image_label.setFont(QtGui.QFont('Times New Roman', 36, QtGui.QFont.Bold))
                self.restored_image_label.setStyleSheet('color: #FFFFFF;')
                self.images_layout.addWidget(self.restored_image_label, 0, 1)
                if hasattr(self, 'draw_mask_button'):
                    self.draw_mask_button.setEnabled(False)
                Logger.log('Video thumbnail displayed')
            else:  # inserted
                Logger.log(f'Image selected: {selected_file_path}0')
                self.is_video = False
                self.original_image_path = selected_file_path
                self.video_input_path = None
                temp_dir = tempfile.mkdtemp()
                temp_image_path = os.path.join(temp_dir, os.path.basename(selected_file_path))
                try:
                    image = Image.open(selected_file_path)
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    exif = image._getexif()
                    if exif is not None:
                        exif = dict(exif.items())
                        if exif.get(orientation) == 3:
                            image = image.rotate(180, expand=True)
                        else:  # inserted
                            if exif.get(orientation) == 6:
                                image = image.rotate(270, expand=True)
                            else:  # inserted
                                if exif.get(orientation) == 8:
                                    image = image.rotate(90, expand=True)
                    image.save(temp_image_path, quality=95, icc_profile=image.info.get('icc_profile'))
                except (AttributeError, KeyError, IndexError):
                    shutil.copy(selected_file_path, temp_image_path)
                self.process_image_path = temp_image_path
                self.batch_input_folder = None
                self.clear_images(keep_labels=False)
                self.mask = None
                self.saved_mask = None
                self.cached_mask = None
                self.last_expand_size = None
                self.last_mask_mode = None
                self.cached_restored_face_mask = None
                self.last_codeformer_fidelity_mask = None
                self.last_codeformer_fidelity = None
                self.original_image_label = QtWidgets.QLabel('Original Image')
                self.original_image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.original_image_label.setFont(QtGui.QFont('Times New Roman', 36, QtGui.QFont.Bold))
                self.original_image_label.setStyleSheet('color: #FFFFFF;')
                self.images_layout.addWidget(self.original_image_label, 0, 0)
                self.restored_image_label = QtWidgets.QLabel('Restored Image')
                self.restored_image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.restored_image_label.setFont(QtGui.QFont('Times New Roman', 36, QtGui.QFont.Bold))
                self.restored_image_label.setStyleSheet('color: #FFFFFF;')
                self.images_layout.addWidget(self.restored_image_label, 0, 1)
                self.display_image(self.process_image_path, self.original_image_label)
                self.restored_image_label.clear()
                Logger.log('Single photo displayed')
                self.draw_mask_button = QtWidgets.QPushButton('Vẽ Mask')
                self.draw_mask_button.clicked.connect(self.open_mask_drawer)
                self.draw_mask_button.setStyleSheet('\n                    QPushButton {\n                        background-color: #FFFFFF;\n                        color: black;\n                        font: bold 18px;\n                        padding: 5px;\n                        border-radius: 5px;\n                    }\n                    QPushButton:hover {\n                        background-color: #FFC300;\n                    }\n                ')
                self.images_layout.addWidget(self.draw_mask_button, 1, 0)
                self.draw_mask_button.setEnabled(True)
        else:  # inserted
            Logger.log('No photo or video selected')
            self.original_image_path = None
            self.start_button.setEnabled(True)

    def receive_mask(self, mask):
        self.mask = mask
        self.saved_mask = mask
        Logger.log('Mask received')

    def open_mask_drawer(self):
        if self.original_image_path:
            self.mask_drawer = MaskDrawer(self.original_image_path, self.saved_mask)
            self.mask_drawer.mask_drawn.connect(self.receive_mask)
            self.mask_drawer.show()

    def display_image(self, image_path, label):
        Logger.log(f'Displaying file: {image_path}0')
        try:
            selected_extension = os.path.splitext(image_path)[1].lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
            if selected_extension in video_extensions:
                thumbnail_path = os.path.join(self.temp_dir, 'video_thumbnail.jpg')
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                extract_first_frame(image_path, thumbnail_path)
                img = QtGui.QPixmap(thumbnail_path)
                if img.isNull():
                    Logger.log(f'Failed to load video thumbnail: {thumbnail_path}0')
                else:  # inserted
                    Logger.log(f'Video thumbnail QPixmap size: {img.size()}')
                    img = img.scaled(512, 512, QtCore.Qt.KeepAspectRatio)
                    label.setPixmap(img)
                    Logger.log('Video thumbnail set on label')
                    label.repaint()
                    self.update()
                    Logger.log('Label repainted and UI updated for video thumbnail')
                    label.setToolTip('This is a video file. Displayed thumbnail is the first frame.')
                    label.setStyleSheet('\n                        QLabel {\n                            background-color: #311432;\n                            color: #FFFFFF;\n                            font-size: 18px;\n                        }\n                        QLabel::hover {\n                            background-color: #7d3c98;\n                            color: #FFFFFF;\n                            font-size: 24px;\n                        }\n                    ')
                    return
            else:  # inserted
                img = QtGui.QPixmap(image_path)
                if img.isNull():
                    Logger.log(f'Failed to load image: {image_path}0')
                    return
                Logger.log(f'Image QPixmap size: {img.size()}')
                img = img.scaled(512, 512, QtCore.Qt.KeepAspectRatio)
                label.setPixmap(img)
                Logger.log('Image set on label')
                label.repaint()
                self.update()
                Logger.log('Label repainted and UI updated for image')
                try:
                    original_img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
                    original_height, original_width = original_img.shape[:2]
                    label.setToolTip(f'Resolution: {original_width}0 x {original_height}0')
                    label.setStyleSheet('\n                            QLabel {\n                                background-color: #311432;\n                                color: #FFFFFF;\n                                font-size: 18px;\n                            }\n                            QLabel::hover {\n                                background-color: #7d3c98;\n                                color: #FFFFFF;\n                                font-size: 24px;\n                            }\n                        ')
                except Exception as e:
                    Logger.log(f'Failed to get image resolution: {e}0')
        except Exception as e:
            Logger.log(f'Error displaying file: {e}0')

    def on_browse_folder(self):
        Logger.log('Browsing folder')
        self.mask = None
        self.saved_mask = None
        self.cached_mask = None
        self.last_expand_size = None
        self.last_mask_mode = None
        self.cached_restored_face_mask = None
        self.last_codeformer_fidelity_mask = None
        self.last_codeformer_fidelity = None
        self.batch_input_folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if self.batch_input_folder:
            Logger.log(f'Folder selected: {self.batch_input_folder}0')
            self.original_image_path = None
            self.clear_images(keep_labels=False)
            self.temp_dir = tempfile.mkdtemp()
            self.original_to_temp_paths = {}
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp']
            self.image_files = [file_name for file_name in os.listdir(self.batch_input_folder) if Path(file_name).suffix.lower() in image_extensions]
            self.total_images = len(self.image_files)
            self.current_index = 0
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f'Đang tải 0/{self.total_images} ảnh')
            self.timer = QTimer()
            self.timer.timeout.connect(self.load_next_batch)
            self.timer.start(100)
        else:  # inserted
            Logger.log('No folder selected')

    def load_next_batch(self):
        batch_size = 10
        if self.current_index >= self.total_images:
            self.timer.stop()
            self.progress_bar.setFormat('Tải ảnh hoàn tất')
            Logger.log('All images processed')
            self.display_thumbnails(self.temp_dir)
            return
        batch_end = min(self.current_index + batch_size, self.total_images)
        for i in range(self.current_index, batch_end):
            file_name = self.image_files[i]
            original_file_path = os.path.join(self.batch_input_folder, file_name)
            temp_image_path = os.path.join(self.temp_dir, file_name)
            try:
                image = Image.open(original_file_path)
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = image._getexif()
                if exif is not None:
                    exif = dict(exif.items())
                    if exif.get(orientation) == 3:
                        image = image.rotate(180, expand=True)
                    else:  # inserted
                        if exif.get(orientation) == 6:
                            image = image.rotate(270, expand=True)
                        else:  # inserted
                            if exif.get(orientation) == 8:
                                image = image.rotate(90, expand=True)
                image.save(temp_image_path, quality=95, icc_profile=image.info.get('icc_profile'))
            except (AttributeError, KeyError, IndexError):
                shutil.copy(original_file_path, temp_image_path)
            self.original_to_temp_paths[original_file_path] = temp_image_path
        self.current_index = batch_end
        self.progress_bar.setValue(self.current_index)
        self.progress_bar.setFormat(f'Đang tải {self.current_index}/{self.total_images} ảnh')

    def display_thumbnails(self, folder_path):
        Logger.log(f'Displaying thumbnails for folder: {folder_path}0')
        try:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp']
            image_files = [file for file in os.listdir(folder_path) if Path(file).suffix.lower() in image_extensions]
            if self.thumbnail_display_count!= 'All':
                display_limit = int(self.thumbnail_display_count)
                image_files = image_files[:display_limit]
            for i, file in enumerate(image_files):
                label = QtWidgets.QLabel()
                thumbnail = QtGui.QPixmap(os.path.join(folder_path, file)).scaled(512, 512, QtCore.Qt.KeepAspectRatio)
                label.setPixmap(thumbnail)
                original_img = cv2.imdecode(np.fromfile(os.path.join(folder_path, file), dtype=np.uint8), cv2.IMREAD_COLOR)
                original_height, original_width = original_img.shape[:2]
                label.setToolTip(f'Resolution: {original_width}0 x {original_height}0')
                label.setStyleSheet('\n                    QLabel {\n                        background-color: #311432;\n                        color: #FFFFFF;\n                        font-size: 18px;\n                    }\n                    QLabel::hover {\n                        background-color: #7d3c98;\n                        color: #FFFFFF;\n                        font-size: 24px;\n                    }\n                ')
                draw_mask_button = QtWidgets.QPushButton('Vẽ Mask')
                draw_mask_button.setStyleSheet('\n                    QPushButton {\n                        background-color: #FFFFFF;\n                        color: black;\n                        font: bold 18px;\n                        padding: 5px;\n                        border-radius: 5px;\n                    }\n                    QPushButton:hover {\n                        background-color: #FFC300;\n                    }\n                ')
                draw_mask_button.clicked.connect(lambda checked, path=os.path.join(folder_path, file): self.open_mask_drawer_for_batch(path))
                row = i + 1
                self.images_layout.addWidget(label, row, 0)
                self.images_layout.addWidget(draw_mask_button, row, 1)
                self.image_path_to_row[os.path.normpath(os.path.join(folder_path, file))] = row
            Logger.log('Thumbnails displayed')
        except Exception as e:
            Logger.log(f'Error displaying thumbnails: {e}0')

    def display_restored_thumbnail(self, original_image_path, restored_image_path, restored_width, restored_height):
        Logger.log(f'Displaying restored thumbnail for: {original_image_path}0')
        row = self.image_path_to_row.get(os.path.normpath(original_image_path))
        if row is None:
            Logger.log(f'Error: original_image_path not found in image_path_to_row: {original_image_path}0')
            row = 1
            self.image_path_to_row[original_image_path] = row
        try:
            restored_extension = os.path.splitext(restored_image_path)[1].lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
            if restored_extension in video_extensions:
                Logger.log(f'Restored file is a video. Extracting thumbnail for: {restored_image_path}0')
                thumbnail_path = os.path.join(self.temp_dir, 'output_video_thumbnail.jpg')
                extract_first_frame(restored_image_path, thumbnail_path)
                thumbnail = QtGui.QPixmap(thumbnail_path)
            else:  # inserted
                Logger.log(f'Restored file is an image. Loading thumbnail for: {restored_image_path}0')
                thumbnail = QtGui.QPixmap(restored_image_path)
            label = QtWidgets.QLabel()
            thumbnail = thumbnail.scaled(512, 512, QtCore.Qt.KeepAspectRatio)
            label.setPixmap(thumbnail)
            if restored_width and restored_height:
                label.setToolTip(f'Resolution: {restored_width}0 x {restored_height}0')
            label.setStyleSheet('\n                QLabel {\n                    background-color: #311432;\n                    color: #FFFFFF;\n                    font-size: 18px;\n                }\n                QLabel::hover {\n                    background-color: #7d3c98;\n                    color: #FFFFFF;\n                    font-size: 24px;\n                }\n            ')

            def mouse_press_event_handler(event):
                Logger.log(f'Mouse clicked on thumbnail. Original: {original_image_path}0, Restored: {restored_image_path}0')
                try:
                    self.show_full_screen_comparison(original_image_path, restored_image_path)
                except Exception as e:
                    Logger.log(f'Error showing full-screen comparison: {e}0')
            label.mousePressEvent = mouse_press_event_handler
            self.images_layout.addWidget(label, row, 1)
            Logger.log('Restored thumbnail displayed successfully')
        except Exception as e:
            Logger.log(f'Error displaying restored thumbnail: {e}0')

    def open_mask_drawer_for_batch(self, image_path):
        Logger.log(f'Opening mask drawer for batch image: {image_path}0')
        temp_mask_path = os.path.splitext(image_path)[0] + '_mask.png'
        saved_mask = None
        if os.path.exists(temp_mask_path):
            saved_mask = cv2.imdecode(np.fromfile(temp_mask_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        self.mask_drawer = MaskDrawer(image_path, saved_mask)
        self.mask_drawer.mask_drawn.connect(lambda mask: self.save_mask_for_batch(image_path, mask))
        self.mask_drawer.show()

    def save_mask_for_batch(self, image_path, mask):
        Logger.log(f'Saving mask for batch image: {image_path}0')
        temp_mask_path = os.path.splitext(image_path)[0] + '_mask.png'
        cv2.imwrite(temp_mask_path, mask)
        Logger.log(f'Mask saved at: {temp_mask_path}0')

    def on_start(self):
        if hasattr(self, 'thumbnail_window') and self.thumbnail_window is not None:
            self.thumbnail_window.close()
            self.thumbnail_window = None
        Logger.log('Start processing')
        if not self.original_image_path and (not self.batch_input_folder):
            Logger.log('No image or folder selected')
            QtWidgets.QMessageBox.warning(self, 'No Image Selected', 'Please select an image or folder before starting.')
            return
        if self.is_processing:
            return
        self.is_processing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.disable_ui_elements()
        upscale = self.upscale_var.value() + 1
        codeformer_fidelity = self.fidelity_var.value() * (-0.05)
        codeformer_fidelity_mask = self.mask_fidelity_var.value() * (-0.05)
        resize_values = [512, 768, 1024, 1536, 2048, 2560, 3072, 3584, 4096, 4608, 5120, 5632, 6144, 6656, 7168, 7680, 11264]
        resize_value = resize_values[self.resize_var.value()]
        selected_model = self.model_selection_combo.currentData()
        Logger.log(f'Selected model: {selected_model}0')
        mask_mode = self.mask_mode_combo.currentText()
        Logger.log(f'Selected mask mode: {mask_mode}0')
        Logger.log(f"Settings - Upscale: {upscale}0, Accuracy: {codeformer_fidelity:.2f}4, Resize: {resize_value}0, Device: {self.device}0")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if self.predictor is None:
            Logger.log('Loading shape_predictor_68_face_landmarks.dat...')
            self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        if selected_model == 'RestoreFormer':
            if self.restoreformer_net is None:
                Logger.log('Loading RestoreFormer++ model (lazy load)')
                self.restoreformer_net = load_restoreformer(device)
            self.codeformer_net = None
        else:  # inserted
            if selected_model == 'CodeFormer':
                if self.codeformer_net is None:
                    Logger.log('Loading CodeFormer model (lazy load)')
                    self.codeformer_net = load_codeformer(device)
                self.restoreformer_net = None
            else:  # inserted
                Logger.log(f'Invalid model selected: {selected_model}0')
                QtWidgets.QMessageBox.warning(self, 'Invalid Model', 'The selected model is not recognized. Please choose a valid model.')
                return
        if self.upsampler is None:
            Logger.log('Setting up RealESRGAN (lazy load)')
            self.run_skin = self.run_skin_checkbox.isChecked()
            self.upsampler = set_realesrgan(device, option='normal', run_skin=self.run_skin)
        script_directory = os.path.dirname(os.path.abspath(__file__))
        icc_folder = os.path.join(script_directory, 'icc_profiles')
        srgb_icc_profile_path = os.path.join(icc_folder, 'sRGB Color Space Profile.icm')
        temp_dir = os.path.join(script_directory, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        if self.original_image_path:
            Logger.log(f'Processing single photo: {self.original_image_path}0')
            output_dir = os.path.join(os.path.dirname(self.original_image_path), 'output')
            filename = Path(self.original_image_path).name
            mask_to_use = self.mask if self.use_mask else None
            expand_size_value = self.expand_size_var.value() * 1
            blend_visibility = self.blend_visibility_var.value() * 1
            blend_visibility_mask = self.blend_visibility_mask_var.value() * 1
            blend_visibility_face035 = self.blend_visibility_face035_var.value() * 1
            blend_visibility_mask_face035 = self.blend_visibility_mask_face035_var.value() * 1
            self.run_skin = self.run_skin_checkbox.isChecked()
            self.skin_run_value = self.skin_run_var.value()
            self.worker = Worker(self.process_image_path, upscale, codeformer_fidelity, codeformer_fidelity_mask, resize_value, output_dir, filename, self.output_format, self.image_quality, device, icc_folder, srgb_icc_profile_path, temp_dir, self.background_enhance, self.face_upsample, self.use_mask, self.check_colorspace, mask=mask_to_use, restoreformer_net=self.restoreformer_net, codeformer_net=self.codeformer_net, expand_size=expand_size_value, blend_visibility=blend_visibility, blend_visibility_mask=blend_visibility_mask, blend_visibility_face035=blend_visibility_face035, blend_visibility_mask_face035=blend_visibility_mask_face035, run_skin=self.run_skin, skin_run_value=self.skin_run_value, eye_dist_threshold=self.eye_dist_threshold, user_watermark_enabled=self.watermark_enabled, user_watermark_text=self.watermark_text, user_watermark_positions=self.watermark_positions, font_family=self.font_family, text_color=self.text_color, size_ratio=self.size_ratio, offset_x=self.offset_x, offset_y=self.offset_y, mask_mode=mask_mode, selected_model=selected_model)
            self.worker.faces_ready.connect(self.store_faces)
            self.worker.max_usage_hours = self.max_usage_hours
            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.image_processed.connect(self.display_restored_image)
            self.worker.progress_update.connect(self.update_progress)
            self.thread.start()
            self.thread.finished.connect(self.on_task_complete)
        else:  # inserted
            if self.batch_input_folder:
                Logger.log(f'Processing batch folder: {self.batch_input_folder}0')
                output_dir_base = os.path.join(self.batch_input_folder, 'output')
                if not os.path.exists(output_dir_base):
                    os.makedirs(output_dir_base)
                existing_dirs = [d for d in os.listdir(output_dir_base) if os.path.isdir(os.path.join(output_dir_base, d)) and d.isdigit()]
                existing_dirs.sort()
                next_dir_number = int(existing_dirs[(-1)]) + 1 if existing_dirs else 1
                output_dir = os.path.join(output_dir_base, f"{next_dir_number:03d}")
                os.makedirs(output_dir, exist_ok=True)
                self.latest_output_dir = output_dir
                temp_images_folder = self.batch_input_folder if self.is_video else self.temp_dir
                expand_size_value = self.expand_size_var.value() * 1
                blend_visibility = self.blend_visibility_var.value() * 1
                blend_visibility_mask = self.blend_visibility_mask_var.value() * 1
                blend_visibility_face035 = self.blend_visibility_face035_var.value() * 1
                blend_visibility_mask_face035 = self.blend_visibility_mask_face035_var.value() * 1
                self.run_skin = self.run_skin_checkbox.isChecked()
                self.skin_run_value = self.skin_run_var.value()
                self.worker = BatchWorker(temp_images_folder, output_dir, upscale, codeformer_fidelity, codeformer_fidelity_mask, resize_value, self.output_format, self.image_quality, device, icc_folder, srgb_icc_profile_path, self.thumbnail_display_count, temp_dir, self.background_enhance, self.face_upsample, self.use_mask, self.check_colorspace, restoreformer_net=self.restoreformer_net, codeformer_net=self.codeformer_net, expand_size=expand_size_value, blend_visibility=blend_visibility, blend_visibility_mask=blend_visibility_mask, blend_visibility_face035=blend_visibility_face035, blend_visibility_mask_face035=blend_visibility_mask_face035, run_skin=self.run_skin, skin_run_value=self.skin_run_value, eye_dist_threshold=self.eye_dist_threshold, user_watermark_enabled=self.watermark_enabled, user_watermark_text=self.watermark_text, user_watermark_positions=self.watermark_positions, font_family=self.font_family, text_color=self.text_color, size_ratio=self.size_ratio, offset_x=self.offset_x, offset_y=self.offset_y, is_video=self.is_video, video_input_path=self.video_input_path, mask_mode=mask_mode, selected_model=selected_model)
                self.worker.max_usage_hours = self.max_usage_hours
                self.worker.output_dir_signal.connect(self.update_latest_output_dir)
                self.thread = QThread()
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.worker.image_processed.connect(self.display_restored_thumbnail)
                self.worker.progress_update.connect(self.update_progress)
                self.thread.start()
                self.thread.finished.connect(self.on_task_complete)
                self.thread.finished.connect(lambda: Logger.log('Batch processing thread finished'))

    def on_stop(self):
        Logger.log('Processing stopped')
        self.is_processing = False
        if self.worker:
            self.worker.stop()
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.enable_ui_elements()

    def on_task_complete(self):
        self.is_processing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.enable_ui_elements()
        self.blend_visibility_var.setEnabled(True)
        self.blend_visibility_mask_var.setEnabled(True)
        self.skin_run_var.setEnabled(True)
        if self.is_video and os.path.exists(self.batch_input_folder):
            shutil.rmtree(self.batch_input_folder)
            Logger.log(f'Temporary frames directory {self.batch_input_folder} removed.')

    def update_progress(self, value, message, color='green'):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)
        self.progress_bar.setStyleSheet(f'\n            QProgressBar {\n                border: 2px solid #FFFFFF;\n                border-radius: 5px;\n                text-align: center;\n                font-size: 22px;\n                color: white;\n            }\n            QProgressBar::chunk {\n                background-color: {color};\n                width: 20px;\n            }\n        ')

    def display_restored_image(self, original_image_path, restored_image_path, restored_width, restored_height):
        try:
            Logger.log('Starting to display restored image...')
            Logger.log(f'Original image path: {original_image_path}0')
            Logger.log(f'Restored image path: {restored_image_path}0')
            restored_image = cv2.imdecode(np.fromfile(restored_image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if restored_image is None:
                raise ValueError('Failed to decode restored image. The file may be corrupted.')
            restored_image = cv2.cvtColor(restored_image, cv2.COLOR_BGR2RGB)
            restored_image = QtGui.QImage(restored_image.data, restored_image.shape[1], restored_image.shape[0], restored_image.strides[0], QtGui.QImage.Format_RGB888)
            self.restored_image_label.setPixmap(QtGui.QPixmap.fromImage(restored_image).scaled(512, 512, QtCore.Qt.KeepAspectRatio))
            self.restored_image_label.repaint()
            Logger.log('Restored image successfully displayed on QLabel.')

            def mouse_event_handler(event, orig_path=original_image_path, rest_path=restored_image_path):
                try:
                    Logger.log(f'Mouse clicked on restored image. Original: {orig_path}0, Restored: {rest_path}0')
                    self.show_full_screen_comparison(orig_path, rest_path)
                except Exception as e:
                    Logger.log(f'Error during full-screen comparison: {e}0')
                    raise
            self.restored_image_label.mousePressEvent = mouse_event_handler
            Logger.log('Mouse event handler successfully assigned.')
            if not self.is_video:
                self.latest_output_dir = os.path.dirname(restored_image_path)
                Logger.log(f'Latest output directory set to: {self.latest_output_dir}0')
            else:  # inserted
                Logger.log('No update for latest output directory as the file is a video.')
            self.restored_image_label.setToolTip(f'Resolution: {restored_width} x {restored_height}0')
            self.restored_image_label.setStyleSheet('\n                QLabel {\n                    background-color: #311432;\n                    color: #FFFFFF;\n                    font-size: 18px;\n                }\n                QLabel::hover {\n                    background-color: #7d3c98;\n                    color: #FFFFFF;\n                    font-size: 24px;\n                }\n            ')
            Logger.log('Tooltip and styles successfully applied.')
        except Exception as e:
            Logger.log(f'Error displaying restored image: {e}0')

    def on_option(self):
        dialog = OptionDialog(self.output_format, self.image_quality, self.device, self.thumbnail_display_count, self.background_enhance, self.face_upsample, self.eye_dist_threshold, self.watermark_enabled, self.watermark_text, self.watermark_positions, self.font_family, self.text_color, self.size_ratio, self.offset_x, self.offset_y, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.output_format, self.image_quality, self.device, self.thumbnail_display_count, self.background_enhance, self.face_upsample, self.eye_dist_threshold, self.watermark_enabled, self.watermark_text, self.watermark_positions, self.font_family, self.text_color, self.size_ratio, self.offset_x, self.offset_y = dialog.get_options()
            Logger.log(f'Watermark Enabled: {self.watermark_enabled}, Text: {self.watermark_text}, Positions: {self.watermark_positions}, Font: {self.font_family}, Color: {self.text_color}, Size Ratio: {self.size_ratio}%, Offset X: {self.offset_x}, Offset Y: {self.offset_y}')
            self.save_settings()

    def update_latest_output_dir(self, output_dir):
        Logger.log(f'Nhận thư mục output cuối từ worker: {output_dir}0')
        self.latest_output_dir = output_dir

    def open_outputs_folder(self):
        Logger.log('Opening outputs folder')
        if self.is_video and self.latest_output_dir:
            Logger.log(f'Opening latest video output directory: {self.latest_output_dir}0')
            self.open_folder(self.latest_output_dir)
        else:  # inserted
            if self.latest_output_dir:
                Logger.log(f'Opening latest output directory: {self.latest_output_dir}0')
                self.open_folder(self.latest_output_dir)
            else:  # inserted
                output_folder = QFileDialog.getExistingDirectory(self, 'Select Outputs Folder')
                if output_folder:
                    Logger.log(f'Outputs folder selected: {output_folder}0')
                    self.open_folder(output_folder)
                else:  # inserted
                    Logger.log('No outputs folder selected')

    def open_folder(self, folder_path):
        os.startfile(folder_path)

    def clear_fields(self):
        Logger.log('Clearing fields')
        self.upscale_var.setValue(1)
        self.fidelity_var.setValue(10)
        self.original_image_label.clear()
        self.restored_image_label.clear()

    def clear_images(self, keep_labels=False):
        Logger.log(f'Clearing images, keep_labels={keep_labels}0')
        for i in reversed(range(self.images_layout.count())):
            widget_to_remove = self.images_layout.itemAt(i).widget()
            if widget_to_remove and (not keep_labels or widget_to_remove not in (self.original_image_label, self.restored_image_label)):
                widget_to_remove.setParent(None)
        if keep_labels:
            self.original_image_label.clear()
            self.restored_image_label.clear()

    def show_full_screen_comparison(self, original_image_path, restored_image_path):
        self.full_screen_comparison = FullScreenComparison(original_image_path, restored_image_path)
        self.full_screen_comparison.showFullScreen()

    def calculate_secret_code(self):
        return int(self.user_code[39:]) - int(self.user_code[:39])

    def calculate_serial_key(self, secret_code, offset_multiplier):
        serial_key_offset = 19850619851706198517061985588616
        return int(self.user_code) + serial_key_offset * offset_multiplier * secret_code

    def on_confirm_activation_code(self):
        entered_code = self.activation_code_input.text()
        self.activation_code_input.clear()
        if not entered_code:
            self.show_message_box('Sai mã kích hoạt', 'hãy nhập mã kích hoạt trước khi bấm xác nhận')
            return
        secret_code = self.calculate_secret_code()
        valid_keys = {1: self.calculate_serial_key(secret_code, 1), 100: self.calculate_serial_key(secret_code, 100), 1200: self.calculate_serial_key(secret_code, 1200), 999999: self.calculate_serial_key(secret_code, 999999)}
        if entered_code in self.usage_data.get('activation_history', []):
            self.show_message_box('Sai mã kích hoạt', 'Mã này đã được dùng rồi')
            return
        try:
            entered_code_int = int(entered_code)
        except ValueError:
            self.show_message_box('Mã sai', 'Mã kích hoạt không đúng')
            return None
        valid_hours = {v: k for k, v in valid_keys.items()}
        if entered_code_int in valid_hours:
            self.max_usage_hours += valid_hours[entered_code_int]
            self.usage_data.setdefault('activation_history', []).append(entered_code)
            self.usage_data['max_usage_hours'] = self.max_usage_hours
            save_usage_data(self.usage_data)
            self.usage_data['cpu_serial'] = self.cpu_serial
            save_usage_data(self.usage_data)
            self.update_usage_time()
            self.max_usage_time_label.setText(f'<span style=\"color:#FFFFFF;\">Hạn Mức Dùng:</span> <span style=\"color:#FFFFFF;\">{self.max_usage_hours}h</span>')
            self.show_message_box('Kích hoạt thành công', f'Thời gian sử dụng của bạn đã tăng thêm {valid_hours[entered_code_int]}0 giờ.')
            self.user_code = str(int(self.user_code) + random.randint(1, 9999))
            self.user_code_label.setText(f'User Code: {self.user_code}0')
            self.activation_attempts = 0
        else:  # inserted
            self.show_message_box('Mã sai', 'hãy kiểm tra lại')
            self.activation_attempts += 1
            if self.activation_attempts >= 3:
                self.user_code = str(int(self.user_code) + random.randint(1, 9999))
                self.user_code_label.setText(f'User Code: {self.user_code}0')
                self.activation_attempts = 0

    def show_message_box(self, title, message):
        msg_box = ClickableMessageBox(title, message)
        msg_box.exec_()

    def copy_user_code(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.user_code)
        self.show_message_box('Copy thành công', 'Gửi thông tin này đến hỗ trợ')

class FullScreenComparison(QtWidgets.QWidget):
    def __init__(self, original_image_path, restored_image_path):
        super().__init__()
        self.original_image_path = original_image_path
        self.restored_image_path = restored_image_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Full Screen Image Slider Comparison')
        screen = QtGui.QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.setGeometry(screen_geometry)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet('background-color: black;')
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        close_button = QtWidgets.QPushButton('X')
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet('\n            QPushButton {\n                background-color: red;\n                color: white;\n                font: bold 20px;\n                padding: 10px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #ff4d4d;\n            }\n        ')
        close_button.setFixedSize(50, 50)
        close_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.setContentsMargins(0, 0, 0, 0)
        close_layout.addWidget(close_button, 0, QtCore.Qt.AlignRight)
        layout.addLayout(close_layout)
        self.comparison_slider = ComparisonSlider(self.original_image_path, self.restored_image_path)
        layout.addWidget(self.comparison_slider)
        self.setLayout(layout)

class ComparisonSlider(QtWidgets.QWidget):
    def __init__(self, original_image_path, restored_image_path):
        super().__init__()
        self.original_image_path = original_image_path
        self.restored_image_path = restored_image_path
        self.zoom_factor = 1.0
        self.dragging = False
        self.last_mouse_pos = None
        self.initializeUI()

    def initializeUI(self):
        self.original_img_original = QtGui.QPixmap(self.original_image_path)
        self.restored_img_original = QtGui.QPixmap(self.restored_image_path)
        screen_height = QtWidgets.QApplication.desktop().screenGeometry().height()
        self.zoom_factor = screen_height / self.original_img_original.height()
        self.resize_images_by_zoom_factor()
        self.center_images()
        self.slider_pos = self.original_image.width() // 2
        self.setMouseTracking(True)
        self.instruction_label = QtWidgets.QLabel('- Scroll chuột giữa để Zoom ảnh.\n- Nhấn giữ và kéo chuột trái để so sánh.\n- Nhấn giữ và kéo chuột phải để di chuyển ảnh.', self)
        self.instruction_label.setStyleSheet('color: white; font-size: 20px; background-color: rgba(0, 0, 0, 150); padding: 10px;')
        self.instruction_label.setAlignment(QtCore.Qt.AlignLeft)
        self.instruction_label.setFixedSize(400, 100)
        self.instruction_label.move(20, 20)

    def resize_images_by_zoom_factor(self):
        new_width = int(self.original_img_original.width() * self.zoom_factor)
        new_height = int(self.original_img_original.height() * self.zoom_factor)
        self.original_image = self.original_img_original.scaled(new_width, new_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.restored_image = self.restored_img_original.scaled(new_width, new_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.update()

    def center_images(self):
        screen = QtGui.QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.setFixedSize(screen_geometry.size())
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        image_width = self.original_image.width()
        image_height = self.original_image.height()
        self.orig_x = (screen_width - image_width) // 2
        self.orig_y = (screen_height - image_height) // 2

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(int(self.orig_x), int(self.orig_y), self.original_image)
        painter.drawPixmap(int(self.orig_x + self.slider_pos), int(self.orig_y), self.restored_image, int(self.slider_pos), 0, int(self.restored_image.width() - self.slider_pos), int(self.restored_image.height()))
        painter.setPen(QtCore.Qt.red)
        painter.drawLine(int(self.orig_x + self.slider_pos), int(self.orig_y), int(self.orig_x + self.slider_pos), int(self.orig_y + self.original_image.height()))

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.slider_pos = event.x() - self.orig_x
            self.update()
        else:  # inserted
            if event.buttons() == QtCore.Qt.RightButton and self.dragging:
                if self.last_mouse_pos:
                    dx = event.x() - self.last_mouse_pos.x()
                    dy = event.y() - self.last_mouse_pos.y()
                    self.orig_x += dx
                    self.orig_y += dy
                self.last_mouse_pos = event.pos()
                self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.slider_pos = event.x() - self.orig_x
            self.update()
        else:  # inserted
            if event.button() == QtCore.Qt.RightButton:
                self.dragging = True
                self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.dragging = False
            self.last_mouse_pos = None

    def wheelEvent(self, event):
        old_zoom_factor = self.zoom_factor
        delta = event.angleDelta().y() / 120
        self.zoom_factor += delta * 0.1
        self.zoom_factor = max(0.1, self.zoom_factor)
        mouse_x = event.x()
        mouse_y = event.y()
        scale_factor = self.zoom_factor / old_zoom_factor
        self.orig_x = mouse_x - scale_factor * (mouse_x - self.orig_x)
        self.orig_y = mouse_y - scale_factor * (mouse_y - self.orig_y)
        self.resize_images_by_zoom_factor()

class OptionDialog(QtWidgets.QDialog):
    def __init__(self, current_format, current_quality, current_device, current_thumbnail_display_count, current_background_enhance, current_face_upsample, current_eye_dist_threshold, current_watermark_enabled, current_watermark_text, current_watermark_positions, current_font_family, current_text_color, current_size_ratio, current_offset_x, current_offset_y, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Output Options')
        self.setGeometry(100, 100, 600, 1000)
        layout = QtWidgets.QVBoxLayout()
        format_label = QtWidgets.QLabel('Định dạng ảnh xuất ra:')
        format_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(['JPEG', 'PNG', 'BMP', 'TIFF'])
        self.format_combo.setCurrentText(current_format)
        self.format_combo.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        quality_label = QtWidgets.QLabel('Chất lượng ảnh xuất ra:')
        quality_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.quality_combo = QtWidgets.QComboBox()
        self.quality_combo.addItems(['Low', 'Medium', 'High', 'Very High'])
        self.quality_combo.setCurrentText(current_quality)
        self.quality_combo.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        device_label = QtWidgets.QLabel('Bộ xử lý ảnh:')
        device_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.device_combo = QtWidgets.QComboBox()
        self.device_combo.addItems(['cuda', 'cpu'])
        if 'cuda' in str(current_device).lower():
            self.device_combo.setCurrentText('cuda')
        else:  # inserted
            self.device_combo.setCurrentText('cpu')
        self.device_combo.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        thumbnail_display_count_label = QtWidgets.QLabel('Số lượng ảnh hiển thị khi chạy Hàng Loạt:')
        thumbnail_display_count_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.thumbnail_display_count_combo = QtWidgets.QComboBox()
        self.thumbnail_display_count_combo.addItems(['All', '1', '2', '3', '4', '5'])
        self.thumbnail_display_count_combo.setCurrentText(current_thumbnail_display_count)
        self.thumbnail_display_count_combo.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        background_enhance_label = QtWidgets.QLabel('Cải thiện nền:')
        background_enhance_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.background_enhance_checkbox = QtWidgets.QCheckBox()
        self.background_enhance_checkbox.setChecked(current_background_enhance)
        self.background_enhance_checkbox.setStyleSheet('QCheckBox { color: black; background-color: yellow; font: bold 18px; } QCheckBox::indicator { width: 20px; height: 20px; }')
        face_upsample_label = QtWidgets.QLabel('Cải thiện gương mặt:')
        face_upsample_label.setStyleSheet('color: red; background-color: yellow; font: bold 18px;')
        self.face_upsample_checkbox = QtWidgets.QCheckBox()
        self.face_upsample_checkbox.setChecked(current_face_upsample)
        self.face_upsample_checkbox.setStyleSheet('QCheckBox { color: black; background-color: yellow; font: bold 18px; } QCheckBox::indicator { width: 20px; height: 20px; }')
        eye_dist_label = QtWidgets.QLabel('Eye Distance Threshold:')
        eye_dist_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.eye_dist_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.eye_dist_slider.setRange(1, 500)
        self.eye_dist_slider.setValue(current_eye_dist_threshold)
        self.eye_dist_slider.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.eye_dist_display = QtWidgets.QLabel(str(current_eye_dist_threshold))
        self.eye_dist_display.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        self.eye_dist_display.setFixedWidth(50)
        self.eye_dist_slider.valueChanged.connect(lambda value: self.eye_dist_display.setText(str(value)))
        watermark_label = QtWidgets.QLabel('Thêm Watermark:')
        watermark_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.watermark_checkbox = QtWidgets.QCheckBox()
        self.watermark_checkbox.setChecked(current_watermark_enabled)
        self.watermark_checkbox.setStyleSheet('QCheckBox { color: black; background-color: yellow; font: bold 18px; } QCheckBox::indicator { width: 20px; height: 20px; }')
        watermark_text_label = QtWidgets.QLabel('Nội dung Watermark:')
        watermark_text_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.watermark_text_input = QtWidgets.QLineEdit()
        self.watermark_text_input.setText(current_watermark_text)
        self.watermark_text_input.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        watermark_positions_label = QtWidgets.QLabel('Vị trí Watermark:')
        watermark_positions_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.watermark_positions_list = QtWidgets.QListWidget()
        self.watermark_positions_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.watermark_positions_list.addItems(['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right', 'Center'])
        for i in range(self.watermark_positions_list.count()):
            item = self.watermark_positions_list.item(i)
            if item.text() in current_watermark_positions:
                item.setSelected(True)
        self.watermark_positions_list.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        font_style_label = QtWidgets.QLabel('Font Style:')
        font_style_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.font_combo = QtWidgets.QFontComboBox()
        self.font_combo.setCurrentFont(QtGui.QFont(current_font_family))
        self.font_combo.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        text_color_label = QtWidgets.QLabel('Text Color:')
        text_color_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.text_color_button = QtWidgets.QPushButton('Select Color')
        self.text_color_button.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        self.text_color_button.clicked.connect(self.select_text_color)
        self.text_color = QtGui.QColor(current_text_color)
        self.text_color_button.setStyleSheet(f'background-color: {current_text_color}; color: black; font: bold 18px;')
        size_ratio_label = QtWidgets.QLabel('Watermark Size Ratio:')
        size_ratio_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        self.size_ratio_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_ratio_slider.setRange(10, 200)
        self.size_ratio_slider.setValue(current_size_ratio)
        self.size_ratio_slider.setStyleSheet('\n            QSlider::groove:horizontal {\n                background: #333333;\n                height: 10px;\n            }\n            QSlider::handle:horizontal {\n                background: #FFFFFF;\n                width: 20px;\n                margin: -5px 0;\n            }\n        ')
        self.size_ratio_display = QtWidgets.QLabel(f'{current_size_ratio}0%')
        self.size_ratio_display.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        self.size_ratio_display.setFixedWidth(50)
        self.size_ratio_slider.valueChanged.connect(lambda value: self.size_ratio_display.setText(f'{value}%'))
        offset_label = QtWidgets.QLabel('Watermark Offset:')
        offset_label.setStyleSheet('color: red; background-color: yellow; font: bold 20px;')
        offset_x_label = QtWidgets.QLabel('X Offset:')
        offset_x_label.setStyleSheet('color: red; background-color: yellow; font: bold 18px;')
        self.offset_x_spinbox = QtWidgets.QSpinBox()
        self.offset_x_spinbox.setRange((-1000), 1000)
        self.offset_x_spinbox.setValue(current_offset_x)
        self.offset_x_spinbox.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        offset_y_label = QtWidgets.QLabel('Y Offset:')
        offset_y_label.setStyleSheet('color: red; background-color: yellow; font: bold 18px;')
        self.offset_y_spinbox = QtWidgets.QSpinBox()
        self.offset_y_spinbox.setRange((-1000), 1000)
        self.offset_y_spinbox.setValue(current_offset_y)
        self.offset_y_spinbox.setStyleSheet('color: black; background-color: yellow; font: bold 18px;')
        offset_layout = QtWidgets.QHBoxLayout()
        offset_layout.addWidget(offset_x_label)
        offset_layout.addWidget(self.offset_x_spinbox)
        offset_layout.addWidget(offset_y_label)
        offset_layout.addWidget(self.offset_y_spinbox)
        ok_button = QtWidgets.QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet('color: black; background-color: white; font: bold 18px;')
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet('color: black; background-color: white; font: bold 18px;')
        layout.addWidget(format_label)
        layout.addWidget(self.format_combo)
        layout.addWidget(quality_label)
        layout.addWidget(self.quality_combo)
        layout.addWidget(device_label)
        layout.addWidget(self.device_combo)
        layout.addWidget(thumbnail_display_count_label)
        layout.addWidget(self.thumbnail_display_count_combo)
        layout.addWidget(background_enhance_label)
        layout.addWidget(self.background_enhance_checkbox)
        layout.addWidget(face_upsample_label)
        layout.addWidget(self.face_upsample_checkbox)
        eye_dist_layout = QtWidgets.QHBoxLayout()
        eye_dist_layout.addWidget(eye_dist_label)
        eye_dist_layout.addWidget(self.eye_dist_slider)
        eye_dist_layout.addWidget(self.eye_dist_display)
        layout.addLayout(eye_dist_layout)
        layout.addWidget(watermark_label)
        layout.addWidget(self.watermark_checkbox)
        layout.addWidget(watermark_text_label)
        layout.addWidget(self.watermark_text_input)
        layout.addWidget(watermark_positions_label)
        layout.addWidget(self.watermark_positions_list)
        layout.addWidget(font_style_label)
        layout.addWidget(self.font_combo)
        layout.addWidget(text_color_label)
        layout.addWidget(self.text_color_button)
        layout.addWidget(size_ratio_label)
        size_ratio_layout = QtWidgets.QHBoxLayout()
        size_ratio_layout.addWidget(self.size_ratio_slider)
        size_ratio_layout.addWidget(self.size_ratio_display)
        layout.addLayout(size_ratio_layout)
        layout.addWidget(offset_label)
        layout.addLayout(offset_layout)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        self.setLayout(layout)

    def select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color
            self.text_color_button.setStyleSheet(f'background-color: {color.name()}0; color: black; font: bold 18px;')

    def get_options(self):
        selected_positions = [item.text() for item in self.watermark_positions_list.selectedItems()]
        return (self.format_combo.currentText(), self.quality_combo.currentText(), self.device_combo.currentText(), self.thumbnail_display_count_combo.currentText(), self.background_enhance_checkbox.isChecked(), self.face_upsample_checkbox.isChecked(), self.eye_dist_slider.value(), selected_positions, self.font_combo.currentFont().family(), self.text_color.name(), self.size_ratio_slider.value(), self.offset_x_spinbox.value(), self.offset_y_spinbox.value())

class ClickableMessageBox(QtWidgets.QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 600, 400)
        layout = QtWidgets.QVBoxLayout()
        text_browser = QtWidgets.QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(f'<p style=\'font-size: 18px; color: red;\'>{message}</p>')
        layout.addWidget(text_browser)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.setStyleSheet('\n            QPushButton {\n                background-color: yellow;\n                color: black;\n                font-size: 16px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #FFC300;\n            }\n        ')
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        self.setLayout(layout)

class MaskDrawer(QtWidgets.QMainWindow):
    mask_drawn = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, image_path, saved_mask=None):
        super().__init__()
        self.setWindowTitle('Mask Drawer')
        self.expand_size = 0
        self.image_path = image_path
        self.image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        self.mask = saved_mask if saved_mask is not None else np.zeros(self.image.shape[:2], dtype=np.uint8)
        self.brush_size = 15
        self.canvas = MaskCanvas(self.image, self.mask)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas.brush_size = self.brush_size
        brush_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        brush_size_slider.setMinimum(1)
        brush_size_slider.setMaximum(100)
        brush_size_slider.setValue(self.brush_size)
        brush_size_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        brush_size_slider.setTickInterval(5)
        brush_size_slider.valueChanged.connect(self.change_brush_size)
        brush_size_label = QtWidgets.QLabel('Brush Size')
        brush_size_label.setAlignment(QtCore.Qt.AlignCenter)
        save_button = QtWidgets.QPushButton('Save Mask')
        save_button.clicked.connect(self.save_mask)
        save_button.setStyleSheet('\n            QPushButton {\n                background-color: #FFFFFF;\n                color: black;\n                font: bold 18px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #FFC300;\n            }\n        ')
        clear_button = QtWidgets.QPushButton('Clear Mask')
        clear_button.clicked.connect(self.clear_mask)
        clear_button.setStyleSheet('\n            QPushButton {\n                background-color: red;\n                color: white;\n                font: bold 18px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #ff4d4d;\n            }\n        ')
        undo_button = QtWidgets.QPushButton('Undo')
        undo_button.clicked.connect(self.undo_mask)
        undo_button.setStyleSheet('\n            QPushButton {\n                background-color: #FF8C00;\n                color: white;\n                font: bold 18px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #FFA500;\n            }\n        ')
        invert_button = QtWidgets.QPushButton('Invert Mask')
        invert_button.clicked.connect(self.invert_mask)
        invert_button.setStyleSheet('\n            QPushButton {\n                background-color: #4682B4;\n                color: white;\n                font: bold 18px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #5A9BD4;\n            }\n        ')
        auto_mask_button = QtWidgets.QPushButton('Tạo Mask Tự Động')
        auto_mask_button.clicked.connect(self.create_facial_mask)
        auto_mask_button.setStyleSheet('\n            QPushButton {\n                background-color: #4682B4;\n                color: white;\n                font: bold 18px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #5A9BD4;\n            }\n        ')
        mode_toggle_button = QtWidgets.QPushButton('Toggle Brush/Eraser')
        mode_toggle_button.clicked.connect(self.toggle_mode)
        mode_toggle_button.setStyleSheet('\n            QPushButton {\n                background-color: #4682B4;\n                color: white;\n                font: bold 18px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #5A9BD4;\n            }\n        ')
        expand_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        expand_slider.setMinimum(0)
        expand_slider.setMaximum(150)
        expand_slider.setValue(self.expand_size)
        expand_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        expand_slider.setTickInterval(10)
        expand_slider.valueChanged.connect(self.change_expand_size)
        expand_label = QtWidgets.QLabel('Expand Size')
        expand_label.setAlignment(QtCore.Qt.AlignCenter)
        brush_size_layout = QtWidgets.QVBoxLayout()
        brush_size_layout.addWidget(brush_size_label)
        brush_size_layout.addWidget(brush_size_slider)
        brush_size_layout.addWidget(expand_label)
        brush_size_layout.addWidget(expand_slider)
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(undo_button)
        button_layout.addWidget(invert_button)
        button_layout.addWidget(auto_mask_button)
        button_layout.addWidget(mode_toggle_button)
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addLayout(brush_size_layout)
        controls_layout.addLayout(button_layout)
        controls_layout.addStretch()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(controls_layout)
        container = QtWidgets.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_display_image(self):
        display_image = self.image.copy()
        display_image[self.mask > 0] = [255, 0, 0]
        qimage = QtGui.QImage(display_image.data, display_image.shape[1], display_image.shape[0], display_image.strides[0], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.canvas.setPixmap(pixmap)

    def change_brush_size(self, value):
        self.brush_size = value
        self.canvas.brush_size = value

    def change_expand_size(self, value):
        self.expand_size = value

    def save_mask(self):
        resized_mask = cv2.resize(self.canvas.mask, (self.canvas.original_image.shape[1], self.canvas.original_image.shape[0]), interpolation=cv2.INTER_LINEAR)
        self.mask_drawn.emit(resized_mask)
        self.close()

    def clear_mask(self):
        self.canvas.clear_mask()
        self.mask = None
        self.saved_mask = None

    def undo_mask(self):
        self.canvas.undo_mask()

    def invert_mask(self):
        self.canvas.invert_mask()

    def toggle_mode(self):
        if self.canvas.mode == 'brush':
            self.canvas.mode = 'eraser'
            self.statusBar().showMessage('Mode: Eraser')
        else:  # inserted
            self.canvas.mode = 'brush'
            self.statusBar().showMessage('Mode: Brush')

    def create_facial_mask(self):
        temp_mask = cv2.resize(self.mask, (self.image.shape[1], self.image.shape[0]), interpolation=cv2.INTER_NEAREST)
        gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        rects = self.detector(gray, 1)
        for rect in rects:
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            features = {'mouth': shape[48:68], 'right_eye': shape[36:42], 'left_eye': shape[42:48], 'right_eyebrow': shape[17:22], 'left_eyebrow': shape[22:27], 'nose': shape[27:36]}
            for feature in features.values():
                hull = cv2.convexHull(feature)
                cv2.drawContours(temp_mask, [hull], (-1), 255, (-1))
        if self.expand_size > 0:
            kernel = np.ones((self.expand_size, self.expand_size), np.uint8)
            temp_mask = cv2.dilate(temp_mask, kernel, iterations=1)
        self.mask = cv2.resize(temp_mask, (self.canvas.resized_image.shape[1], self.canvas.resized_image.shape[0]), interpolation=cv2.INTER_NEAREST)
        self.canvas.mask = self.mask.copy()
        self.canvas.mask_history.append(self.canvas.mask.copy())
        self.canvas.update_display_image()

class MaskCanvas(QtWidgets.QLabel):
    def __init__(self, image, mask):
        super().__init__()
        self.original_image = image
        self.original_mask = mask
        self.drawing = False
        self.brush_size = 20
        self.mode = 'brush'
        self.resized_image, self.resize_factor = self.resize_image_to_height(image, 900)
        self.mask = cv2.resize(mask, (self.resized_image.shape[1], self.resized_image.shape[0]), interpolation=cv2.INTER_NEAREST)
        self.mask_history = [self.mask.copy()]
        self.update_offsets()
        self.dragging = False
        self.last_mouse_pos = None
        self.update_display_image()

    def resize_image_to_height(self, image, target_height=None):
        if target_height is None:
            target_height = self.height() - 100
        height, width = image.shape[:2]
        resize_factor = target_height / height
        new_width = int(width * resize_factor)
        resized_image = cv2.resize(image, (new_width, target_height), interpolation=cv2.INTER_LINEAR)
        return (resized_image, resize_factor)

    def update_offsets(self):
        """Cập nhật offset để căn chỉnh hình ảnh ở giữa canvas."""  # inserted
        self.image_offset_x = (self.width() - self.resized_image.shape[1]) // 2
        self.image_offset_y = (self.height() - self.resized_image.shape[0]) // 2

    def update_display_image(self):
        if self.mask.shape[:2]!= self.resized_image.shape[:2]:
            self.mask = cv2.resize(self.mask, (self.resized_image.shape[1], self.resized_image.shape[0]), interpolation=cv2.INTER_NEAREST)
        display_image = self.resized_image.copy()
        display_image[self.mask > 0] = [255, 0, 0]
        qimage = QtGui.QImage(display_image.data, display_image.shape[1], display_image.shape[0], display_image.strides[0], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        offset_pixmap = QtGui.QPixmap(self.size())
        offset_pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(offset_pixmap)
        painter.drawPixmap(self.image_offset_x, self.image_offset_y, pixmap)
        painter.end()
        self.setPixmap(offset_pixmap)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            if not np.array_equal(self.mask, self.mask_history[(-1)]):
                self.mask_history.append(self.mask.copy())
            self.draw(event.pos())
        else:  # inserted
            if event.button() == QtCore.Qt.RightButton:
                self.dragging = True
                self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.draw(event.pos())
        else:  # inserted
            if self.dragging:
                dx = event.pos().x() - self.last_mouse_pos.x()
                dy = event.pos().y() - self.last_mouse_pos.y()
                self.image_offset_x += dx
                self.image_offset_y += dy
                self.last_mouse_pos = event.pos()
                self.update_display_image()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            if not np.array_equal(self.mask, self.mask_history[(-1)]):
                self.mask_history.append(self.mask.copy())
        else:  # inserted
            if event.button() == QtCore.Qt.RightButton:
                self.dragging = False
                self.last_mouse_pos = None

    def draw(self, pos):
        x = pos.x() - self.image_offset_x
        y = pos.y() - self.image_offset_y
        if 0 <= x < self.mask.shape[1] and 0 <= y < self.mask.shape[0]:
            if self.mode == 'brush':
                cv2.circle(self.mask, (x, y), self.brush_size, 255, (-1))
            else:  # inserted
                if self.mode == 'eraser':
                    cv2.circle(self.mask, (x, y), self.brush_size, 0, (-1))
            self.update_display_image()

    def clear_mask(self):
        self.mask[:] = 0
        self.mask_history.append(self.mask.copy())
        self.update_display_image()

    def undo_mask(self):
        if len(self.mask_history) > 1:
            self.mask_history.pop()
            self.mask = self.mask_history[(-1)].copy()
            self.update_display_image()

    def invert_mask(self):
        self.mask = cv2.bitwise_not(self.mask)
        self.mask_history.append(self.mask.copy())
        self.update_display_image()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.resize_factor += delta * 0.1
        self.resize_factor = max(0.1, self.resize_factor)
        self.resize_images_by_zoom_factor()

    def resize_images_by_zoom_factor(self):
        new_size = (int(self.original_image.shape[1] * self.resize_factor), int(self.original_image.shape[0] * self.resize_factor))
        self.resized_image = cv2.resize(self.original_image, new_size, interpolation=cv2.INTER_LINEAR)
        self.mask = cv2.resize(self.mask, new_size, interpolation=cv2.INTER_NEAREST)
        self.update_offsets()
        self.update_display_image()

    def resizeEvent(self, event):
        """This method is called whenever the widget is resized."""  # inserted
        self.update_offsets()
        self.update_display_image()
        super().resizeEvent(event)
if __name__ == '__main__':
    import sys
    import os
    import psutil
    from PyQt5 import QtWidgets
    from PyQt5.QtCore import QSettings
    from PyQt5.QtWidgets import QMessageBox

    def check_and_set_single_instance(settings: QSettings):
        """\n        Hàm này kiểm tra xem ứng dụng đã được đánh dấu đang chạy hay chưa.\n        Nếu \'app_is_running\' = True, thì kiểm tra xem process ID (app_pid) có còn sống hay không.\n          - Nếu process còn sống => thoát (đang có một instance khác).\n          - Nếu process không tồn tại => reset cờ, cho chạy tiếp.\n        Sau đó gán process ID hiện tại vào settings để lần sau còn kiểm tra.\n        """  # inserted
        current_pid = os.getpid()
        is_app_running = settings.value('app_is_running', False, type=bool)
        stored_pid = settings.value('app_pid', 0, type=int)
        if is_app_running:
            if stored_pid!= 0 and psutil.pid_exists(stored_pid):
                QMessageBox.warning(None, 'Cảnh báo', 'Ứng dụng đã được mở.')
                sys.exit(0)
            else:  # inserted
                settings.setValue('app_is_running', False)
                settings.setValue('app_pid', 0)
        settings.setValue('app_is_running', True)
        settings.setValue('app_pid', current_pid)
    try:
        settings = QSettings('sys_config_1289', 'srv_manager_323')
        check_and_set_single_instance(settings)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        app = QtWidgets.QApplication([])
        app.setStyleSheet('\n            QMessageBox QLabel {\n                color: #ffffff;            /* Màu chữ */\n                font-size: 24px;           /* Kích thước chữ */\n            }\n            QMessageBox {\n                background-color: #ffffff; /* Màu nền */\n            }\n            QMessageBox QPushButton {\n                color: white;              /* Màu chữ của nút bấm */\n                background-color: #673147; /* Màu nền của nút bấm */\n                font-size: 14px;           /* Kích thước chữ của nút bấm */\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QMessageBox QPushButton:hover {\n                background-color: #7d3c98; /* Màu nền khi rê chuột lên nút bấm */\n            }\n        ')
        app.setStyleSheet('\n            /* Các style tương tự... */\n\n            QInputDialog QLabel {\n                color: #ffffff;            \n                font-size: 24px;           \n            }\n            QInputDialog QLineEdit {\n                color: #ffffff;            \n                background-color: #333333; \n            }\n            QInputDialog {\n                background-color: #000000; \n            }\n            QInputDialog QPushButton {\n                color: white;\n                background-color: #673147;\n                font-size: 14px;\n                padding: 5px;\n                border-radius: 5px;\n            }\n            QInputDialog QPushButton:hover {\n                background-color: #7d3c98;\n            }\n        ')
        window = RetouchPixelApp()
        window.show()
        code = app.exec_()
        settings.setValue('app_is_running', False)
        settings.setValue('app_pid', 0)
        sys.exit(code)
    except Exception as e:
        settings.setValue('app_is_running', False)
        settings.setValue('app_pid', 0)
        print(f'Lỗi không bắt được: {e}0')
        sys.exit(1)