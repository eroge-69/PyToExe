import cv2
import mediapipe as mp
import numpy as np


class GestureDrawingAppCV:
    def __init__(self):
        self.use_white_bg = False
        self.draw_color = (0, 0, 255)  # Red in BGR
        self.thickness = 40
        self.canvas_image = None

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=10,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

        self.cap = cv2.VideoCapture(0)

    def is_finger_extended(self, lm, tip_id, pip_id, mcp_id):
        tip = np.array([lm[tip_id].x, lm[tip_id].y])
        pip = np.array([lm[pip_id].x, lm[pip_id].y])
        mcp = np.array([lm[mcp_id].x, lm[mcp_id].y])

        v1 = pip - mcp
        v2 = tip - pip
        angle = np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1.0, 1.0))
        angle_deg = np.degrees(angle)

        # Consider finger extended only if angle is low (straight = ~30-60 deg)
        return angle_deg < 45  # Adjust if needed


    def run(self):
        self.last_draw_mask = np.zeros((480, 640), dtype=np.uint8)  # update shape dynamically if needed
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Background toggle
            if self.use_white_bg:
                seg = self.segmentation.process(rgb).segmentation_mask
                seg = cv2.medianBlur((seg * 255).astype(np.uint8), 7)
                seg = seg.astype(np.float32) / 255.0
                seg = np.clip(seg, 0.1, 0.9)
                seg_3d = np.repeat(seg[:, :, np.newaxis], 3, axis=2)
                white_bg = np.ones_like(frame, dtype=np.uint8) * 255
                frame = (frame.astype(np.float32) * seg_3d +
                         white_bg.astype(np.float32) * (1 - seg_3d)).astype(np.uint8)

            if self.canvas_image is None:
                self.canvas_image = np.zeros_like(frame)

            results = self.hands.process(rgb)
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    lm = hand_landmarks.landmark
                    label = handedness.classification[0].label
                    for idx, landmark in enumerate(lm):
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(frame, (cx, cy), 2, (0, 0, 0), -1)

                        if idx == 0:
                            # Display handedness and coordinates
                            label_text = f"{label}: ({cx}, {cy})"
                            cv2.putText(frame, label_text, (cx + 10, cy),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
                        


                    label = handedness.classification[0].label  # 'Left' or 'Right'
                    lm = hand_landmarks.landmark

                    fingers_open = [
                        self.is_finger_extended(lm, 8, 6, 5),   # Index
                        self.is_finger_extended(lm, 12, 10, 9), # Middle
                        self.is_finger_extended(lm, 16, 14, 13),# Ring
                        self.is_finger_extended(lm, 20, 18, 17),# Pinky
                        self.is_finger_extended(lm, 4, 3, 2)    # Thumb (optional)
                    ]

                    palm_open = sum(fingers_open) >= 4

                    # Get hand convex hull
                    hand_points = np.array([
                        [int(lm[i].x * w), int(lm[i].y * h)]
                        for i in range(21)
                    ], dtype=np.int32)

                    if palm_open:
                        hull = cv2.convexHull(hand_points)

                        # Create a blank mask the size of frame
                        palm_mask = np.zeros((h, w), dtype=np.uint8)
                        cv2.fillConvexPoly(palm_mask, hull, 255)

                        # Smooth edges with GaussianBlur
                        palm_mask = cv2.GaussianBlur(palm_mask, (self.thickness//2*2+1, self.thickness//2*2+1), 0)

                        if label == "Right":
                            # DRAW: blend the palm shape gradually into canvas
                            color_layer = np.zeros_like(self.canvas_image)
                            for c in range(3):
                                color_layer[:, :, c] = palm_mask

                            mask_color = cv2.merge([
                                (palm_mask / 255.0 * self.draw_color[0]).astype(np.uint8),
                                (palm_mask / 255.0 * self.draw_color[1]).astype(np.uint8),
                                (palm_mask / 255.0 * self.draw_color[2]).astype(np.uint8)
                            ])
                            self.canvas_image = cv2.addWeighted(self.canvas_image, 1.0, mask_color, 0.5, 0)

                        elif label == "Left":
                            # ERASE: subtract using smoothed palm mask
                            erase_mask = cv2.merge([palm_mask] * 3)
                            self.canvas_image = cv2.bitwise_and(self.canvas_image, cv2.bitwise_not(erase_mask))

            # Blend canvas with frame
            mask = cv2.cvtColor(self.canvas_image, cv2.COLOR_BGR2GRAY)
            _, bin_mask = cv2.threshold(mask, 20, 255, cv2.THRESH_BINARY)
            inv_mask = cv2.bitwise_not(bin_mask)
            bg = cv2.bitwise_and(frame, frame, mask=inv_mask)
            fg = cv2.bitwise_and(self.canvas_image, self.canvas_image, mask=bin_mask)
            output = cv2.add(bg, fg)

            cv2.putText(output, "[q]=Quit  [w]=ToggleBG  [c]=Clear", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.imshow("Gesture Drawing", output)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('w'):
                self.use_white_bg = not self.use_white_bg
            elif key == ord('c'):
                self.canvas_image = np.zeros_like(frame)

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = GestureDrawingAppCV()
    app.run()
