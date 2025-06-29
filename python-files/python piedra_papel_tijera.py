import cv2
import mediapipe as mp

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Configurar detección de manos
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Captura de video
cap = cv2.VideoCapture(0)

def detectar_gesto(mano_landmarks):
    dedos = []

    # Índice de landmarks de la punta de cada dedo
    tips_ids = [4, 8, 12, 16, 20]

    # Pulgar
    if mano_landmarks.landmark[tips_ids[0]].x < mano_landmarks.landmark[tips_ids[0] - 1].x:
        dedos.append(1)
    else:
        dedos.append(0)

    # Otros 4 dedos
    for i in range(1, 5):
        if mano_landmarks.landmark[tips_ids[i]].y < mano_landmarks.landmark[tips_ids[i] - 2].y:
            dedos.append(1)
        else:
            dedos.append(0)

    # Clasificar gesto
    total_dedos = dedos.count(1)
    if total_dedos == 0:
        return "Piedra"
    elif total_dedos == 2 and dedos[1] == 1 and dedos[2] == 1:
        return "Tijera"
    elif total_dedos == 5:
        return "Papel"
    else:
        return "Desconocido"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Voltear imagen para efecto espejo
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    texto_gesto = "No detectado"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            texto_gesto = detectar_gesto(hand_landmarks)

            # Dibujar puntos de referencia de la mano
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Mostrar texto en pantalla
    cv2.putText(frame, f"Gesto: {texto_gesto}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Piedra, Papel o Tijera", frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
