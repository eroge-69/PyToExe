import sys
import time
import signal
import traceback
import faulthandler
import atexit
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog, QPlainTextEdit, QCheckBox, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin, urlparse, parse_qs
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Enable faulthandler for low-level crashes
faulthandler.enable()

def cleanup():
    """Cleanup function on exit"""
    # Close all Qt connections
    if hasattr(sys, 'app'):
        sys.app.quit()
    # Close all request sessions
    if hasattr(sys, 'session'):
        sys.session.close()

# Register cleanup function
atexit.register(cleanup)

def signal_handler(signum, frame):
    print(f"Signal {signum} received")
    print("Stack trace:")
    traceback.print_stack(frame)
    cleanup()
    sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

class URLProcessor:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.setup_session()

    def setup_session(self):
        """Setup session with browser-like headers"""
        # Configure automatic decompression
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'identity',  # Verhindert Komprimierung
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })

    def fetch_html_from_url(self, url):
        """Fetch HTML content from URL with improved error handling"""
        try:
            # Clean up URL and ensure it has viewfull=1
            cleaned_url = self.ensure_viewfull_parameter(url)

            # Add forum-specific headers
            headers = {
                'Referer': 'https://vipergirls.to/',
                'Origin': 'https://vipergirls.to',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }

            response = self.session.get(cleaned_url, timeout=30, allow_redirects=True, headers=headers)
            response.raise_for_status()

            # Force decode as UTF-8
            response.encoding = 'utf-8'
            html_content = response.text

            # Check if we got actual HTML
            if not html_content or len(html_content) < 100:
                raise Exception("Received empty or very short response")

            # Check for common error patterns
            html_lower = html_content.lower()
            if any(error in html_lower for error in ['access denied', 'forbidden', 'blocked', 'captcha']):
                raise Exception("Access blocked by website")

            # Check if it looks like HTML
            if not any(tag in html_lower for tag in ['<html', '<head', '<body', '<div']):
                raise Exception("Response doesn't appear to be HTML")

            return html_content, cleaned_url

        except Exception as e:
            raise Exception(f"Error fetching URL: {str(e)}")

    def ensure_viewfull_parameter(self, url):
        """Ensure URL has viewfull=1 parameter for better image display"""
        if 'viewfull=1' in url:
            return url

        # Add viewfull=1 parameter
        if '?' in url:
            if url.endswith('&'):
                return url + 'viewfull=1'
            else:
                return url + '&viewfull=1'
        else:
            return url + '?viewfull=1'

class DownloadWorker(QThread):
    """Worker thread for downloading images"""
    progress_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, content, target_dir, download_thumbnails, download_fullsize, is_url=False):
        super().__init__()
        self.content = content  # Kann HTML-String oder URL sein
        self.target_dir = target_dir
        self.download_thumbnails = download_thumbnails
        self.download_fullsize = download_fullsize
        self.is_url = is_url
        self.session = None
        self.should_stop = False
        self.url_processor = None

    def stop(self):
        """Stop the download process"""
        self.should_stop = True

    def create_session(self):
        """Create robust session with retry mechanism"""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Realistic browser headers for bot protection
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

        return session

    def is_valid_image(self, content, url):
        """Check if content is a valid image"""
        # Check minimum size
        if len(content) < 1024:  # Less than 1KB is suspicious
            return False

        # Check for HTML responses
        try:
            content_start = content[:200].decode('utf-8', errors='ignore').lower()
            if any(html_indicator in content_start for html_indicator in ['<html', '<!doctype', '<head', '<body']):
                return False
        except:
            pass

        # Check for valid image signatures
        image_signatures = {
            b'\xFF\xD8\xFF': 'jpg',  # JPEG
            b'\x89PNG\r\n\x1a\n': 'png',  # PNG
            b'GIF87a': 'gif',  # GIF87a
            b'GIF89a': 'gif',  # GIF89a
            b'RIFF': 'webp',  # WebP (starts with RIFF)
            b'BM': 'bmp',  # BMP
        }

        for signature, format_type in image_signatures.items():
            if content.startswith(signature):
                return True

        # Special WebP check (RIFF + WebP)
        if content.startswith(b'RIFF') and b'WEBP' in content[:20]:
            return True

        return False

    def download_image(self, url, target_path, image_type="Image"):
        """Download a single image with validation"""
        try:
            self.progress_signal.emit(f"Downloading {image_type}: {url}")
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()

            # Check Content-Type header
            content_type = response.headers.get('content-type', '').lower()
            if content_type and 'image' not in content_type:
                self.progress_signal.emit(f"Warning: Content-Type is not 'image': {content_type}")

            # Check if content is a valid image
            if not self.is_valid_image(response.content, url):
                self.progress_signal.emit(f"Invalid image content detected (Size: {len(response.content)} bytes)")
                return False

            # Check file size
            content_length = len(response.content)
            if content_length < 1024:  # Less than 1KB
                self.progress_signal.emit(f"File too small ({content_length} bytes) - probably error page")
                return False

            with open(target_path, 'wb') as f:
                f.write(response.content)

            # Log successful size
            size_kb = content_length / 1024
            self.progress_signal.emit(f"{image_type} successfully saved: {os.path.basename(target_path)} ({size_kb:.1f} KB)")
            return True

        except Exception as e:
            self.progress_signal.emit(f"Error downloading {image_type}: {str(e)}")
            return False

    def test_image_url_with_head(self, url):
        """Test URL with HEAD request and check for valid image"""
        try:
            self.progress_signal.emit(f"Testing URL with HEAD: {url}")

            # Special headers for imx.to
            headers = {
                'Referer': 'https://imx.to/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Cache-Control': 'no-cache'
            }

            # Try HEAD request
            try:
                response = self.session.head(url, timeout=15, allow_redirects=True, headers=headers)

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    content_length = response.headers.get('content-length')

                    if 'image' in content_type:
                        if content_length:
                            size = int(content_length)
                            if size > 5000:  # Larger than 5KB
                                self.progress_signal.emit(f"HEAD: Valid image found: {url} ({content_type}, {size} bytes)")
                                return True
                            else:
                                self.progress_signal.emit(f"HEAD: Image too small: {size} bytes")
                        else:
                            self.progress_signal.emit(f"HEAD: Image found (unknown size): {url}")
                            return True
                    else:
                        self.progress_signal.emit(f"HEAD: No image Content-Type: {content_type}")
                elif response.status_code == 403:
                    self.progress_signal.emit(f"HEAD: 403 Forbidden - trying GET...")
                else:
                    self.progress_signal.emit(f"HEAD: HTTP error {response.status_code}")
                    return False

            except Exception as head_error:
                self.progress_signal.emit(f"HEAD request failed: {str(head_error)} - trying GET...")

            # Fallback: GET request with stream
            try:
                self.progress_signal.emit(f"Trying GET request for: {url}")
                get_response = self.session.get(url, timeout=15, headers=headers, stream=True)

                if get_response.status_code == 200:
                    content_type = get_response.headers.get('content-type', '').lower()
                    content_length = get_response.headers.get('content-length')

                    if 'image' in content_type:
                        try:
                            first_bytes = next(get_response.iter_content(chunk_size=1024), b'')
                            if self.is_valid_image(first_bytes, url):
                                size_info = f"{content_length} bytes" if content_length else "unknown size"
                                self.progress_signal.emit(f"GET: Valid image confirmed: {url} ({content_type}, {size_info})")
                                get_response.close()
                                return True
                            else:
                                self.progress_signal.emit(f"GET: First bytes are not a valid image")
                        except:
                            if content_length and int(content_length) > 5000:
                                self.progress_signal.emit(f"GET: Trust Content-Type: {url}")
                                get_response.close()
                                return True
                    else:
                        self.progress_signal.emit(f"GET: No image Content-Type: {content_type}")
                else:
                    self.progress_signal.emit(f"GET: HTTP error {get_response.status_code}")

                get_response.close()

            except Exception as get_error:
                self.progress_signal.emit(f"GET request failed: {str(get_error)}")

        except Exception as e:
            self.progress_signal.emit(f"General error during URL test: {str(e)}")

        return False

    def run(self):
        """Main download process with URL support"""
        try:
            self.progress_signal.emit("Starting processing...")
            self.session = self.create_session()
            self.url_processor = URLProcessor(self.session)

            # Bestimme HTML-Content
            if self.is_url:
                self.progress_signal.emit(f"Fetching HTML from URL: {self.content}")
                html_content, final_url = self.url_processor.fetch_html_from_url(self.content)
                self.progress_signal.emit(f"HTML fetched successfully from: {final_url}")
                self.progress_signal.emit(f"HTML length: {len(html_content)} characters")
            else:
                html_content = self.content
                self.progress_signal.emit("Using provided HTML content")

            # Create subdirectories for thumbnails and fullsize images
            thumbnail_dir = os.path.join(self.target_dir, "thumbnails") if self.download_thumbnails else None
            fullsize_dir = os.path.join(self.target_dir, "fullsize") if self.download_fullsize else None

            if thumbnail_dir and not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir)
            if fullsize_dir and not os.path.exists(fullsize_dir):
                os.makedirs(fullsize_dir)

            soup = BeautifulSoup(html_content, 'html.parser')

            # Debug: Analyze HTML structure
            self.progress_signal.emit("\n=== HTML Analysis ===")
            self.progress_signal.emit(f"HTML preview (first 500 chars):")
            self.progress_signal.emit(html_content[:500])

            # Find the actual post content (vBulletin forum structure)
            post_content = None

            # Try different selectors for post content
            selectors_to_try = [
                'div.postbit',  # vBulletin postbit
                'div.message',  # Generic message
                'div.content',  # Generic content
                'div[id*="post_message"]',  # Post message with ID
                'div.postcontent',  # Post content
                'div.messageContent',  # XenForo style
            ]

            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    post_content = elements[0]  # Take first match
                    self.progress_signal.emit(f"Found post content using selector: {selector}")
                    break

            if not post_content:
                # Fallback: look for any div containing imx.to links
                all_divs = soup.find_all('div')
                for div in all_divs:
                    if div.find('a', href=lambda x: x and 'imx.to' in x):
                        post_content = div
                        self.progress_signal.emit("Found post content by searching for imx.to links")
                        break

            if not post_content:
                self.progress_signal.emit("Warning: Could not find specific post content, using entire page")
                post_content = soup

            # Find links with images only within post content
            links = post_content.find_all('a')
            self.progress_signal.emit(f"Found total links in post content: {len(links)}")

            # Filter for links that contain images AND point to image hosts
            valid_links = []
            for link in links:
                href = link.get('href', '')
                img_tag = link.find('img')

                if img_tag and href:
                    img_src = img_tag.get('src', '')

                    # Only process links to known image hosts
                    image_hosts = ['imx.to', 'imagebam.com', 'imgbox.com', 'pixhost.to', 'imagetwist.com']

                    if any(host in href.lower() or host in img_src.lower() for host in image_hosts):
                        valid_links.append(link)
                        self.progress_signal.emit(f"Valid image link found: {href}")

            self.progress_signal.emit(f"Found valid image links: {len(valid_links)}")

            if len(valid_links) == 0:
                self.progress_signal.emit("No valid image links found in post content!")
                return

            image_counter = 1
            download_delay = 1

            for link in valid_links:
                if self.should_stop:
                    self.progress_signal.emit("Download canceled by user")
                    break

                href = link.get('href')
                if not href:
                    continue

                # Search for img tag within the link
                img_tag = link.find('img')
                if img_tag:
                    thumbnail_url = img_tag.get('src')
                    if not thumbnail_url:
                        continue

                    self.progress_signal.emit(f"\n=== Processing Image {image_counter} ===")
                    self.progress_signal.emit(f"Thumbnail URL: {thumbnail_url}")
                    self.progress_signal.emit(f"Link URL: {href}")

                    try:
                        self.status_signal.emit(f"Processing image: {image_counter}")

                        if image_counter > 1:
                            time.sleep(download_delay)

                        # Base filename for both images
                        base_filename = f"image_{image_counter:03d}"

                        # Download thumbnail
                        if self.download_thumbnails:
                            thumbnail_extension = os.path.splitext(urlparse(thumbnail_url).path)[1]
                            if not thumbnail_extension:
                                thumbnail_extension = '.jpg'

                            thumbnail_filename = f"{base_filename}_thumb{thumbnail_extension}"
                            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

                            if self.download_image(thumbnail_url, thumbnail_path, "Thumbnail"):
                                self.status_signal.emit(f"Thumbnail downloaded: {thumbnail_filename}")

                        # Download fullsize image
                        if self.download_fullsize:
                            # Special handling for imx.to
                            if 'imx.to' in urlparse(thumbnail_url).netloc.lower():
                                # Convert thumbnail URL to fullsize URL
                                # /u/t/2025/07/27/686zr0.jpg -> /u/i/2025/07/27/686zr0.jpg
                                if '/u/t/' in thumbnail_url:
                                    fullsize_url = thumbnail_url.replace('/u/t/', '/u/i/')
                                    self.progress_signal.emit(f"imx.to thumbnail-to-fullsize conversion:")
                                    self.progress_signal.emit(f"  Preview: {thumbnail_url}")
                                    self.progress_signal.emit(f"  Fullsize: {fullsize_url}")

                                    # Test if fullsize exists
                                    if self.test_image_url_with_head(fullsize_url):
                                        self.progress_signal.emit(f"Fullsize URL confirmed: {fullsize_url}")

                                        fullsize_extension = os.path.splitext(urlparse(fullsize_url).path)[1]
                                        if not fullsize_extension:
                                            fullsize_extension = '.jpg'

                                        fullsize_filename = f"{base_filename}_full{fullsize_extension}"
                                        fullsize_path = os.path.join(fullsize_dir, fullsize_filename)

                                        if self.download_image(fullsize_url, fullsize_path, "Fullsize"):
                                            self.status_signal.emit(f"Fullsize downloaded: {fullsize_filename}")
                                        else:
                                            self.progress_signal.emit("Download of converted fullsize failed")
                                    else:
                                        self.progress_signal.emit("Converted fullsize URL not available")
                                else:
                                    self.progress_signal.emit("Unknown imx.to URL format")
                            else:
                                self.progress_signal.emit("No fullsize found - skipping")

                        image_counter += 1

                    except Exception as e:
                        self.progress_signal.emit(f"Error processing image {image_counter}: {str(e)}")
                        continue

            if not self.should_stop:
                self.progress_signal.emit(f"\n=== Processing completed ===")
                self.progress_signal.emit(f"Total {image_counter - 1} images processed")
                self.status_signal.emit("Download completed!")

        except Exception as e:
            self.progress_signal.emit(f"Unexpected error: {str(e)}")
            traceback.print_exc()
        finally:
            if self.session:
                self.session.close()
            self.finished_signal.emit()

class ImageDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTML Image Downloader with URL Support")
        self.setGeometry(100, 100, 1000, 950)

        self.download_worker = None

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # URL input field (NEU)
        url_layout = QVBoxLayout()
        url_label = QLabel("Forum Post URL (recommended - paste forum link here):")
        url_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL to forum post")
        self.url_input.setMinimumHeight(30)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Separator
        separator_label = QLabel("--- OR ---")
        separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_label.setStyleSheet("color: gray; margin: 10px;")
        layout.addWidget(separator_label)

        # HTML input field (modifiziert)
        html_label = QLabel("Manual HTML input (only if no URL provided above):")
        html_label.setStyleSheet("color: #333333;")
        layout.addWidget(html_label)
        self.html_input = QTextEdit()
        self.html_input.setPlaceholderText("Paste your HTML code here (only needed if no URL above)...")
        self.html_input.setMaximumHeight(150)  # Kleinere Höhe da URL bevorzugt wird
        layout.addWidget(self.html_input)

        # Options
        options_layout = QHBoxLayout()
        self.download_thumbnails = QCheckBox("Download thumbnails")
        self.download_thumbnails.setChecked(False)  # Default OFF
        self.download_fullsize = QCheckBox("Download fullsize images")
        self.download_fullsize.setChecked(True)
        options_layout.addWidget(self.download_thumbnails)
        options_layout.addWidget(self.download_fullsize)
        layout.addLayout(options_layout)

        # Debug log area
        debug_label = QLabel("Download Progress:")
        debug_label.setStyleSheet("color: #333333;")
        layout.addWidget(debug_label)
        self.debug_log = QPlainTextEdit()
        self.debug_log.setReadOnly(True)
        self.debug_log.setMaximumHeight(400)
        layout.addWidget(self.debug_log)

        # Status label
        self.status_label = QLabel("Ready - Enter a forum URL above to start")
        self.status_label.setStyleSheet("padding: 5px; background-color: #E8F5E8; border-radius: 3px; color: #2E7D32;")
        layout.addWidget(self.status_label)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.download_button = QPushButton("Download Images")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setMinimumHeight(35)
        self.download_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        buttons_layout.addWidget(self.download_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setMinimumHeight(35)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

    def closeEvent(self, event):
        """Called when window is closed"""
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.stop()
            self.download_worker.wait()
        event.accept()

    def log_debug(self, message):
        """Add message to debug log"""
        print(message)
        self.debug_log.appendPlainText(str(message))
        QApplication.processEvents()

    def start_download(self):
        """Start the download process with URL or HTML support"""
        try:
            self.debug_log.clear()
            self.log_debug("Starting processing...")

            if not self.download_thumbnails.isChecked() and not self.download_fullsize.isChecked():
                self.log_debug("Please select at least one download option!")
                return

            target_dir = QFileDialog.getExistingDirectory(self, "Select target folder")
            if not target_dir:
                return

            # Prüfe URL oder HTML
            url_content = self.url_input.text().strip()
            html_content = self.html_input.toPlainText().strip()

            if url_content:
                # URL verwenden
                content = url_content
                is_url = True
                self.log_debug(f"Using URL: {url_content}")
            elif html_content:
                # HTML verwenden
                content = html_content
                is_url = False
                self.log_debug("Using provided HTML content")
            else:
                self.log_debug("Please provide either a forum URL or HTML content!")
                return

            # Create and start worker thread
            self.download_worker = DownloadWorker(
                content,
                target_dir,
                self.download_thumbnails.isChecked(),
                self.download_fullsize.isChecked(),
                is_url
            )

            # Connect signals
            self.download_worker.progress_signal.connect(self.log_debug)
            self.download_worker.status_signal.connect(self.status_label.setText)
            self.download_worker.finished_signal.connect(self.download_finished)

            # Update UI
            self.download_button.setEnabled(False)
            self.cancel_button.setEnabled(True)

            # Start download
            self.download_worker.start()

        except Exception as e:
            self.log_debug(f"Error starting download: {str(e)}")

    def cancel_download(self):
        """Cancel the download process"""
        if self.download_worker and self.download_worker.isRunning():
            self.log_debug("Canceling download...")
            self.download_worker.stop()
            self.status_label.setText("Canceling...")

    def download_finished(self):
        """Called when download is finished"""
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        # Clear input fields after successful download
        self.url_input.clear()
        self.html_input.clear()

        # Show completion message
        self.log_debug("\n✓ DOWNLOAD COMPLETED!")
        self.log_debug("All images have been downloaded successfully.")
        self.log_debug("Input fields have been cleared for next download.")

        if self.download_worker:
            self.download_worker.deleteLater()
            self.download_worker = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.app = app  # For cleanup
    window = ImageDownloaderApp()
    window.show()
    sys.exit(app.exec())