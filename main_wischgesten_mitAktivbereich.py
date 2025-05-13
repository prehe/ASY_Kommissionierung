import cv2
import mediapipe as mp
import numpy as np

# Mediapipe Hand Tracking setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize variables
hand_tracker = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)
prev_x = None
prev_y = None
swipe_direction = None
gesture_active = False  # Activation state
activation_message = "Gestenerkennung inaktiv"
start_point = None  # Start point of the swipe
last_gesture = ""  # Store the last detected gesture

def is_triangle_gesture(hand_landmarks_list):
    if len(hand_landmarks_list) < 2:
        return False

    # Get landmarks for both hands
    thumb_tip_1 = hand_landmarks_list[0].landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip_1 = hand_landmarks_list[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip_2 = hand_landmarks_list[1].landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip_2 = hand_landmarks_list[1].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # Calculate distances between the points
    d1 = np.sqrt((thumb_tip_1.x - index_tip_2.x) ** 2 + (thumb_tip_1.y - index_tip_2.y) ** 2)
    d2 = np.sqrt((thumb_tip_2.x - index_tip_1.x) ** 2 + (thumb_tip_2.y - index_tip_1.y) ** 2)
    d3 = np.sqrt((thumb_tip_1.x - thumb_tip_2.x) ** 2 + (thumb_tip_1.y - thumb_tip_2.y) ** 2)

    # Check if the distances form a triangle (approximation)
    return d1 < 0.1 and d2 < 0.1 and d3 < 0.1

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hand_tracker.process(rgb_frame)

    if result.multi_hand_landmarks:
        hand_landmarks_list = result.multi_hand_landmarks

        # Check for triangle gesture to deactivate gesture detection
        if is_triangle_gesture(hand_landmarks_list):
            gesture_active = False
            activation_message = "Gestenerkennung inaktiv"
            last_gesture = "Triangle Gesture"

        for hand_landmarks in hand_landmarks_list:
            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the x and y coordinates of the thumb tip and index finger tip
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

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
                # Add a delay before deactivating to avoid immediate reactivation
                if gesture_active:
                    gesture_active = False
                    activation_message = "Gestenerkennung inaktiv"

            # Detect swipe direction only if gesture is active
            if gesture_active:
                # Get the x and y coordinates of the index finger tip (landmark 8)
                fingertip_x = int(index_tip.x * frame.shape[1])
                fingertip_y = int(index_tip.y * frame.shape[0])

                if prev_x is not None and prev_y is not None:
                    if fingertip_x - prev_x > 20:  # Swipe right
                        swipe_direction = "Right"
                        last_gesture = "Swipe Right"
                        gesture_active = False  # Deactivate gesture detection
                        activation_message = "Gestenerkennung inaktiv"
                    elif prev_x - fingertip_x > 20:  # Swipe left
                        swipe_direction = "Left"
                        last_gesture = "Swipe Left"
                        gesture_active = False  # Deactivate gesture detection
                        activation_message = "Gestenerkennung inaktiv"
                    else:
                        swipe_direction = None

                # Update previous coordinates
                prev_x, prev_y = fingertip_x, fingertip_y

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
