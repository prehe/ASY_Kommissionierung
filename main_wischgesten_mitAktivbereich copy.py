import cv2
import mediapipe as mp
import numpy as np
import time

# Mediapipe Hand Tracking setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize variables
hand_tracker = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)
prev_x = None
prev_y = None
gesture_active = False  # Activation state
activation_message = "Gestenerkennung inaktiv"
start_point = None  # Start point of the swipe
last_gesture = ""  # Store the last detected gesture
last_gesture_time = 0  # Time of the last detected gesture
cooldown_time = 2  # Cooldown time in seconds

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hand_tracker.process(rgb_frame)

    # Define the region for gesture detection (top 40% of the frame)
    frame_height = frame.shape[0]
    gesture_region_end = int(frame_height * 0.4)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get the y-coordinate of the index finger tip
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            fingertip_y = int(index_tip.y * frame.shape[0])

            # Skip gesture detection if the fingertip is in the top 40% of the frame
            if fingertip_y < gesture_region_end:
                continue

            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the x and y coordinates of the thumb tip and index finger tip
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Calculate the distance between thumb tip and index finger tip
            thumb_index_distance = np.sqrt(
                (thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2
            )
            # Check for "thumbs up" gesture (distance is small)
            if thumb_index_distance < 0.05:
                if not gesture_active:
                    gesture_active = True
                    activation_message = "Gestenerkennung aktiv"
            else:
                if gesture_active:
                    gesture_active = False
                    activation_message = "Gestenerkennung inaktiv"

            # Detect swipe direction only if gesture is active and cooldown has passed
            current_time = time.time()
            if gesture_active and current_time - last_gesture_time > cooldown_time:
                fingertip_x = int(index_tip.x * frame.shape[1])

                if prev_x is not None and prev_y is not None:
                    if fingertip_x - prev_x > 50:  # Swipe right
                        last_gesture = "Swipe Right"
                        start_point = (prev_x, prev_y)  # Save the start point
                        gesture_active = False
                        activation_message = "Gestenerkennung inaktiv"
                        last_gesture_time = current_time
                    elif prev_x - fingertip_x > 50:  # Swipe left
                        last_gesture = "Swipe Left"
                        start_point = (prev_x, prev_y)  # Save the start point
                        gesture_active = False
                        activation_message = "Gestenerkennung inaktiv"
                        last_gesture_time = current_time
                    elif prev_y - fingertip_y > 50:  # Swipe up
                        last_gesture = "Swipe Up"
                        start_point = (prev_x, prev_y)  # Save the start point
                        gesture_active = False
                        activation_message = "Gestenerkennung inaktiv"
                        last_gesture_time = current_time

                prev_x, prev_y = fingertip_x, fingertip_y

    # Draw the swipe line if a start point exists
    if start_point and prev_x is not None and prev_y is not None:
        cv2.line(frame, start_point, (prev_x, prev_y), (255, 0, 0), 2)

    # Display the last detected gesture
    if last_gesture:
        cv2.putText(frame, f"Last Gesture: {last_gesture}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display activation message on the frame
    cv2.putText(frame, activation_message, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show the frame
    cv2.imshow("Hand Gesture Tracking", frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
