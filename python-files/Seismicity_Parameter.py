# earthquake_analysis.py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
# Get the current working directory
cwd = os.getcwd()
os.chdir('D:/')
cwd1 = os.getcwd()
# Create aliases for deprecated types
np.bool = bool
np.float = float
np.int = int
np.complex = complex
np.object = object
np.str = str
np.unicode = str
from openquake.hmtk.parsers.catalogue import CsvCatalogueParser
from openquake.hmtk.seismicity.occurrence.weichert import Weichert
from openquake.hazardlib.mfd import TruncatedGRMFD
from openquake.hmtk.seismicity.occurrence.utils import get_completeness_counts


def main():
    print("==== Earthquake Analysis Tool ====")
    print("This tool calculates the a and b values and plots cumulative occurrence rates.\n")
    
    while True:
        # Get input file path
        while True:
            try:
                catalogue_filename = input("Enter the path to your earthquake catalogue CSV file (or press Enter to exit): ")
                if not catalogue_filename:
                    return
                
                parser = CsvCatalogueParser(catalogue_filename)
                catalogue1 = pd.read_csv(catalogue_filename)
                StartYear=catalogue1["year"].min()
                ENDYEAR=catalogue1["year"].max()
                min_magnitude = catalogue1["magnitude"].min()
                max_magnitude = catalogue1["magnitude"].max()
                catalogue = parser.read_file(start_year=StartYear, end_year=ENDYEAR)
                break
            except Exception as e:
                print(f"Error reading file: {e}\nPlease try again.\n")
        
        # Get completeness table input
        while True:
            try:
                completeness_input = input("Enter completeness table as [[year1,mag1],[year2,mag2],...]: ")
                if not completeness_input:
                    break
                
                completeness_table = np.array(eval(completeness_input))
                
                # Validate completeness table
                if completeness_table.ndim != 2 or completeness_table.shape[1] != 2:
                    raise ValueError("Completeness table must be nx2 array")
                    
                break
            except Exception as e:
                print(f"Invalid input format: {e}\nPlease use format like [[1970,3.5],[1900,4.5]]\n")
        
        # Process the catalogue
        catalogue.sort_catalogue_chronologically()
        
        # Calculate a and b values
        occurrence = Weichert()
        recurrence_config = {"magnitude_interval": 0.1}
        bval1, sigma_b, aval1, sigma_a = occurrence.calculate(
            catalogue, recurrence_config, completeness_table)
        
        print(f"\nResults:\na = {aval1:.3f} (+/- {sigma_a:.3f})")
        print(f"b = {bval1:.3f} (+/- {sigma_b:.3f})\n")
        
        # Create MFD and calculate rates
        min_magnitude1=min_magnitude-0.5
        max_magnitude1=max_magnitude+0.5
        mfd1 = TruncatedGRMFD(min_magnitude1, max_magnitude, 0.2, aval1, bval1)
        occr1 = mfd1.get_annual_occurrence_rates()
        annual_rates1 = np.array([[val[0], val[1]] for val in occr1])
        cumulative_rates_model = np.array([np.sum(annual_rates1[i:, 1]) for i in range(len(annual_rates1))])
        magnitudes_model = [x[0] for x in occr1]
        
        # Get observed rates
        cent_mag, t_per, n_obs = get_completeness_counts(catalogue, completeness_table, 0.2)
        obs_rates = n_obs / t_per
        cum_obs_rates = np.array([np.sum(obs_rates[i:]) for i in range(len(obs_rates))])
        
        # Filter data
        cent_mag1, t_per1, nobs1 = get_completeness_counts(catalogue, completeness_table, 0.2)
        valid_indices = nobs1 > 0
        nobs_filtered = nobs1[valid_indices]
        t_filtered = t_per1[valid_indices]
        magnitudes_filtered = cent_mag1[valid_indices]
        
        # Compute cumulative rates with error bars
        CN = nobs_filtered / t_filtered
        nobs = nobs_filtered.astype(int)
        
        # Predefined error values
        predefined_UN = np.array([2.30, 2.64, 2.92, 3.16, 3.38, 3.58, 3.80, 4.00, 4.10])
        predefined_DN = np.array([0.827, 1.292, 1.63, 1.91, 2.16, 2.38, 2.58, 2.77, 2.94])
        
        UN = np.zeros_like(nobs, dtype=float)
        DN = np.zeros_like(nobs, dtype=float)
        
        for i in range(len(nobs)):
            if nobs[i] <= 9:
                UN[i] = predefined_UN[nobs[i] - 1]
                DN[i] = predefined_DN[nobs[i] - 1]
            else:
                UN[i] = 0.75 + np.sqrt(nobs[i] + 0.5)
                DN[i] = np.sqrt(nobs[i])
        
        UN /= t_filtered
        DN /= t_filtered
        
        # Compute cumulative rates
        YC = np.zeros_like(CN)
        YP = np.zeros_like(CN)
        YM = np.zeros_like(CN)
        
        YC[-1] = CN[-1]
        U = UN[-1]
        D = DN[-1]
        YP[-1] = YC[-1] + U
        YM[-1] = YC[-1] - D
        
        for k in range(len(CN) - 2, -1, -1):
            YC[k] = YC[k + 1] + CN[k]
            U = np.sqrt(UN[k]**2 + U**2)
            YP[k] = YC[k] + U
            D = np.sqrt(DN[k]**2 + D**2)
            YM[k] = YC[k] - D
        
        # Plot results
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_yscale('log')
        
        # Plot observed rates with error bars
        ax.errorbar(magnitudes_filtered, YC, 
                   yerr=[YC - YM, YP - YC], 
                   fmt='o', capsize=5, 
                   label="Observed Rate ± Error")
        
        # Plot model rates
        ax.plot(magnitudes_model, cumulative_rates_model, 
                'r-', label='Model Cumulative Rates')
        
        # Format plot
        ax.set_title('Seismicity Analysis', fontsize=14)
        ax.set_xlabel('Magnitude', fontsize=12)
        ax.set_ylabel('Cumulative Occurrence Rate (per year)', fontsize=12)
        ax.grid(True, which='both', linestyle='--', alpha=0.7)
        ax.legend(fontsize=10)
        plt.xlim([3.5, 8.0])
        plt.ylim([0.00005, 2])
        
        plt.tight_layout()
        
        # Save figure if user wants
        save_fig = input("\nWould you like to save the figure? (y/n): ").lower()
        if save_fig == 'y':
            default_name = os.path.join(os.getcwd(), 'seismicity_plot.png')
            save_path = input(f"Enter save path (default: {default_name}): ") or default_name
            plt.savefig(save_path, dpi=300)
            print(f"Figure saved to {save_path}")
        
        # Show plot (this keeps window open)
        print("\nClose the plot window to continue...")
        plt.show()
        
        # Option to run another analysis
        another = input("\nWould you like to analyze another file? (y/n): ").lower()
        if another != 'y':
            break

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        input("\nPress Enter to exit...")


