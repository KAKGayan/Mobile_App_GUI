import numpy as np
import tkinter as tk
import time
import threading
from customtkinter import *
from PIL import Image, ImageTk
import serial
import cv2
import Human
import queue

# Serial Communication
# ser=serial.Serial('/dev/ttyACM0',9600,timeout=1)
# ser.flush()

gui = CTk()
gui.title("Navigation Control Panel")
gui.geometry("1000x600")
gui.resizable(True, True)
set_appearance_mode("Dark")

# Camera frame
camframe = CTkFrame(gui, width=500, height=300, fg_color="transparent")
camframe.place(x=450, y=100)
cap = cv2.VideoCapture(0)

def show_frames():
    _, frame = cap.read()
    frame = cv2.resize(frame, (600, 500))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    video.imgtk = imgtk
    video.configure(image=imgtk)
    video.after(20, show_frames)

video = CTkLabel(camframe, text=" ")
video.pack()
show_frames()

label_1 = CTkLabel(gui, text="CONTROLLING INTERFACE", fg_color="blue", font=("Agency", 30), text_color="white", corner_radius=15)
label_1.pack()
label2 = CTkLabel(gui, text="Camera Preview", fg_color="red", font=("Agency", 15), text_color="white", corner_radius=15).place(x=450, y=65)

def printt():
    print("Stop")
    # ser.write(b"stop\n")
    time.sleep(1)

def exit_gui():
    exit()

def forward():
    print("forward")
    # ser.write(b"forward\n")
    time.sleep(1)

def backward():
    print("backward")
    # ser.write(b"backward\n")
    time.sleep(1)

def left():
    print("left")
    # ser.write(b"left\n")
    time.sleep(1)

def right():
    print("right")
    # ser.write(b"right\n")
    time.sleep(1)

def control_options():
    # Load images with error handling
    try:
        forward_img = CTkImage(Image.open("up_arrow.png"), size=(50, 50))
        backward_img = CTkImage(Image.open("down_arrow.png"), size=(50, 50))
        left_img = CTkImage(Image.open("left_arrow.png"), size=(50, 50))
        right_img = CTkImage(Image.open("right_arrow.png"), size=(50, 50))
        stop_img = CTkImage(Image.open("stop.png"), size=(50, 50))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Stop button
    stop_btn1 = CTkButton(gui, image=stop_img, text="", width=100, height=100, corner_radius=10, border_width=2, fg_color="red", command=printt).place(x=150, y=300)
    # Forward move button
    forward_btn = CTkButton(gui, image=forward_img, text="", width=100, height=100, corner_radius=10, border_width=2, fg_color="green", command=forward).place(x=150, y=200)
    # Backward move button
    back_btn = CTkButton(gui, image=backward_img, text="", width=100, height=100, corner_radius=10, border_width=2, fg_color="white", command=backward).place(x=150, y=400)
    # Turn left
    left_btn = CTkButton(gui, image=left_img, text="", width=100, height=100, corner_radius=10, border_width=2, fg_color="yellow", command=left).place(x=50, y=300)
    # Turn right
    right_btn = CTkButton(gui, image=right_img, text="", width=100, height=100, corner_radius=10, border_width=2, fg_color="yellow", command=right).place(x=250, y=300)

mode_var = IntVar()

def Select_Mode():
    Auto_mode = CTkRadioButton(gui, text="Autonomous Mode", font=("Agency", 20), fg_color="yellow", text_color="red", value=1, variable=mode_var).place(x=100, y=60)
    Manual_mode = CTkRadioButton(gui, text="Manual Mode", font=("Agency", 20), text_color="red", fg_color="yellow", value=2, variable=mode_var).place(x=100, y=95)
    check = CTkButton(gui, text="Save", fg_color="green", command=Mode).place(x=100, y=140)

selection_mode = threading.Thread(target=Select_Mode, daemon=True)
selection_mode.start()

def Mode():
    val = mode_var.get()
    if val == 1:
        print("Auto")
        Auto_thread = threading.Thread(target=autonomous_mode)
        Auto_thread.start()
    elif val == 2:
        print("Manual")
        manual_thread.start()

def autonomous_mode():
    print("Running autonomous mode")
    # Autonomous mode implementation
    Human.autonomous_mode()

manual_thread = threading.Thread(target=control_options)

# Progress bar for visual feedback
progress_bar = CTkProgressBar(gui, width=300, height=20, border_color="blue", border_width=2, corner_radius=10)
progress_bar.place(x=350, y=550)
progress_bar.set(0.5)  # Set progress bar to 50%

# Exit from the interface
Exit_btn = CTkButton(gui, width=50, height=30, corner_radius=10, border_color="blue", border_width=3, font=("Agency", 20), text="Exit", command=exit_gui, hover_color="red").place(x=900, y=520)

gui.mainloop()
cap.release()
