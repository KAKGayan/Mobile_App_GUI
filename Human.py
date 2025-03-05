import cv2
import mediapipe as mp
import math
import time
from multiprocessing import Process, Queue
from threading import Thread
from queue import Empty

# Initialize Mediapipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# PID control parameters
Kp = 1.0
Ki = 0.1
Kd = 0.5
integral = 0
previous_error = 0

left_edge = 165
right_edge = 330
top_edge = 165
bottom_edge = 330

# Grid parameters
num_rows = 3
num_cols = 3

def pid_control(target, current):
    global integral, previous_error
    error = target - current
    integral += error
    derivative = error - previous_error
    output = Kp * error + Ki * integral + Kd * derivative
    previous_error = error
    return output

def autonomous_mode():
    # Start video capture
    cap = cv2.VideoCapture(0)
    frame_count = 0
    skip_frames = 5  # Number of frames to skip

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % skip_frames != 0:
            continue

        # Reduce frame size to lower processing load
        frame = cv2.resize(frame, (500, 500))

        # Draw grid lines
        grid_color = (0, 255, 0)  # Green color for grid lines
        grid_thickness = 3
        row_height = frame.shape[0] // num_rows
        col_width = frame.shape[1] // num_cols

        # Draw horizontal grid lines
        for i in range(1, num_rows):
            cv2.line(frame, (0, i * row_height), (frame.shape[1], i * row_height), grid_color, grid_thickness)

        # Draw vertical grid lines
        for j in range(1, num_cols):
            cv2.line(frame, (j * col_width, 0), (j * col_width, frame.shape[0]), grid_color, grid_thickness)

        start_point = (left_edge, top_edge)
        end_point = (right_edge, bottom_edge)
        color = (0, 0, 255)
        thickness = 5
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb_frame)

        if result.pose_landmarks:
            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Get the coordinates of the shoulders
            left_shoulder_x = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]
            left_shoulder_y = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0]
            right_shoulder_x = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]
            right_shoulder_y = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0]

            left_hip_x = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * frame.shape[1]
            left_hip_y = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * frame.shape[0]
            right_hip_x = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * frame.shape[1]
            right_hip_y = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * frame.shape[0]

            # Calculate the center point between the shoulders
            center_shoulder_x = (left_shoulder_x + right_shoulder_x) / 2
            center_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2

            # Calculate the center point between the hips
            center_hip_x = (left_hip_x + right_hip_x) / 2
            center_hip_y = (right_hip_y + left_hip_y) / 2

            center_x = (center_hip_x + center_shoulder_x) / 2
            center_y = (center_hip_y + center_shoulder_y) / 2

            # Calculate control signal using PID
            frame_center_x = frame.shape[1] / 2
            frame_center_y = frame.shape[0] / 2
            control_signal_x = pid_control(frame_center_x, center_x)
            control_signal_y = pid_control(frame_center_y, center_y)

            center_body = (int(center_x - 20), int(center_y - 20))
            frame_center = (int(frame_center_x), int(frame_center_y))

            cv2.circle(frame, center_body, 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, frame_center, 5, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, center_body, frame_center, (255, 255, 0), 2)
            line_length = math.sqrt((frame_center[0] - center_body[0]) ** 2 + (frame_center[1] - center_body[1]) ** 2)

            # Determine movement command based on position
            if(line_length >= 353):
                print("Skip")
            elif (left_edge <= center_body[0] <= right_edge) and (top_edge <= center_body[1] <= bottom_edge):
                command = "stop"
                print(command)
            elif center_body[0] < left_edge:
                command = "left"
                print(command)
            elif center_body[0] > right_edge:
                command = "right"
                print(command)
            elif center_body[1] < top_edge:
                command = "backward"
                print(command)
            elif center_body[1] > bottom_edge:
                command = "forward"
                print(command)
            else:
                command = "stop"
                print(command)
            
        cv2.imshow('Autonomous Mode', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()