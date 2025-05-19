import cv2
import mediapipe as mp
import time  
import os

# Funktion zum Zeichnen des Menüs
def draw_menu(image, is_submenu_active, main_menu_items, main_menu_positions, submenu_items, submenu_positions, submenu_button_size, menu_button_size):
    if is_submenu_active:
        # Zeichne das Untermenü
        for i, (text, pos) in enumerate(zip(submenu_items, submenu_positions)):
            top_left = (pos[0], pos[1])
            bottom_right = (pos[0] + submenu_button_size[0], pos[1] + submenu_button_size[1])
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), -1)  # Grüner Hintergrund
            for j, line in enumerate(text.split("\n")):  # Zeilenumbruch berücksichtigen
                cv2.putText(image, line, (pos[0] + 10, pos[1] + 20 + j * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    else:
        # Zeichne das Hauptmenü
        for i, (text, pos) in enumerate(zip(main_menu_items, main_menu_positions)):
            top_left = (pos[0], pos[1])
            bottom_right = (pos[0] + menu_button_size[0], pos[1] + menu_button_size[1])
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), -1)  # Grüner Hintergrund
            cv2.putText(image, text, (pos[0] + 10, pos[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

def run_gesture_recognition(cap):
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Menüeinträge und Positionen für den Haupt- und Untermenüzustand
    main_menu_items = ["vor", "zurueck", "Menue"]
    main_menu_positions = [(510, 350), (10, 350), (10, 125)]  # Positionen der Hauptmenüeinträge

    submenu_items = ["zwischen-\nspeichern", "abbrechen", "zurueck"]
    submenu_positions = [(510, 240), (10, 240), (10, 350)]  # Positionen der Untermenüeinträge

    menu_button_size = (100, 100)  # Breite und Höhe der Buttons
    submenu_button_size = (130, 50)  # Breite und Höhe der Untermenü-Buttons

    # Letzter Auslösezeitpunkt für jeden Button (Haupt- und Untermenü)
    last_selected_time = [0] * (len(main_menu_items) + len(submenu_items))  # Initialisiere mit 0 für jeden Button

    is_submenu_active = False  # Flag, um den Zustand des Menüs zu verfolgen

    # Bereich definieren, in dem keine Gestenerkennung stattfinden soll
    ignore_area_top_left = (150, 0)  # Obere linke Ecke des zu ignorierenden Bereichs
    ignore_area_bottom_right = (500, 480)  # Untere rechte Ecke des zu ignorierenden Bereichs

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame is None:  # Überprüfen, ob das Frame gültig ist
            print("Fehler: Kein gültiges Kamerabild.")
            break

        # Bild spiegeln und in RGB konvertieren
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Handerkennung
        result = hands.process(rgb_frame)

        # Menü zeichnen
        draw_menu(frame, is_submenu_active, main_menu_items, main_menu_positions, submenu_items, submenu_positions, submenu_button_size, menu_button_size)

        finger_detected = False  # Flag, um zu überprüfen, ob ein Finger erkannt wurde
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:

                # Finger-Tap erkennen (Daumenspitze und Zeigefingerspitze nahe beieinander)
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                thumb_coords = (int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0]))
                index_coords = (int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0]))

                # Zeichne eine blaue Kugel um Daumen und Zeigefinger, wenn sie nah beieinander sind
                distance = ((thumb_coords[0] - index_coords[0]) ** 2 + (thumb_coords[1] - index_coords[1]) ** 2) ** 0.5

                # Überprüfen, ob die Koordinaten außerhalb des zu ignorierenden Bereichs liegen
                if not (ignore_area_top_left[0] <= index_coords[0] <= ignore_area_bottom_right[0] and
                        ignore_area_top_left[1] <= index_coords[1] <= ignore_area_bottom_right[1]):
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    if distance < 30:  # Schwellenwert für Nähe
                        cv2.circle(frame, thumb_coords, 15, (255, 0, 0), -1)  # Blaue Kugel um Daumen
                        cv2.circle(frame, index_coords, 15, (255, 0, 0), -1)  # Blaue Kugel um Zeigefinger

                    if distance < 30:  # Schwellenwert für Tippgeste
                        finger_detected = True
                        current_time = time.time()  # Aktuelle Zeit in Sekunden
                        if is_submenu_active:
                            # Überprüfen, ob ein Untermenü-Button gedrückt wurde
                            for i, pos in enumerate(submenu_positions):
                                top_left = (pos[0], pos[1])
                                bottom_right = (pos[0] + submenu_button_size[0], pos[1] + submenu_button_size[1])
                                if top_left[0] <= index_coords[0] <= bottom_right[0] and top_left[1] <= index_coords[1] <= bottom_right[1]:
                                    if current_time - last_selected_time[len(main_menu_items) + i] > 3:  # 3 Sekunden Sperrzeit
                                        print(f"{submenu_items[i]} ausgewählt")
                                        latest_selected = submenu_items[i]
                                        last_selected_time[len(main_menu_items) + i] = current_time  # Zeitstempel aktualisieren
                                        if submenu_items[i] == "zurueck":
                                            is_submenu_active = False  # Zurück zum Hauptmenü
                                        if submenu_items[i] == "zwischen-\nspeichern":
                                            # Aktion für "zwischen-\nspeichern" hier hinzufügen
                                            pass
                                        if submenu_items[i] == "abbrechen":
                                            # kill die python anwendung
                                            os._exit(0)
                        else:
                            # Überprüfen, ob ein Hauptmenü-Button gedrückt wurde
                            for i, pos in enumerate(main_menu_positions):
                                top_left = (pos[0], pos[1])
                                bottom_right = (pos[0] + menu_button_size[0], pos[1] + menu_button_size[1])
                                if top_left[0] <= index_coords[0] <= bottom_right[0] and top_left[1] <= index_coords[1] <= bottom_right[1]:
                                    if current_time - last_selected_time[i] > 3:  # 3 Sekunden Sperrzeit
                                        print(f"{main_menu_items[i]} ausgewählt")
                                        latest_selected = main_menu_items[i]
                                        last_selected_time[i] = current_time  # Zeitstempel aktualisieren
                                        if main_menu_items[i] == "Menue":
                                            is_submenu_active = True  # Wechsel ins Untermenü
                                        if main_menu_items[i] == "vor":
                                            # Aktion für "vor" hier hinzufügen
                                            pass
                                        if main_menu_items[i] == "zurueck":
                                            # Aktion für "zurueck" hier hinzufügen
                                            pass

        # Zeichne den zu ignorierenden Bereich (optional, zur Visualisierung)
        cv2.rectangle(frame, ignore_area_top_left, ignore_area_bottom_right, (0, 0, 255), 2)

        cv2.imshow("Menu", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' zum Beenden
            break