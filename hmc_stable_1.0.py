# Author : Skyzen Labs
# Created : 2026-01-22
# Version : 1.0
# Open Source : Allowed

import cv2
import pyautogui
import time
import mediapipe as mp
import os

# -----------------------------
# Mediapipe Setup
# -----------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# -----------------------------
# Screen Settings
# -----------------------------
screen_w, screen_h = pyautogui.size()
alt_tab_active = False

# -----------------------------
# Helper Functions
# -----------------------------
def get_distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def minimize_all_windows():
    pyautogui.hotkey('win', 'd')

def lock_screen():
    os.system("rundll32.exe user32.dll,LockWorkStation")

def alt_tab_start():
    pyautogui.keyDown('alt')

def alt_tab_end():
    pyautogui.keyUp('alt')

# -----------------------------
# Camera
# -----------------------------
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]

        # Finger tips
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]

        # Convert to screen coordinates
        thumb_pos = (int(thumb_tip.x * screen_w), int(thumb_tip.y * screen_h))
        index_pos = (int(index_tip.x * screen_w), int(index_tip.y * screen_h))
        middle_pos = (int(middle_tip.x * screen_w), int(middle_tip.y * screen_h))
        ring_pos = (int(ring_tip.x * screen_w), int(ring_tip.y * screen_h))

        # Distances
        dist_index_thumb = get_distance(index_pos, thumb_pos)
        dist_middle_thumb = get_distance(middle_pos, thumb_pos)
        dist_ring_thumb = get_distance(ring_pos, thumb_pos)

        # Gestures
        if dist_index_thumb < 40:
            minimize_all_windows()
            time.sleep(0.5)

        elif dist_middle_thumb < 40:
            lock_screen()
            time.sleep(0.5)

        elif dist_ring_thumb < 40:
            if not alt_tab_active:
                alt_tab_start()
                alt_tab_active = True
            # Move mouse to the ring finger coordinates to visualize choice (optional)
            pyautogui.moveTo(ring_pos[0], ring_pos[1], duration=0.01)
        else:
            if alt_tab_active:
                alt_tab_end()
                alt_tab_active = False

        # Draw landmarks
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("HMC2 - Hand Mouse Control 2", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        if alt_tab_active:
            alt_tab_end()
        break

cap.release()
cv2.destroyAllWindows()