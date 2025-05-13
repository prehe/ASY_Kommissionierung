import cv2
import mediapipe as mp

# Mediapipe initialisieren
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Menüeinträge
menu_items = ["Next", "Back", "Stop"]
menu_positions = [(100, 100), (100, 200), (100, 300)]  # Positionen der Menüeinträge
button_size = (200, 50)  # Breite und Höhe der Buttons

# Funktion zum Zeichnen des Menüs
def draw_menu(image):
    for i, (text, pos) in enumerate(zip(menu_items, menu_positions)):
        top_left = (pos[0], pos[1])
        bottom_right = (pos[0] + button_size[0], pos[1] + button_size[1])
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), -1)  # Grüner Hintergrund
        cv2.putText(image, text, (pos[0] + 10, pos[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Hauptprogramm
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Bild spiegeln und in RGB konvertieren
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Handerkennung
    result = hands.process(rgb_frame)

    # Menü zeichnen
    draw_menu(frame)

    finger_detected = False  # Flag, ob ein Finger erkannt wurde

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Finger-Tap erkennen (Daumenspitze und Zeigefingerspitze nahe beieinander)
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            thumb_coords = (int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0]))
            index_coords = (int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0]))

            distance = ((thumb_coords[0] - index_coords[0]) ** 2 + (thumb_coords[1] - index_coords[1]) ** 2) ** 0.5

            if distance < 30:  # Schwellenwert für Tippgeste
                finger_detected = True
                for i, pos in enumerate(menu_positions):
                    top_left = (pos[0], pos[1])
                    bottom_right = (pos[0] + button_size[0], pos[1] + button_size[1])
                    if top_left[0] <= index_coords[0] <= bottom_right[0] and top_left[1] <= index_coords[1] <= bottom_right[1]:
                        print(f"{menu_items[i]} ausgewählt")

    # Zeige, ob ein Finger erkannt wurde
    status_text = "Finger erkannt" if finger_detected else "Kein Finger erkannt"
    cv2.putText(frame, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if finger_detected else (0, 0, 255), 2)

    cv2.imshow("Menu", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' zum Beenden
        break

cap.release()
cv2.destroyAllWindows()