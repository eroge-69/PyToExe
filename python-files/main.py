
import cv2
import mediapipe as mp
import numpy as np

# Inicializa o MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a = np.array(a)  # Primeiro ponto (ombro)
    b = np.array(b)  # Ponto do meio (cotovelo)
    c = np.array(c)  # Último ponto (punho)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle

# Altera para ler do arquivo de vídeo fornecido
video_path = '/home/ubuntu/upload/REDESNEURAISnacâmeradaINTELBRAScomPYTHONeOPENCV.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Erro ao abrir o vídeo: {video_path}")
    exit()

# Configurações para salvar o vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec para .mp4
output_filename = 'output_video.mp4'
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Converte a imagem de BGR para RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Processa a imagem e detecta a pose
        results = pose.process(image)

        # Converte a imagem de volta para BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Obter coordenadas dos pontos chave
            # Ombros
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

            # Cotovelos
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

            # Punhos
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calcular ângulos para os braços
            left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

            # Detectar se os braços estão levemente levantados
            left_arm_raised = False
            right_arm_raised = False

            if left_wrist[1] < left_shoulder[1] + 0.05 and left_arm_angle > 10: 
                left_arm_raised = True
            if right_wrist[1] < right_shoulder[1] + 0.05 and right_arm_angle > 10: 
                right_arm_raised = True

            # Exibir status na tela
            cv2.putText(image, f'Braco Esquerdo Levantado: {left_arm_raised}', 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f'Braco Direito Levantado: {right_arm_raised}', 
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Desenha os landmarks da pose
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                    )

        except:
            pass

        # Escreve o frame no arquivo de saída
        out.write(image)

cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Vídeo processado e salvo como {output_filename}")


