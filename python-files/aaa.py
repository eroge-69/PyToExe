import sys
import cv2
import numpy as np
import onnxruntime
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                             QFileDialog, QLineEdit, QDialog, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import insightface
from insightface.utils import face_align
import onnx
from onnx import numpy_helper
import mediapipe as mp # MediaPipe'ı içeri aktar

# --- LOGIN DIALOG CLASS START ---
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Giriş Yap")
        self.setFixedSize(300, 150) # Sabit bir boyut belirledik

        self.username_label = QLabel("Kullanıcı Adı:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin") # Örnek kullanıcı adı

        self.password_label = QLabel("Şifre:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Şifreyi gizle
        self.password_input.setPlaceholderText("admin") # Örnek şifre

        self.login_button = QPushButton("Giriş")
        self.cancel_button = QPushButton("İptal")

        self.login_button.clicked.connect(self.check_login)
        self.cancel_button.clicked.connect(self.reject) # İptal butonuna basınca dialog kapanır (reject ile)

        # Layout düzenlemesi
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            self.accept() # Doğruysa dialog kapanır (accept ile)
        else:
            QMessageBox.warning(self, "Giriş Hatası", "Kullanıcı adı veya şifre yanlış.", QMessageBox.StandardButton.Ok)
            self.username_input.clear()
            self.password_input.clear()
# --- LOGIN DIALOG CLASS END ---

# IOU hesaplama fonksiyonu (Değişmeden kalacak)
def calculate_iou(boxA, boxB):
    # boxA ve boxB formatı: (x1, y1, x2, y2)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_width = max(0, xB - xA + 1)
    inter_height = max(0, yB - yA + 1)
    inter_area = inter_width * inter_height

    boxA_area = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxB_area = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    union_area = float(boxA_area + boxB_area - inter_area)
    
    if union_area == 0:
        return 0.0

    iou = inter_area / union_area
    return iou

class INSwapper:
    def __init__(self, model_file=None, session=None):
        self.model_file = model_file
        self.session = session
        model = onnx.load(self.model_file)
        graph = model.graph
        self.emap = numpy_helper.to_array(graph.initializer[-1])
        self.input_mean = 0.0
        self.input_std = 255.0

        if self.session is None:
            # ONNX Runtime için sağlayıcı önceliği: GPU > CPU
            self.session = onnxruntime.InferenceSession(self.model_file, 
                                                        providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
        
        inputs = self.session.get_inputs()
        self.input_names = []
        for inp in inputs:
            self.input_names.append(inp.name)
        outputs = self.session.get_outputs()
        output_names = []
        for out in outputs:
            output_names.append(out.name)
        self.output_names = output_names
        assert len(self.output_names)==1
        output_shape = outputs[0].shape
        input_cfg = inputs[0]
        input_shape = input_cfg.shape
        self.input_shape = input_shape
        self.input_size = tuple(input_shape[2:4][::-1])

    def forward(self, img, latent):
        img = (img - self.input_mean) / self.input_std
        pred = self.session.run(self.output_names, {self.input_names[0]: img, self.input_names[1]: latent})[0]
        return pred

    def get(self, img, target_face, source_face, paste_back=True, hand_mask=None): 
        aimg, M = face_align.norm_crop2(img, target_face.kps, self.input_size[0])
        blob = cv2.dnn.blobFromImage(aimg, 1.0 / self.input_std, self.input_size,
                                     (self.input_mean, self.input_mean, self.input_mean), swapRB=True)
        
        latent = source_face.embedding.reshape((1,-1))
        latent = np.dot(latent, self.emap)
        latent /= np.linalg.norm(latent)

        pred = self.session.run(self.output_names, {self.input_names[0]: blob, self.input_names[1]: latent})[0]
        img_fake = pred.transpose((0,2,3,1))[0]
        bgr_fake = np.clip(255 * img_fake, 0, 255).astype(np.uint8)[:,:,::-1]
        
        if not paste_back:
            return bgr_fake, M
        else:
            target_img = img
            fake_diff = bgr_fake.astype(np.float32) - aimg.astype(np.float32)
            fake_diff = np.abs(fake_diff).mean(axis=2)
            fake_diff[:2,:] = 0
            fake_diff[-2:,:] = 0
            fake_diff[:,:2] = 0
            fake_diff[:,-2:] = 0
            
            IM = cv2.invertAffineTransform(M)
            
            # fthresh tanımı
            fthresh = 10 
            
            # 1. Yüz maskesini oluştur
            img_white = np.full((aimg.shape[0],aimg.shape[1]), 255, dtype=np.float32)
            
            # Yüz maskesini orijinal kare boyutuna geri dönüştür
            img_mask_full_frame = cv2.warpAffine(img_white, IM, 
                                                 (target_img.shape[1], target_img.shape[0]), 
                                                 borderValue=0.0)
            img_mask_full_frame[img_mask_full_frame > 20] = 255 # Maskeyi ikilik yap (0 veya 255)

            # --- El maskesini yüz maskesinden çıkar ---
            if hand_mask is not None:
                # El maskesini float32'ye dönüştürüp 0-1 aralığına normalize et
                hand_mask_float = hand_mask.astype(np.float32) / 255.0

                # Elin olduğu yerlerde 0, diğer yerlerde 1 olan bir çarpan maskesi oluştur
                inverted_hand_mask_3ch = np.stack([1.0 - hand_mask_float, 
                                                   1.0 - hand_mask_float, 
                                                   1.0 - hand_mask_float], axis=-1)

                # Yüz maskesini de 3 kanallı hale getir (RGB için)
                img_mask_full_frame_float = img_mask_full_frame.astype(np.float32) / 255.0 # Normalizasyon
                img_mask_full_frame_3ch = np.stack([img_mask_full_frame_float, 
                                                    img_mask_full_frame_float, 
                                                    img_mask_full_frame_float], axis=-1)

                # Çarpma işlemi, elin olduğu yerlerde maske değerini sıfırlayacak
                final_face_mask_3ch = img_mask_full_frame_3ch * inverted_hand_mask_3ch
                final_face_mask = np.clip(final_face_mask_3ch * 255, 0, 255).astype(np.uint8)[:,:,0] # Tek kanala düşür

            else:
                # El maskesi yoksa, orijinal yüz maskesini kullan
                final_face_mask = img_mask_full_frame
            # --- El maskesi çıkarma sonu ---

            mask_h_inds, mask_w_inds = np.where(final_face_mask == 255)
            
            # Eğer maskede geçerli beyaz piksel kalmadıysa (yüz tamamen el ile kaplıysa veya başka bir nedenden)
            if mask_h_inds.size == 0 or mask_w_inds.size == 0:
                return target_img # Hiçbir takas yapma, orijinal görüntüyü döndür.

            mask_h = np.max(mask_h_inds) - np.min(mask_h_inds)
            mask_w = np.max(mask_w_inds) - np.min(mask_w_inds)
            mask_size = int(np.sqrt(mask_h * mask_w))

            # **Maske Aşındırma (Erode) Parametresi Ayarı**
            # Daha küçük bir kernel boyutu ile maskeyi daha az aşındırırız.
            k_erode = max(mask_size // 20, 5) # Önceki 10'dan 20'ye, min 10'dan 5'e düşürüldü
            kernel_erode = np.ones((k_erode, k_erode), np.uint8)
            final_face_mask = cv2.erode(final_face_mask, kernel_erode, iterations=1) 
            
            # fake_diff_full_frame'i burada işliyoruz
            fake_diff_full_frame = cv2.warpAffine(fake_diff, IM, (target_img.shape[1], target_img.shape[0]), borderValue=0.0)
            fake_diff_full_frame[fake_diff_full_frame < fthresh] = 0 
            fake_diff_full_frame[fake_diff_full_frame >= fthresh] = 255
            
            kernel_dilate_diff = np.ones((2, 2), np.uint8) 
            fake_diff_full_frame = cv2.dilate(fake_diff_full_frame, kernel_dilate_diff, iterations=1)

            # **Yüz Maskesi Bulanıklaştırma (GaussianBlur) Parametresi Ayarı**
            # Daha küçük bir kernel boyutu ile maskeyi daha az bulanıklaştırırız.
            k_blur_face = max(mask_size // 40, 3) # Önceki 20'den 40'a, min 5'ten 3'e düşürüldü
            kernel_size_face = (k_blur_face, k_blur_face)
            blur_size_face = tuple(2 * i + 1 for i in kernel_size_face)
            final_face_mask = cv2.GaussianBlur(final_face_mask, blur_size_face, 0) 

            # **Fake Diff Bulanıklaştırma (GaussianBlur) Parametresi Ayarı**
            # Fake diff maskesi için de bulanıklığı azaltıyoruz.
            k_blur_diff = 3 # Sabit olarak 3'e düşürüldü (önceki 5'ti)
            kernel_size_diff = (k_blur_diff, k_blur_diff)
            blur_size_diff = tuple(2 * i + 1 for i in kernel_size_diff)
            fake_diff_full_frame = cv2.GaussianBlur(fake_diff_full_frame, blur_size_diff, 0)

            final_face_mask_normalized = final_face_mask.astype(np.float32) / 255.0
            
            final_face_mask_3ch = np.reshape(final_face_mask_normalized, [final_face_mask_normalized.shape[0], final_face_mask_normalized.shape[1], 1])
            
            bgr_fake_full_frame = cv2.warpAffine(bgr_fake, IM, (target_img.shape[1], target_img.shape[0]), borderValue=0.0)
            
            fake_merged = final_face_mask_3ch * bgr_fake_full_frame.astype(np.float32) + \
                          (1 - final_face_mask_3ch) * target_img.astype(np.float32)
            
            fake_merged = fake_merged.astype(np.uint8)
            return fake_merged


class XSegWrapper:
    # Bu sınıf şu an için boş, ihtiyacınıza göre genişletebilirsiniz.
    pass 

class FaceSwapApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J-Actor") # Pencere başlığını güncelledim
        self.resize(900, 700)

        # UI elemanları
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedSize(800, 600)

        self.btn_start = QPushButton("Webcam Başlat")
        self.btn_stop = QPushButton("Webcam Durdur")
        self.btn_guide = QPushButton("Rehber Foto Seç")
        self.btn_stop.setEnabled(False) # Başlangıçta durdur butonu devre dışı

        # Layout düzenlemesi
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.btn_guide)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        self.setLayout(layout)

        # Kamera ve zamanlayıcı değişkenleri
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.running = False

        self.guide_face_obj = None # Rehber yüz objesi

        # Modelleri yükleme
        try:
            print("Modeller yükleniyor...")
            self.swapper = INSwapper('models/buffalo_l/inswapper_128.onnx')
            print("INSwapper modeli başarıyla yüklendi.") 

            self.detector = insightface.app.FaceAnalysis(allowed_modules=['detection', 'recognition'])
            self.detector.prepare(ctx_id=0, det_size=(640, 640))
            print("FaceAnalysis modelleri başarıyla yüklendi.")

            self.mp_hands = mp.solutions.hands # MediaPipe Hands modülü
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            print("MediaPipe Hands modeli başarıyla yüklendi.")
            print("Uygulama başlatılmaya hazır.")

        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            sys.exit(1) # Hata durumunda uygulamayı kapat

        # Buton bağlantıları
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_guide.clicked.connect(self.select_guide_photo)

    def select_guide_photo(self):
        # Rehber fotoğraf seçme işlevi
        path, _ = QFileDialog.getOpenFileName(self, "Rehber Foto Seç", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return

        img = cv2.imread(path)
        if img is None:
            print("Hata: Fotoğraf yüklenemedi. Dosya yolu doğru mu?")
            return

        faces = self.detector.get(img)
        if not faces or len(faces) == 0:
            print("Rehber fotoğrafta yüz bulunamadı.")
            self.guide_face_obj = None
            return
        
        if faces[0].embedding is None:
            print("Hata: Rehber yüzün embedding'i (özellik vektörü) çıkarılamadı. FaceAnalysis modeli 'recognition' modülüyle yüklendi mi?")
            self.guide_face_obj = None
            return
        
        self.guide_face_obj = faces[0] 
        print("Rehber yüz başarıyla yüklendi ve embedding'i alındı.")

    def start_camera(self):
        # Kamera başlatma işlevi
        self.cap = cv2.VideoCapture(0) # Genellikle 0 varsayılan kameradır
        if not self.cap.isOpened():
            print("Hata: Kamera açılamadı. Kamera bağlı ve başka bir uygulama tarafından kullanılmıyor mu?")
            return
        
        self.running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.timer.start(45) # Her 30 ms'de bir kare güncelle

    def stop_camera(self):
        # Kamera durdurma işlevi
        self.running = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.clear()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def update_frame(self):
        # Her kare güncelleme işlevi
        if not self.running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Kameradan görüntü alınamadı.")
            return

        frame_h, frame_w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe ile el algılama
        hands_results = self.hands.process(frame_rgb)

        # InsightFace ile yüz algılama
        faces = self.detector.get(frame)
        
        # El maskesi için boş bir maske oluştur, tüm kare boyutuyla
        hand_mask_overall = np.zeros((frame_h, frame_w), dtype=np.uint8)

        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                points = []
                for lm in hand_landmarks.landmark:
                    points.append([int(lm.x * frame_w), int(lm.y * frame_h)])
                points = np.array(points)

                # MediaPipe'in bağlantılarını kullanarak daha sofistike bir maske oluşturalım.
                temp_hand_mask = np.zeros((frame_h, frame_w), dtype=np.uint8)

                # Her bağlantı için bir çizgi çizerek maske oluştur
                for connection in self.mp_hands.HAND_CONNECTIONS:
                    start_node = connection[0]
                    end_node = connection[1]
                    if start_node < len(points) and end_node < len(points):
                        # Çizgiyi kalın bir şekilde çizerek maske oluşturma
                        cv2.line(temp_hand_mask, 
                                 tuple(points[start_node]), 
                                 tuple(points[end_node]), 
                                 255, 
                                 thickness=5) # Kalınlığı artırarak daha dolgun bir maske elde edebiliriz

                # Çizilen çizgilerin içini doldurmak için konturları bul ve doldur
                contours, _ = cv2.findContours(temp_hand_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    # En büyük konturu bul (genellikle tüm eli kapsayan)
                    largest_contour = max(contours, key=cv2.contourArea)
                    cv2.drawContours(hand_mask_overall, [largest_contour], 0, 255, -1) # Doldurulmuş kontur

        current_frame = frame.copy() # Orijinal kareyi değiştirmemek için kopya al

        if faces and len(faces) > 0 and self.guide_face_obj is not None:
            for face in faces:
                if face.embedding is None:
                    print("Hata: Hedef yüzün embedding'i çıkarılamadı.")
                    continue 
                else:
                    try:
                        # hand_mask_overall'ı INSwapper'a iletiyoruz
                        # INSwapper, bu maskeyi kendi içindeki yüz maskesinden çıkaracak
                        swapped_frame = self.swapper.get(current_frame, face, self.guide_face_obj, hand_mask=hand_mask_overall)
                        current_frame = swapped_frame # Takas edilen kareyi current_frame'e ata
                    except Exception as e:
                        print(f"Face swap hatası: {e}")
                        # Hata durumunda orijinal kareyi kullanmaya devam et, işleme devam et
                        pass 
        
        # PyQt arayüzünde göstermek için kareyi dönüştür
        rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        # Görüntüyü QLabel'e sığdır
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

if __name__ == "__main__":
    print("Uygulama başlatılıyor...")
    app = QApplication(sys.argv)

    # Önce giriş ekranını göster
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted: # Kullanıcı giriş yaptıysa
        window = FaceSwapApp()
        window.show()
        sys.exit(app.exec())
    else: # Kullanıcı iptal ettiyse veya yanlış giriş yaptıysa
        sys.exit(0) # Uygulamayı kapat