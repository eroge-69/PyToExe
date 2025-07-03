import cv2
import time

def capture_et_affiche():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erreur : impossible d'accéder à la webcam")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erreur lors de la capture.")
                break

            cv2.namedWindow("Webcam", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Webcam", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Webcam", frame)

            cv2.waitKey(1000)  # Affiche 1 seconde
            cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print("Arrêt manuel.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_et_affiche()

