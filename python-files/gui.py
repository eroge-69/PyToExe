import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageDraw
import joblib
from sklearn.datasets import fetch_openml
from sklearn.decomposition import PCA
from sklearn.svm import SVC
import threading
import time

# Global variables for data and models
X_train_data, y_train_data = None, None
model = None
pca_model = None

# --- GUI Application Class ---
class DigitRecognizerApp:
    def __init__(self, master):
        self.master = master
        master.title("Handwritten Digit Recognizer")

        # Create a frame for the control buttons
        control_frame = tk.Frame(master)
        control_frame.pack(pady=10)

        # Buttons and controls
        self.fetch_button = tk.Button(control_frame, text="Fetch Data", command=self.fetch_data_with_progress)
        self.fetch_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(control_frame, text="Load Models", command=self.load_models)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.train_button = tk.Button(control_frame, text="Train Model", command=self.train_model)
        self.train_button.pack(side=tk.LEFT, padx=5)

        # Training data percentage selection
        self.percentage_label = tk.Label(control_frame, text="Train on:")
        self.percentage_label.pack(side=tk.LEFT, padx=(10, 2))
        
        self.training_percentage = tk.StringVar(master)
        self.training_percentage.set("100%")  # default value
        
        percentages = ["1%","10%", "25%", "50%", "75%","90%", "100%"]
        self.percentage_menu = tk.OptionMenu(control_frame, self.training_percentage, *percentages)
        self.percentage_menu.pack(side=tk.LEFT, padx=5)

        # Labels for status and data count
        self.status_label = tk.Label(master, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.data_count_label = tk.Label(master, text="Training Data: Not Loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.data_count_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Progress bar for training and fetching
        self.progress_bar = ttk.Progressbar(master, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

        # Drawing canvas
        self.canvas_width = 280
        self.canvas_height = 280
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="black", cursor="cross")
        self.canvas.pack(pady=10)
        self.canvas.bind("<B1-Motion>", self.paint)
        
        self.image = Image.new("L", (self.canvas_width, self.canvas_height), 0)
        self.draw = ImageDraw.Draw(self.image)

        # Drawing control buttons
        draw_frame = tk.Frame(master)
        draw_frame.pack(pady=5)

        self.clear_button = tk.Button(draw_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.predict_button = tk.Button(draw_frame, text="Predict", command=self.predict_digit)
        self.predict_button.pack(side=tk.LEFT, padx=5)

        # Result label
        self.result_label = tk.Label(master, text="Prediction: ", font=("Helvetica", 24))
        self.result_label.pack(pady=10)

    # --- Canvas and Prediction Logic ---
    def paint(self, event):
        x1, y1 = (event.x - 10), (event.y - 10)
        x2, y2 = (event.x + 10), (event.y + 10)
        self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="white")
        self.draw.rectangle([x1, y1, x2, y2], fill="white")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw.rectangle((0, 0, self.canvas_width, self.canvas_height), fill="black")
        self.result_label.config(text="Prediction: ")
        self.status_label.config(text="Status: Canvas cleared")

    def predict_digit(self):
        global model, pca_model
        if model is None or pca_model is None:
            messagebox.showerror("Error", "Please load or train the models first.")
            return
        
        img = self.image.resize((28, 28), Image.LANCZOS)
        img_array = np.array(img).reshape(1, -1) / 255.0

        try:
            # Apply PCA to the drawn image
            img_pca = pca_model.transform(img_array)
            
            # Make the prediction using the transformed data
            prediction = model.predict(img_pca)
            self.result_label.config(text=f"Prediction: {prediction[0]}")
            self.status_label.config(text="Status: Prediction completed.")
        except ValueError as e:
            messagebox.showerror("Error", f"Prediction failed: {e}. Check if both PCA and SVM models are loaded correctly.")
            self.status_label.config(text="Status: Prediction failed.")

    # --- Data and Model Logic with Threading and Progress ---
    def _fetch_data_task(self):
        global X_train_data, y_train_data
        
        self.update_progress(0, "Fetching data...")
        time.sleep(1) 
        
        X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)
        X_train_data = X / 255.0
        y_train_data = y
        
        self.update_progress(100, "Data fetched!")
        
        self.master.after(200, lambda: self.finish_data_fetch(len(X_train_data)))

    def fetch_data_with_progress(self):
        self.fetch_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._fetch_data_task)
        thread.start()

    def update_progress(self, value, message):
        self.progress_bar['value'] = value
        self.status_label.config(text=f"Status: {message}")
        self.master.update_idletasks()

    def finish_data_fetch(self, data_size):
        self.data_count_label.config(text=f"Training Data: {data_size} samples")
        self.status_label.config(text="Status: Data loaded successfully.")
        self.fetch_button.config(state=tk.NORMAL)

    def load_models(self):
        global model, pca_model
        svm_path = filedialog.askopenfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")], title="Select the SVM model file (mnist_svm_model.pkl)")
        if not svm_path:
            return

        pca_path = filedialog.askopenfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")], title="Select the PCA model file (pca_transformer.pkl)")
        if not pca_path:
            return
            
        try:
            model = joblib.load(svm_path)
            pca_model = joblib.load(pca_path)
            self.status_label.config(text="Status: Models loaded successfully!")
            messagebox.showinfo("Success", "Models loaded successfully!")
        except Exception as e:
            self.status_label.config(text=f"Status: Error loading models: {e}")
            messagebox.showerror("Error", f"Could not load the models: {e}")
    
    def train_model(self):
        global model, pca_model, X_train_data, y_train_data
        if X_train_data is None:
            messagebox.showerror("Error", "Please fetch data first before training.")
            return

        self.train_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Training started...")
        self.progress_bar.start()

        percentage_str = self.training_percentage.get().replace('%', '')
        percentage = int(percentage_str) / 100
        num_samples = int(len(X_train_data) * percentage)
        
        def _training_task():
            # Step 1: Train the PCA model
            self.update_progress(10, "Training PCA...")
            pca_model = PCA(n_components=50)  # Assuming 50 components from your report
            X_transformed = pca_model.fit_transform(X_train_data[:num_samples])

            # Step 2: Train the SVM model on the transformed data
            self.update_progress(50, "Training SVM...")
            model = SVC(kernel='rbf', C=10)
            model.fit(X_transformed, y_train_data[:num_samples])

            # Step 3: Save both models
            self.update_progress(80, "Saving models...")
            try:
                joblib.dump(model, 'mnist_svm_model.pkl')
                joblib.dump(pca_model, 'pca_transformer.pkl')
                self.status_label.config(text=f"Status: Training on {num_samples} samples completed! Models saved as mnist_svm_model.pkl and pca_transformer.pkl")
            except Exception as e:
                self.status_label.config(text=f"Status: Training completed, but error saving models: {e}")

            self.master.after(0, self.finish_training)

        thread = threading.Thread(target=_training_task)
        thread.start()

    def finish_training(self):
        self.progress_bar.stop()
        self.progress_bar['value'] = 0
        self.train_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "Model training and saving completed!")

# --- Main part of the application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DigitRecognizerApp(root)
    root.mainloop()