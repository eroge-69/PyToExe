import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from xgboost import XGBRegressor
import joblib
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.preprocessing import StandardScaler

 
# Load model
try:
    model = joblib.load("xgb_flood_prediction.pkl")
except FileNotFoundError:
    model = None
 
features = {
    'MonsoonIntensity': '(0-16)',
    'TopographyDrainage': '(0-18)',
    'RiverManagement': '(0-16)',
    'Deforestation': '(0-17)',
    'Urbanization': '(0-17)',
    'ClimateChange': '(0-17)',
    'DamsQuality': '(0-16)',
    'Siltation': '(0-16)',
    'AgriculturalPractices': '(0-16)',
    'Encroachments': '(0-18)',
    'IneffectiveDisasterPreparedness': '(0-16)',
    'DrainageSystems': '(0-17)',
    'CoastalVulnerability': '(0-17)',
    'Landslides': '(0-16)',
    'Watersheds': '(0-16)',
    'DeterioratingInfrastructure': '(0-17)',
    'PopulationScore': '(0-19)',
    'WetlandLoss': '(0-22)',
    'InadequatePlanning': '(0-16)',
    'PoliticalFactors': '(0-16)'
}
 
class FloodApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌊 Flood Risk Prediction App")
        self.df = None
        self.input_entries = {}
 
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')
 
        self.create_home_tab()
        self.create_hist_tab()
        self.create_box_tab()
        self.create_corr_tab()
        self.create_dendro_tab()
        self.create_feature_importance_tab()
        self.create_predict_tab()





    def create_home_tab(self):
        home_tab = tk.Frame(self.notebook, bg="#E0F7FA")
        self.notebook.add(home_tab, text="🏠 Home")
 
        tk.Label(home_tab, text="Flood Risk Prediction System", font=("Arial", 20, "bold"), bg="#E0F7FA", fg="#00796B").pack(pady=20)
 
        tk.Button(
            home_tab,
            text="📂 Upload CSV File",
            command=self.upload_csv,
            font=("Helvetica", 16),
            bg="#0288D1",
            fg="white",
            height=2,
            width=25
        ).pack(pady=30)
 
        self.info_label = tk.Label(home_tab, text="", font=("Helvetica", 14), bg="#E0F7FA", fg="#004D40")
        self.info_label.pack()
 
    def create_hist_tab(self):
        self.hist_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.hist_tab, text="📊 Histograms")
 
    def create_box_tab(self):
        self.box_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.box_tab, text="📦 Boxplots")
 
    def create_corr_tab(self):
        self.corr_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.corr_tab, text="📈 Correlation Matrix")
 
        # Setup scrollable canvas inside corr_tab with both vertical and horizontal scrollbars
        self.corr_canvas = tk.Canvas(self.corr_tab, bg="white")
        self.corr_v_scrollbar = tk.Scrollbar(self.corr_tab, orient="vertical", command=self.corr_canvas.yview)
        self.corr_h_scrollbar = tk.Scrollbar(self.corr_tab, orient="horizontal", command=self.corr_canvas.xview)
 
        self.corr_v_scrollbar.pack(side="right", fill="y")
        self.corr_h_scrollbar.pack(side="bottom", fill="x")
        self.corr_canvas.pack(side="left", fill="both", expand=True)
 
        self.corr_canvas.configure(yscrollcommand=self.corr_v_scrollbar.set, xscrollcommand=self.corr_h_scrollbar.set)
        self.corr_canvas.bind('<Configure>', lambda e: self.corr_canvas.configure(scrollregion=self.corr_canvas.bbox("all")))
 
        self.corr_frame = tk.Frame(self.corr_canvas, bg="white")
        self.corr_canvas.create_window((0, 0), window=self.corr_frame, anchor="nw")
 
    def create_dendro_tab(self):
        self.dendro_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.dendro_tab, text="🧬 Dendrogram")

        # Setup scrollable canvas inside dendro_tab with vertical and horizontal scrollbars
        self.dendro_canvas = tk.Canvas(self.dendro_tab, bg="white")
        self.dendro_v_scrollbar = tk.Scrollbar(self.dendro_tab, orient="vertical", command=self.dendro_canvas.yview)
        self.dendro_h_scrollbar = tk.Scrollbar(self.dendro_tab, orient="horizontal", command=self.dendro_canvas.xview)

        self.dendro_v_scrollbar.pack(side="right", fill="y")
        self.dendro_h_scrollbar.pack(side="bottom", fill="x")
        self.dendro_canvas.pack(side="left", fill="both", expand=True)

        self.dendro_canvas.configure(yscrollcommand=self.dendro_v_scrollbar.set, xscrollcommand=self.dendro_h_scrollbar.set)
        self.dendro_canvas.bind('<Configure>', lambda e: self.dendro_canvas.configure(scrollregion=self.dendro_canvas.bbox("all")))

        self.dendro_frame = tk.Frame(self.dendro_canvas, bg="white")
        self.dendro_canvas.create_window((0, 0), window=self.dendro_frame, anchor="nw")


    def create_feature_importance_tab(self):
        self.feature_tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.feature_tab, text="⭐ Feature Importance")

        # Scrollable canvas setup
        self.feature_canvas = tk.Canvas(self.feature_tab, bg="white")
        self.feature_v_scrollbar = tk.Scrollbar(self.feature_tab, orient="vertical", command=self.feature_canvas.yview)
        self.feature_h_scrollbar = tk.Scrollbar(self.feature_tab, orient="horizontal", command=self.feature_canvas.xview)

        self.feature_v_scrollbar.pack(side="right", fill="y")
        self.feature_h_scrollbar.pack(side="bottom", fill="x")
        self.feature_canvas.pack(side="left", fill="both", expand=True)

        self.feature_canvas.configure(yscrollcommand=self.feature_v_scrollbar.set, xscrollcommand=self.feature_h_scrollbar.set)
        self.feature_canvas.bind('<Configure>', lambda e: self.feature_canvas.configure(scrollregion=self.feature_canvas.bbox("all")))

        self.feature_frame = tk.Frame(self.feature_canvas, bg="white")
        self.feature_canvas.create_window((0, 0), window=self.feature_frame, anchor="nw")

    def plot_feature_importance(self):
        # Clear previous plot
        for widget in self.feature_frame.winfo_children():
            widget.destroy()

        if self.df is not None:
            # Prepare data for feature importance
            df_copy = self.df.copy()

            if 'FloodProbability' not in df_copy.columns:
                label = tk.Label(self.feature_frame, text="FloodProbability column not found in dataset.", bg="white", fg="red")
                label.pack(pady=20)
                return

            X = df_copy.drop(columns=["FloodProbability"])
            y = df_copy["FloodProbability"]

            # One-hot encode categorical columns (if any)
            X_encoded = pd.get_dummies(X)

            # Standard scaling
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_encoded)

            # Train ExtraTreesRegressor
            model = ExtraTreesRegressor(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)

            importances = model.feature_importances_
            feature_names = X_encoded.columns

            # Plotting
            fig, ax = plt.subplots(figsize=(12, max(6, len(feature_names)*0.3)))
            sns.barplot(x=importances, y=feature_names, ax=ax, palette="viridis")
            ax.set_title("Feature Importance (ExtraTreesRegressor)", fontsize=16)
            ax.set_xlabel("Importance")
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.feature_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)


    def create_predict_tab(self):
        pred_tab = tk.Frame(self.notebook, bg="#F1F8E9")
        self.notebook.add(pred_tab, text="🔮 Predict")
 
        tk.Label(pred_tab, text="Enter Input Features", font=("Arial", 18, "bold"), bg="#F1F8E9", fg="#33691E").pack(pady=10)
 
        input_frame = tk.Frame(pred_tab, bg="#F1F8E9")
        input_frame.pack(padx=10, pady=10)
 
        for feature, range_ in features.items():
            row = tk.Frame(input_frame, bg="#F1F8E9")
            tk.Label(row, text=f"{feature} {range_}", width=40, anchor='w', bg="#F1F8E9", font=("Helvetica", 10)).pack(side=tk.LEFT)
            entry = tk.Entry(row, width=20)
            entry.pack(side=tk.LEFT)
            self.input_entries[feature] = entry
            row.pack(pady=2)
 
        tk.Button(
            pred_tab,
            text="Predict Flood Risk",
            command=self.predict_risk,
            font=("Helvetica", 16),
            bg="green",
            fg="white",
            height=2,
            width=25
        ).pack(pady=30)
 
    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path, encoding='ISO-8859-1')
            self.info_label.config(
                text="✅ File uploaded successfully!\nUse the tabs above to view Histograms, Boxplots, Correlation Matrix, Dendrogram and Predict for Custom inputs",
                fg="#004D40"
            )
            self.plot_histograms()
            self.plot_boxplots()
            self.plot_correlation()
            self.plot_dendrogram()
            self.plot_feature_importance()

 
    def plot_histograms(self):
        for widget in self.hist_tab.winfo_children():
            widget.destroy()
        if self.df is not None:
            canvas = tk.Canvas(self.hist_tab)
            y_scroll = tk.Scrollbar(self.hist_tab, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas)
            scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=y_scroll.set)
            canvas.pack(side="left", fill="both", expand=True)
            y_scroll.pack(side="right", fill="y")
 
            for col in self.df.select_dtypes(include=['int64', 'float64']):
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.histplot(self.df[col].dropna(), kde=True, ax=ax)
                ax.set_title(f"Histogram of {col}")
                canvas_fig = FigureCanvasTkAgg(fig, master=scroll_frame)
                canvas_fig.draw()
                canvas_fig.get_tk_widget().pack(pady=10)
 
    def plot_boxplots(self):
        for widget in self.box_tab.winfo_children():
            widget.destroy()
        if self.df is not None:
            canvas = tk.Canvas(self.box_tab)
            y_scroll = tk.Scrollbar(self.box_tab, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas)
            scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=y_scroll.set)
            canvas.pack(side="left", fill="both", expand=True)
            y_scroll.pack(side="right", fill="y")
 
            for col in self.df.select_dtypes(include=['int64', 'float64']):
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.boxplot(x=self.df[col].dropna(), ax=ax, color="skyblue")
                ax.set_title(f"Boxplot of {col}")
                canvas_fig = FigureCanvasTkAgg(fig, master=scroll_frame)
                canvas_fig.draw()
                canvas_fig.get_tk_widget().pack(pady=10)
 
    def plot_correlation(self):
        # Clear old plots
        for widget in self.corr_frame.winfo_children():
            widget.destroy()
        if self.df is not None:
            numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
            corr_matrix = self.df[numeric_cols].corr()
 
            # First plot: full correlation matrix - bigger size for readability
            fig1, ax1 = plt.subplots(figsize=(16, 14))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax1, cbar_kws={"shrink": .75})
            ax1.set_title("Full Correlation Matrix", fontsize=16)
            fig1.tight_layout()
 
            canvas1 = FigureCanvasTkAgg(fig1, master=self.corr_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(pady=20)
 
            # Second plot: correlation with target variable "FloodProbability"
            if 'FloodProbability' in corr_matrix.columns:
                corr_target = corr_matrix['FloodProbability'].drop('FloodProbability').sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(6, 6))
                sns.barplot(x=corr_target.values, y=corr_target.index, palette="viridis", ax=ax2)
                ax2.set_title("Correlation with FloodProbability")
                ax2.set_xlabel("Correlation coefficient")
                fig2.tight_layout()
 
                canvas2 = FigureCanvasTkAgg(fig2, master=self.corr_frame)
                canvas2.draw()
                canvas2.get_tk_widget().pack(pady=20)
 
    def plot_dendrogram(self):
        # Clear old plots
        for widget in self.dendro_frame.winfo_children():
            widget.destroy()
        if self.df is not None:
            numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
            corr = self.df[numeric_cols].corr()
            # Use absolute correlation to cluster
            dist = 1 - np.abs(corr)
            linked = linkage(dist, method='ward')
 
            fig, ax = plt.subplots(figsize=(max(8, len(numeric_cols) * 0.5), 8))
            dendro = dendrogram(linked, labels=numeric_cols, ax=ax, leaf_rotation=45, leaf_font_size=10)
            ax.set_title("Dendrogram of Feature Correlations", fontsize=16)
            plt.tight_layout()
 
            canvas = FigureCanvasTkAgg(fig, master=self.dendro_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
 
    def predict_risk(self):
        if model is None:
            messagebox.showerror("Model Error", "Prediction model not loaded.")
            return
 
        try:
            input_data = []
            for feature in features.keys():
                val = self.input_entries[feature].get()
                if val.strip() == "":
                    raise ValueError(f"Please enter a value for {feature}")
                val_float = float(val)
                input_data.append(val_float)
 
            input_df = pd.DataFrame([input_data], columns=features.keys())
            prediction = model.predict(input_df)[0]
            messagebox.showinfo("Prediction Result", f"Predicted Flood Risk Score: {prediction:.3f}")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
 
if __name__ == "__main__":
    root = tk.Tk()
    app = FloodApp(root)
    root.mainloop()
