import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

class PCAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisis PCA Jaringan SD-WAN")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        self.df = None
        self.pca_result = None
        self.eigenvalues = None
        self.explained_variance_ratio = None

        self.setup_gui()

    def setup_gui(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.graph_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.graph_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.fig, self.axes = plt.subplots(1, 3, figsize=(12, 4))
        self.axes[0].set_title("Scree Plot")
        self.axes[1].set_title("PCA Plot")
        self.axes[2].set_title("Anomaly Detection")
        for ax in self.axes:
            ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        table_frame = tk.Frame(self.control_frame)
        table_frame.pack(pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, height=5)
        self.tree["columns"] = (
        "Latensi_MPLS", "Jitter_MPLS", "PacketLoss_MPLS", "Bandwidth_MPLS",
        "Latensi_Broadband", "Jitter_Broadband", "PacketLoss_Broadband", "Bandwidth_Broadband",
        "Latensi_4G", "Jitter_4G", "PacketLoss_4G", "Bandwidth_4G"
        )
        self.tree.column("#0", width=0, stretch=False)

        column_widths = {
            "Latensi_MPLS": 80,
            "Jitter_MPLS": 80,
            "PacketLoss_MPLS": 120,
            "Bandwidth_MPLS": 100,
            "Latensi_Broadband": 100,
            "Jitter_Broadband": 100,
            "PacketLoss_Broadband": 140,
            "Bandwidth_Broadband": 120,
            "Latensi_4G": 80,
            "Jitter_4G": 80,
            "PacketLoss_4G": 120,
            "Bandwidth_4G": 100
        }
        for col in self.tree["columns"]:
            self.tree.column(col, width=column_widths[col], anchor="center")
            self.tree.heading(col, text=col)

        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        x_scrollbar.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=x_scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)

        btn_frame = tk.Frame(self.control_frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Generate Data", command=self.generate_data, 
                  bg="#4CAF50", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Execute Program", command=self.execute_program, 
                  bg="#2196F3", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def generate_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        np.random.seed(42)
        n_samples = 100
        self.data = {
            'Latensi_MPLS': np.random.normal(50, 10, n_samples),
            'Jitter_MPLS': np.random.normal(5, 2, n_samples),
            'PacketLoss_MPLS': np.random.uniform(0, 2, n_samples),
            'Bandwidth_MPLS': np.random.normal(100, 20, n_samples),
            'Latensi_Broadband': np.random.normal(70, 15, n_samples),
            'Jitter_Broadband': np.random.normal(10, 3, n_samples),
            'PacketLoss_Broadband': np.random.uniform(1, 3, n_samples),
            'Bandwidth_Broadband': np.random.normal(80, 15, n_samples),
            'Latensi_4G': np.random.normal(90, 20, n_samples),
            'Jitter_4G': np.random.normal(15, 5, n_samples),
            'PacketLoss_4G': np.random.uniform(2, 5, n_samples),
            'Bandwidth_4G': np.random.normal(50, 10, n_samples),
        }
        self.df = pd.DataFrame(self.data)

        for i, row in self.df.head().iterrows():
            self.tree.insert("", "end", values=[f"{x:.2f}" for x in row])

    def execute_program(self):
        if self.df is None:
            tk.messagebox.showwarning("Warning", "Generate data first!")
            return

        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(self.df)

        cov_matrix = np.cov(scaled_data.T)
        cov_matrix_df = pd.DataFrame(cov_matrix, index=self.df.columns, columns=self.df.columns)
        print("\n3. Matriks Kovarians:")
        print(cov_matrix_df)

        pca = PCA()
        self.pca_result = pca.fit_transform(scaled_data)
        self.eigenvalues = pca.explained_variance_
        self.explained_variance_ratio = pca.explained_variance_ratio_

        print("\n4. Seluruh Eigenvalue dari Komponen Utama:")
        for i, eigenvalue in enumerate(self.eigenvalues, 1):
            print(f"PC{i}: {eigenvalue:.4f}")
        print("\n5. Rasio Variansi yang Dijelaskan (Persentase):")
        for i, ratio in enumerate(self.explained_variance_ratio, 1):
            print(f"PC{i}: {ratio*100:.2f}%")
        print(f"Total Variansi yang Dijelaskan: {sum(self.explained_variance_ratio)*100:.2f}%")

        components_df = pd.DataFrame(
            pca.components_, columns=self.df.columns, index=[f'PC{i+1}' for i in range(len(pca.components_))]
        )
        print("\n6. Matriks PC (Eigenvector):")
        print(components_df)

        pca_df = pd.DataFrame(data=self.pca_result[:, :2], columns=['PC1', 'PC2'])
        print("\n7. Matriks Principal Component (PC1 dan PC2, 5 baris pertama):")
        print(pca_df.head())

        for ax in self.axes:
            ax.clear()

        self.axes[0].plot(range(1, len(self.eigenvalues) + 1), self.eigenvalues, marker='o', linestyle='--')
        self.axes[0].set_xlabel('Komponen Utama')
        self.axes[0].set_ylabel('Eigenvalue')
        self.axes[0].set_title('Scree Plot dari Eigenvalue PCA')
        self.axes[0].grid(True)

        self.axes[1].scatter(pca_df['PC1'], pca_df['PC2'], c='blue', alpha=0.5)
        self.axes[1].set_xlabel(f'PC1 ({self.explained_variance_ratio[0]*100:.2f}% variansi)')
        self.axes[1].set_ylabel(f'PC2 ({self.explained_variance_ratio[1]*100:.2f}% variansi)')
        self.axes[1].set_title('PCA dari Metrik Jaringan SD-WAN')
        self.axes[1].grid(True)

        distances = np.sqrt((self.pca_result[:, 0] - self.pca_result[:, 0].mean())**2 + 
                            (self.pca_result[:, 1] - self.pca_result[:, 1].mean())**2)
        threshold = np.percentile(distances, 95)
        anomalies = distances > threshold
        self.axes[2].scatter(pca_df['PC1'], pca_df['PC2'], c='blue', alpha=0.5, label='Data Normal')
        self.axes[2].scatter(pca_df['PC1'][anomalies], pca_df['PC2'][anomalies], c='red', label='Anomali')
        self.axes[2].set_xlabel(f'PC1 ({self.explained_variance_ratio[0]*100:.2f}% variansi)')
        self.axes[2].set_ylabel(f'PC2 ({self.explained_variance_ratio[1]*100:.2f}% variansi)')
        self.axes[2].set_title('Deteksi Anomali pada Data Jaringan SD-WAN')
        self.axes[2].legend()
        self.axes[2].grid(True)

        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PCAApp(root)
    root.mainloop()