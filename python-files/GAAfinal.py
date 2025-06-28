# Genetic Analyzer Final Version
# Supports: Sire-only (half-sibs), Sire-Dam (full-sibs)
# Includes: Descriptive stats, Nested ANOVA, Heritability, Genetic/Phenotypic/Environmental correlations

import tkinter as tk
from tkinter import filedialog, messagebox
from math import sqrt
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
import sys
import io

class GeneticAnalyzerApp:
    """
    A Tkinter-based application for genetic analysis.
    It supports Sire-only (half-sibs) and Sire-Dam (full-sibs) models
    to calculate heritability and other genetic parameters.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Genetic Assistant Program")
        self.language = "EN"
        self.data = []
        self.traits = []
        self.output = ""
        self.results_df = {} # New dictionary to store results as DataFrames
        self.model_type = tk.StringVar(value="sire")
        self.translation = {
            "Genetic Assistant Program": "برنامج المساعد الوراثي",
            "Load CSV File": "تحميل ملف CSV",
            "Analyze": "تحليل",
            "Save Results": "حفظ النتائج",
            "Switch Language": "تبديل اللغة",
            "Trait": "الصفة",
            "Mean": "المتوسط",
            "Std Dev": "الانحراف المعياري",
            "Std Error": "الخطأ القياسي",
            "Min": "أقل قيمة",
            "Max": "أعلى قيمة",
            "Count": "عدد القيم",
            "Within-family variance": "التباين داخل العائلة",
            "Between-family variance": "التباين بين العائلات",
            "Total variance": "التباين الكلي",
            "Heritability (h²)": "التوريث (h²)",
            "Genetic correlation": "الارتباط الوراثي",
            "Phenotypic correlation": "الارتباط المظهري",
            "Environmental correlation": "الارتباط البيئي",
            "Sire-only Model (Half-sibs)": "نموذج الأب فقط (نصف الأشقاء)",
            "Sire-Dam Model (Full-sibs)": "نموذج الأب والأم (الأشقاء الكاملين)",
            "Select model type:": "اختر نوع النموذج:",
            "Results": "النتائج",
            "Success": "نجاح",
            "Results exported to Excel successfully.": "تم تصدير النتائج إلى Excel بنجاح.",
            "No results to save.": "لا توجد نتائج لحفظها.",
            "Info": "معلومات",
            "Error": "خطأ",
            "Failed to load CSV file. Please check the file format.": "فشل تحميل ملف CSV. يرجى التحقق من تنسيق الملف.",
            "Please load a data file first.": "يرجى تحميل ملف البيانات أولاً.",
            "Descriptive Statistics": "الإحصاءات الوصفية",
            "Nested ANOVA": "تحليل التباين المتداخل",
            "Variance Components": "مكونات التباين",
            "Correlations": "الارتباطات",
            "Source of Variation": "مصدر التباين",
            "Degrees of Freedom": "درجات الحرية",
            "Sum of Squares": "مجموع المربعات",
            "Mean Squares": "متوسط المربعات",
            "Expected Mean Squares": "متوسط المربعات المتوقع",
            "F-value": "قيمة F",
            "P-value": "قيمة P",
            "Between Sires": "بين الآباء",
            "Within Sires": "داخل الآباء",
            "Total": "المجموع",
            "Between-Dam-within-Sire": "بين الأمهات داخل الآباء",
            "Within-Family (Error)": "داخل العائلة (خطأ)",
            "Genetic": "الوراثي",
            "Phenotypic": "المظهري",
            "Environmental": "البيئي",
            "Correlations Matrix": "مصفوفة الارتباطات"
        }
        self.setup_ui()

    def t(self, text):
        """Translates text based on the current language setting."""
        if self.language == "AR":
            return self.translation.get(text, text)
        return text

    def setup_ui(self):
        """Sets up the user interface elements."""
        # Frame for controls
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(pady=5, padx=10, fill=tk.X)

        self.load_button = tk.Button(control_frame, text=self.t("Load CSV File"), command=self.load_csv)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(control_frame, text=self.t("Analyze"), command=self.analyze)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(control_frame, text=self.t("Save Results"), command=self.save_results)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.export_excel_button = tk.Button(control_frame, text="Export to Excel", command=self.export_to_excel)
        self.export_excel_button.pack(side=tk.LEFT, padx=5)
        
        self.switch_lang_button = tk.Button(control_frame, text=self.t("Switch Language"), command=self.switch_language)
        self.switch_lang_button.pack(side=tk.RIGHT, padx=5)

        # Frame for model selection
        model_frame = tk.LabelFrame(self.root, text=self.t("Select model type:"), padx=10, pady=5)
        model_frame.pack(pady=5, padx=10, fill=tk.X)

        self.sire_radio = tk.Radiobutton(model_frame, text=self.t("Sire-only Model (Half-sibs)"), variable=self.model_type, value="sire")
        self.sire_radio.pack(side=tk.LEFT, padx=10)

        self.sire_dam_radio = tk.Radiobutton(model_frame, text=self.t("Sire-Dam Model (Full-sibs)"), variable=self.model_type, value="sire_dam")
        self.sire_dam_radio.pack(side=tk.LEFT, padx=10)

        # Output Text box
        output_frame = tk.LabelFrame(self.root, text=self.t("Results"), padx=10, pady=5)
        output_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(output_frame, wrap="word", height=20, width=80)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=self.scrollbar.set)
        
        self.update_ui_text()

    def update_ui_text(self):
        """Updates all UI text based on the current language."""
        self.root.title(self.t("Genetic Assistant Program"))
        self.load_button.config(text=self.t("Load CSV File"))
        self.analyze_button.config(text=self.t("Analyze"))
        self.save_button.config(text=self.t("Save Results"))
        self.switch_lang_button.config(text=self.t("Switch Language"))
        
        # Update radio button texts using the translation dictionary
        self.sire_radio.config(text=self.t("Sire-only Model (Half-sibs)"))
        self.sire_dam_radio.config(text=self.t("Sire-Dam Model (Full-sibs)"))
        
        # A more robust way to update the LabelFrame text
        # Assumes the frames are created in the same order
        frames = [w for w in self.root.winfo_children() if isinstance(w, tk.LabelFrame)]
        if frames:
            frames[0].config(text=self.t("Select model type:"))
            frames[1].config(text=self.t("Results"))


    def switch_language(self):
        """Switches the application's language between English and Arabic."""
        self.language = "AR" if self.language == "EN" else "EN"
        self.update_ui_text()

    def load_csv(self):
        """
        Loads data from a CSV file.
        Expects a comma-separated file with sire ID, dam ID, ID, and trait values.
        This version robustly handles a header row if present.
        
        Expected format: sire_id, dam_id, ID, trait_1, trait_2, ...
        """
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        try:
            # Use pandas for robust CSV reading.
            # We use header=None to read the file without assuming a header.
            df = pd.read_csv(path, header=None)

            # --- Check and handle the header row ---
            # Assume the first row is a header if it contains non-numeric values
            # in the trait columns (from index 3 onwards).
            try:
                # Attempt to convert the trait columns of the first row to float.
                # If this succeeds, the data has no header row.
                _ = df.iloc[0, 3:].astype(float) # Check columns from index 3
                data_df = df
            except ValueError:
                # If conversion fails, the first row is a header.
                # We'll use the rest of the DataFrame as data and set traits from the header.
                data_df = df.iloc[1:]
                self.traits = df.iloc[0, 3:].tolist() # Traits start from column index 3
            
            # Now, set the data based on the cleaned DataFrame.
            # We select columns for sire (0), dam (1), and traits (from 3 onwards).
            # The ID column (index 2) is now correctly ignored for the analysis.
            self.data = data_df.iloc[:, [0, 1] + list(range(3, data_df.shape[1]))].values.tolist()
            if not self.traits: # If there was no header, use generic names
                self.traits = [f"Trait {i+1}" for i in range(data_df.shape[1] - 3)]

            messagebox.showinfo(self.t("Success"), f"Loaded {len(self.data)} records from the file.")
            
        except FileNotFoundError:
            messagebox.showerror(self.t("Error"), f"File not found at {path}")
        except pd.errors.ParserError:
            messagebox.showerror(self.t("Error"), self.t("Failed to load CSV file. Please check the file format."))
        except Exception as e:
            messagebox.showerror(self.t("Error"), f"An unexpected error occurred: {e}")

    def analyze(self):
        """
        Performs the analysis based on the selected model type.
        """
        if not self.data:
            messagebox.showinfo(self.t("Info"), self.t("Please load a data file first."))
            return

        self.output_text.delete("1.0", tk.END)
        self.output = ""
        self.results_df = {} # Reset results dictionary
        
        model = self.model_type.get()
        
        if model == "sire":
            self.output += self.t("Sire-only Model (Half-sibs)") + "\n" + "=" * 50 + "\n"
            self.analyze_sire_model()
        elif model == "sire_dam":
            self.output += self.t("Sire-Dam Model (Full-sibs)") + "\n" + "=" * 50 + "\n"
            self.analyze_sire_dam_model()
        else:
            self.output += "Invalid model selected.\n"
        
        self.output_text.insert(tk.END, self.output)

    def analyze_sire_model(self):
        """
        Performs genetic analysis for the Sire-only model (half-sibs).
        Includes descriptive stats, ANOVA, heritability, and correlations.
        
        Data format after loading: [Sire_ID, Dam_ID, Trait1, Trait2, ...]
        """
        if len(self.data) == 0 or len(self.data[0]) < 2:
            self.output += self.t("Error: Data must have at least Sire, Dam, and one trait column.") + "\n"
            return
            
        num_traits = len(self.traits)
        
        # Group individuals by sire
        sire_families = defaultdict(list)
        all_trait_data = []
        # Sire ID is at index 0, traits start at index 2
        for row in self.data:
            sire_id = row[0]
            try:
                traits_data = [float(val) for val in row[2:]]
                sire_families[sire_id].append(traits_data)
                all_trait_data.append(traits_data)
            except ValueError as e:
                self.output += f"Error processing a data row: {row}. Skipping this row. Details: {e}\n"
                continue
        
        if not sire_families or not all_trait_data:
            self.output += self.t("Error: No valid numerical data found for analysis.") + "\n"
            return

        # --- 1. Descriptive Statistics ---
        self.output += "\n" + self.t("Descriptive Statistics") + "\n" + "-" * 30 + "\n"
        desc_stats_data = []
        for i, trait_name in enumerate(self.traits):
            trait_values = [row[i] for row in all_trait_data]
            trait_series = pd.Series(trait_values, dtype=float)
            stats_row = {
                self.t('Trait'): trait_name,
                self.t('Mean'): f"{trait_series.mean():.4f}",
                self.t('Std Dev'): f"{trait_series.std():.4f}",
                self.t('Std Error'): f"{trait_series.sem():.4f}",
                self.t('Min'): f"{trait_series.min():.4f}",
                self.t('Max'): f"{trait_series.max():.4f}",
                self.t('Count'): f"{trait_series.count():d}"
            }
            desc_stats_data.append(stats_row)
            # Add to output text
            self.output += f"\n--- {self.t('Trait')}: {trait_name} ---\n"
            for key, value in stats_row.items():
                if key != self.t('Trait'):
                    self.output += f"{key}: {value}\n"
        self.results_df['Descriptive_Stats'] = pd.DataFrame(desc_stats_data).set_index(self.t('Trait'))
            
        # --- 2. Nested ANOVA and Variance Components ---
        self.output += "\n" + self.t("Nested ANOVA") + "\n" + "-" * 30 + "\n"
        
        # Calculate Variance-Covariance matrices
        grand_mean_vector = np.mean(all_trait_data, axis=0)
        
        # Total Sum of Squares/Cross-Products (SSCP_total)
        SSCP_total = np.cov(np.array(all_trait_data).T, bias=False) * (len(all_trait_data) - 1)
        
        # Between-Sire Sum of Squares/Cross-Products (SSCP_b)
        SSCP_b = np.zeros((num_traits, num_traits))
        sire_counts = []
        for sire_id, sibs_data in sire_families.items():
            sire_trait_values = np.array(sibs_data)
            n_i = len(sire_trait_values)
            sire_counts.append(n_i)
            sire_mean_vector = np.mean(sire_trait_values, axis=0)
            diff = sire_mean_vector - grand_mean_vector
            SSCP_b += n_i * np.outer(diff, diff)
            
        # Within-Sire Sum of Squares/Cross-Products (SSCP_w)
        SSCP_w = SSCP_total - SSCP_b

        # Degrees of Freedom
        N = len(all_trait_data)
        S = len(sire_families)
        DFT = N - 1
        DFB = S - 1
        DFW = DFT - DFB

        # Mean Squares and Cross-Products (MSCP)
        MSCP_b = SSCP_b / DFB if DFB > 0 else np.zeros((num_traits, num_traits))
        MSCP_w = SSCP_w / DFW if DFW > 0 else np.zeros((num_traits, num_traits))
        
        # Estimate average number of individuals per sire (k) for unbalanced data
        sire_counts_array = np.array(sire_counts)
        k = (N - np.sum(sire_counts_array**2) / N) / (S - 1) if S > 1 else 0
        
        # Variance Components (V_s, V_w) - Ensure non-negative variances
        V_w = MSCP_w
        V_s_raw = (MSCP_b - MSCP_w) / k if k > 0 else np.zeros((num_traits, num_traits))
        # Set negative variances to zero
        V_s = np.diag(np.maximum(np.diag(V_s_raw), 0))
        for i in range(num_traits):
            for j in range(num_traits):
                if i != j:
                    V_s[i, j] = V_s_raw[i, j]
        
        # Phenotypic Variance-Covariance Matrix (V_p)
        V_p = V_s + V_w

        # --- Store ANOVA and Variance Components in DataFrames ---
        anova_data = []
        var_comp_data = []
        for i, trait_name in enumerate(self.traits):
            # ANOVA Table data
            SSB_i = SSCP_b[i, i]
            SSW_i = SSCP_w[i, i]
            SST_i = SSCP_total[i, i]
            MSB_i = MSCP_b[i, i]
            MSW_i = MSCP_w[i, i]
            
            # Store ANOVA table for each trait
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Between Sires'),
                self.t('Degrees of Freedom'): DFB,
                self.t('Sum of Squares'): SSB_i,
                self.t('Mean Squares'): MSB_i,
                self.t('Expected Mean Squares'): f"σ²w + {k:.2f}σ²s"
            })
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Within Sires'),
                self.t('Degrees of Freedom'): DFW,
                self.t('Sum of Squares'): SSW_i,
                self.t('Mean Squares'): MSW_i,
                self.t('Expected Mean Squares'): "σ²w"
            })
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Total'),
                self.t('Degrees of Freedom'): DFT,
                self.t('Sum of Squares'): SST_i,
                self.t('Mean Squares'): np.nan,
                self.t('Expected Mean Squares'): ""
            })
            
            # Variance Components data
            sigmas_sq_w = V_w[i, i]
            sigmas_sq_s = V_s[i, i]
            sigma_sq_p = V_p[i, i]
            h_sq = 4 * sigmas_sq_s / sigma_sq_p if sigma_sq_p > 0 else 0

            var_comp_data.append({
                self.t('Trait'): trait_name,
                'σ²s': sigmas_sq_s,
                'σ²w': sigmas_sq_w,
                'σ²p': sigma_sq_p,
                'h²': h_sq
            })

            # Add to output text for display
            self.output += f"\n--- {self.t('Trait')}: {trait_name} ---\n"
            anova_df = pd.DataFrame([row for row in anova_data if row[self.t('Trait')] == trait_name])
            self.output += anova_df.to_string(index=False, float_format="%.4f") + "\n"
            self.output += "\n" + self.t("Variance Components") + "\n" + "-" * 20 + "\n"
            self.output += f"{self.t('Between-family variance')}: σ²s = {sigmas_sq_s:.4f}\n"
            self.output += f"{self.t('Within-family variance')}: σ²w = {sigmas_sq_w:.4f}\n"
            self.output += f"{self.t('Total variance')}: σ²p = {sigma_sq_p:.4f}\n"
            self.output += f"{self.t('Heritability (h²)')}: {h_sq:.4f}\n"
            self.output += "\n"
            
        self.results_df['ANOVA'] = pd.DataFrame(anova_data).set_index(self.t('Trait'))
        self.results_df['Variance_Components'] = pd.DataFrame(var_comp_data).set_index(self.t('Trait'))
        
        # --- 4. Correlations Analysis (If more than one trait) ---
        if num_traits > 1:
            self.output += "\n" + self.t("Correlations") + "\n" + "-" * 30 + "\n"

            # Genetic Correlation Matrix (r_g)
            rg_matrix = np.zeros((num_traits, num_traits))
            for i in range(num_traits):
                for j in range(num_traits):
                    cov_s_ij = V_s[i, j]
                    var_s_i = V_s[i, i]
                    var_s_j = V_s[j, j]
                    
                    if var_s_i > 0 and var_s_j > 0:
                        rg_matrix[i, j] = cov_s_ij / sqrt(var_s_i * var_s_j)
            
            # Phenotypic Correlation Matrix (r_p)
            rp_matrix = np.zeros((num_traits, num_traits))
            for i in range(num_traits):
                for j in range(num_traits):
                    cov_p_ij = V_p[i, j]
                    var_p_i = V_p[i, i]
                    var_p_j = V_p[j, j]
                    
                    if var_p_i > 0 and var_p_j > 0:
                        rp_matrix[i, j] = cov_p_ij / sqrt(var_p_i * var_p_j)
            
            # Environmental Correlation Matrix (r_e)
            V_e_raw = V_w - 3 * V_s
            V_e = np.diag(np.maximum(np.diag(V_e_raw), 0))
            for i in range(num_traits):
                for j in range(num_traits):
                    if i != j:
                        V_e[i, j] = V_e_raw[i, j]

            re_matrix = np.zeros((num_traits, num_traits))
            for i in range(num_traits):
                for j in range(num_traits):
                    cov_e_ij = V_e[i, j]
                    var_e_i = V_e[i, i]
                    var_e_j = V_e[j, j]
                    
                    if var_e_i > 0 and var_e_j > 0:
                        re_matrix[i, j] = cov_e_ij / sqrt(var_e_i * var_e_j)

            # Store correlation matrices as DataFrames
            self.results_df['Genetic_Correlation'] = pd.DataFrame(rg_matrix, index=self.traits, columns=self.traits)
            self.results_df['Phenotypic_Correlation'] = pd.DataFrame(rp_matrix, index=self.traits, columns=self.traits)
            self.results_df['Environmental_Correlation'] = pd.DataFrame(re_matrix, index=self.traits, columns=self.traits)

            # Print Correlation Matrices to output text
            self.output += f"\n--- {self.t('Correlations Matrix')} ({self.t('Genetic')}) ---\n"
            self.output += self.results_df['Genetic_Correlation'].to_string(float_format="%.4f") + "\n"
            self.output += f"\n--- {self.t('Correlations Matrix')} ({self.t('Phenotypic')}) ---\n"
            self.output += self.results_df['Phenotypic_Correlation'].to_string(float_format="%.4f") + "\n"
            self.output += f"\n--- {self.t('Correlations Matrix')} ({self.t('Environmental')}) ---\n"
            self.output += self.results_df['Environmental_Correlation'].to_string(float_format="%.4f") + "\n"


    def analyze_sire_dam_model(self):
        """
        Performs genetic analysis for the Sire-Dam model (full-sibs).
        
        Data format after loading: [Sire_ID, Dam_ID, Trait1, Trait2, ...]
        """
        if len(self.data) == 0 or len(self.data[0]) < 2:
            self.output += self.t("Error: Data must have at least Sire, Dam, and one trait column.") + "\n"
            return
            
        num_traits = len(self.traits)

        # Group individuals by sire and then by dam within sire
        sire_dam_families = defaultdict(lambda: defaultdict(list))
        all_trait_data = []
        # Sire ID is at index 0 and Dam ID is at index 1
        for row in self.data:
            sire_id, dam_id = row[0], row[1]
            try:
                traits_data = [float(val) for val in row[2:]]
                sire_dam_families[sire_id][dam_id].append(traits_data)
                all_trait_data.append(traits_data)
            except ValueError as e:
                self.output += f"Error processing a data row: {row}. Skipping this row. Details: {e}\n"
                continue

        if not sire_dam_families or not all_trait_data:
            self.output += self.t("Error: No valid numerical data found for analysis.") + "\n"
            return
        
        # --- 1. Descriptive Statistics ---
        self.output += "\n" + self.t("Descriptive Statistics") + "\n" + "-" * 30 + "\n"
        desc_stats_data = []
        for i, trait_name in enumerate(self.traits):
            trait_values = [row[i] for row in all_trait_data]
            trait_series = pd.Series(trait_values, dtype=float)
            stats_row = {
                self.t('Trait'): trait_name,
                self.t('Mean'): f"{trait_series.mean():.4f}",
                self.t('Std Dev'): f"{trait_series.std():.4f}",
                self.t('Std Error'): f"{trait_series.sem():.4f}",
                self.t('Min'): f"{trait_series.min():.4f}",
                self.t('Max'): f"{trait_series.max():.4f}",
                self.t('Count'): f"{trait_series.count():d}"
            }
            desc_stats_data.append(stats_row)
            # Add to output text
            self.output += f"\n--- {self.t('Trait')}: {trait_name} ---\n"
            for key, value in stats_row.items():
                if key != self.t('Trait'):
                    self.output += f"{key}: {value}\n"
        self.results_df['Descriptive_Stats'] = pd.DataFrame(desc_stats_data).set_index(self.t('Trait'))
        
        # --- 2. Nested ANOVA and Variance Components ---
        self.output += "\n" + self.t("Nested ANOVA (Sire/Dam)") + "\n" + "-" * 30 + "\n"
        
        # Calculate Variance-Covariance matrices
        grand_mean_vector = np.mean(all_trait_data, axis=0)
        
        # SSCP for Sire
        SSCP_sire = np.zeros((num_traits, num_traits))
        for sire_id, dam_families in sire_dam_families.items():
            sire_values = np.concatenate([np.array(family) for family in dam_families.values()])
            n_sire = len(sire_values)
            sire_mean = np.mean(sire_values, axis=0)
            diff = sire_mean - grand_mean_vector
            SSCP_sire += n_sire * np.outer(diff, diff)

        # SSCP for Dam-within-Sire
        SSCP_dam_within_sire = np.zeros((num_traits, num_traits))
        for sire_id, dam_families in sire_dam_families.items():
            sire_values = np.concatenate([np.array(family) for family in dam_families.values()])
            sire_mean = np.mean(sire_values, axis=0)
            for dam_id, family in dam_families.items():
                family_values = np.array(family)
                n_dam = len(family_values)
                dam_mean = np.mean(family_values, axis=0)
                diff = dam_mean - sire_mean
                SSCP_dam_within_sire += n_dam * np.outer(diff, diff)

        # SSCP for Error/Within-family
        SSCP_error = np.zeros((num_traits, num_traits))
        for sire_id, dam_families in sire_dam_families.items():
            for dam_id, family in dam_families.items():
                family_values = np.array(family)
                family_mean = np.mean(family_values, axis=0)
                for individual_data in family_values:
                    diff = individual_data - family_mean
                    SSCP_error += np.outer(diff, diff)

        # Degrees of Freedom
        N = len(all_trait_data)
        S = len(sire_dam_families)
        D = sum(len(dams) for dams in sire_dam_families.values())
        
        DFT = N - 1
        DF_sire = S - 1
        DF_dam_within_sire = D - S
        DF_error = N - D

        # Mean Squares and Cross-Products (MSCP)
        MSCP_sire = SSCP_sire / DF_sire if DF_sire > 0 else np.zeros((num_traits, num_traits))
        MSCP_dam = SSCP_dam_within_sire / DF_dam_within_sire if DF_dam_within_sire > 0 else np.zeros((num_traits, num_traits))
        MSCP_error = SSCP_error / DF_error if DF_error > 0 else np.zeros((num_traits, num_traits))

        # --- Corrected Calculation for Unbalanced Data Coefficients (k and d_avg) ---
        family_sizes = [len(f) for d_families in sire_dam_families.values() for f in d_families.values()]
        sum_of_n_ij_squared = sum(size**2 for size in family_sizes)
        k = (N - sum_of_n_ij_squared / N) / (D - 1) if D > 1 else 0

        sire_dam_counts = [len(dams) for dams in sire_dam_families.values()]
        sum_of_d_i_squared = sum(count**2 for count in sire_dam_counts)
        d_avg = (D - sum_of_d_i_squared / D) / (S - 1) if S > 1 else 0
        
        # Variance Components (V_s, V_d, V_e) - Ensure non-negative variances
        V_e = MSCP_error
        V_d_raw = (MSCP_dam - MSCP_error) / k if k > 0 else np.zeros((num_traits, num_traits))
        V_s_raw = (MSCP_sire - MSCP_dam) / (d_avg * k) if d_avg > 0 and k > 0 else np.zeros((num_traits, num_traits))
        
        V_e = np.diag(np.maximum(np.diag(V_e), 0))
        V_d = np.diag(np.maximum(np.diag(V_d_raw), 0))
        V_s = np.diag(np.maximum(np.diag(V_s_raw), 0))
        
        for i in range(num_traits):
            for j in range(num_traits):
                if i != j:
                    V_d[i, j] = V_d_raw[i, j]
                    V_s[i, j] = V_s_raw[i, j]
        
        # Total Phenotypic Variance-Covariance Matrix
        V_p = V_s + V_d + V_e
        
        # --- Store ANOVA and Variance Components in DataFrames ---
        anova_data = []
        var_comp_data = []
        for i, trait_name in enumerate(self.traits):
            # ANOVA Table data
            SS_sire_i = SSCP_sire[i, i]
            SS_dam_i = SSCP_dam_within_sire[i, i]
            SS_error_i = SSCP_error[i, i]
            SST_i = SS_sire_i + SS_dam_i + SS_error_i
            
            MS_sire_i = MSCP_sire[i, i]
            MS_dam_i = MSCP_dam[i, i]
            MS_error_i = MSCP_error[i, i]
            
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Between Sires'),
                self.t('Degrees of Freedom'): DF_sire,
                self.t('Sum of Squares'): SS_sire_i,
                self.t('Mean Squares'): MS_sire_i,
                self.t('Expected Mean Squares'): f"σ²e + {k:.2f}σ²d + {d_avg*k:.2f}σ²s"
            })
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Between-Dam-within-Sire'),
                self.t('Degrees of Freedom'): DF_dam_within_sire,
                self.t('Sum of Squares'): SS_dam_i,
                self.t('Mean Squares'): MS_dam_i,
                self.t('Expected Mean Squares'): f"σ²e + {k:.2f}σ²d"
            })
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Within-Family (Error)'),
                self.t('Degrees of Freedom'): DF_error,
                self.t('Sum of Squares'): SS_error_i,
                self.t('Mean Squares'): MS_error_i,
                self.t('Expected Mean Squares'): "σ²e"
            })
            anova_data.append({
                self.t('Trait'): trait_name,
                self.t('Source of Variation'): self.t('Total'),
                self.t('Degrees of Freedom'): DFT,
                self.t('Sum of Squares'): SST_i,
                self.t('Mean Squares'): np.nan,
                self.t('Expected Mean Squares'): ""
            })
            
            # Variance Components data
            sigma_sq_s = V_s[i, i]
            sigma_sq_d = V_d[i, i]
            sigma_sq_e = V_e[i, i]
            sigma_sq_p = V_p[i, i]
            h_sq_sire = 4 * sigma_sq_s / sigma_sq_p if sigma_sq_p > 0 else 0
            h_sq_dam = 4 * sigma_sq_d / sigma_sq_p if sigma_sq_p > 0 else 0
            h_sq_combined = 2 * (sigma_sq_s + sigma_sq_d) / sigma_sq_p if sigma_sq_p > 0 else 0
            
            var_comp_data.append({
                self.t('Trait'): trait_name,
                'σ²s': sigma_sq_s,
                'σ²d': sigma_sq_d,
                'σ²e': sigma_sq_e,
                'σ²p': sigma_sq_p,
                'h² (Sire)': h_sq_sire,
                'h² (Dam)': h_sq_dam,
                'h² (Combined)': h_sq_combined
            })
            
            # Add to output text for display
            self.output += f"\n--- {self.t('Trait')}: {trait_name} ---\n"
            anova_df = pd.DataFrame([row for row in anova_data if row[self.t('Trait')] == trait_name])
            self.output += anova_df.to_string(index=False, float_format="%.4f") + "\n"
            self.output += "\n" + self.t("Variance Components") + "\n" + "-" * 20 + "\n"
            self.output += f"σ²s (Sire): {sigma_sq_s:.4f}\n"
            self.output += f"σ²d (Dam): {sigma_sq_d:.4f}\n"
            self.output += f"σ²e (Error): {sigma_sq_e:.4f}\n"
            self.output += f"{self.t('Total variance')}: σ²p = {sigma_sq_p:.4f}\n"
            self.output += f"{self.t('Heritability (h²)')} (Sire component): {h_sq_sire:.4f}\n"
            self.output += f"{self.t('Heritability (h²)')} (Dam component): {h_sq_dam:.4f}\n"
            self.output += f"{self.t('Heritability (h²)')} (Combined): {h_sq_combined:.4f}\n"
            self.output += "\n"

        self.results_df['ANOVA'] = pd.DataFrame(anova_data).set_index(self.t('Trait'))
        self.results_df['Variance_Components'] = pd.DataFrame(var_comp_data).set_index(self.t('Trait'))

        # --- 4. Correlations Analysis (If more than one trait) ---
        if num_traits > 1:
            self.output += "\n" + self.t("Correlations") + "\n" + "-" * 30 + "\n"
            
            # Genetic Correlation Matrix (r_g)
            V_g_sire_dam = 2 * (V_s + V_d)
            
            rg_matrix = np.zeros((num_traits, num_traits))
            for i in range(num_traits):
                for j in range(num_traits):
                    cov_g_ij = V_g_sire_dam[i, j]
                    var_g_i = V_g_sire_dam[i, i]
                    var_g_j = V_g_sire_dam[j, j]
                    
                    if var_g_i > 0 and var_g_j > 0:
                        rg_matrix[i, j] = cov_g_ij / sqrt(var_g_i * var_g_j)
            
            # Phenotypic Correlation Matrix (r_p)
            rp_matrix = np.zeros((num_traits, num_traits))
            for i in range(num_traits):
                for j in range(num_traits):
                    cov_p_ij = V_p[i, j]
                    var_p_i = V_p[i, i]
                    var_p_j = V_p[j, j]
                    
                    if var_p_i > 0 and var_p_j > 0:
                        rp_matrix[i, j] = cov_p_ij / sqrt(var_p_i * var_p_j)
            
            # Environmental Correlation Matrix (r_e)
            V_e = V_e
            
            re_matrix = np.zeros((num_traits, num_traits))
            for i in range(num_traits):
                for j in range(num_traits):
                    cov_e_ij = V_e[i, j]
                    var_e_i = V_e[i, i]
                    var_e_j = V_e[j, j]
                    
                    if var_e_i > 0 and var_e_j > 0:
                        re_matrix[i, j] = cov_e_ij / sqrt(var_e_i * var_e_j)

            # Store correlation matrices as DataFrames
            self.results_df['Genetic_Correlation'] = pd.DataFrame(rg_matrix, index=self.traits, columns=self.traits)
            self.results_df['Phenotypic_Correlation'] = pd.DataFrame(rp_matrix, index=self.traits, columns=self.traits)
            self.results_df['Environmental_Correlation'] = pd.DataFrame(re_matrix, index=self.traits, columns=self.traits)

            # Print Correlation Matrices to output text
            self.output += f"\n--- {self.t('Correlations Matrix')} ({self.t('Genetic')}) ---\n"
            self.output += self.results_df['Genetic_Correlation'].to_string(float_format="%.4f") + "\n"
            self.output += f"\n--- {self.t('Correlations Matrix')} ({self.t('Phenotypic')}) ---\n"
            self.output += self.results_df['Phenotypic_Correlation'].to_string(float_format="%.4f") + "\n"
            self.output += f"\n--- {self.t('Correlations Matrix')} ({self.t('Environmental')}) ---\n"
            self.output += self.results_df['Environmental_Correlation'].to_string(float_format="%.4f") + "\n"


    def export_to_excel(self):
        """
        Exports the analysis results to a structured Excel file using the stored DataFrames.
        """
        if not self.results_df:
            messagebox.showinfo(self.t("Info"), self.t("No results to save."))
            return
        
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
            
        try:
            with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
                for sheet_name, df in self.results_df.items():
                    # Sanitize sheet name for Excel (max 31 chars, no invalid chars)
                    sheet_name_sanitized = sheet_name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")[:31]
                    df.to_excel(writer, sheet_name=sheet_name_sanitized)

            messagebox.showinfo(self.t("Success"), self.t("Results exported to Excel successfully."))
            
        except Exception as e:
            messagebox.showerror(self.t("Error"), f"Failed to export to Excel: {e}")

    def save_results(self):
        """Saves the output to a text file."""
        if not self.output:
            messagebox.showinfo(self.t("Info"), self.t("No results to save."))
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output)
            messagebox.showinfo(self.t("Success"), "Results saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneticAnalyzerApp(root)
    root.mainloop()