import cv2
import numpy as np
import psutil
import time
import threading
from PIL import ImageGrab
import win32gui
import win32process
import math
import re

class AggressiveNSFWDetector:
    def __init__(self, check_interval=0.5, sensitivity='medium'):
        """
        Aggressive NSFW Detection System with Website URL checking
        """
        self.check_interval = check_interval
        self.sensitivity = sensitivity
        self.monitoring = False
        self.monitor_thread = None
        
        # Much more aggressive thresholds
        self.thresholds = {
            'low': {'total_score': 35, 'skin_threshold': 25, 'explicit_threshold': 20},
            'medium': {'total_score': 25, 'skin_threshold': 18, 'explicit_threshold': 15},
            'high': {'total_score': 15, 'skin_threshold': 12, 'explicit_threshold': 10}
        }
        
        self.excluded_processes = {
            'dwm.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe', 
            'smss.exe', 'wininit.exe', 'services.exe', 'lsass.exe',
            'svchost.exe', 'taskhost.exe', 'python.exe', 'pythonw.exe',
            'cmd.exe', 'powershell.exe', 'conhost.exe', 'taskmgr.exe'
        }
        
        # Known NSFW websites and patterns
        self.nsfw_domains = {
            'pornhub.com', 'xvideos.com', 'xnxx.com', 'redtube.com',
            'youporn.com', 'tube8.com', 'spankbang.com', 'xhamster.com',
            'brazzers.com', 'bangbros.com', 'realitykings.com', 'naughtyamerica.com',
            'chaturbate.com', 'cam4.com', 'bongacams.com', 'stripchat.com',
            'onlyfans.com', 'fansly.com', 'manyvids.com', 'clips4sale.com',
            'reddit.com/r/nsfw', 'reddit.com/r/gonewild', 'reddit.com/r/porn',
            'tumblr.com', 'twitter.com', 'instagram.com', # These need content checking
            'xfree.com', 'ficfab.com'  
        }
        
        # NSFW URL patterns
        self.nsfw_patterns = [
            r'porn', r'xxx', r'sex', r'nude', r'naked', r'adult',
            r'erotic', r'fetish', r'bdsm', r'milf', r'teen',
            r'amateur', r'webcam', r'cam', r'live.*sex',
            r'escort', r'hookup', r'dating.*adult'
        ]
        
        # Browser processes to monitor
        self.browser_processes = {
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe',
            'brave.exe', 'iexplore.exe', 'safari.exe', 'vivaldi.exe'
        }
        
        self.last_detection_time = 0
        self.detection_cooldown = 1.5
        self.consecutive_detections = 0
        
    def is_youtube_content(self, url, window_title=""):
        """Check if the current content is YouTube"""
        text_to_check = f"{url or ''} {window_title}".lower()
        
        # Check for YouTube domains and patterns
        youtube_indicators = [
            'youtube.com',
            'youtu.be',
            'youtube',
            'm.youtube.com',
            'www.youtube.com'
        ]
        
        for indicator in youtube_indicators:
            if indicator in text_to_check:
                return True
        
        return False
        
    def get_browser_url(self, process_name, window_title):
        """Extract URL from browser window title or try other methods"""
        url = None
        
        # Try to extract URL from window title (works for many browsers)
        url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+',  # Standard URL pattern
            r'www\.[^\s<>"{}|\\^`\[\]]+',      # www. pattern
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, window_title, re.IGNORECASE)
            if matches:
                url = matches[0]
                if not url.startswith('http'):
                    url = 'https://' + url
                break
        
        # For Chrome, try to get URL from title format "Page Title - Google Chrome"
        if not url and 'chrome' in process_name.lower():
            if ' - Google Chrome' in window_title:
                # Sometimes the URL is in the title before the browser name
                parts = window_title.replace(' - Google Chrome', '').strip()
                if any(domain in parts.lower() for domain in self.nsfw_domains):
                    url = parts
        
        return url
    
    def is_nsfw_website(self, url, window_title=""):
        """Check if URL or window title indicates NSFW content"""
        if not url and not window_title:
            return False, "No URL or title to check"
        
        text_to_check = f"{url or ''} {window_title}".lower()
        
        # Check against known NSFW domains
        for domain in self.nsfw_domains:
            if domain in text_to_check:
                return True, f"Blocked domain: {domain}"
        
        # Check against NSFW patterns
        for pattern in self.nsfw_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True, f"Blocked pattern: {pattern}"
        
        # Special checks for social media platforms
        if any(social in text_to_check for social in ['reddit.com', 'twitter.com', 'instagram.com']):
            nsfw_social_patterns = [
                r'/r/nsfw', r'/r/gonewild', r'/r/porn', r'/r/sex',
                r'#nsfw', r'#porn', r'#nude', r'#sex'
            ]
            for pattern in nsfw_social_patterns:
                if re.search(pattern, text_to_check, re.IGNORECASE):
                    return True, f"NSFW social media content: {pattern}"
        
        return False, "Clean content"
    
    def get_active_window(self):
        """Get the currently active window with enhanced browser detection"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                process_name = process.name()
                window_title = win32gui.GetWindowText(hwnd)
                
                if process_name.lower() not in self.excluded_processes:
                    window_info = {
                        'hwnd': hwnd,
                        'pid': pid,
                        'process_name': process_name,
                        'window_title': window_title,
                        'is_browser': process_name.lower() in self.browser_processes
                    }
                    
                    # If it's a browser, try to get the URL
                    if window_info['is_browser']:
                        url = self.get_browser_url(process_name, window_title)
                        window_info['url'] = url
                    
                    return window_info
        except Exception:
            pass
        return None
    
    def capture_screen_fast(self):
        """Fast screen capture optimized for detection"""
        try:
            screenshot = ImageGrab.grab()
            img = np.array(screenshot)
            
            # Convert RGB to BGR for OpenCV
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Resize for faster processing but keep enough detail
            height, width = img.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height))
            
            return img
        except Exception as e:
            return None
    
    def aggressive_skin_detection(self, image):
        """Extremely aggressive skin detection"""
        if image is None:
            return 0
        
        # Multiple color space analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Very broad HSV skin ranges
        hsv_masks = []
        
        # Range 1: Light skin tones
        lower1 = np.array([0, 15, 50])
        upper1 = np.array([30, 255, 255])
        hsv_masks.append(cv2.inRange(hsv, lower1, upper1))
        
        # Range 2: Medium skin tones  
        lower2 = np.array([0, 25, 70])
        upper2 = np.array([25, 200, 255])
        hsv_masks.append(cv2.inRange(hsv, lower2, upper2))
        
        # Range 3: Pink/flesh tones
        lower3 = np.array([160, 20, 80])
        upper3 = np.array([180, 150, 255])
        hsv_masks.append(cv2.inRange(hsv, lower3, upper3))
        
        # YCrCb skin detection (very sensitive)
        lower_ycrcb = np.array([0, 130, 80])
        upper_ycrcb = np.array([255, 185, 140])
        ycrcb_mask = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)
        
        # RGB skin detection
        lower_rgb = np.array([80, 50, 40])
        upper_rgb = np.array([255, 200, 170])
        rgb_mask = cv2.inRange(rgb, lower_rgb, upper_rgb)
        
        # Combine all masks
        combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for mask in hsv_masks:
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        combined_mask = cv2.bitwise_or(combined_mask, ycrcb_mask)
        combined_mask = cv2.bitwise_or(combined_mask, rgb_mask)
        
        # Less aggressive morphological operations to preserve details
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        # Calculate skin percentage
        skin_pixels = cv2.countNonZero(combined_mask)
        total_pixels = image.shape[0] * image.shape[1]
        skin_percentage = (skin_pixels / total_pixels) * 100
        
        return skin_percentage
    
    def detect_explicit_regions(self, image):
        """Detect regions that commonly appear in explicit content"""
        if image is None:
            return 0
        
        # Convert to multiple color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for large skin-colored regions
        lower_skin = np.array([0, 20, 60])
        upper_skin = np.array([25, 255, 255])
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(skin_mask, connectivity=8)
        
        large_regions_score = 0
        total_area = image.shape[0] * image.shape[1]
        
        # Analyze each connected component
        for i in range(1, num_labels):  # Skip background (label 0)
            area = stats[i, cv2.CC_STAT_AREA]
            
            # Look for large regions (potential body parts)
            if area > total_area * 0.03:  # 3% of image
                large_regions_score += (area / total_area) * 100
        
        # Edge analysis for body contours
        edges = cv2.Canny(gray, 20, 60)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        curve_score = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Significant size
                # Calculate contour properties
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    compactness = 4 * math.pi * area / (perimeter * perimeter)
                    
                    # Look for curved, organic shapes
                    if 0.2 < compactness < 0.9:
                        curve_score += min(area / 1000, 10)
        
        return large_regions_score + curve_score
    
    def detect_flesh_concentration(self, image):
        """Detect high concentration of flesh-like pixels"""
        if image is None:
            return 0
        
        # Convert to RGB for flesh detection
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Multiple flesh color ranges
        flesh_masks = []
        
        # Light flesh
        flesh_masks.append(cv2.inRange(rgb, np.array([180, 130, 110]), np.array([255, 200, 180])))
        
        # Medium flesh
        flesh_masks.append(cv2.inRange(rgb, np.array([140, 100, 80]), np.array([200, 160, 130])))
        
        # Pink flesh
        flesh_masks.append(cv2.inRange(rgb, np.array([200, 150, 140]), np.array([255, 210, 190])))
        
        # Darker flesh
        flesh_masks.append(cv2.inRange(rgb, np.array([100, 70, 50]), np.array([170, 120, 100])))
        
        # Combine flesh masks
        combined_flesh = np.zeros(image.shape[:2], dtype=np.uint8)
        for mask in flesh_masks:
            combined_flesh = cv2.bitwise_or(combined_flesh, mask)
        
        # Calculate flesh percentage
        flesh_pixels = cv2.countNonZero(combined_flesh)
        total_pixels = image.shape[0] * image.shape[1]
        flesh_percentage = (flesh_pixels / total_pixels) * 100
        
        return flesh_percentage
    
    def analyze_image_content(self, image):
        """Comprehensive image analysis for explicit content"""
        if image is None:
            return 0
        
        # Get all detection scores
        skin_score = self.aggressive_skin_detection(image)
        explicit_score = self.detect_explicit_regions(image)
        flesh_score = self.detect_flesh_concentration(image)
        
        # Calculate brightness and contrast (explicit content often has specific characteristics)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Brightness/contrast adjustment (explicit content often has certain lighting)
        brightness_factor = 1.0
        if 80 < brightness < 180:  # Typical range for explicit content
            brightness_factor = 1.2
        
        # Weighted combination of all factors
        total_score = (
            skin_score * 0.35 + 
            explicit_score * 0.25 + 
            flesh_score * 0.3 + 
            (contrast / 10) * 0.1
        ) * brightness_factor
        
        return total_score, skin_score, explicit_score, flesh_score
    
    def is_explicit_content(self, image):
        """Determine if content is explicit with detailed logging"""
        if image is None:
            return False, {}
        
        total_score, skin_score, explicit_score, flesh_score = self.analyze_image_content(image)
        threshold = self.thresholds[self.sensitivity]['total_score']
        
        detection_info = {
            'total_score': total_score,
            'skin_score': skin_score,
            'explicit_score': explicit_score,
            'flesh_score': flesh_score,
            'threshold': threshold,
            'is_explicit': total_score > threshold
        }
        
        return total_score > threshold, detection_info
    
    def close_application(self, pid, process_name, window_title):
        """Close application immediately"""
        try:
            process = psutil.Process(pid)
            
            print(f"🚫 CLOSING: {process_name} - {window_title}")
            
            # Immediate termination for explicit content
            process.terminate()
            
            # Force kill after short wait
            try:
                process.wait(timeout=1)
            except psutil.TimeoutExpired:
                process.kill()
                print(f"⚡ Force killed {process_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error closing {process_name}: {e}")
            return False
    
    def monitor_for_explicit_content(self):
        """Main monitoring loop with aggressive detection and URL checking"""
        print("🔥 AGGRESSIVE NSFW MONITOR ACTIVE")
        print(f"⚙️  Sensitivity: {self.sensitivity.upper()}")
        print(f"🔄 Check every: {self.check_interval}s")
        print("🎯 Will close ANY app showing explicit content")
        print("🌐 Now includes website URL checking!")
        print("📺 YouTube content is EXCLUDED from detection")
        print("🔄 Running continuously in background...\n")
        
        detection_count = 0
        
        while self.monitoring:
            try:
                current_time = time.time()
                
                # Shorter cooldown for aggressive monitoring
                if current_time - self.last_detection_time < self.detection_cooldown:
                    time.sleep(0.1)
                    continue
                
                # Get active window first
                window = self.get_active_window()
                is_nsfw_detected = False
                detection_reason = ""
                
                # Check if YouTube content - if so, skip all detection
                if window and window.get('is_browser'):
                    url = window.get('url', '')
                    if self.is_youtube_content(url, window['window_title']):
                        time.sleep(self.check_interval)
                        continue
                
                # Check for NSFW website first (faster than image analysis)
                if window and window.get('is_browser'):
                    url = window.get('url', '')
                    is_nsfw_site, site_reason = self.is_nsfw_website(url, window['window_title'])
                    
                    if is_nsfw_site:
                        is_nsfw_detected = True
                        detection_reason = f"NSFW Website: {site_reason}"
                        print(f"\n🌐 NSFW WEBSITE DETECTED!")
                        print(f"🔗 URL/Title: {url or window['window_title']}")
                        print(f"📋 Reason: {site_reason}")
                
                # If no website detection, do image analysis
                if not is_nsfw_detected:
                    screenshot = self.capture_screen_fast()
                    
                    if screenshot is not None:
                        is_explicit, info = self.is_explicit_content(screenshot)
                        
                        if is_explicit:
                            is_nsfw_detected = True
                            detection_reason = f"Explicit Image: Score {info['total_score']:.1f}"
                            print(f"\n🚨 EXPLICIT CONTENT DETECTED!")
                            print(f"📊 Scores - Total: {info['total_score']:.1f}, Skin: {info['skin_score']:.1f}, Explicit: {info['explicit_score']:.1f}, Flesh: {info['flesh_score']:.1f}")
                            print(f"🎯 Threshold: {info['threshold']}")
                
                # If NSFW detected by either method, close the application
                if is_nsfw_detected:
                    detection_count += 1
                    self.consecutive_detections += 1
                    self.last_detection_time = current_time
                    
                    print(f"\n🚫 DETECTION #{detection_count}: {detection_reason}")
                    
                    if window:
                        success = self.close_application(
                            window['pid'],
                            window['process_name'], 
                            window['window_title']
                        )
                        
                        if success:
                            print("✅ Application terminated successfully")
                        else:
                            print("❌ Failed to terminate application")
                    else:
                        print("❓ No active window found")
                    
                    print("⏳ Brief cooldown...\n")
                else:
                    self.consecutive_detections = 0
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(0.5)
    
    def start_monitoring(self):
        """Start the aggressive monitor"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_for_explicit_content)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            return True
        return False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

def main():
    print("🔥 AGGRESSIVE NSFW DETECTION SYSTEM 🔥")
    print("⚡ Will aggressively detect and close explicit content")
    print("🎯 Now includes website URL checking + image analysis")
    print("🌐 Blocks known NSFW websites instantly!")
    print("📺 YouTube content is EXCLUDED from detection\n")
    
    # Use default settings - no user input required
    sensitivity = 'medium'
    interval = 0.5
    
    print(f"⚙️  AUTO CONFIGURATION:")
    print(f"   - Sensitivity: {sensitivity.upper()}")
    print(f"   - Check interval: {interval}s")
    print(f"   - Website checking: ENABLED")
    print(f"   - Image analysis: ENABLED")
    print(f"   - YouTube exception: ENABLED")
    print(f"   - Target: Active window")
    print(f"   - Action: Immediate termination")
    print(f"   - Mode: CONTINUOUS (runs until process terminated)")
    
    monitor = AggressiveNSFWDetector(check_interval=interval, sensitivity=sensitivity)
    
    print("\n🚨 Starting ENHANCED monitoring automatically...")
    print("🔄 Monitor will run continuously in background...")
    print("🛑 Use Task Manager to stop if needed\n")
    
    monitor.start_monitoring()
    
    # Keep the main thread alive indefinitely
    while monitor.monitoring:
        time.sleep(1)

if __name__ == "__main__":
    required_packages = ['opencv-python', 'psutil', 'pillow', 'numpy', 'pywin32']
    print("📦 Required:", ', '.join(required_packages))
    print("📥 Install: pip install " + ' '.join(required_packages))
    print("=" * 60)
    
    try:
        main()
    except ImportError as e:
        print(f"\n❌ Missing: {e}")
        print("Install packages first!")