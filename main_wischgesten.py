"""Hand Gesture Tracking using OpenCV and Mediapipe."""

import cv2
import mediapipe as mp  # type: ignore
import numpy as np

# Mediapipe Hand Tracking setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize variables
PREV_X = None
PREV_Y = None
SWIPE_DIRECTION = None
START_POINT = None  # Start point of the swipe
GESTURE_ACTIVE = False  # Activation state

# Initialize video capture
cap = cv2.VideoCapture(0)

# Mediapipe Hands instance
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hand_tracker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # Process the frame with Mediapipe
        result = hand_tracker.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the x and y coordinates of the thumb tip and index finger tip
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                # Calculate the distance between thumb tip and index finger tip
                thumb_index_distance = np.sqrt(
                    (thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2
                )

                if thumb_index_distance < 0.05:  # Threshold for gesture activation
                    GESTURE_ACTIVE = True
                    cv2.putText(
                        frame,
                        "Gesture Activated",
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )  # Display gesture activation
                else:
                    GESTURE_ACTIVE = False

                # Get the fingertip coordinates
                fingertip_x = int(index_tip.x * frame.shape[1])
                fingertip_y = int(index_tip.y * frame.shape[0])

                if PREV_X is not None and PREV_Y is not None:
                    if fingertip_x - PREV_X > 25:  # Swipe right
                        SWIPE_DIRECTION = "Right"
                        if not GESTURE_ACTIVE:  # Reset start point if gesture is not active
                            START_POINT = (PREV_X, PREV_Y)
                    elif PREV_X - fingertip_x > 25:  # Swipe left
                        SWIPE_DIRECTION = "Left"
                        if not GESTURE_ACTIVE:  # Reset start point if gesture is not active
                            START_POINT = (PREV_X, PREV_Y)
                    else:
                        START_POINT = None  # Reset start point if no swipe detected

                PREV_X, PREV_Y = fingertip_x, fingertip_y

        # Draw the swipe path
        if START_POINT and PREV_X is not None and PREV_Y is not None:
            cv2.line(
                frame,
                START_POINT,
                (PREV_X, PREV_Y),
                (0, 255, 0),
                2
            )  # Draw swipe path
            cv2.putText(
                frame,
                f"Swipe: {SWIPE_DIRECTION}",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        # Show the frame
        cv2.imshow("Hand Gesture Tracking", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
