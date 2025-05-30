import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import linregress
import argparse

def create_regression_report(input_csv, output_pdf):
    df = pd.read_csv(input_csv)
    grouped = df.groupby('AnalysisID')

    with PdfPages(output_pdf) as pdf:
        for analysis_id, group in grouped:
            x = group['X'].values
            y = group['Y'].values

            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            y_pred = slope * x + intercept

            fig, ax = plt.subplots(figsize=(8,6))
            ax.plot(x, y, 'o', label='Data points')
            ax.plot(x, y_pred, 'r-', label=f'Fit line: y={slope:.3f}x + {intercept:.3f}')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title(f'Linear Regression - Analysis: {analysis_id}')
            ax.legend()
            ax.grid(True)

            textstr = f'Slope: {slope:.4f}\nIntercept: {intercept:.4f}\nR²: {r_value**2:.4f}'
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            pdf.savefig(fig)
            plt.close(fig)

            plt.figure(figsize=(8,6))
            plt.axis('off')
            summary = (f"Linear Regression Summary for {analysis_id}:\n\n"
                       f"Slope = {slope:.4f}\n"
                       f"Intercept = {intercept:.4f}\n"
                       f"R-squared = {r_value**2:.4f}\n"
                       f"P-value = {p_value:.4g}\n"
                       f"Std Err = {std_err:.4f}")
            plt.text(0.1, 0.5, summary, fontsize=14)
            pdf.savefig()
            plt.close()

            print(f"Processed {analysis_id} - slope: {slope:.4f}, intercept: {intercept:.4f}, R²: {r_value**2:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate linear regression PDF report.')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output PDF file path')
    args = parser.parse_args()

    create_regression_report(args.input, args.output)
