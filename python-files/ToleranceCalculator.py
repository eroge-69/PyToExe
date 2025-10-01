#!/usr/bin/env python3
"""
ISO 286-2 / IS 919-2 (1993) Tolerance Calculator
Complete tolerance calculator with GUI interface
Based on Indian Standard IS 919-2 (1993)

Author: Engineering Tolerance Calculator
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class Complete_ISO_Tolerance_Calculator:
    def __init__(self):
        # Complete standard tolerance grades IT01 to IT18 (micrometers)
        self.tolerance_table = {
            (0, 3): {0.1: 0.3, 0: 0.5, 1: 0.8, 2: 1.2, 3: 2, 4: 3, 5: 4, 6: 6, 7: 10, 8: 14, 9: 25, 10: 40, 11: 60, 12: 100, 13: 140, 14: 250, 15: 400, 16: 600, 17: 1000, 18: 1400},
            (3, 6): {0.1: 0.4, 0: 0.6, 1: 1.0, 2: 1.5, 3: 2.5, 4: 4, 5: 5, 6: 8, 7: 12, 8: 18, 9: 30, 10: 48, 11: 75, 12: 120, 13: 180, 14: 300, 15: 480, 16: 750, 17: 1200, 18: 1800},
            (6, 10): {0.1: 0.4, 0: 0.6, 1: 1.0, 2: 1.5, 3: 2.5, 4: 4, 5: 6, 6: 9, 7: 15, 8: 22, 9: 36, 10: 58, 11: 90, 12: 150, 13: 220, 14: 360, 15: 580, 16: 900, 17: 1500, 18: 2200},
            (10, 18): {0.1: 0.5, 0: 0.8, 1: 1.2, 2: 2, 3: 3, 4: 5, 5: 8, 6: 11, 7: 18, 8: 27, 9: 43, 10: 70, 11: 110, 12: 180, 13: 270, 14: 430, 15: 700, 16: 1100, 17: 1800, 18: 2700},
            (18, 30): {0.1: 0.6, 0: 1, 1: 1.5, 2: 2.5, 3: 4, 4: 6, 5: 9, 6: 13, 7: 21, 8: 33, 9: 52, 10: 84, 11: 130, 12: 210, 13: 330, 14: 520, 15: 840, 16: 1300, 17: 2100, 18: 3300},
            (30, 50): {0.1: 0.6, 0: 1, 1: 1.5, 2: 2.5, 3: 4, 4: 7, 5: 11, 6: 16, 7: 25, 8: 39, 9: 62, 10: 100, 11: 160, 12: 250, 13: 390, 14: 620, 15: 1000, 16: 1600, 17: 2500, 18: 3900},
            (50, 80): {0.1: 0.7, 0: 1.2, 1: 2, 2: 3, 3: 5, 4: 8, 5: 13, 6: 19, 7: 30, 8: 46, 9: 74, 10: 120, 11: 190, 12: 300, 13: 460, 14: 740, 15: 1200, 16: 1900, 17: 3000, 18: 4600},
            (80, 120): {0.1: 0.8, 0: 1.5, 1: 2.5, 2: 4, 3: 6, 4: 10, 5: 15, 6: 22, 7: 35, 8: 54, 9: 87, 10: 140, 11: 220, 12: 350, 13: 540, 14: 870, 15: 1400, 16: 2200, 17: 3500, 18: 5400},
            (120, 180): {0.1: 1, 0: 2, 1: 3.5, 2: 5, 3: 8, 4: 12, 5: 18, 6: 25, 7: 40, 8: 63, 9: 100, 10: 160, 11: 250, 12: 400, 13: 630, 14: 1000, 15: 1600, 16: 2500, 17: 4000, 18: 6300},
            (180, 250): {0.1: 1.2, 0: 2.5, 1: 4.5, 2: 7, 3: 10, 4: 14, 5: 20, 6: 29, 7: 46, 8: 72, 9: 115, 10: 185, 11: 290, 12: 460, 13: 720, 14: 1150, 15: 1850, 16: 2900, 17: 4600, 18: 7200},
            (250, 315): {0.1: 1.4, 0: 3, 1: 6, 2: 8, 3: 12, 4: 16, 5: 23, 6: 32, 7: 52, 8: 81, 9: 130, 10: 210, 11: 320, 12: 520, 13: 810, 14: 1300, 15: 2100, 16: 3200, 17: 5200, 18: 8100},
            (315, 400): {0.1: 1.6, 0: 3.5, 1: 7, 2: 9, 3: 13, 4: 18, 5: 25, 6: 36, 7: 57, 8: 89, 9: 140, 10: 230, 11: 360, 12: 570, 13: 890, 14: 1400, 15: 2300, 16: 3600, 17: 5700, 18: 8900},
            (400, 500): {0.1: 1.8, 0: 4, 1: 8, 2: 10, 3: 15, 4: 20, 5: 27, 6: 40, 7: 63, 8: 97, 9: 155, 10: 250, 11: 400, 12: 630, 13: 970, 14: 1550, 15: 2500, 16: 4000, 17: 6300, 18: 9700},
            (500, 630): {1: 9, 2: 11, 3: 16, 4: 22, 5: 32, 6: 44, 7: 70, 8: 110, 9: 175, 10: 280, 11: 440, 12: 700, 13: 1100, 14: 1750, 15: 2800, 16: 4400, 17: 7000, 18: 11000},
            (630, 800): {1: 10, 2: 13, 3: 18, 4: 25, 5: 36, 6: 50, 7: 80, 8: 125, 9: 200, 10: 320, 11: 500, 12: 800, 13: 1250, 14: 2000, 15: 3200, 16: 5000, 17: 8000, 18: 12500},
            (800, 1000): {1: 11, 2: 15, 3: 21, 4: 28, 5: 40, 6: 56, 7: 90, 8: 140, 9: 230, 10: 360, 11: 560, 12: 900, 13: 1400, 14: 2300, 15: 3600, 16: 5600, 17: 9000, 18: 14000},
            (1000, 1250): {1: 13, 2: 18, 3: 24, 4: 33, 5: 47, 6: 66, 7: 105, 8: 165, 9: 260, 10: 420, 11: 660, 12: 1050, 13: 1650, 14: 2600, 15: 4200, 16: 6600, 17: 10500, 18: 16500},
            (1250, 1600): {1: 15, 2: 21, 3: 29, 4: 39, 5: 55, 6: 78, 7: 125, 8: 195, 9: 310, 10: 500, 11: 780, 12: 1250, 13: 1950, 14: 3100, 15: 5000, 16: 7800, 17: 12500, 18: 19500},
            (1600, 2000): {1: 18, 2: 25, 3: 35, 4: 46, 5: 65, 6: 92, 7: 150, 8: 230, 9: 370, 10: 600, 11: 920, 12: 1500, 13: 2300, 14: 3700, 15: 6000, 16: 9200, 17: 15000, 18: 23000},
            (2000, 2500): {1: 22, 2: 30, 3: 41, 4: 55, 5: 78, 6: 110, 7: 175, 8: 280, 9: 440, 10: 700, 11: 1100, 12: 1750, 13: 2800, 14: 4400, 15: 7000, 16: 11000, 17: 17500, 18: 28000},
            (2500, 3150): {1: 26, 2: 36, 3: 50, 4: 68, 5: 96, 6: 135, 7: 210, 8: 330, 9: 540, 10: 860, 11: 1350, 12: 2100, 13: 3300, 14: 5400, 15: 8600, 16: 13500, 17: 21000, 18: 33000},
        }

    def get_tolerance_grade(self, diameter, grade):
        for (lower, upper), grades in self.tolerance_table.items():
            if lower < diameter <= upper:
                return grades.get(grade, None)
        return None

    def calculate_fundamental_deviation(self, diameter, letter, IT, is_hole=True):
        letter_upper = letter.upper()

        if letter_upper == 'H' and is_hole:
            return (IT, 0)
        elif letter_upper == 'H' and not is_hole:
            return (0, -IT)
        elif letter_upper == 'JS':
            half_IT = IT / 2.0
            return (half_IT, -half_IT)
        elif letter_upper == 'G' and not is_hole:
            if diameter <= 3: return (-2, -(IT + 2))
            elif diameter <= 6: return (-3, -(IT + 3))
            elif diameter <= 10: return (-4, -(IT + 4))
            elif diameter <= 18: return (-5, -(IT + 5))
            elif diameter <= 30: return (-6, -(IT + 6))
            elif diameter <= 50: return (-7, -(IT + 7))
            elif diameter <= 80: return (-9, -(IT + 9))
            elif diameter <= 120: return (-10, -(IT + 10))
            else: return (-12, -(IT + 12))
        elif letter_upper == 'F' and not is_hole:
            if diameter <= 3: return (-6, -(IT + 6))
            elif diameter <= 6: return (-8, -(IT + 8))
            elif diameter <= 10: return (-10, -(IT + 10))
            elif diameter <= 18: return (-13, -(IT + 13))
            elif diameter <= 30: return (-16, -(IT + 16))
            elif diameter <= 50: return (-20, -(IT + 20))
            elif diameter <= 80: return (-25, -(IT + 25))
            elif diameter <= 120: return (-30, -(IT + 30))
            else: return (-36, -(IT + 36))
        elif letter_upper == 'E' and not is_hole:
            if diameter <= 3: return (-14, -(IT + 14))
            elif diameter <= 6: return (-20, -(IT + 20))
            elif diameter <= 10: return (-25, -(IT + 25))
            elif diameter <= 18: return (-32, -(IT + 32))
            elif diameter <= 30: return (-40, -(IT + 40))
            elif diameter <= 50: return (-50, -(IT + 50))
            elif diameter <= 80: return (-60, -(IT + 60))
            elif diameter <= 120: return (-72, -(IT + 72))
            elif diameter <= 180: return (-85, -(IT + 85))
            else: return (-100, -(IT + 100))
        elif letter_upper == 'D' and not is_hole:
            if diameter <= 3: return (-20, -(IT + 20))
            elif diameter <= 6: return (-30, -(IT + 30))
            elif diameter <= 10: return (-40, -(IT + 40))
            elif diameter <= 18: return (-50, -(IT + 50))
            elif diameter <= 30: return (-65, -(IT + 65))
            elif diameter <= 50: return (-80, -(IT + 80))
            elif diameter <= 80: return (-100, -(IT + 100))
            elif diameter <= 120: return (-120, -(IT + 120))
            elif diameter <= 180: return (-145, -(IT + 145))
            else: return (-170, -(IT + 170))
        elif letter_upper == 'K':
            if is_hole:
                if diameter <= 3: return (0, -IT)
                elif diameter <= 6: return (IT + 0.5, 0.5)
                elif diameter <= 10: return (IT + 1, 1)
                elif diameter <= 18: return (IT + 2, 2)
                elif diameter <= 30: return (IT + 2, 2)
                elif diameter <= 50: return (IT + 3, 3)
                else: return (IT + 4, 4)
            else:
                if diameter <= 3: return (0, -IT)
                elif diameter <= 6: return (0.5, -(IT - 0.5))
                elif diameter <= 10: return (1, -(IT - 1))
                elif diameter <= 18: return (2, -(IT - 2))
                elif diameter <= 30: return (2, -(IT - 2))
                elif diameter <= 50: return (3, -(IT - 3))
                else: return (4, -(IT - 4))
        else:
            return None

    def calculate_tolerance(self, diameter, fit_type):
        fit_type = fit_type.strip()

        if fit_type.upper().startswith('IT'):
            try:
                grade_str = fit_type[2:]
                if grade_str == '01':
                    grade = 0.1
                elif grade_str == '0':
                    grade = 0
                else:
                    grade = int(grade_str)
            except:
                return {"error": "Invalid IT grade format"}

            IT = self.get_tolerance_grade(diameter, grade)
            if IT is None:
                return {"error": f"Grade {fit_type} not available for diameter {diameter} mm"}

            return {
                "fit_type": fit_type,
                "diameter": diameter,
                "IT_value": IT,
                "tolerance": f"±{IT/2:.4f} μm"
            }
        else:
            letter = fit_type[0]
            try:
                grade_str = fit_type[1:]
                if grade_str == '01':
                    grade = 0.1
                elif grade_str == '0':
                    grade = 0
                else:
                    grade = int(grade_str)
            except:
                return {"error": "Invalid fit type format"}

            is_hole = letter.isupper()
            IT = self.get_tolerance_grade(diameter, grade)
            if IT is None:
                return {"error": f"Grade IT{grade} not found for diameter {diameter} mm"}

            deviations = self.calculate_fundamental_deviation(diameter, letter, IT, is_hole)
            if deviations is None:
                return {"error": f"Fit '{letter}' not fully implemented. Check IS 919-2 tables."}

            upper, lower = deviations

            return {
                "fit_type": fit_type,
                "diameter": diameter,
                "IT_grade": f"IT{grade if grade >= 1 else ('01' if grade == 0.1 else '0')}",
                "IT_value": IT,
                "upper_deviation": upper,
                "lower_deviation": lower,
                "upper_limit": diameter + upper/1000,
                "lower_limit": diameter + lower/1000,
                "tolerance_zone": f"{upper:+.1f}μm / {lower:+.1f}μm",
                "type": "HOLE" if is_hole else "SHAFT"
            }


class ToleranceCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ISO 286-2 Tolerance Calculator")
        self.root.geometry("800x650")
        self.root.resizable(False, False)

        self.calc = Complete_ISO_Tolerance_Calculator()

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", pady=15)
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="ISO 286-2 / IS 919-2 Tolerance Calculator",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack()

        subtitle = tk.Label(
            title_frame,
            text="Complete Tolerance Grades: IT01 to IT18 | Size Range: 0-3150 mm",
            font=("Arial", 9),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle.pack()

        # Input Frame
        input_frame = tk.LabelFrame(self.root, text="Input Parameters", font=("Arial", 11, "bold"), padx=20, pady=20)
        input_frame.pack(padx=20, pady=10, fill="x")

        # Diameter input
        tk.Label(input_frame, text="Diameter (mm):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.diameter_entry = tk.Entry(input_frame, font=("Arial", 10), width=20)
        self.diameter_entry.grid(row=0, column=1, pady=5, padx=10)

        # Fit type input
        tk.Label(input_frame, text="Fit Type:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.fit_entry = tk.Entry(input_frame, font=("Arial", 10), width=20)
        self.fit_entry.grid(row=1, column=1, pady=5, padx=10)

        tk.Label(input_frame, text="(e.g., H8, h7, e8, IT16)", font=("Arial", 8), fg="gray").grid(row=1, column=2, sticky="w")

        # Calculate button
        calc_btn = tk.Button(
            input_frame,
            text="Calculate Tolerance",
            command=self.calculate,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        calc_btn.grid(row=2, column=0, columnspan=3, pady=15)

        # Results Frame
        result_frame = tk.LabelFrame(self.root, text="Calculation Results", font=("Arial", 11, "bold"), padx=20, pady=10)
        result_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=("Courier New", 10),
            height=18,
            wrap=tk.WORD,
            bg="#ecf0f1"
        )
        self.result_text.pack(fill="both", expand=True)

        # Info Frame
        info_frame = tk.Frame(self.root, pady=5)
        info_frame.pack(fill="x", padx=20)

        info_label = tk.Label(
            info_frame,
            text="Supported: Holes (H,G,F,E,D,K,JS) | Shafts (h,g,f,e,d,k,js) | Based on IS 919-2 (1993)",
            font=("Arial", 8),
            fg="gray"
        )
        info_label.pack()

    def calculate(self):
        try:
            diameter = float(self.diameter_entry.get())
            fit_type = self.fit_entry.get().strip()

            if not fit_type:
                messagebox.showerror("Error", "Please enter a fit type")
                return

            if diameter <= 0 or diameter > 3150:
                messagebox.showerror("Error", "Diameter must be between 0 and 3150 mm")
                return

            result = self.calc.calculate_tolerance(diameter, fit_type)

            if "error" in result:
                messagebox.showerror("Error", result["error"])
                return

            # Display results
            self.result_text.delete(1.0, tk.END)
            output = "=" * 70 + "\n"
            output += "TOLERANCE CALCULATION RESULTS\n"
            output += "=" * 70 + "\n\n"
            output += f"Nominal Diameter:       {result['diameter']} mm\n"
            output += f"Fit Type:               {result['fit_type']}\n"

            if 'IT_grade' in result:
                output += f"Tolerance Grade:        {result['IT_grade']}\n"

            output += f"IT Value:               {result['IT_value']:.4f} μm\n"

            if 'type' in result:
                output += f"Type:                   {result['type']}\n"
                output += f"Tolerance Zone:         {result['tolerance_zone']}\n"
                output += f"Upper Deviation:        {result['upper_deviation']:+.2f} μm\n"
                output += f"Lower Deviation:        {result['lower_deviation']:+.2f} μm\n"
                output += "\n" + "-" * 70 + "\n"
                output += "DIMENSIONAL LIMITS:\n"
                output += "-" * 70 + "\n"
                output += f"Upper Limit:            {result['upper_limit']:.6f} mm\n"
                output += f"Lower Limit:            {result['lower_limit']:.6f} mm\n"
                output += f"Total Tolerance:        {result['IT_value']/1000:.6f} mm\n"

            output += "=" * 70

            self.result_text.insert(1.0, output)

        except ValueError:
            messagebox.showerror("Error", "Invalid diameter. Please enter a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = ToleranceCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
