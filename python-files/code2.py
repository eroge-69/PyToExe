"""
Clean Age Detection System
- Only shows age above the face
- No FPS or control texts
- Automatic fullscreen
- Clean minimal interface
"""

import cv2
import numpy as np
import os
import time
import sys


class CleanAgeDetector:
    def __init__(self, debug=False):
        self.debug = debug
        self.prev_age = None
        self.alpha = 0.3  # Smoothing factor

        if debug:
            print("🔧 Initializing Age Detection System...")

        # Initialize face detection
        self._init_face_detection()

        # Initialize age prediction models
        self._init_age_models()

    def _init_face_detection(self):
        """Initialize face detection with multiple fallbacks"""
        # Try MediaPipe first
        self.mp_detector = None
        try:
            import mediapipe as mp
            self.mp = mp
            self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.6)
            self.mp_detector = True
            if self.debug:
                print("✅ MediaPipe face detection loaded")
        except Exception as e:
            if self.debug:
                print(f"⚠️ MediaPipe not available: {e}")
            self.mp_detector = False

        # OpenCV Haar Cascade fallback
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            if self.face_cascade.empty():
                raise Exception("Haar cascade file not found")
            if self.debug:
                print("✅ OpenCV Haar Cascade loaded")
        except Exception as e:
            if self.debug:
                print(f"❌ Failed to load Haar Cascade: {e}")
            sys.exit(1)

    def _init_age_models(self):
        """Initialize age prediction models"""
        self.age_models = {}

        # Try DeepFace (suppress output)
        try:
            import warnings
            warnings.filterwarnings('ignore')
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

            from deepface import DeepFace
            self.deepface = DeepFace
            self.age_models['deepface'] = True
            if self.debug:
                print("✅ DeepFace loaded for age prediction")
        except Exception as e:
            if self.debug:
                print(f"⚠️ DeepFace not available: {e}")
            self.age_models['deepface'] = False

        # Fallback simple model
        self.age_models['fallback'] = True
        if self.debug:
            print("✅ Fallback age estimation ready")

    def detect_face(self, frame):
        """Detect largest face in frame"""
        faces = []

        # Try MediaPipe first
        if self.mp_detector:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.mp_face_detection.process(rgb_frame)

                if results.detections:
                    h, w = frame.shape[:2]
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        x = int(bbox.xmin * w)
                        y = int(bbox.ymin * h)
                        width = int(bbox.width * w)
                        height = int(bbox.height * h)

                        # Ensure coordinates are within frame
                        x = max(0, x)
                        y = max(0, y)
                        width = min(width, w - x)
                        height = min(height, h - y)

                        faces.append((x, y, width, height, width * height))
            except Exception as e:
                if self.debug:
                    print(f"MediaPipe detection error: {e}")

        # Fallback to Haar Cascade
        if not faces:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detected_faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

                for (x, y, w, h) in detected_faces:
                    faces.append((x, y, w, h, w * h))
            except Exception as e:
                if self.debug:
                    print(f"Haar cascade error: {e}")

        if not faces:
            return None, None

        # Return largest face
        largest_face = max(faces, key=lambda f: f[4])
        x, y, w, h, _ = largest_face

        # Extract face region with padding
        padding = int(0.2 * min(w, h))
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(frame.shape[1], x + w + padding)
        y2 = min(frame.shape[0], y + h + padding)

        face_crop = frame[y1:y2, x1:x2]
        bbox = (x1, y1, x2, y2)

        return face_crop, bbox

    def predict_age(self, face_image):
        """Predict age using available models"""
        predictions = []

        # Try DeepFace prediction
        if self.age_models.get('deepface', False):
            try:
                # Convert BGR to RGB for DeepFace
                rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

                # Analyze with DeepFace
                result = self.deepface.analyze(
                    rgb_face,
                    actions=['age'],
                    enforce_detection=False,
                    silent=True
                )

                if isinstance(result, list):
                    result = result[0]

                age = result.get('Tentative age', 25)
                predictions.append((float(age), 0.8))  # High confidence for DeepFace

            except Exception as e:
                if self.debug:
                    print(f"DeepFace prediction error: {e}")

        # Fallback prediction
        if not predictions:
            try:
                age = self._simple_age_estimation(face_image)
                predictions.append((age, 0.5))  # Medium confidence for fallback
            except Exception as e:
                if self.debug:
                    print(f"Fallback prediction error: {e}")
                predictions.append((30.0, 0.3))  # Default age

        # Average predictions if multiple
        if len(predictions) > 1:
            total_weight = sum(conf for _, conf in predictions)
            if total_weight > 0:
                weighted_age = sum(age * conf for age, conf in predictions) / total_weight
                avg_conf = sum(conf for _, conf in predictions) / len(predictions)
            else:
                weighted_age = sum(age for age, _ in predictions) / len(predictions)
                avg_conf = 0.5
        else:
            weighted_age, avg_conf = predictions[0]

        return weighted_age, avg_conf

    def _simple_age_estimation(self, face_image):
        """Simple age estimation based on image characteristics"""
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Calculate image statistics
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)

        # Edge detection for wrinkle estimation
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Simple age estimation heuristics
        base_age = 25

        # Adjust based on edge density (wrinkles)
        age_from_edges = base_age + (edge_density * 80)

        # Adjust based on intensity variation
        age_from_texture = base_age + (std_intensity - 30) * 0.5

        # Combine estimates
        estimated_age = (age_from_edges + age_from_texture) / 2

        # Clamp to reasonable range
        estimated_age = max(5, min(85, estimated_age))

        return float(estimated_age)

    def smooth_age(self, current_age):
        """Apply temporal smoothing to age predictions"""
        if self.prev_age is None:
            self.prev_age = current_age
            return current_age

        # Exponential moving average
        smoothed = self.alpha * current_age + (1 - self.alpha) * self.prev_age

        # Prevent sudden jumps (max 2 years change per frame)
        max_change = 2.0
        change = smoothed - self.prev_age
        if abs(change) > max_change:
            smoothed = self.prev_age + np.sign(change) * max_change

        self.prev_age = smoothed
        return smoothed

    def run(self, camera_index=0):
        """Run age detection with clean interface"""
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            if self.debug:
                print("❌ Could not open camera")
            return False

        # Set camera properties for best quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, 30)

        # Create fullscreen window
        window_name = "Age Detection"

        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            gui_available = True
        except cv2.error as e:
            if self.debug:
                print(f"⚠️ GUI not available: {e}")
            return False

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    if self.debug:
                        print("❌ Failed to read from camera")
                    break

                # Mirror the frame for better user experience
                frame = cv2.flip(frame, 1)
                display_frame = frame.copy()

                # Detect face
                face_crop, bbox = self.detect_face(frame)

                if face_crop is not None and face_crop.size > 0:
                    # Predict age
                    raw_age, confidence = self.predict_age(face_crop)
                    smoothed_age = self.smooth_age(raw_age)

                    # Draw results - ONLY age text above face
                    x1, y1, x2, y2 = bbox

                    # Choose color based on confidence
                    if confidence > 0.7:
                        color = (0, 255, 0)  # Green - high confidence
                    elif confidence > 0.5:
                        color = (0, 255, 255)  # Yellow - medium confidence
                    else:
                        color = (0, 165, 255)  # Orange - low confidence

                    # Draw bounding box
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 3)

                    # ONLY show age - clean and minimal
                    age_text = f"Tentative Age: {int(round(smoothed_age))} years"

                    # Calculate text size for better positioning
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1.2
                    thickness = 3
                    (text_width, text_height), _ = cv2.getTextSize(age_text, font, font_scale, thickness)

                    # Position text above the bounding box, centered
                    text_x = x1 + (x2 - x1 - text_width) // 2
                    text_y = y1 - 20

                    # Make sure text doesn't go off screen
                    if text_y < text_height + 10:
                        text_y = y2 + text_height + 20
                    if text_x < 0:
                        text_x = 10
                    elif text_x + text_width > display_frame.shape[1]:
                        text_x = display_frame.shape[1] - text_width - 10

                    # Draw text with outline for better visibility
                    # Black outline
                    cv2.putText(display_frame, age_text, (text_x, text_y),
                                font, font_scale, (0, 0, 0), thickness + 2)
                    # Colored text
                    cv2.putText(display_frame, age_text, (text_x, text_y),
                                font, font_scale, color, thickness)

                # Display frame
                try:
                    cv2.imshow(window_name, display_frame)

                    # Check for 'q' key to quit (hidden functionality)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        break

                except cv2.error as e:
                    if self.debug:
                        print(f"Display error: {e}")
                    break

        except KeyboardInterrupt:
            if self.debug:
                print("\n🛑 Interrupted by user")
        except Exception as e:
            if self.debug:
                print(f"❌ Error during processing: {e}")
        finally:
            # Cleanup
            cap.release()
            try:
                cv2.destroyAllWindows()
            except:
                pass
            if self.debug:
                print("👋 Age detection stopped")

        return True


def main():
    """Main function - clean startup"""
    # Suppress all warnings and debug output
    import warnings
    warnings.filterwarnings('ignore')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # Create detector (debug=False for clean output)
    detector = CleanAgeDetector(debug=False)

    # Run detection
    detector.run(camera_index=0)


if __name__ == "__main__":
    main()