# aug_14_2.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Only show errors
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model # ADDED
import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2

# --- Function to be called from the login GUI ---
def activity_test(user_id):
    #---------- CONFIGURATION ----------
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "v12",
        "database": "mysql"
    }
    # Path to your dataset
    dataset_dir = r"C:/Users/vaishnavi1/SEM5/INTERNSHIP/internshipclasscode/dataset"
    
    # ADDED: Path to save/load your trained model
    MODEL_PATH = "human_activity_model.h5"

    # ---------- DATABASE HELPER FUNCTION ----------
    def insert_activity_db(user_id, activity, confidence):
        if not all([user_id, activity, confidence is not None]):
            print("DB Warning: Missing data for database insertion.")
            return
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            insert_q = "INSERT INTO activity_log (user_id, activity, confidence) VALUES (%s, %s, %s)"
            cursor.execute(insert_q, (user_id, activity, float(confidence)))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Activity '{activity}' successfully saved to the database.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect or insert data: {err}")

    # ---------- MODEL AND DATA PREPARATION ----------
    if not os.path.exists(dataset_dir):
        messagebox.showerror("File Error", f"Dataset directory not found at '{dataset_dir}'")
        return

    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "validation")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        messagebox.showerror("File Error", f"'train' or 'validation' subdirectories not found in '{dataset_dir}'")
        return
        
    train_datagen = ImageDataGenerator(rescale=1./255)
    train_gen = train_datagen.flow_from_directory(
        train_dir, target_size=(150, 150), batch_size=32, class_mode='categorical', shuffle=True
    )

    val_datagen = ImageDataGenerator(rescale=1./255)
    val_gen = val_datagen.flow_from_directory(
        val_dir, target_size=(150, 150), batch_size=32, class_mode='categorical'
    )

    # --- CHANGED: LOAD MODEL IF IT EXISTS, OTHERWISE TRAIN AND SAVE IT ---
    if os.path.exists(MODEL_PATH):
        print(f"Loading existing model from {MODEL_PATH}...")
        model = load_model(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        print(f"No saved model found. Training a new model...")
        model = tf.keras.models.Sequential([
            tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2,2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(train_gen.num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        model.summary()
        
        print("\nStarting model training...")
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=5,
            steps_per_epoch=max(1, train_gen.samples // train_gen.batch_size),
            validation_steps=max(1, val_gen.samples // val_gen.batch_size)
        )
        print("Model training complete.")
        model.save(MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")

    # ------------------ TKINTER GUI APPLICATION ---------------------------------------
    class HARApp:
        def __init__(self, root, model, class_labels, user_id=None):
            self.root = root
            # ... (the rest of your HARApp class is fine and does not need changes) ...
            # ... I am omitting it here for brevity but you should keep it as is ...
            self.root = root
            self.root.title("Live Human Activity Recognition")
            self.root.geometry("600x700")
            self.root.configure(bg="#f0f0f0")

            self.model = model
            self.class_labels = class_labels
            self.user_id = user_id

            # --- State variables for camera and prediction ---
            self.last_activity = None
            self.last_confidence = None
            self.is_camera_on = False
            self.video_capture = None

            # --- Create and configure widgets ---
            style = ttk.Style()
            style.configure("TButton", font=("Helvetica", 10), padding=5)
            style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")

            main_frame = tk.Frame(root, bg="#f0f0f0")
            main_frame.pack(padx=10, pady=10, fill="both", expand=True)
            
            # --- Camera Control Frame ---
            control_frame = tk.Frame(main_frame, bg="#f0f0f0")
            control_frame.pack(pady=5)
            
            self.start_button = tk.Button(control_frame, text="Start Camera", command=self.start_camera, bg="#007bff", fg="white", font=("Helvetica", 11, "bold"))
            self.start_button.grid(row=0, column=0, padx=5)
            
            self.stop_button = tk.Button(control_frame, text="Stop Camera", command=self.stop_camera, bg="#dc3545", fg="white", font=("Helvetica", 11, "bold"), state="disabled")
            self.stop_button.grid(row=0, column=1, padx=5)

            # Label to display the video feed
            self.image_label = tk.Label(main_frame, bg="lightgray", relief="groove", text="Camera feed will appear here")
            self.image_label.pack(pady=10, fill="both", expand=True)
            
            # Labels to show prediction results
            self.activity_var = tk.StringVar(value="Activity: -")
            self.conf_var = tk.StringVar(value="Confidence: -")
            ttk.Label(main_frame, textvariable=self.activity_var, font=("Helvetica", 16, "bold")).pack()
            ttk.Label(main_frame, textvariable=self.conf_var, font=("Helvetica", 14)).pack(pady=(0,10))

            # Button to submit the result to the database
            tk.Button(main_frame, text="Submit to Database", command=self.save_to_db, bg="#28a745", fg="white", font=("Helvetica", 11, "bold")).pack(pady=10)

            # Ensure camera is released on window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        def start_camera(self):
            self.video_capture = cv2.VideoCapture(0) # 0 is the default camera
            if not self.video_capture.isOpened():
                messagebox.showerror("Camera Error", "Unable to access the camera.")
                return
                
            self.is_camera_on = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.update_video_feed()

        def stop_camera(self):
            self.is_camera_on = False
            if self.video_capture:
                self.video_capture.release()
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.reset_ui()

        def update_video_feed(self):
            if not self.is_camera_on:
                return

            ret, frame = self.video_capture.read()
            if not ret:
                print("Failed to grab frame")
                self.stop_camera()
                return

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.image_label.config(image=img_tk, text="")
            self.image_label.image = img_tk

            img_resized = cv2.resize(frame, (150, 150))
            img_array = image.img_to_array(img_resized) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            prediction = self.model.predict(img_array)
            predicted_class_index = np.argmax(prediction)
            
            self.last_activity = self.class_labels[predicted_class_index]
            self.last_confidence = np.max(prediction) * 100

            self.activity_var.set(f"Activity: {self.last_activity}")
            self.conf_var.set(f"Confidence: {self.last_confidence:.2f}%")

            self.root.after(30, self.update_video_feed)

        def save_to_db(self):
            if not self.last_activity:
                messagebox.showwarning("No Data", "No activity has been detected yet.")
                return
            
            insert_activity_db(self.user_id, self.last_activity, self.last_confidence)
            messagebox.showinfo("Success", "Your activity is saved.")

        def reset_ui(self):
            self.image_label.config(image="", text="Camera feed will appear here", bg="lightgray")
            self.image_label.image = None
            self.activity_var.set("Activity: -")
            self.conf_var.set("Confidence: -")
            self.last_activity = None
            self.last_confidence = None

        def on_closing(self):
            self.stop_camera()
            self.root.destroy()

    # ---------- SCRIPT EXECUTION ----------
    class_labels = list(train_gen.class_indices.keys())
    # This now creates the main window for the activity recognition part
    root = tk.Tk() 
    app = HARApp(root, model=model, class_labels=class_labels, user_id=user_id)
    root.mainloop()