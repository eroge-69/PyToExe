import mss
import numpy as np
import cv2
import time
import os
import sys
import multiprocessing as mp
from collections import deque
from typing import Dict, List
import logging
import gc
import threading
from queue import Queue, Empty

# Try to import pydirectinput for mouse control
try:
    import pydirectinput
    pydirectinput.FAILSAFE = False # Disable failsafe feature
    MOUSE_CONTROL_ENABLED = True
except ImportError:
    MOUSE_CONTROL_ENABLED = False
    print("Warning: pydirectinput not found. Mouse control will be disabled. Install with: pip install pydirectinput")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import yaml, provide fallback if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning("PyYAML not installed. Install with: pip install PyYAML")

# --- Performance Optimized Configuration & GPU Setup ---
# Set environment variables for better performance and GPU utilization
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['OMP_NUM_THREADS'] = str(max(1, mp.cpu_count() // 2))
os.environ['MKL_NUM_THREADS'] = str(max(1, mp.cpu_count() // 2))
os.environ['NUMEXPR_NUM_THREADS'] = str(max(1, mp.cpu_count() // 2))

# --- Optimized Configuration Class ---
class Config:
    # Model settings
    CONFIDENCE_THRESHOLD = 0.6
    MODEL_INPUT_SIZE = 416
    IOU_THRESHOLD = 0.4
    MAX_DETECTIONS = 50
    
    # Performance settings
    REGION_SIZE_FACTOR = 0.75
    TARGET_FPS = 30
    FRAME_SKIP = 3
    
    # Display settings
    PRINT_FPS_TO_CONSOLE_DEFAULT = False 
    SHOW_GUI_FPS_DEFAULT = False 
    
    # Memory optimization
    BATCH_SIZE = 1
    HALF_PRECISION = True
    
    # Threading
    USE_THREADING = True
    CAPTURE_BUFFER_SIZE = 2
    
    # Mouse control settings
    AIMBOT_ENABLED_DEFAULT = False 
    AUTOFIIRE_ENABLED_DEFAULT = False
    # AIM_SMOOTHING should be a value between 0.0 (no movement) and 1.0 (instant snap).
    # A value of 0.2-0.5 is a good starting point for smooth aim.
    AIM_SMOOTHING = 0.0009
    # AIM_OFFSET_Y: A value from 0.0 (top of box) to 1.0 (bottom of box).
    # A value of 0.2-0.4 is a good starting point for a head/neck shot.
    AIM_OFFSET_Y = 0.3
    # This delay is no longer used, as we now rely on the loop speed for responsiveness.
    MOUSE_MOVE_DELAY = 0.05
    
    # Paths
    # !! UPDATE THESE PATHS TO YOUR SPECIFIC FILES !!
    DATA_YAML_PATH = "C:\\Users\\decla\\OneDrive\\Desktop\\Yolo Anticheat test\\data.yaml"
    MODEL_PATH = "C:\\Users\\decla\\OneDrive\\Desktop\\Yolo Anticheat test\\runs\\detect\\train3\\weights\\best.engine"

# --- Helper Functions ---
def setup_region(monitor: Dict, region_size_factor: float) -> Dict:
    """Calculates the screen capture region."""
    region_width = int(monitor['height'] * region_size_factor)
    region_height = int(monitor['height'] * region_size_factor)
    
    # Align dimensions to multiples of 32 for better performance
    region_width = (region_width // 32) * 32
    region_height = (region_height // 32) * 32
    
    return {
        'top': monitor['top'] + (monitor['height'] - region_height) // 2,
        'left': monitor['left'] + (monitor['width'] - region_width) // 2,
        'width': region_width,
        'height': region_height
    }

def load_class_names_from_yaml(yaml_path: str) -> Dict[int, str]:
    """Load class names from a YAML file."""
    if not YAML_AVAILABLE:
        return parse_yaml_manually(yaml_path)
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        if 'names' not in data:
            logger.error(f"'names' section not found in {yaml_path}")
            return {}
        names = data['names']
        if isinstance(names, dict):
            return {int(key): str(value) for key, value in names.items() if isinstance(key, (int, str)) and str(key).isdigit()}
        elif isinstance(names, list):
            return {i: name for i, name in enumerate(names)}
        else:
            logger.error(f"Unexpected format for 'names' in {yaml_path}")
            return {}
    except Exception as e:
        logger.error(f"YAML loading failed, trying manual parsing: {e}")
        return parse_yaml_manually(yaml_path)

def parse_yaml_manually(yaml_path: str) -> Dict[int, str]:
    """Manual YAML parsing as a fallback."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            content = file.read()
        class_names = {}
        in_names_section = False
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('names:'):
                in_names_section = True
                continue
            if in_names_section and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"\'')
                    if key.isdigit():
                        class_names[int(key)] = value
        return class_names
    except Exception as e:
        logger.error(f"Manual YAML parsing failed: {e}")
        return {0: "person", 1: "head", 2: "body"}

# --- Threaded Screen Capture (Fixed and Optimized) ---
class ThreadedCapture:
    def __init__(self):
        self.frame_queue = Queue(maxsize=Config.CAPTURE_BUFFER_SIZE)
        self.running = False
        self.thread = None
        with mss.mss() as sct:
            self.monitor = sct.monitors[1]
        self.region = setup_region(self.monitor, Config.REGION_SIZE_FACTOR)
        self.region_center_x = self.region['width'] / 2
        self.region_center_y = self.region['height'] / 2
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            
    def get_frame(self) -> np.ndarray:
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None
        
    def _capture_loop(self):
        try:
            with mss.mss() as sct:
                logger.info("MSS instance created in capture thread.")
                while self.running:
                    try:
                        raw_pixels = sct.grab(self.region)
                        frame = np.array(raw_pixels)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        
                        if self.frame_queue.full():
                            try:
                                self.frame_queue.get_nowait()
                            except Empty:
                                pass
                                
                        self.frame_queue.put(frame)
                        
                    except mss.exception.ScreenShotError as e:
                        logger.error(f"Screen capture error: {e}")
                        time.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Unexpected capture loop error: {e}")
                        time.sleep(0.1)
                        try:
                            sct = mss.mss()
                            logger.info("Recreated MSS object after error.")
                        except Exception as e:
                            logger.error(f"Could not re-create MSS object: {e}")
                self.running = False
        except Exception as e:
            logger.error(f"Failed to create MSS instance in capture thread: {e}")
            self.running = False

# --- High-Performance Performance Monitor ---
class HighPerformanceMonitor:
    def __init__(self, window_size: int = 60):
        self.fps_history = deque(maxlen=window_size)
        self.model_fps_history = deque(maxlen=window_size)
        self.last_time = time.perf_counter()
        self.frame_count = 0
        
    def update_loop_fps(self) -> float:
        current_time = time.perf_counter()
        fps = 1.0 / (current_time - self.last_time)
        self.fps_history.append(fps)
        self.last_time = current_time
        self.frame_count += 1
        return fps
        
    def update_model_fps(self, inference_time: float):
        if inference_time > 0:
            self.model_fps_history.append(1.0 / inference_time)
            
    def get_average_loop_fps(self) -> float:
        return sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0.0
        
    def get_average_model_fps(self) -> float:
        return sum(self.model_fps_history) / len(self.model_fps_history) if self.model_fps_history else 0.0
    
    def get_stats(self) -> dict:
        loop_fps_array = np.array(self.fps_history)
        model_fps_array = np.array(self.model_fps_history)
        return {
            'loop_avg': np.mean(loop_fps_array),
            'loop_min': np.min(loop_fps_array),
            'loop_max': np.max(loop_fps_array),
            'model_avg': np.mean(model_fps_array),
            'model_min': np.min(model_fps_array),
            'model_max': np.max(model_fps_array),
        }

# --- Main Application Class ---
class UltraOptimizedYOLODetector:
    def __init__(self):
        self.config = Config()
        
        if Config.USE_THREADING:
            self.threaded_capture = ThreadedCapture()
            self.screen_capture = None
        else:
            self.screen_capture = mss.mss()
            self.monitor = self.screen_capture.monitors[1]
            self.region = setup_region(self.monitor, self.config.REGION_SIZE_FACTOR)
            self.region_center_x = self.region['width'] / 2
            self.region_center_y = self.region['height'] / 2
            self.threaded_capture = None
            
        self.performance_monitor = HighPerformanceMonitor()
        self.model = None
        self.class_names = {}
        self.target_class_id = None
        self.show_cv_view = False 
        self.print_fps_to_console = Config.PRINT_FPS_TO_CONSOLE_DEFAULT
        self.show_gui_fps = Config.SHOW_GUI_FPS_DEFAULT 
        self.aimbot_enabled = Config.AIMBOT_ENABLED_DEFAULT
        self.autofire_enabled = Config.AUTOFIIRE_ENABLED_DEFAULT
        self.frame_skip = 1
        self.paused = False
        self.frame_counter = 0
        self.last_console_print_time = time.perf_counter()
        self.display_frame = None
        self._setup_memory_optimization()
        
        # New: Queue for detections and control thread
        self.detection_queue = Queue(maxsize=1)
        self.mouse_control_thread = None
        self.mouse_control_running = False
        self.mouse_down_active = False

    def _setup_memory_optimization(self):
        gc.set_threshold(700, 10, 10)
        
    def initialize(self):
        self._ask_for_initial_settings()
        
        if not self._setup_cuda(): return False
        if not self._load_model_and_classes(): return False
        if not self._select_target_class(): return False
        
        if self.threaded_capture:
            self.threaded_capture.start()
        
        if MOUSE_CONTROL_ENABLED:
            self._start_mouse_control_thread()
            
        return True
    
    def _ask_for_initial_settings(self):
        while True:
            response = input("Enable computer vision display window (Y/n)? ").strip().lower()
            if response in ['y', 'yes']:
                self.show_cv_view = True
                logger.info("Computer vision display enabled.")
                break
            elif response in ['n', 'no', '']:
                self.show_cv_view = False
                logger.info("Computer vision display disabled.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        while True:
            response = input("Show GUI FPS on the display window (Y/n)? ").strip().lower()
            if response in ['y', 'yes']:
                self.show_gui_fps = True
                logger.info("GUI FPS display enabled.")
                break
            elif response in ['n', 'no', '']:
                self.show_gui_fps = False
                logger.info("GUI FPS display disabled.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
        
        while True:
            response = input("Enable Aimbot (Y/n)? ").strip().lower()
            if response in ['y', 'yes']:
                self.aimbot_enabled = True
                logger.info("Aimbot enabled.")
                break
            elif response in ['n', 'no', '']:
                self.aimbot_enabled = False
                logger.info("Aimbot disabled.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        while True:
            response = input("Enable Auto-fire (Y/n)? ").strip().lower()
            if response in ['y', 'yes']:
                self.autofire_enabled = True
                logger.info("Auto-fire enabled.")
                break
            elif response in ['n', 'no', '']:
                self.autofire_enabled = False
                logger.info("Auto-fire disabled.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        while True:
            response = input("Enable Frame Skipping (Y/n)? ").strip().lower()
            if response in ['y', 'yes']:
                self.frame_skip = Config.FRAME_SKIP
                logger.info(f"Frame skipping enabled. Skipping {self.frame_skip - 1} frames per detection loop.")
                break
            elif response in ['n', 'no', '']:
                self.frame_skip = 1
                logger.info("Frame skipping disabled.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        while True:
            response = input("Show FPS in console (Y/n)? ").strip().lower()
            if response in ['y', 'yes']:
                self.print_fps_to_console = True
                logger.info("Console FPS display enabled.")
                break
            elif response in ['n', 'no', '']:
                self.print_fps_to_console = False
                logger.info("Console FPS display disabled.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def _setup_cuda(self) -> bool:
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.set_device(0)
                torch.backends.cudnn.enabled = True
                torch.backends.cudnn.benchmark = True
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                torch.cuda.empty_cache()
                torch.cuda.set_per_process_memory_fraction(0.9)
                logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
                logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**2} MB")
                return True
            else:
                logger.warning("No GPU detected. Running on CPU with optimizations.")
                torch.set_num_threads(mp.cpu_count())
                torch.set_num_interop_threads(mp.cpu_count())
                return True
        except ImportError:
            logger.error("PyTorch not available")
            return False
    
    def _load_model_and_classes(self) -> bool:
        try:
            from ultralytics import YOLO
            self.class_names = load_class_names_from_yaml(self.config.DATA_YAML_PATH)
            if not self.class_names: return False
            if not os.path.exists(self.config.MODEL_PATH):
                logger.error(f"Model file not found: {self.config.MODEL_PATH}")
                return False
            self.model = YOLO(self.config.MODEL_PATH)
            if hasattr(self.model.model, 'half') and Config.HALF_PRECISION:
                try:
                    self.model.model.half()
                    logger.info("Enabled FP16 precision")
                except:
                    logger.warning("FP16 not supported, using FP32")
            dummy_frame = np.random.randint(0, 255, (Config.MODEL_INPUT_SIZE, Config.MODEL_INPUT_SIZE, 3), dtype=np.uint8)
            _ = self.model(dummy_frame, conf=self.config.CONFIDENCE_THRESHOLD, verbose=False)
            logger.info(f"Model loaded and warmed up: {self.config.MODEL_PATH}")
            logger.info(f"Available classes: {self.class_names}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def _select_target_class(self) -> bool:
        print("Available classes:", list(self.class_names.values()))
        while True:
            try:
                target_class_name = input("Enter the name of the target class: ").strip()
                if target_class_name in self.class_names.values():
                    self.target_class_id = next(key for key, value in self.class_names.items() if value == target_class_name)
                    logger.info(f"Target class set to: {target_class_name} (ID: {self.target_class_id})")
                    return True
                else:
                    print(f"Invalid class name. Available: {list(self.class_names.values())}")
            except KeyboardInterrupt:
                return False
            except Exception as e:
                logger.error(f"Error selecting target class: {e}")
                return False
    
    def run(self):
        logger.info("Starting high-performance detection loop")
        self._print_controls()
        
        try:
            while True:
                # Always wait for keypress to allow for controls even with no display
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'): break
                elif key == ord('r'): self.paused = not self.paused; logger.info(f"Toggled Pause: {'ON' if self.paused else 'OFF'}")
                elif key == ord('v'): self.show_cv_view = not self.show_cv_view; logger.info(f"Toggled CV view: {'ON' if self.show_cv_view else 'OFF'}")
                elif key == ord('f'): self.print_fps_to_console = not self.print_fps_to_console; logger.info(f"Toggled Console FPS: {'ON' if self.print_fps_to_console else 'OFF'}")
                elif key == ord('a'): self.aimbot_enabled = not self.aimbot_enabled; logger.info(f"Toggled Aimbot: {'ON' if self.aimbot_enabled else 'OFF'}")
                elif key == ord('t'): self.autofire_enabled = not self.autofire_enabled; logger.info(f"Toggled Autofire: {'ON' if self.autofire_enabled else 'OFF'}")
                
                if self.paused:
                    time.sleep(0.001)
                    continue
                
                self.frame_counter += 1
                if self.frame_skip > 1 and self.frame_counter % self.frame_skip != 0: continue
                
                frame = None
                if self.threaded_capture:
                    frame = self.threaded_capture.get_frame()
                else:
                    raw_pixels = self.screen_capture.grab(self.region)
                    frame = np.array(raw_pixels)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                if frame is None: continue
                
                # Process the frame and get inference time
                inference_time = self._process_frame_optimized(frame)
            
                # Update overall loop FPS
                self.performance_monitor.update_loop_fps()
                # Update model-specific FPS
                self.performance_monitor.update_model_fps(inference_time)
                
                # Print stats to console if enabled
                if self.print_fps_to_console and (time.perf_counter() - self.last_console_print_time) > 1.0:
                    model_fps = self.performance_monitor.get_average_model_fps()
                    loop_fps = self.performance_monitor.get_average_loop_fps()
                    print(f"Overall FPS: {loop_fps:.1f} | Model FPS: {model_fps:.1f}")
                    self.last_console_print_time = time.perf_counter()

                if self.frame_counter % 1000 == 0: gc.collect()
                    
        except KeyboardInterrupt:
            logger.info("Script stopped by user")
        finally:
            self._cleanup()
    
    def _process_frame_optimized(self, frame: np.ndarray) -> float:
        start_time = time.perf_counter()
        
        results = self.model(
            frame, 
            conf=self.config.CONFIDENCE_THRESHOLD,
            iou=self.config.IOU_THRESHOLD,
            max_det=self.config.MAX_DETECTIONS,
            verbose=False,
            device=0 if torch.cuda.is_available() else 'cpu'
        )
        
        inference_time = time.perf_counter() - start_time
        
        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes
            target_mask = boxes.cls == self.target_class_id
            if target_mask.any():
                detections = [boxes[i] for i in range(len(boxes)) if target_mask[i]]
        
        # New: Put the latest detections into a queue for the mouse control thread to use
        # This sends an empty list if no targets are found, which signals the control thread to stop.
        if self.detection_queue.full():
            self.detection_queue.get_nowait()
        self.detection_queue.put(detections)
        
        if self.show_cv_view:
            self._display_frame_optimized(frame, detections)
        
        return inference_time

    def _start_mouse_control_thread(self):
        self.mouse_control_running = True
        self.mouse_control_thread = threading.Thread(target=self._mouse_control_loop, daemon=True)
        self.mouse_control_thread.start()
        logger.info("Mouse control thread started.")
    
    def _find_closest_detection(self, detections: List):
        """
        --- MODIFIED ---
        Finds the detection closest to the current mouse cursor position.
        This provides a more natural aim assist feel than snapping to the center.
        """
        if not detections:
            return None
        
        # Get the current mouse position in absolute screen coordinates
        current_mouse_x, current_mouse_y = pydirectinput.position()
        
        # Determine the capture region's offset to convert box coords to screen coords
        region_offset_x = self.threaded_capture.region['left'] if self.threaded_capture else self.region['left']
        region_offset_y = self.threaded_capture.region['top'] if self.threaded_capture else self.region['top']
        
        min_distance = float('inf')
        closest_detection = None
        
        for detection in detections:
            coords = detection.xyxy[0].cpu().numpy().astype(np.int32)
            x1, y1, x2, y2 = coords
            
            # Calculate the dimensions of the full bounding box
            box_width = x2 - x1
            box_height = y2 - y1
            
            # Define the inner 75% region
            # This is 12.5% in from each side (100% - 75% = 25%; 25% / 2 = 12.5%)
            inner_x1 = int(x1 + box_width * 0.125)
            inner_y1 = int(y1 + box_height * 0.125)
            inner_x2 = int(x2 - box_width * 0.125)
            inner_y2 = int(y2 - box_height * 0.125)

            # Calculate the new center of the inner 75% region
            target_center_x = (inner_x1 + inner_x2) / 2 + region_offset_x
            target_center_y = (inner_y1 + inner_y2) / 2 + region_offset_y
            
            # Calculate the distance from the mouse cursor to the box center
            distance = np.sqrt((target_center_x - current_mouse_x)**2 + (target_center_y - current_mouse_y)**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_detection = detection
                
        return closest_detection
    
    # New helper function to safely convert floats to integers
    def _safe_int(self, value: float) -> int:
        """Converts a float to a non-zero integer if the value is between -1 and 1."""
        if value > 0 and value < 1:
            return 1
        elif value < 0 and value > -1:
            return -1
        return int(value)

    def _mouse_control_loop(self):
        last_time = time.perf_counter()
        while self.mouse_control_running:
            current_time = time.perf_counter()
            delta_time = current_time - last_time
            last_time = current_time
            
            try:
                detections = self.detection_queue.get()
                
                closest_target = self._find_closest_detection(detections)
                
                # We need to get the current mouse position to calculate distance for both aimbot and autofire
                current_mouse_x, current_mouse_y = pydirectinput.position()
                
                if closest_target and self.aimbot_enabled:
                    coords = closest_target.xyxy[0].cpu().numpy().astype(np.int32)
                    x1, y1, x2, y2 = coords
                    
                    region_offset_x = self.threaded_capture.region['left'] if self.threaded_capture else self.region['left']
                    region_offset_y = self.threaded_capture.region['top'] if self.threaded_capture else self.region['top']
                    
                    # Calculate the dimensions of the full bounding box
                    box_width = x2 - x1
                    box_height = y2 - y1
                    
                    # Define the inner 75% region
                    inner_x1 = int(x1 + box_width * 0.125)
                    inner_y1 = int(y1 + box_height * 0.125)
                    inner_x2 = int(x2 - box_width * 0.125)
                    inner_y2 = int(y2 - box_height * 0.125)

                    # Calculate the new center of the inner 75% region
                    target_center_x = (inner_x1 + inner_x2) / 2 + region_offset_x
                    target_center_y = (inner_y1 + inner_y2) / 2 + region_offset_y

                    dx = target_center_x - current_mouse_x
                    dy = target_center_y - current_mouse_y
                    
                    proportional_gain = self.config.AIM_SMOOTHING
                    
                    move_x = self._safe_int(dx * proportional_gain)
                    move_y = self._safe_int(dy * proportional_gain)
                    
                    if move_x != 0 or move_y != 0:
                        pydirectinput.moveRel(move_x, move_y, duration=0.0001)

                # Autofire logic (also updated to use the new target center)
                if self.autofire_enabled:
                    if closest_target:
                        coords = closest_target.xyxy[0].cpu().numpy().astype(np.int32)
                        x1, y1, x2, y2 = coords
                        
                        region_offset_x = self.threaded_capture.region['left'] if self.threaded_capture else self.region['left']
                        region_offset_y = self.threaded_capture.region['top'] if self.threaded_capture else self.region['top']
                        
                        box_width = x2 - x1
                        box_height = y2 - y1
                        
                        inner_x1 = int(x1 + box_width * 0.125)
                        inner_y1 = int(y1 + box_height * 0.125)
                        inner_x2 = int(x2 - box_width * 0.125)
                        inner_y2 = int(y2 - box_height * 0.125)
                        
                        target_center_x = (inner_x1 + inner_x2) / 2 + region_offset_x
                        target_center_y = (inner_y1 + inner_y2) / 2 + region_offset_y
                        
                        fire_tolerance = 15
                        if np.sqrt((target_center_x - current_mouse_x)**2 + (target_center_y - current_mouse_y)**2) < fire_tolerance:
                            if not self.mouse_down_active:
                                pydirectinput.mouseDown()
                                self.mouse_down_active = True
                        else:
                            if self.mouse_down_active:
                                pydirectinput.mouseUp()
                                self.mouse_down_active = False
                    elif self.mouse_down_active:
                        pydirectinput.mouseUp()
                        self.mouse_down_active = False

            except Empty:
                time.sleep(0.001)
            except Exception as e:
                logger.error(f"Mouse control loop error: {e}")
            time.sleep(0.01)
    
    def _display_frame_optimized(self, frame: np.ndarray, detections: List):
        if self.display_frame is None or self.display_frame.shape != frame.shape:
            self.display_frame = frame.copy()
        else:
            np.copyto(self.display_frame, frame)
        
        for detection in detections:
            coords = detection.xyxy[0].cpu().numpy().astype(np.int32)
            x1, y1, x2, y2 = coords
            class_id = int(detection.cls)
            confidence = float(detection.conf)
            class_name = self.class_names.get(class_id, f"Class {class_id}")
            
            cv2.rectangle(self.display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            label = f'{class_name}: {confidence:.2f}'
            cv2.putText(self.display_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        center_x, center_y = 0, 0
        if self.threaded_capture:
            center_x = int(self.threaded_capture.region_center_x)
            center_y = int(self.threaded_capture.region_center_y)
        else:
            center_x = int(self.region_center_x)
            center_y = int(self.region_center_y)
            
        cv2.line(self.display_frame, (center_x-10, center_y), (center_x+10, center_y), (0, 0, 255), 1)
        cv2.line(self.display_frame, (center_x, center_y-10), (center_x, center_y+10), (0, 0, 255), 1)
        
        # New: Display FPS directly on the GUI window
        if self.show_gui_fps:
            loop_fps = self.performance_monitor.get_average_loop_fps()
            model_fps = self.performance_monitor.get_average_model_fps()
            cv2.putText(self.display_frame, f"Loop FPS: {loop_fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(self.display_frame, f"Model FPS: {model_fps:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Ultra-Optimized YOLO Detector", self.display_frame)
    
    def _print_controls(self):
        print("\n=== Ultra-Optimized YOLO Detector ===")
        print("   'V'   - Toggle computer vision preview")
        print("   'R'   - Toggle pause/resume")
        print("   'F'   - Toggle console FPS display")
        print("   'A'   - Toggle aimbot")
        print("   'T'   - Toggle autofire (new!)")
        print("   'Q'   - Quit application")
        print("======================================\n")
        print(f"Performance Settings:")
        print(f"   - Target FPS: {Config.TARGET_FPS}")
        print(f"   - Frame Skip: {self.frame_skip}")
        print(f"   - Input Size: {Config.MODEL_INPUT_SIZE}")
        print(f"   - Threading: {'ON' if Config.USE_THREADING else 'OFF'}")
        print(f"   - Half Precision: {'ON' if Config.HALF_PRECISION else 'OFF'}")
        print("======================================\n")
    
    def _cleanup(self):
        if self.threaded_capture:
            self.threaded_capture.stop()
        if self.mouse_control_thread:
            self.mouse_control_running = False
            # Wait for the mouse control thread to finish cleanly
            if self.mouse_control_thread.is_alive():
                self.mouse_control_thread.join()
        if self.mouse_down_active:
            pydirectinput.mouseUp()
        cv2.destroyAllWindows()
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        logger.info("Cleanup completed")

# --- Process Priority Setup ---
def setup_process_priority():
    try:
        import psutil
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)
        else:
            os.nice(-10)
        logger.info("Process priority set to high")
    except ImportError:
        logger.warning("psutil not available, couldn't set process priority")
    except Exception as e:
        logger.warning(f"Could not set process priority: {e}")

# --- Main Entry Point ---
def main():
    print("=== Ultra-Optimized YOLO Detector ===")
    setup_process_priority()
    
    missing_deps = []
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        if torch.cuda.is_available():
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        missing_deps.append("torch")
    
    try:
        from ultralytics import YOLO
        logger.info("Ultralytics YOLO available")
    except ImportError:
        missing_deps.append("ultralytics")
        
    if MOUSE_CONTROL_ENABLED:
        logger.info("pydirectinput available for mouse control.")
    else:
        missing_deps.append("pydirectinput")
    
    try:
        import psutil
        logger.info(f"CPU cores: {mp.cpu_count()}")
        logger.info(f"Available RAM: {psutil.virtual_memory().total // 1024**2} MB")
    except ImportError:
        logger.warning("psutil not available - install for better system monitoring")
    
    if not YAML_AVAILABLE:
        print("Warning: PyYAML not found. Manual YAML parsing will be used.")
    
    if missing_deps:
        print(f"Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install them using pip:")
        for dep in missing_deps:
            print(f"  pip install {dep}")
        sys.exit(1)
    
    app = UltraOptimizedYOLODetector()
    
    if app.initialize():
        app.run()
    else:
        logger.error("Failed to initialize application")
        sys.exit(1)

if __name__ == '__main__':
    try:
        import torch
    except ImportError:
        print("PyTorch is required. Install with: pip install torch")
        sys.exit(1)
        
    main()