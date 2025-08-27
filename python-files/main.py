import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.fft import ifft, fftfreq
import warnings
import os
warnings.filterwarnings('ignore')

def main():
    while True:
        print("=" * 60)
        
        # Ask user what to plot
        while True:
            print("--- Analysis Options ---\n")
            plot_option = input("RFFT? (y/n/quit): ").lower().strip()
            if plot_option in ['y']:
                plot_full = True
                break
            elif plot_option in ['n']:
                plot_full = False
                break
            elif plot_option in ['quit', 'exit', 'q', 'e']:
                print("Goodbye!")
                return
            else:
                print("Please enter 'y', 'n', or 'quit'.")

        # Get maxAmplitude from console input
        while True:
            try:
                maxAmplitude_input = input("\nEnter the maximum amplitude threshold (or press Enter for default 0.01): ")
                if maxAmplitude_input == "":
                    maxAmplitude = 0.01
                    break
                else: maxAmplitude = float(maxAmplitude_input)
                if maxAmplitude <= 0:
                    print("Please enter a positive value.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        

        # Get optional frequency threshold
        while True:
            try:
                freq_input = input("Enter the maximum frequency threshold in kHz (or press Enter for default 800): ")
                if freq_input == "":
                    maxFrequency = 800
                    break
                maxFrequency = float(freq_input)
                if maxFrequency <= 0:
                    print("Please enter a positive value.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

       #file_path = "F:/Documents/_workMEI/_Python/1.txt" 
        file_path = "C:/1.txt" 
        filter_threshold = maxAmplitude

        x_vals = []
        y_vals = []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, 1):
                    parts = line.strip().split()
                    if len(parts) == 2:
                        try:
                            x, y = float(parts[0]), float(parts[1])
                            if y < maxAmplitude and x < maxFrequency:
                                x_vals.append(x)
                                y_vals.append(y)
                        except ValueError:
                            print(f"Warning: Could not convert values in line {line_num}")
                    elif line.strip():  # Skip empty lines but warn about non-empty malformed lines
                        print(f"Warning: Line {line_num} has {len(parts)} columns, expected 2")
                        
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            print("Please check the file path and try again.")
            file_path = input("\nInsert the file path: ")
            continue
        except Exception as e:
            print(f"Error reading file: {e}")
            continue

        # Check if we have enough points
        if len(x_vals) < 2:
            print("Not enough data points after filtering to interpolate.")
            print("Try adjusting your amplitude or frequency thresholds.")
            continue

        x_vals = np.array(x_vals)
        y_vals = np.array(y_vals)

        # Create interpolator and generate evenly spaced frequency data
        f_interp = interp1d(x_vals, y_vals, kind='linear', bounds_error=False, fill_value=0.0)

        if plot_full:
            # Create a dense, evenly spaced frequency array for FFT
            num_points = 2**14  # Power of 2 for efficient FFT (adjust as needed)
            freq_max = max(x_vals)
            freq_min = min(x_vals)
            freq_dense = np.linspace(freq_min, freq_max, num_points)

            # Interpolate amplitude values
            amp_dense = f_interp(freq_dense)

            # Convert kHz to Hz for proper time scaling (FFT expects Hz)
            freq_dense_hz = freq_dense * 1000  # Convert kHz to Hz

            # Perform inverse Fourier transform
            # We need to create a symmetric spectrum for real-valued time signal
            # Create the full spectrum (positive and negative frequencies)
            full_spectrum = np.concatenate([amp_dense, amp_dense[-2:0:-1]])
            time_signal = ifft(full_spectrum, norm='ortho')

            # Since ifft returns complex values, we take the real part
            time_signal_real = np.real(time_signal)

            # Create time array
            sampling_rate = 2 * freq_max * 1000  # Nyquist rate in Hz
            dt = 1 / sampling_rate
            time_seconds = np.arange(len(time_signal_real)) * dt

            # Convert time to milliseconds for better readability
            time_ms = time_seconds * 1000

        # Plot the results
        plt.figure(figsize=(15, 10 if plot_full else 8))

        if plot_full:
            # Plot 1: Original filtered data and interpolation
            plt.subplot(2, 2, 1)
            plt.plot(x_vals, y_vals, 'o', markersize=3, label='Original Data', alpha=0.7)
            plt.plot(freq_dense, amp_dense, '-', label='Interpolated', linewidth=1, alpha=0.8)
            plt.title(f"Frequency Domain (Filtered)\nAmplitude < {maxAmplitude}, Frequency < {maxFrequency} kHz")
            plt.xlabel("Frequency [kHz]")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True, alpha=0.3)

            # Plot 2: Time domain signal (full view)
            plt.subplot(2, 2, 2)
            plt.plot(time_ms, time_signal_real, 'b-', linewidth=1)
            plt.title("Time Domain Signal (Inverse FFT)")
            plt.xlabel("Time [ms]")
            plt.ylabel("Amplitude")
            plt.grid(True, alpha=0.3)

            # Plot 3: Time domain signal (zoomed in to first few periods)
            plt.subplot(2, 2, 3)
            zoom_samples = min(1000, len(time_signal_real) // 10)  # Show first 10% or 1000 samples
            plt.plot(time_ms[:zoom_samples], time_signal_real[:zoom_samples], 'r-', linewidth=1.5)
            plt.title("Time Domain Signal (Zoomed)")
            plt.xlabel("Time [ms]")
            plt.ylabel("Amplitude")
            plt.grid(True, alpha=0.3)

            # Plot 4: Magnitude of the time signal
            plt.subplot(2, 2, 4)
            plt.plot(time_ms, np.abs(time_signal_real), 'g-', linewidth=1, alpha=0.7)
            plt.title("Absolute Value of Time Signal")
            plt.xlabel("Time [ms]")
            plt.ylabel("|Amplitude|")
            plt.grid(True, alpha=0.3)

        else:
            # Just plot the first graph (frequency domain)
            # Generate interpolated values for plotting
            x_new = np.linspace(min(x_vals), max(x_vals), 1000)
            y_new = f_interp(x_new)
            
            plt.plot(x_vals, y_vals, 'o', markersize=3, label='Original Data', alpha=0.7)
            plt.plot(x_new, y_new, '-', label='Interpolated', linewidth=1.5, alpha=0.8)
            plt.title(f"Filtered Linear Interpolation\nAmplitude < {maxAmplitude}, Frequency < {maxFrequency} kHz")
            plt.xlabel("Frequency [kHz]")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # Print statistics
        print(f"\n" + "=" * 60)
        print("ANALYSIS RESULTS:")
        print("=" * 60)
        print(f"Filter criteria: Amplitude < {maxAmplitude}, Frequency < {maxFrequency} kHz")
        print(f"Original data points: {len(x_vals)}")
        print(f"Frequency range: {min(x_vals):.2f} - {max(x_vals):.2f} kHz")
        print(f"Amplitude range: {min(y_vals):.6f} - {max(y_vals):.6f}")

        if plot_full:
            print(f"Interpolated points for FFT: {num_points}")
            print(f"Time signal length: {len(time_signal_real)} samples")
            print(f"Time duration: {time_ms[-1]:.2f} ms")
            print(f"Max time signal amplitude: {np.max(np.abs(time_signal_real)):.6f}")

            # Optional: Save the time domain signal to a file
            save_option = input("\nDo you want to save the time domain data to a file? (y/n): ")
            if save_option.lower() in ['y', 'yes']:
                output_file = "time_domain_output.txt"
                np.savetxt(output_file, np.column_stack((time_ms, time_signal_real)), 
                           header="Time[ms] Amplitude", fmt='%.6f')
                print(f"Time domain data saved to {output_file}")

        # Ask if user wants to run another analysis
        print("\n" + "-" * 60)
        while True:
            restart = input("Do you want to perform another analysis? (y/n): ").lower().strip()
            if restart in ['y', 'yes', '']:
                print("\n" + "=" * 60)
                print("Starting new analysis...")
                print("=" * 60)
                break
            elif restart in ['n', 'no']:
                print("\n Goodbye!")
                return
            else:
                print("Please enter 'y' or 'n'.")

# Start the program
if __name__ == "__main__":
    main()