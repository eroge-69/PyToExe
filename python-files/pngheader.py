import requests
import base64
import os
import subprocess
import tempfile
import re
from urllib.parse import urljoin
import time
from tqdm import tqdm

class HLSConverter:
    def __init__(self, headers=None):
        self.temp_dir = tempfile.mkdtemp()
        self.init_segment_data = None
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://hh4d.site/'
        }
        
    def set_referer(self, referer):
        self.headers['Referer'] = referer

    def parse_m3u8(self, m3u8_content, base_url=None):
        segments = []
        init_segment = None
        
        lines = m3u8_content.strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.startswith('#EXT-X-MAP'):
                uri_match = re.search(r'URI="([^"]+)"', line)
                if uri_match:
                    init_segment = uri_match.group(1)
                    if base_url and not init_segment.startswith(('http://', 'https://', 'data:')):
                        init_segment = urljoin(base_url, init_segment)
            
            elif line.startswith('#EXTINF'):
                if i + 1 < len(lines) and not lines[i + 1].startswith('#'):
                    segment_url = lines[i + 1].strip()
                    if base_url and not segment_url.startswith(('http://', 'https://')):
                        segment_url = urljoin(base_url, segment_url)
                    
                    duration_match = re.search(r'#EXTINF:([\d.]+)', line)
                    duration = float(duration_match.group(1)) if duration_match else 0
                    
                    segments.append({
                        'url': segment_url,
                        'duration': duration,
                        'index': len(segments)
                    })
        
        return init_segment, segments

    def decode_init_segment(self, init_segment):
        if init_segment.startswith('data:'):
            try:
                base64_data = init_segment.split('base64,')[1]
                self.init_segment_data = base64.b64decode(base64_data)
                return self.init_segment_data
            except Exception as e:
                return None

    def analyze_segment(self, data, segment_index):
        """Phân tích segment để hiểu cấu trúc"""
        analysis = {
            'total_size': len(data),
            'has_png_header': data.startswith(b'\x89PNG'),
            'has_mp4_boxes': False,
            'mp4_boxes_found': [],
            'has_png_wrapper': False
        }
        
        # Kiểm tra PNG wrapper
        if data.startswith(b'\x89PNG'):
            analysis['has_png_wrapper'] = True
            iend_pos = data.find(b'IEND\xaeB`\x82')
            if iend_pos != -1:
                analysis['png_data_size'] = iend_pos + 8
                analysis['video_data_size'] = len(data) - analysis['png_data_size']
        
        # Tìm MP4 boxes
        mp4_boxes = [b'ftyp', b'moof', b'mdat', b'free', b'skip', b'sidx']
        for box in mp4_boxes:
            if box in data:
                analysis['has_mp4_boxes'] = True
                analysis['mp4_boxes_found'].append(box.decode())
        
        return analysis

    def download_segment_with_retry(self, url, segment_index, total_segments, max_retries=1000):
        """Download segment với retry 1000 lần"""
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                response = requests.get(url, headers=self.headers, timeout=60)
                response.raise_for_status()
                
                raw_data = response.content
                
                if len(raw_data) < 500:
                    retry_count += 1
                    time.sleep(2)
                    continue
                
                # Lưu segment
                segment_file = os.path.join(self.temp_dir, f"raw_segment_{segment_index:04d}.bin")
                with open(segment_file, 'wb') as f:
                    f.write(raw_data)
                
                return {
                    'raw_data': raw_data,
                    'file_path': segment_file,
                    'duration': 0,
                    'index': segment_index,
                }
                
            except requests.exceptions.RequestException as e:
                last_error = e
                retry_count += 1
                wait_time = min(2 * retry_count, 30)
                time.sleep(wait_time)
                
            except Exception as e:
                last_error = e
                retry_count += 1
                time.sleep(3)
        
        return None

    def download_all_segments_first(self, segments):
        """Download tất cả segments trước với retry liên tục"""
        print(f"Downloading {len(segments)} segments...")
        
        downloaded_segments = []
        failed_segments = []
        
        # Sử dụng tqdm để hiển thị progress bar
        with tqdm(total=len(segments), desc="Downloading segments", unit="segment") as pbar:
            for i, segment in enumerate(segments):
                segment_info = self.download_segment_with_retry(
                    segment['url'], 
                    i, 
                    len(segments),
                    max_retries=1000
                )
                
                if segment_info:
                    segment_info['duration'] = segment['duration']
                    downloaded_segments.append(segment_info)
                else:
                    failed_segments.append(i + 1)
                
                # Cập nhật progress bar
                pbar.update(1)
                pbar.set_postfix({
                    'success': len(downloaded_segments),
                    'failed': len(failed_segments)
                })
        
        print(f"Download completed: {len(downloaded_segments)}/{len(segments)} segments")
        
        if failed_segments:
            print(f"Failed segments: {len(failed_segments)}")
        
        return downloaded_segments

    def evaluate_mp4_candidate(self, data, start_pos):
        """Đánh giá candidate MP4 data"""
        if start_pos < 0 or start_pos >= len(data) - 8:
            return 0
        
        score = 0
        
        try:
            # Kiểm tra box size hợp lệ
            box_size = int.from_bytes(data[start_pos:start_pos+4], byteorder='big')
            box_type = data[start_pos+4:start_pos+8]
            
            if 4 <= box_size <= min(1000000, len(data) - start_pos):
                score += 10
                
                # Điểm cho box type quan trọng
                if box_type in [b'ftyp', b'moof']:
                    score += 20
                elif box_type in [b'mdat', b'sidx']:
                    score += 15
                elif box_type in [b'free', b'skip']:
                    score += 5
            
            # Kiểm tra có multiple boxes
            next_pos = start_pos + box_size
            if next_pos < len(data) - 8:
                next_box_size = int.from_bytes(data[next_pos:next_pos+4], byteorder='big')
                next_box_type = data[next_pos+4:next_pos+8]
                
                if 4 <= next_box_size <= len(data) - next_pos:
                    score += 10
        
        except:
            pass
        
        return score

    def extract_mp4_from_png_container(self, raw_data, segment_index):
        """Trích xuất MP4 data từ container PNG"""
        # Tìm tất cả vị trí có thể bắt đầu MP4 data
        mp4_signatures = [
            (b'ftyp', 0),  # File type box
            (b'moof', 0),  # Movie fragment box  
            (b'mdat', 0),  # Media data box
            (b'free', 0),  # Free space box
            (b'skip', 0),  # Skip box
            (b'\x00\x00\x00', 4),  # Potential box size
        ]
        
        best_candidate = None
        best_score = 0
        
        for signature, offset in mp4_signatures:
            pos = 0
            while pos < len(raw_data) - 20:
                found_pos = raw_data.find(signature, pos)
                if found_pos == -1:
                    break
                    
                # Tính điểm cho candidate này
                candidate_pos = found_pos - offset
                score = self.evaluate_mp4_candidate(raw_data, candidate_pos)
                if score > best_score:
                    best_score = score
                    best_candidate = candidate_pos
                
                pos = found_pos + 1
        
        if best_candidate is not None and best_candidate > 0:
            video_data = raw_data[best_candidate:]
            return video_data
        
        # Phương pháp cuối: sử dụng ffmpeg
        return self.fix_segment_with_ffmpeg(raw_data, segment_index)

    def find_mp4_data_in_segment(self, data, segment_index):
        """Tìm MP4 data trong segment"""
        # Tìm box size và type pattern
        pos = 0
        while pos < len(data) - 8:
            if pos + 8 > len(data):
                break
                
            # Đọc box size (4 bytes big-endian)
            try:
                box_size = int.from_bytes(data[pos:pos+4], byteorder='big')
                box_type = data[pos+4:pos+8]
                
                # Validate box
                if (4 <= box_size <= len(data) - pos and 
                    box_type in [b'ftyp', b'moof', b'mdat', b'free', b'skip', b'sidx']):
                    
                    # Lấy data từ box này trở đi
                    video_data = data[pos:]
                    
                    if self.validate_mp4_structure(video_data):
                        return video_data
                    else:
                        # Thử fix structure
                        fixed_data = self.fix_mp4_structure(video_data, segment_index)
                        if fixed_data:
                            return fixed_data
            except:
                pass
            
            pos += 1
        
        # Nếu không tìm thấy box hợp lệ, trả về data gốc
        return data

    def fix_mp4_structure(self, data, segment_index):
        """Cố gắng fix MP4 structure"""
        # Thử thêm missing moov/mdat headers nếu cần
        if data.startswith(b'\x00\x00\x00'):
            # Có thể đã là MP4 data hợp lệ
            return data
        
        # Thử tạo minimal MP4 structure
        if len(data) > 1000:
            # Giả sử đây là mdat data, thêm box header
            try:
                mdat_size = len(data) + 8
                mdat_header = mdat_size.to_bytes(4, byteorder='big') + b'mdat'
                return mdat_header + data
            except:
                pass
        
        return None

    def clean_segment_data(self, raw_data, segment_index):
        """Loại bỏ PNG header và đảm bảo MP4 structure - Phiên bản cải tiến"""
        if len(raw_data) < 8:
            return raw_data
        
        # Phương pháp 1: Tìm và loại bỏ PNG header hoàn toàn
        png_signature = b'\x89PNG'
        if raw_data.startswith(png_signature):
            # Tìm IEND chunk - kết thúc của PNG
            iend_pos = raw_data.find(b'IEND\xaeB`\x82')
            if iend_pos != -1:
                video_start = iend_pos + 8
                video_data = raw_data[video_start:]
                
                if len(video_data) > 1000:
                    # Kiểm tra xem video data có bắt đầu bằng MP4 boxes không
                    if self.validate_mp4_structure(video_data):
                        return video_data
                    else:
                        # Tìm MP4 boxes trong video data
                        return self.find_mp4_data_in_segment(video_data, segment_index)
            
            # Nếu không tìm thấy IEND, thử tìm trực tiếp MP4 data
            return self.extract_mp4_from_png_container(raw_data, segment_index)
        
        # Phương pháp 2: Tìm trực tiếp MP4 boxes
        return self.find_mp4_data_in_segment(raw_data, segment_index)

    def validate_mp4_structure(self, data):
        """Validate cơ bản MP4 structure"""
        if len(data) < 8:
            return False
        
        mp4_signatures = [b'ftyp', b'moof', b'mdat', b'free', b'skip']
        for sig in mp4_signatures:
            if sig in data[:100]:
                return True
        
        if data[0] == 0x47 and len(data) >= 188 and data[188] == 0x47:
            return True
            
        return False

    def fix_segment_with_ffmpeg(self, raw_data, segment_index):
        """Sử dụng FFmpeg để fix segment"""
        try:
            raw_file = os.path.join(self.temp_dir, f"raw_seg_{segment_index}.bin")
            with open(raw_file, 'wb') as f:
                f.write(raw_data)
            
            fixed_file = os.path.join(self.temp_dir, f"fixed_seg_{segment_index}.m4s")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', raw_file,
                '-c', 'copy',
                '-f', 'mp4',
                fixed_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if os.path.exists(fixed_file) and os.path.getsize(fixed_file) > 1000:
                with open(fixed_file, 'rb') as f:
                    fixed_data = f.read()
                return fixed_data
            else:
                return self.extract_video_data_manual(raw_data, segment_index)
                
        except Exception as e:
            return self.extract_video_data_manual(raw_data, segment_index)

    def extract_video_data_manual(self, raw_data, segment_index):
        """Extract video data thủ công"""
        patterns = [
            b'\x00\x00\x00',
            b'\x47',
            b'\x00\x00\x01',
        ]
        
        for pattern in patterns:
            pos = raw_data.find(pattern)
            if pos != -1 and pos < len(raw_data) - 100:
                video_data = raw_data[pos:]
                if self.validate_mp4_structure(video_data) or len(video_data) > 1000:
                    return video_data
        
        return raw_data

    def process_all_segments(self, downloaded_segments):
        """Xử lý tất cả segments đã download"""
        print("Processing segments...")
        
        processed_segments = []
        
        # Sử dụng tqdm để hiển thị progress bar
        with tqdm(total=len(downloaded_segments), desc="Processing segments", unit="segment") as pbar:
            for i, segment_info in enumerate(downloaded_segments):
                # Đọc raw data từ file
                with open(segment_info['file_path'], 'rb') as f:
                    raw_data = f.read()
                
                # Clean segment data
                cleaned_data = self.clean_segment_data(raw_data, segment_info['index'])
                
                if cleaned_data:
                    processed_segments.append({
                        'data': cleaned_data,
                        'duration': segment_info['duration'],
                        'index': segment_info['index']
                    })
                else:
                    # Sử dụng raw data nếu không clean được
                    processed_segments.append({
                        'data': raw_data,
                        'duration': segment_info['duration'],
                        'index': segment_info['index']
                    })
                
                # Cập nhật progress bar
                pbar.update(1)
        
        print(f"Processing completed: {len(processed_segments)} segments ready")
        return processed_segments

    def create_final_mp4(self, processed_segments, output_file):
        """Tạo MP4 cuối cùng từ tất cả segments đã xử lý"""
        # Tạo file chứa tất cả segments
        all_segments_file = os.path.join(self.temp_dir, "all_segments.bin")
        
        total_size = 0
        with open(all_segments_file, 'wb') as f:
            # Viết init segment
            if self.init_segment_data:
                f.write(self.init_segment_data)
                total_size += len(self.init_segment_data)
            
            # Viết tất cả media segments
            for segment_info in processed_segments:
                f.write(segment_info['data'])
                total_size += len(segment_info['data'])
        
        # Sử dụng FFmpeg để tạo MP4 chuẩn
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', all_segments_file,
                '-c', 'copy',
                '-movflags', '+faststart',
                '-f', 'mp4',
                output_file
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            
            if self.validate_output_file(output_file):
                return True
            else:
                return self.create_mp4_alternative(processed_segments, output_file)
                
        except subprocess.CalledProcessError as e:
            return self.create_mp4_alternative(processed_segments, output_file)

    def create_mp4_alternative(self, processed_segments, output_file):
        """Phương pháp thay thế để tạo MP4"""
        try:
            # Tạo từng file MP4 riêng rồi nối
            individual_files = []
            
            # Tạo init file
            init_file = os.path.join(self.temp_dir, "init.mp4")
            with open(init_file, 'wb') as f:
                f.write(self.init_segment_data)
            individual_files.append(init_file)
            
            # Tạo file cho từng segment
            for i, segment_info in enumerate(processed_segments):
                segment_file = os.path.join(self.temp_dir, f"seg_{i:04d}.m4s")
                with open(segment_file, 'wb') as f:
                    f.write(segment_info['data'])
                individual_files.append(segment_file)
            
            # Tạo concat list
            concat_list = os.path.join(self.temp_dir, "concat_list.txt")
            with open(concat_list, 'w') as f:
                for file_path in individual_files:
                    f.write(f"file '{os.path.abspath(file_path)}'\n")
            
            # Nối với FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                '-movflags', '+faststart',
                output_file
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            return True
            
        except Exception as e:
            return False

    def validate_output_file(self, output_file):
        """Validate file output cuối cùng"""
        if not os.path.exists(output_file):
            return False
        
        file_size = os.path.getsize(output_file)
        
        if file_size < 100000:
            return False
        
        return True

    def process_hls_stream(self, m3u8_content, base_url=None, output_file="output.mp4"):
        """Xử lý toàn bộ HLS stream"""
        init_segment, segments = self.parse_m3u8(m3u8_content, base_url)
        
        if not init_segment:
            return False
        
        if not self.decode_init_segment(init_segment):
            return False
        
        # BƯỚC 1: Download tất cả segments trước
        downloaded_segments = self.download_all_segments_first(segments)
        
        if not downloaded_segments:
            return False
        
        # BƯỚC 2: Xử lý tất cả segments đã download
        processed_segments = self.process_all_segments(downloaded_segments)
        
        if not processed_segments:
            return False
        
        # BƯỚC 3: Tạo MP4 cuối cùng
        success = self.create_final_mp4(processed_segments, output_file)
        
        return success

    def process_from_url(self, m3u8_url, output_file="output.mp4"):
        """Process từ URL"""
        # Luôn sử dụng referer mặc định là https://hh4d.site/
        self.set_referer('https://hh4d.site/')
            
        try:
            response = requests.get(m3u8_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            base_url = '/'.join(m3u8_url.split('/')[:-1]) + '/' if '/' in m3u8_url else None
            return self.process_hls_stream(response.text, base_url, output_file)
        except Exception as e:
            return False

    def cleanup(self):
        """Dọn dẹp temp files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

def ensure_downloads_directory():
    """Đảm bảo thư mục Downloads tồn tại"""
    downloads_path = "D:/Downloads"
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    return downloads_path

def check_file_exists(output_file):
    """Kiểm tra file đã tồn tại chưa"""
    if os.path.exists(output_file):
        print(f"❌ File {output_file} đã tồn tại!")
        return True
    return False

def get_user_input():
    """Lấy thông tin từ người dùng"""
    print("\n" + "="*50)
    print("🎬 HLS Video Downloader")
    print("="*50)
    
    # Nhập M3U8 URL
    m3u8_url = input("🔗 Nhập M3U8 URL: ").strip()
    if not m3u8_url:
        print("❌ URL không được để trống!")
        return None, None
    
    # Nhập và kiểm tra tên file output
    downloads_dir = ensure_downloads_directory()
    
    while True:
        output_filename = input("💾 Nhập tên file output (không cần .mp4): ").strip()
        if not output_filename:
            output_filename = "downloaded_video"
        
        # Thêm extension nếu chưa có
        if not output_filename.lower().endswith('.mp4'):
            output_filename += '.mp4'
        
        # Tạo đường dẫn đầy đủ
        output_file = os.path.join(downloads_dir, output_filename)
        
        # Kiểm tra file đã tồn tại chưa
        if not check_file_exists(output_file):
            break
        else:
            print("🔄 Vui lòng nhập tên file khác!")
    
    return m3u8_url, output_file

def main():
    """Chương trình chính với vòng lặp vĩnh viễn"""
    print("🚀 Khởi động HLS Video Downloader...")
    print("🔗 Referer mặc định: https://hh4d.site/")
    
    while True:
        try:
            # Lấy thông tin từ người dùng
            m3u8_url, output_file = get_user_input()
            
            if m3u8_url is None:
                continue
            
            # Hiển thị thông tin
            print(f"\n📋 Thông tin download:")
            print(f"   🔗 URL: {m3u8_url}")
            print(f"   💾 Output: {output_file}")
            
            # Bắt đầu download ngay lập tức
            print("\n🚀 Bắt đầu download...")
            
            # Tạo converter và xử lý
            converter = HLSConverter()
            
            try:
                success = converter.process_from_url(
                    m3u8_url=m3u8_url,
                    output_file=output_file
                )
                
                if success:
                    final_size = os.path.getsize(output_file)
                    print(f"Final output size: {final_size / (1024*1024):.1f} MB")
                    print(f"File: {output_file} ({final_size / (1024*1024):.1f} MB)")
                else:
                    print("💥 Download thất bại!")
                
                # Tự động quay lại menu chính để download tiếp
                print("\n" + "="*50)
                print("🔄 Quay lại menu chính...")
                print("="*50)
            
            finally:
                converter.cleanup()
                
        except KeyboardInterrupt:
            print("\n\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")
            print("🔄 Thử lại...")

if __name__ == "__main__":
    main()