
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import warnings
import threading
import sys
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from PIL import Image, ImageTk # Import Pillow for image handling

# Try importing pmdarima and handle potential ImportError
try:
    from pmdarima import auto_arima
except ImportError:
    root_check = tk.Tk()
    root_check.withdraw()
    messagebox.showerror("Error", "Required library 'pmdarima' not found.\nPlease install it by running: pip install pmdarima")
    root_check.destroy()
    auto_arima = None
    sys.exit("pmdarima not found.")

class MonthlyTemperaturePredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monthly Temperature Predictor (SARIMA-ANN Hybrid)")
        self.root.geometry("600x350")
        self.root.configure(bg="#e6f2ff")
        self.file_path = None

        self.font = ("Segoe UI", 12)
        self.title_font = ("Segoe UI", 16, "bold")

        self.title_label = tk.Label(root, text="🌡️ Monthly Average Temperature Predictor", font=self.title_font, bg="#e6f2ff", fg="#003366")
        self.title_label.pack(pady=(15, 10))

        self.file_label = tk.Label(root, text="No file selected (Requires YEAR, Month, and Average temperature columns)", font=self.font, bg="#e6f2ff", fg="#003366")
        self.file_label.pack(pady=5)
        self.browse_button = tk.Button(root, text="Select Monthly Average Excel File", font=self.font, bg="#b3d1ff", fg="#003366", activebackground="#99c2ff", relief=tk.RAISED, command=self.browse_file)
        self.browse_button.pack(pady=5)

        year_frame = tk.Frame(root, bg="#e6f2ff")
        year_frame.pack(pady=15)
        tk.Label(year_frame, text="Predict Until Year:", font=self.font, bg="#e6f2ff", fg="#003366").grid(row=0, column=0, padx=5)
        self.year_entry = tk.Entry(year_frame, width=8, font=self.font)
        self.year_entry.grid(row=0, column=1)
        self.year_entry.insert(0, str(datetime.now().year + 5)) # Default to 5 years ahead

        self.progress = ttk.Progressbar(root, mode='indeterminate', length=400)
        self.progress.pack(pady=10)
        self.progress.pack_forget()

        self.run_button = tk.Button(root, text="Run Hybrid Prediction", font=self.font, bg="#66b3ff", fg="#003366", activebackground="#3399ff", relief=tk.RAISED, command=self.run_prediction)
        self.run_button.pack(pady=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel file with Monthly Averages",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))

    def run_prediction(self):
        if auto_arima is None:
             messagebox.showerror("Error", "pmdarima is not installed or failed to import. Cannot run prediction.")
             return
        if not self.file_path:
            messagebox.showerror("Error", "Please select the Excel file containing monthly average data.")
            return
        try:
            target_year = int(self.year_entry.get())
            if target_year <= datetime.now().year - 50 or target_year > datetime.now().year + 100: # Allow predicting further ahead
                 raise ValueError("Year out of reasonable range")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid target year.")
            return

        self.progress.pack(pady=10)
        self.progress.start(10)
        self.run_button.config(state=tk.DISABLED)
        threading.Thread(target=self._run_prediction_thread, args=(target_year,), daemon=True).start()

    def _finish_prediction_ui(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.run_button.config(state=tk.NORMAL)

    def _run_prediction_thread(self, target_year):
        try:
            self._do_prediction(target_year)
        except Exception as e:
            error_message = f"An unexpected error occurred during prediction: {e}\n\nPlease check the input file format and data integrity."
            self.root.after(0, lambda: messagebox.showerror("Prediction Error", error_message))
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.root.after(0, self._finish_prediction_ui)

    def _check_columns(self, df):
        """Checks if DataFrame has YEAR, Month, and Average temperature columns."""
        cols = df.columns.str.strip().str.upper()
        has_year = 'YEAR' in cols
        has_month = 'MONTH' in cols
        has_avg_temp = 'AVERAGE TEMPERATURE' in cols
        return has_year and has_month and has_avg_temp

    def _create_lagged_features(self, data, n_lags=12):
        df = pd.DataFrame(data)
        for i in range(1, n_lags + 1):
            df[f'lag_{i}'] = df['Average temperature'].shift(i)
        df.dropna(inplace=True)
        return df

    def _build_ann_model(self, input_dim):
        model = Sequential()
        model.add(Dense(10, activation='relu', input_dim=input_dim)) # Simplified to 1 hidden layer with 10 neurons
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        return model

    def _draw_ann_architecture(self, input_dim, hidden_layers_nodes, output_dim, file_path):
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.set_title("Artificial Neural Network Architecture")
        ax.axis("off")

        # Define node colors
        input_color = "skyblue"
        hidden_color = "lightcoral"
        output_color = "lightgreen"

        # Calculate horizontal spacing between layers
        layer_spacing = 2.0
        node_spacing = 0.8 # Increased vertical spacing between nodes

        # Store node positions for drawing connections
        all_layer_node_positions = []

        # Input Layer
        input_layer_x = 0
        input_nodes_y = np.linspace(-((input_dim - 1) * node_spacing) / 2, ((input_dim - 1) * node_spacing) / 2, input_dim)
        input_nodes_pos = [(input_layer_x, y) for y in input_nodes_y]
        all_layer_node_positions.append(input_nodes_pos)

        for i, (x, y) in enumerate(input_nodes_pos):
            ax.add_patch(plt.Circle((x, y), 0.1, color=input_color, ec="black"))
            ax.text(x - 0.2, y, f"Input {i+1}", ha="right", va="center")

        # Hidden Layers
        current_x = input_layer_x + layer_spacing
        for layer_idx, num_nodes in enumerate(hidden_layers_nodes):
            hidden_nodes_y = np.linspace(-((num_nodes - 1) * node_spacing) / 2, ((num_nodes - 1) * node_spacing) / 2, num_nodes)
            current_layer_nodes_pos = [(current_x, y) for y in hidden_nodes_y]
            all_layer_node_positions.append(current_layer_nodes_pos)

            # Draw nodes
            for i, (x, y) in enumerate(current_layer_nodes_pos):
                ax.add_patch(plt.Circle((x, y), 0.1, color=hidden_color, ec="black"))
                ax.text(x, y + 0.2, f"H{layer_idx+1}-{i+1}", ha="center", va="bottom")

            # Draw connections from previous layer
            for prev_node_x, prev_node_y in all_layer_node_positions[-2]:
                for curr_node_x, curr_node_y in current_layer_nodes_pos:
                    ax.plot([prev_node_x, curr_node_x], [prev_node_y, curr_node_y], "k-", lw=0.5)
            current_x += layer_spacing

        # Output Layer
        output_layer_x = current_x
        output_nodes_y = np.linspace(-((output_dim - 1) * node_spacing) / 2, ((output_dim - 1) * node_spacing) / 2, output_dim)
        output_nodes_pos = [(output_layer_x, y) for y in output_nodes_y]
        all_layer_node_positions.append(output_nodes_pos)

        for i, (x, y) in enumerate(output_nodes_pos):
            ax.add_patch(plt.Circle((x, y), 0.1, color=output_color, ec="black"))
            ax.text(x + 0.2, y, f"Output {i+1}", ha="left", va="center")

        # Draw connections from last hidden layer to output layer
        for prev_node_x, prev_node_y in all_layer_node_positions[-2]:
            for curr_node_x, curr_node_y in output_nodes_pos:
                ax.plot([prev_node_x, curr_node_x], [prev_node_y, curr_node_y], "k-", lw=0.5)

        # Adjust plot limits dynamically based on the number of layers and nodes
        max_y_extent = max(len(nodes) for nodes in all_layer_node_positions) * node_spacing / 2 + 0.5 # Add some padding
        ax.set_xlim(-0.5, output_layer_x + 0.5)
        ax.set_ylim(-max_y_extent, max_y_extent)

        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    def _do_prediction(self, final_target_year):
        df_wide_original = None
        header_row = None
        try:
            # --- Read and Validate Input File --- 
            # Try reading with header=0, then header=1
            for h_row in [0, 1]:
                try:
                    df_temp = pd.read_excel(self.file_path, header=h_row)
                    # Normalize column names for checking
                    df_temp.columns = df_temp.columns.str.strip().str.upper()
                    if self._check_columns(df_temp):
                        df_wide_original = pd.read_excel(self.file_path, header=h_row) # Re-read to get original column names
                        header_row = h_row
                        print(f"Detected header on row {h_row}.")
                        break
                except Exception as e:
                    print(f"Attempt to read with header={h_row} failed: {e}")

            if df_wide_original is None:
                self.root.after(0, lambda: messagebox.showerror("Column Error", "Could not automatically detect the header row containing 'YEAR', 'Month', and 'Average temperature' columns. Please ensure these columns exist in the first or second row of your Excel file."))
                return

            df_wide_original.columns = df_wide_original.columns.str.strip().str.upper()
            df_long = df_wide_original.copy()

            # --- Data Transformation (Ensure correct column names and types) ---
            df_long.rename(columns={'AVERAGE TEMPERATURE': 'Average temperature', 'MONTH': 'Month', 'YEAR': 'YEAR'}, inplace=True)

            try:
                df_long['YEAR'] = pd.to_numeric(df_long['YEAR'], errors='coerce')
                df_long['Month'] = pd.to_numeric(df_long['Month'], errors='coerce')
                df_long['Average temperature'] = pd.to_numeric(df_long['Average temperature'], errors='coerce')
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Data Type Error", f"Failed to convert YEAR, Month, or Average temperature columns to numeric types: {e}"))
                return

            df_long.dropna(subset=['YEAR', 'Month', 'Average temperature'], inplace=True)

            if df_long['Average temperature'].isnull().values.any():
                nan_count = df_long['Average temperature'].isnull().sum()
                df_long.dropna(subset=['Average temperature'], inplace=True)
                if df_long.empty:
                    self.root.after(0, lambda: messagebox.showerror("Data Error", f"After removing rows with missing temperature values ({nan_count} found), no data remains."))
                    return
                self.root.after(0, lambda: messagebox.showwarning("Missing Data", f"Found and removed {nan_count} rows with missing temperature values."))

            df_long_current = df_long[['YEAR', 'Month', 'Average temperature']].sort_values(by=['YEAR', 'Month']).reset_index(drop=True)

            if df_long_current.empty:
                self.root.after(0, lambda: messagebox.showerror("Data Error", "No valid data found after processing the file. Please check YEAR, Month, and Average temperature values."))
                return

            last_historical_year = df_long_current["YEAR"].max()
            if final_target_year <= last_historical_year:
                self.root.after(0, lambda: messagebox.showerror("Input Error", f"Target year ({final_target_year}) must be after the last year in the data ({last_historical_year})."))
                return

            # --- Iterative Monthly Hybrid Prediction Loop --- 
            all_predictions_long = [] # Store predictions for all future years here
            min_data_points = 5 # Minimum years of data needed for ARIMA
            n_lags = 12 # Number of lagged features for ANN
            current_year_to_predict = last_historical_year + 1

            # Prepare data for ANN training
            ann_data = self._create_lagged_features(df_long_current[['Average temperature']], n_lags)
            X_ann = ann_data.drop(columns=['Average temperature'])
            y_ann = ann_data['Average temperature']

            # Normalize ANN data
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
            X_ann_scaled = scaler_X.fit_transform(X_ann)
            y_ann_scaled = scaler_y.fit_transform(y_ann.values.reshape(-1, 1))

            # Build and train ANN model
            ann_model = self._build_ann_model(X_ann_scaled.shape[1])
            ann_model.fit(X_ann_scaled, y_ann_scaled, epochs=50, batch_size=32, verbose=0)

            while current_year_to_predict <= final_target_year:
                print(f"Predicting for year: {current_year_to_predict}...")
                yearly_predictions = []
                for month_num in range(1, 13):
                    month_data = df_long_current[df_long_current["Month"] == month_num].copy()
                    month_pred_row = {"YEAR": current_year_to_predict, "Month": month_num}
                    col = 'Average temperature'

                    series = month_data.set_index("YEAR")[col].sort_index()
                    series = series.dropna()

                    sarima_pred_val = np.nan
                    if len(series) >= min_data_points:
                        try:
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore")
                                model = auto_arima(series,
                                                   start_p=1, start_q=1,
                                                   max_p=5, max_q=5,
                                                   seasonal=False,
                                                   stepwise=True,
                                                   suppress_warnings=True,
                                                   error_action='raise',
                                                   trace=False)
                                forecast = model.predict(n_periods=1)
                                sarima_pred_val = forecast.iloc[0] if isinstance(forecast, pd.Series) else forecast[0]
                        except Exception as arima_err:
                            print(f"SARIMA failed for {col}, Month {month_num}, Year {current_year_to_predict}: {arima_err}. Series length: {len(series)}")
                    else:
                        print(f"Skipping SARIMA for {col}, Month {month_num}, Year {current_year_to_predict}: Insufficient data ({len(series)} points)")

                    # ANN prediction (using lagged values from df_long_current)
                    ann_pred_val = np.nan
                    if len(df_long_current) >= n_lags:
                        try:
                            # Get the last n_lags temperature values for ANN input
                            last_n_lags_data = df_long_current[col].tail(n_lags).values.reshape(1, -1)
                            last_n_lags_scaled = scaler_X.transform(last_n_lags_data)
                            ann_pred_scaled = ann_model.predict(last_n_lags_scaled, verbose=0)
                            ann_pred_val = scaler_y.inverse_transform(ann_pred_scaled)[0][0]
                        except Exception as ann_err:
                            print(f"ANN failed for {col}, Month {month_num}, Year {current_year_to_predict}: {ann_err}")

                    # Combine predictions (simple average for now, can be weighted)
                    if not np.isnan(sarima_pred_val) and not np.isnan(ann_pred_val):
                        hybrid_pred_val = (sarima_pred_val + ann_pred_val) / 2
                    elif not np.isnan(sarima_pred_val):
                        hybrid_pred_val = sarima_pred_val
                    elif not np.isnan(ann_pred_val):
                        hybrid_pred_val = ann_pred_val
                    else:
                        hybrid_pred_val = np.nan

                    month_pred_row[col] = hybrid_pred_val
                    yearly_predictions.append(month_pred_row)
                
                # Add the predictions for the current year to the list and update the dataframe for the next iteration
                df_pred_current_year = pd.DataFrame(yearly_predictions)
                all_predictions_long.append(df_pred_current_year)
                # Append predictions to the dataframe used for modeling
                df_long_current = pd.concat([df_long_current, df_pred_current_year[['YEAR', 'Month', 'Average temperature']]], ignore_index=True)
                df_long_current = df_long_current.sort_values(by=['YEAR', 'Month']).reset_index(drop=True)
                
                current_year_to_predict += 1 # Move to the next year

            # --- Prepare Final Output --- 
            if not all_predictions_long:
                 self.root.after(0, lambda: messagebox.showinfo("No Predictions", "No predictions were generated. This might happen if the target year was not after the last historical year."))
                 return
                 
            df_all_pred_long = pd.concat(all_predictions_long, ignore_index=True)

            # Combine original wide data with all the new predicted wide rows
            df_out_long = pd.concat([df_long, df_all_pred_long], ignore_index=True)
            df_out_long["YEAR"] = df_out_long["YEAR"].astype(int)
            df_out_long = df_out_long.sort_values(by=['YEAR', 'Month']).reset_index(drop=True)

            # --- Save and Plot --- 
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            out_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"{base_name}_monthly_predicted_until_{final_target_year}_appended.xlsx",
                title="Save Appended Hybrid Prediction Results"
            )
            if not out_path:
                self.root.after(0, lambda: messagebox.showinfo("Cancelled", "Save operation cancelled."))
                return

            try:
                # Save the combined long data
                df_out_long.to_excel(out_path, index=False)

                # Plotting (uses the final long format data including all predictions)
                plt.style.use('seaborn-v0_8-whitegrid')
                fig, ax = plt.subplots(1, 1, figsize=(12, 6))

                df_plot_long = df_out_long.copy()
                # Corrected line: apply zfill to string accessor .str
                df_plot_long['DateStr'] = df_plot_long['YEAR'].astype(str) + '-' + df_plot_long['Month'].astype(str).str.zfill(2) + '-15'
                df_plot_long['Date'] = pd.to_datetime(df_plot_long['DateStr'], errors='coerce')
                df_plot_long = df_plot_long.dropna(subset=['Date']).set_index('Date')

                hist_data = df_plot_long[df_plot_long['YEAR'] <= last_historical_year]
                pred_data = df_plot_long[df_plot_long['YEAR'] > last_historical_year]

                col = 'Average temperature'
                ax.plot(hist_data.index, hist_data[col], label=f"{col} (Historical Avg)", marker='o', linestyle='-' , markersize=4)
                if not pred_data.empty:
                     ax.plot(pred_data.index, pred_data[col], label=f"{col} (Predicted Avg)", marker='x', linestyle='--', markersize=6, color='red')
                else:
                     print(f"No prediction data to plot after year {last_historical_year}")

                ax.set_ylabel("Temperature (°C)")
                ax.set_title(f"Monthly Average {col}")
                ax.legend()
                ax.grid(True, which='both', linestyle='--', linewidth=0.5)

                ax.set_xlabel("Date (Approx. Mid-Month)")
                fig.suptitle(f"Monthly Temperature Forecast until {final_target_year} (Hybrid SARIMA-ANN)", fontsize=16, y=1.0)
                plt.tight_layout(rect=[0, 0.03, 1, 0.95])

                img_path = out_path.replace(".xlsx", "_forecast.png")
                plt.savefig(img_path, dpi=150)
                plt.close(fig)

                # Generate and save ANN architecture image
                ann_image_path = out_path.replace(".xlsx", "_ann_architecture.png")
                # Pass the actual hidden layer configuration used in _build_ann_model
                self._draw_ann_architecture(input_dim=n_lags, hidden_layers_nodes=[10], output_dim=1, file_path=ann_image_path)

                # Display both the plot and the ANN architecture image
                self.root.after(0, lambda: self._display_results(out_path, img_path, ann_image_path))

            except Exception as e:
                 error_msg = f"Failed to save output file or plot: {e}"
                 print(error_msg)
                 import traceback
                 traceback.print_exc()
                 self.root.after(0, lambda: messagebox.showerror("Save/Plot Error", error_msg))

        except Exception as outer_e:
            error_msg = f"An unexpected error occurred in the prediction process: {outer_e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

    def _display_results(self, excel_path, plot_path, ann_image_path):
        result_window = tk.Toplevel(self.root)
        result_window.title("Prediction Results")
        result_window.geometry("1200x700") # Increased size to accommodate two images

        # Frame for plot
        plot_frame = ttk.LabelFrame(result_window, text="Forecast Plot")
        plot_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Load and display plot image
        plot_img = Image.open(plot_path)
        plot_img = plot_img.resize((550, 450), Image.LANCZOS) # Resize for display
        plot_photo = ImageTk.PhotoImage(plot_img)
        plot_label = tk.Label(plot_frame, image=plot_photo)
        plot_label.image = plot_photo # Keep a reference!
        plot_label.pack(padx=5, pady=5)

        # Frame for ANN architecture
        ann_frame = ttk.LabelFrame(result_window, text="ANN Architecture")
        ann_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Load and display ANN image
        ann_img = Image.open(ann_image_path)
        ann_img = ann_img.resize((550, 450), Image.LANCZOS) # Resize for display
        ann_photo = ImageTk.PhotoImage(ann_img)
        ann_label = tk.Label(ann_frame, image=ann_photo)
        ann_label.image = ann_photo # Keep a reference!
        ann_label.pack(padx=5, pady=5)

        # Display data (e.g., first few rows of the output Excel)
        try:
            df_output = pd.read_excel(excel_path)
            data_text = tk.Text(result_window, height=10, width=100, font=("Courier New", 10))
            data_text.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.BOTH, expand=True)
            data_text.insert(tk.END, "\n--- Predicted Data (First 10 rows) ---\n")
            data_text.insert(tk.END, df_output.head(10).to_string(index=False))
            data_text.config(state=tk.DISABLED) # Make text read-only
        except Exception as e:
            print(f"Error displaying data: {e}")
            messagebox.showerror("Display Error", f"Could not display predicted data: {e}")


if __name__ == "__main__":
    if auto_arima is None:
        print("Exiting because pmdarima is not available.")
    else:
        root = tk.Tk()
        app = MonthlyTemperaturePredictorApp(root)
        root.mainloop()




