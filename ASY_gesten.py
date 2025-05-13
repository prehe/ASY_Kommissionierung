import cv2
import mediapipe as mp
import numpy as np
import time
import math

# Mediapipe Setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hand_tracker = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

cap = cv2.VideoCapture(0)

# Statusvariablen
prev_x = None
prev_y = None
gesture_detection_active = False  # Gesteneingabe aktiv/inaktiv
gesture_message = "Gesteneingabe inaktiv"
last_gesture = ""
gesture_circle_points = []

# Cooldown für Triangle-Geste
last_toggle_time = 0
cooldown_seconds = 3

# Distanzberechnung
def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Triangle-Geste prüfen
def is_triangle_gesture(hand_landmarks_list, image_width, image_height):
    if len(hand_landmarks_list) != 2:
        return False

    hand1 = hand_landmarks_list[0]
    hand2 = hand_landmarks_list[1]

    thumb1 = hand1.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb2 = hand2.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index1 = hand1.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index2 = hand2.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    thumb1_px = (int(thumb1.x * image_width), int(thumb1.y * image_height))
    thumb2_px = (int(thumb2.x * image_width), int(thumb2.y * image_height))
    index1_px = (int(index1.x * image_width), int(index1.y * image_height))
    index2_px = (int(index2.x * image_width), int(index2.y * image_height))

    threshold = 50  # Pixel
    thumbs_close = distance(thumb1_px, thumb2_px) < threshold
    indexes_close = distance(index1_px, index2_px) < threshold

    return thumbs_close and indexes_close

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    gesture_circle_points.clear()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hand_tracker.process(rgb_frame)

    current_time = time.time()

    # Triangle-Geste mit Cooldown prüfen (nur bei 2 Händen)
    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        if is_triangle_gesture(result.multi_hand_landmarks, width, height):
            if current_time - last_toggle_time > cooldown_seconds:
                gesture_detection_active = not gesture_detection_active
                gesture_message = "Gesteneingabe aktiv" if gesture_detection_active else "Gesteneingabe inaktiv"
                last_gesture = "Triangle Gesture"
                last_toggle_time = current_time  # Cooldown-Zeit setzen

    if result.multi_hand_landmarks and gesture_detection_active:
        for hand_landmarks in result.multi_hand_landmarks:
            # Handverbindungen zeichnen
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            thumb_px = (int(thumb_tip.x * width), int(thumb_tip.y * height))
            index_px = (int(index_tip.x * width), int(index_tip.y * height))
            thumb_index_distance = distance(thumb_px, index_px)

            # Daumen an Zeigefinger erkennen
            if thumb_index_distance < 30:
                center_x = (thumb_px[0] + index_px[0]) // 2
                center_y = (thumb_px[1] + index_px[1]) // 2
                gesture_circle_points.append((center_x, center_y))

                if prev_x is not None and prev_y is not None:
                    dx = index_px[0] - prev_x
                    dy = index_px[1] - prev_y
                    swipe_distance = math.hypot(dx, dy)

                    if swipe_distance > 25:  # Mindestlänge des Swipes
                        angle = math.degrees(math.atan2(-dy, dx))  # -dy, weil y-Achse nach unten zeigt in OpenCV

                        if -45 <= angle <= 45:
                            last_gesture = "Swipe Right"
                        elif 45 < angle <= 135:
                            last_gesture = "Swipe Up"
                        elif -135 <= angle < -45:
                            last_gesture = "Swipe Down"
                        else:
                            last_gesture = "Swipe Left"
                        
                prev_x, prev_y = index_px[0], index_px[1]

    # Kreis zur Geste anzeigen
    if gesture_detection_active:
        for x, y in gesture_circle_points:
            cv2.circle(frame, (x, y), 20, (255, 0, 255), -1)

    # Statusanzeige
    if last_gesture:
        cv2.putText(frame, f"Letzte Geste: {last_gesture}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, gesture_message, (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Hand Gesture Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
