import cv2
import time
import numpy as np
from pyzbar.pyzbar import decode
import mediapipe as mp
from ASY_QRCode_Erkennung import highlight_product_qrcodes_from_job, scan_new_job
from ASY_gesten_blöcke import run_gesture_recognition

def init_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(f"Kamera 0 konnte nicht geöffnet werden.")
        assert False, "Kamera konnte nicht geöffnet werden."
    return cap

def close_window(cap):
    cap.release()
    cv2.destroyAllWindows()

def draw_menu(frame, is_submenu_active, main_menu_items, main_menu_positions, submenu_items, submenu_positions, submenu_button_size, menu_button_size):
    if is_submenu_active:
        for i, pos in enumerate(submenu_positions):
            top_left = (pos[0], pos[1])
            bottom_right = (pos[0] + submenu_button_size[0], pos[1] + submenu_button_size[1])
            cv2.rectangle(frame, top_left, bottom_right, (255, 0, 0), 2)
            cv2.putText(frame, submenu_items[i], (top_left[0] + 5, top_left[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    else:
        for i, pos in enumerate(main_menu_positions):
            top_left = (pos[0], pos[1])
            bottom_right = (pos[0] + menu_button_size[0], pos[1] + menu_button_size[1])
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, main_menu_items[i], (top_left[0] + 5, top_left[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def main():
    # Kamera initialisieren
    cap = init_camera()

    # Job-Daten
    job_products = {
        "124343433": ["Platine 234", "Platine 376"],
        "192343324": ["Platine 123"]
    }

    # Initialer Zustand
    state = "gesture_recognition"  # Mögliche Werte: "gesture_recognition", "scan_job", "highlight_products"
    job_id = None

    # Menüeinträge und Positionen für die Gestenerkennung
    main_menu_items = ["vor", "zurueck", "Menue"]
    main_menu_positions = [(510, 350), (10, 350), (10, 125)]
    submenu_items = ["zwischen-\nspeichern", "abbrechen", "zurueck"]
    submenu_positions = [(510, 240), (10, 240), (10, 350)]
    menu_button_size = (100, 100)
    submenu_button_size = (130, 50)

    # Mediapipe-Initialisierung
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Letzter Auslösezeitpunkt für jeden Button
    last_selected_time = [0] * (len(main_menu_items) + len(submenu_items))
    is_submenu_active = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Fehler: Kein gültiges Kamerabild.")
            break

        # Bild spiegeln und in RGB konvertieren
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # **Gestenerkennung**
        if state == "gesture_recognition":
            result = hands.process(rgb_frame)
            draw_menu(frame, is_submenu_active, main_menu_items, main_menu_positions, submenu_items, submenu_positions, submenu_button_size, menu_button_size)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    # Finger-Tap erkennen
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    thumb_coords = (int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0]))
                    index_coords = (int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0]))

                    distance = ((thumb_coords[0] - index_coords[0]) ** 2 + (thumb_coords[1] - index_coords[1]) ** 2) ** 0.5

                    if distance < 30:  # Schwellenwert für Tippgeste
                        current_time = time.time()
                        if is_submenu_active:
                            for i, pos in enumerate(submenu_positions):
                                top_left = (pos[0], pos[1])
                                bottom_right = (pos[0] + submenu_button_size[0], pos[1] + submenu_button_size[1])
                                if top_left[0] <= index_coords[0] <= bottom_right[0] and top_left[1] <= index_coords[1] <= bottom_right[1]:
                                    if current_time - last_selected_time[len(main_menu_items) + i] > 3:
                                        print(f"{submenu_items[i]} ausgewählt")
                                        last_selected_time[len(main_menu_items) + i] = current_time
                                        if submenu_items[i] == "zurueck":
                                            is_submenu_active = False
                                        elif submenu_items[i] == "zwischen-\nspeichern":
                                            print("Zwischenspeichern ausgeführt.")
                                        elif submenu_items[i] == "abbrechen":
                                            print("Programm wird beendet.")
                                            cap.release()
                                            cv2.destroyAllWindows()
                                            return
                        else:
                            for i, pos in enumerate(main_menu_positions):
                                top_left = (pos[0], pos[1])
                                bottom_right = (pos[0] + menu_button_size[0], pos[1] + menu_button_size[1])
                                if top_left[0] <= index_coords[0] <= bottom_right[0] and top_left[1] <= index_coords[1] <= bottom_right[1]:
                                    if current_time - last_selected_time[i] > 3:
                                        print(f"{main_menu_items[i]} ausgewählt")
                                        last_selected_time[i] = current_time
                                        if main_menu_items[i] == "Menue":
                                            is_submenu_active = True
                                        elif main_menu_items[i] == "vor":
                                            state = "scan_job"
                                        elif main_menu_items[i] == "zurueck":
                                            print("Zurück-Aktion ausgeführt.")

        # **QR-Code-Scan für neuen Job**
        elif state == "scan_job":
            decoded_objects = [obj for obj in decode(frame) if obj.type == 'QRCODE']
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                if qr_data in job_products:
                    job_id = qr_data
                    print(f"Neuer Job-ID: {job_id}")
                    state = "highlight_products"
                    break

            cv2.putText(frame, "Scanne QR-Code für neuen Job", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # **Produkte hervorheben**
        elif state == "highlight_products":
            if job_id and job_id in job_products:
                decoded_objects = [obj for obj in decode(frame) if obj.type == 'QRCODE']
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    if qr_data in job_products[job_id]:
                        points = obj.polygon
                        if len(points) > 4:
                            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                            hull = list(map(tuple, np.squeeze(hull)))
                        else:
                            hull = points

                        n = len(hull)
                        for j in range(0, n):
                            cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 0, 255), 2)

                        cv2.putText(frame, qr_data, (obj.rect.left, obj.rect.top - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.putText(frame, "Produkte hervorheben", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Frame anzeigen
        cv2.imshow("ASY System", frame)

        # Beenden mit Taste 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Ressourcen freigeben
    close_window(cap)

if __name__ == "__main__":
    main()
