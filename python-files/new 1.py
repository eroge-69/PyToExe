import numpy as np
from scipy import stats
import os
import sys
from datetime import datetime

# 0. User Inputs
# توضیحات: لطفا نام عنصری که مورد مطالعه قرار می گیرد را وارد کنید.
# مثال: "قطر درخت بلوط" یا "قد دانش آموزان"
element_name = input("لطفا نام پارامتر مورد مطالعه را وارد کنید (مانند: اندازه گیری قطر درختان بلوط) ")

# توضیحات: لطفا واحد اندازه گیری مورد مطالعه را وارد کنید.
# مثال: "cm" برای سانتی متر، "kg" برای کیلوگرم
unit_of_measurement = input("لطفا واحد اندازه گیری را وارد کنید (مثال: cm): ")

# توضیحات: لطفا نوع آزمون را انتخاب کنید.
# برای آزمون یک‌طرفه عدد 1 و برای آزمون دو‌طرفه عدد 2 را وارد کنید.
# (1 برای One-tailed, 2 برای Two-tailed)
try:
    tail = int(input("لطفا نوع آزمون را وارد کنید (1: یک‌طرفه, 2: دو‌طرفه): "))
except ValueError:
    print("خطا: ورودی نامعتبر برای نوع آزمون. لطفا 1 یا 2 را وارد کنید.")
    sys.exit()

direction = ''
if tail == 1:
    # توضیحات: برای آزمون یک‌طرفه، جهت فرضیه جایگزین را مشخص کنید.
    # 'greater' برای "بیشتر از" و 'less' برای "کمتر از"
    direction = input("لطفا جهت آزمون یک‌طرفه را وارد کنید ('greater' برای بیشتر, 'less' برای کمتر): ").lower()
    if direction not in ['greater', 'less']:
        print("خطا: جهت نامعتبر برای آزمون یک‌طرفه. لطفا 'greater' یا 'less' را وارد کنید.")
        sys.exit()
elif tail not in [1, 2]:
    print("خطا: مقدار نامعتبر برای 'tail'. لطفا 1 برای یک‌طرفه یا 2 برای دو‌طرفه وارد کنید.")
    sys.exit()

# Create a timestamp for the filename
current_time = datetime.now()
timestamp_str = current_time.strftime("%Y%m%d_%H%M%S") # Format: %Y%m%d_%H%M%S

# Determine test type string for filename suffix and report
test_type_str_for_filename = ""
test_type_str_for_report = ""

if tail == 2:
    test_type_str_for_filename = "_TwoTailed"
    test_type_str_for_report = "Two-tailed Test"
elif tail == 1:
    if direction == 'greater':
        test_type_str_for_filename = "_OneTailed_Greater"
        test_type_str_for_report = "One-tailed Test (Greater Than)"
    elif direction == 'less':
        test_type_str_for_filename = "_OneTailed_Less"
        test_type_str_for_report = "One-tailed Test (Less Than)"
    # Error handling for direction is already done above

# Dynamically define output filenames
# Replace spaces and special characters in element_name for a valid filename
safe_element_name = "".join(c for c in element_name if c.isalnum() or c in (' ', '.', '_')).replace(' ', '_')
# Include the test type in the filename
output_filename = f"{safe_element_name}_t_test{test_type_str_for_filename}_report_{timestamp_str}.txt"


# 1. Data
# توضیحات: لطفا مقادیر نمونه را با کاما از هم جدا کرده وارد کنید (مثال: 32, 28, 35, 30).
x_input_str = input("لطفا مقادیر نمونه را با کاما جدا شده وارد کنید (مثال: 32, 28, 35): ")
try:
    X = np.array([float(val.strip()) for val in x_input_str.split(',')])
except ValueError:
    print("خطا: ورودی نامعتبر برای مقادیر نمونه. لطفا اعداد را با کاما جدا کنید.")
    sys.exit()

# توضیحات: لطفا میانگین فرضی جامعه (mu_0) را وارد کنید.
# این مقداری است که فرضیه صفر بر اساس آن بنا شده است.
try:
    mu_0 = float(input("لطفا میانگین فرضی جامعه (μ) را وارد کنید: "))
except ValueError:
    print("خطا: ورودی نامعتبر برای میانگین فرضی جامعه. لطفا یک عدد وارد کنید.")
    sys.exit()

n = len(X) # Sample size

# Check if sample size is valid for t-test (at least 2 for calculating std deviation)
if n < 2:
    print("خطا: حجم نمونه باید حداقل 2 باشد تا بتوان انحراف معیار را محاسبه کرد.")
    sys.exit()

# --- Start capturing output to a text file ---
with open(output_filename, 'w', encoding='utf-8') as f:
    sys.stdout = f

    # --- Add new disclaimer ---
    disclaimer_text = "This report has been prepared based on Python software extended by Dr. Ghassem Habibi Bibalani."
    report_width = 120 # Approximate report width for alignment
    padding_spaces = (report_width - len(disclaimer_text)) // 2
    if padding_spaces < 0:
        padding_spaces = 0

    print(" " * padding_spaces + disclaimer_text)
    print("\n")
    # --- End disclaimer ---

    # --- Add initial input and data section to the report ---

    print(f"--- Statistical Analysis Report (One Sample T-test - {test_type_str_for_report}) ---")
    print("-" * 50)
    print("\n")

    print("--- 0. Input Information and Data ---")
    print(f"Subject of study: {element_name}")
    print(f"Unit of measurement: {unit_of_measurement}")
    print(f"Sample Data (X): {X}")
    print(f"Hypothesized Population Mean (μ): {mu_0}")
    print(f"Sample Size (n): {n}")
    
    # Define hypotheses based on test type and direction
    null_hypothesis = ""
    alternative_hypothesis = ""

    if tail == 2:
        null_hypothesis = f"H0: The average {element_name} is equal to {mu_0} {unit_of_measurement} (μ = {mu_0})."
        alternative_hypothesis = f"H1: The average {element_name} is significantly different from {mu_0} {unit_of_measurement} (μ ≠ {mu_0})."
    elif tail == 1:
        if direction == 'greater':
            null_hypothesis = f"H0: The average {element_name} is less than or equal to {mu_0} {unit_of_measurement} (μ ≤ {mu_0})."
            alternative_hypothesis = f"H1: The average {element_name} is significantly greater than {mu_0} {unit_of_measurement} (μ > {mu_0})."
        elif direction == 'less':
            null_hypothesis = f"H0: The average {element_name} is greater than or equal to {mu_0} {unit_of_measurement} (μ ≥ {mu_0})."
            alternative_hypothesis = f"H1: The average {element_name} is significantly less than {mu_0} {unit_of_measurement} (μ < {mu_0})."
    
    print(f"Test Type: {test_type_str_for_report}") # Use the descriptive string for the report
    print(f"Null Hypothesis: {null_hypothesis}")
    print(f"Alternative Hypothesis: {alternative_hypothesis}")
    
    print("\n" + "=" * 50 + "\n")


    # --- 2. Calculate Sample Statistics ---
    X_bar = np.mean(X)
    print(f"Sample Mean (X_bar): {X_bar:.2f}")
    sum_X = np.sum(X)
    print(f"Sum of X_i (ΣX_i): {sum_X}")
    sum_X_sq = np.sum(X**2)
    print(f"Sum of X_i squared (ΣX_i^2): {sum_X_sq}")
    # Calculate sample variance
    if n > 1: # Ensure n-1 is not zero for variance calculation
        S_sq_manual = np.sum((X - X_bar)**2) / (n - 1)
        # S_sq_manual = (sum_X_sq - (sum_X**2) / n) / (n - 1) # Alternative formula, can lead to small negative for float precision
    else:
        S_sq_manual = np.nan # Not defined for n=1
    print(f"Sample Variance (S^2) - manual calculation: {S_sq_manual:.4f}")
    S = np.sqrt(S_sq_manual) if not np.isnan(S_sq_manual) else np.nan
    print(f"Sample Standard Deviation (S): {S:.4f}")
    S_X_bar = S / np.sqrt(n) if n > 0 else np.nan
    print(f"Standard Error of the Mean (S_X_bar): {S_X_bar:.4f}")

    # --- 3. Calculate t-statistic ---
    if S_X_bar > 0: # Avoid division by zero if standard error is zero (e.g., if all data points are identical)
        t_statistic = (X_bar - mu_0) / S_X_bar
    else:
        t_statistic = np.nan # t-statistic not defined
    print(f"Calculated t-statistic: {t_statistic:.2f}")

    # --- 4. Determine Critical t-values and p-value based on test type ---
    df = n - 1 # Degrees of freedom
    print(f"\nDegrees of freedom (df): {df}")
    alpha_5_percent = 0.05
    alpha_1_percent = 0.01

    critical_t_5_percent = np.nan
    critical_t_1_percent = np.nan
    p_value = np.nan

    if df >= 0: # Ensure degrees of freedom are valid
        if tail == 2: # Two-tailed test
            critical_t_5_percent = stats.t.ppf(1 - alpha_5_percent / 2, df)
            critical_t_1_percent = stats.t.ppf(1 - alpha_1_percent / 2, df)
            if not np.isnan(t_statistic):
                p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df))
            print(f"Critical t-value (α=0.05, two-tailed): ±{critical_t_5_percent:.3f}")
            print(f"Critical t-value (α=0.01, two-tailed): ±{critical_t_1_percent:.3f}")
            print(f"P-value (two-tailed): {p_value:.4f}")
        elif tail == 1: # One-tailed test
            if direction == 'greater':
                critical_t_5_percent = stats.t.ppf(1 - alpha_5_percent, df)
                critical_t_1_percent = stats.t.ppf(1 - alpha_1_percent, df)
                if not np.isnan(t_statistic):
                    p_value = 1 - stats.t.cdf(t_statistic, df)
                print(f"Critical t-value (α=0.05, one-tailed, greater): {critical_t_5_percent:.3f}")
                print(f"Critical t-value (α=0.01, one-tailed, greater): {critical_t_1_percent:.3f}")
                print(f"P-value (one-tailed, greater): {p_value:.4f}")
            elif direction == 'less':
                critical_t_5_percent = stats.t.ppf(alpha_5_percent, df)
                critical_t_1_percent = stats.t.ppf(alpha_1_percent, df)
                if not np.isnan(t_statistic):
                    p_value = stats.t.cdf(t_statistic, df)
                print(f"Critical t-value (α=0.05, one-tailed, less): {critical_t_5_percent:.3f}")
                print(f"Critical t-value (α=0.01, one-tailed, less): {critical_t_1_percent:.3f}")
                print(f"P-value (one-tailed, less): {p_value:.4f}")
    else:
        print("Cannot calculate critical t-values or p-value as degrees of freedom is less than 0.")
    
    # --- 5. Interpretation based on Critical Values ---
    print("\n--- Interpretation based on Critical Values ---")
    if np.isnan(t_statistic) or np.isnan(critical_t_5_percent) or np.isnan(critical_t_1_percent):
        print("Cannot interpret based on critical values due to undefined statistics (e.g., insufficient data).")
    else:
        print("\nAt 5% Significance Level (α = 0.05):")
        if tail == 2:
            if abs(t_statistic) > critical_t_5_percent:
                print(f"  Since |t_statistic| ({abs(t_statistic):.2f}) > Critical t-value ({critical_t_5_percent:.3f}), we REJECT the null hypothesis (H0).")
                print(f"  Conclusion: {alternative_hypothesis}")
            else:
                print(f"  Since |t_statistic| ({abs(t_statistic):.2f}) <= Critical t-value ({critical_t_5_percent:.3f}), we FAIL TO REJECT the null hypothesis (H0).")
                print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
                print(f"  (i.e., {null_hypothesis})")
        elif tail == 1:
            if direction == 'greater':
                if t_statistic > critical_t_5_percent:
                    print(f"  Since t_statistic ({t_statistic:.2f}) > Critical t-value ({critical_t_5_percent:.3f}), we REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: {alternative_hypothesis}")
                else:
                    print(f"  Since t_statistic ({t_statistic:.2f}) <= Critical t-value ({critical_t_5_percent:.3f}), we FAIL TO REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
                    print(f"  (i.e., {null_hypothesis})")
            elif direction == 'less':
                if t_statistic < critical_t_5_percent:
                    print(f"  Since t_statistic ({t_statistic:.2f}) < Critical t-value ({critical_t_5_percent:.3f}), we REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: {alternative_hypothesis}")
                else:
                    print(f"  Since t_statistic ({t_statistic:.2f}) >= Critical t-value ({critical_t_5_percent:.3f}), we FAIL TO REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
                    print(f"  (i.e., {null_hypothesis})")

        print("\nAt 1% Significance Level (α = 0.01):")
        if tail == 2:
            if abs(t_statistic) > critical_t_1_percent:
                print(f"  Since |t_statistic| ({abs(t_statistic):.2f}) > Critical t-value ({critical_t_1_percent:.3f}), we REJECT the null hypothesis (H0).")
                print(f"  Conclusion: {alternative_hypothesis}")
            else:
                print(f"  Since |t_statistic| ({abs(t_statistic):.2f}) <= Critical t-value ({critical_t_1_percent:.3f}), we FAIL TO REJECT the null hypothesis (H0).")
                print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
                print(f"  (i.e., {null_hypothesis})")
        elif tail == 1:
            if direction == 'greater':
                if t_statistic > critical_t_1_percent:
                    print(f"  Since t_statistic ({t_statistic:.2f}) > Critical t-value ({critical_t_1_percent:.3f}), we REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: {alternative_hypothesis}")
                else:
                    print(f"  Since t_statistic ({t_statistic:.2f}) <= Critical t-value ({critical_t_1_percent:.3f}), we FAIL TO REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
                    print(f"  (i.e., {null_hypothesis})")
            elif direction == 'less':
                if t_statistic < critical_t_1_percent:
                    print(f"  Since t_statistic ({t_statistic:.2f}) < Critical t-value ({critical_t_1_percent:.3f}), we REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: {alternative_hypothesis}")
                else:
                    print(f"  Since t_statistic ({t_statistic:.2f}) >= Critical t-value ({critical_t_1_percent:.3f}), we FAIL TO REJECT the null hypothesis (H0).")
                    print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
                    print(f"  (i.e., {null_hypothesis})")


    # --- 6. Interpretation based on P-value ---
    print("\n--- Interpretation based on P-value ---")
    if np.isnan(p_value):
        print("Cannot interpret based on p-value due to undefined statistics (e.g., insufficient data).")
    else:
        print("\nAt 5% Significance Level (α = 0.05):")
        if p_value < alpha_5_percent:
            print(f"  Since p-value ({p_value:.4f}) < α ({alpha_5_percent}), we REJECT the null hypothesis (H0).")
            print(f"  Conclusion: {alternative_hypothesis}")
        else:
            print(f"  Since p-value ({p_value:.4f}) >= α ({alpha_5_percent}), we FAIL TO REJECT the null hypothesis (H0).")
            print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
            print(f"  (i.e., {null_hypothesis})")

        print("\nAt 1% Significance Level (α = 0.01):")
        if p_value < alpha_1_percent:
            print(f"  Since p-value ({p_value:.4f}) < α ({alpha_1_percent}), we REJECT the null hypothesis (H0).")
            print(f"  Conclusion: {alternative_hypothesis}")
        else:
            print(f"  Since p-value ({p_value:.4f}) >= α ({alpha_1_percent}), we FAIL TO REJECT the null hypothesis (H0).")
            print(f"  Conclusion: There is NOT sufficient evidence to support the alternative hypothesis.")
            print(f"  (i.e., {null_hypothesis})")


    # --- 7. Generate Statistical Summary Table (Confidence Intervals are still calculated based on two-tailed alpha 0.05 unless changed) ---
    print("\n" * 2)
    print("--- Statistical Reports and t-Test Results ---")
    print("-" * 120)

    # Confidence intervals are typically reported as two-sided, even if the hypothesis test is one-sided.
    # If you wish to calculate one-sided confidence intervals, you would need to add similar logic.
    # For now, I am keeping them two-sided as it's more standard.
    lower_cl_mean_95 = np.nan
    upper_cl_mean_95 = np.nan
    if df >= 0 and not np.isnan(S_X_bar):
        t_critical_for_ci = stats.t.ppf(1 - alpha_5_percent / 2, df)
        lower_cl_mean_95 = X_bar - (t_critical_for_ci * S_X_bar)
        upper_cl_mean_95 = X_bar + (t_critical_for_ci * S_X_bar)
    
    # For standard deviation, confidence intervals are always two-sided.
    lower_cl_std_dev = np.nan
    upper_cl_std_dev = np.nan
    if df > 0 and not np.isnan(S): # Chi-squared for std dev CI requires df > 0
        chi2_lower_tail = stats.chi2.ppf(alpha_5_percent / 2, df)
        chi2_upper_tail = stats.chi2.ppf(1 - alpha_5_percent / 2, df)
        if chi2_upper_tail > 0 and chi2_lower_tail > 0: # Avoid division by zero
            lower_cl_std_dev = np.sqrt(((n - 1) * S**2) / chi2_upper_tail)
            upper_cl_std_dev = np.sqrt(((n - 1) * S**2) / chi2_lower_tail)


    print("\nDescriptive Statistics:")
    print(f"{'Variable':<10} {'N':<5} {'95% LowerCL Mean':<18} {'Mean':<10} {'95% UpperCL Mean':<18} {'LowerCL Std Dev':<18} {'Std Dev':<15} {'UpperCL Std Dev':<18} {'Std Err':<10} {'Minimum':<10} {'Maximum':<10}")
    print(f"{'-'*10:<10} {'-'*5:<5} {'-'*18:<18} {'-'*10:<10} {'-'*18:<18} {'-'*18:<18} {'-'*15:<15} {'-'*18:<18} {'-'*10:<10} {'-'*10:<10} {'-'*10:<10}")
    print(f"{'X':<10} {n:<5} {lower_cl_mean_95:<18.4f} {X_bar:<10.4f} {upper_cl_mean_95:<18.4f} {lower_cl_std_dev:<18.4f} {S:<15.4f} {upper_cl_std_dev:<18.4f} {S_X_bar:<10.4f} {np.min(X):<10.2f} {np.max(X):<10.2f}")

    print("\n" * 1)
    print("t-Test Results:")
    print(f"{'Variable':<10} {'DF':<5} {'t Value':<10} {'P Value':<15}")
    print(f"{'-'*10:<10} {'-'*5:<5} {'-'*10:<10} {'-'*15:<15}")
    print(f"{'X':<10} {df:<5} {t_statistic:<10.2f} {p_value:<15.4f}")
    print("-" * 120)
    print("\n")
# --- End capturing output ---

# Restore sys.stdout to default (console)
sys.stdout = sys.__stdout__
print(f"Analysis complete. Report saved to {output_filename}")