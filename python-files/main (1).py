import pandas as pd
import sympy as sp
import math

# ---------------------------------------------
# Newton's Method Function
# ---------------------------------------------
def newton_method(func_str, x0, tol):
    x = sp.symbols('x')
    f_expr = sp.sympify(func_str)
    f_prime_expr = sp.diff(f_expr, x)
    f = sp.lambdify(x, f_expr, "math")
    f_prime = sp.lambdify(x, f_prime_expr, "math")

    rows = []
    n = 0
    rows.append([n, x0, f(x0), None])  # initial guess

    while True:
        f_x = f(x0)
        f_prime_x = f_prime(x0)

        if f_prime_x == 0:
            print(f"\nDerivative became zero at n={n}, method fails.")
            return None, n, pd.DataFrame(rows, columns=['n', 'x_n', 'f(x_n)', '|x_n - x_(n-1)|']), None

        # Newton formula
        x1 = x0 - f_x / f_prime_x
        step_diff = abs(x1 - x0)

        n += 1
        rows.append([n, x1, f(x1), step_diff])

        if step_diff <= tol:
            df = pd.DataFrame(rows, columns=['n', 'x_n', 'f(x_n)', '|x_n - x_(n-1)|'])
            # Accept the *previous* x_n (x0)
            return x0, n, df, step_diff

        x0 = x1

# ---------------------------------------------
# Secant Method Function
# ---------------------------------------------
def secant_method(func_str, x0, x1, tol):
    func = eval("lambda x: " + func_str, {"math": math})
    rows = []
    n = 1

    rows.append([0, x0, func(x0), None])
    rows.append([1, x1, func(x1), abs(x1 - x0)])

    while True:
        f_x0 = func(x0)
        f_x1 = func(x1)

        if (f_x1 - f_x0) == 0:
            print(f"\nDivision by zero at n={n}, method fails.")
            return None, n, pd.DataFrame(rows, columns=['n', 'x_n', 'f(x_n)', '|x_n - x_(n-1)|']), None

        # Secant formula
        x2 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
        step_diff = abs(x2 - x1)

        n += 1
        rows.append([n, x2, func(x2), step_diff])

        if step_diff <= tol:
            df = pd.DataFrame(rows, columns=['n', 'x_n', 'f(x_n)', '|x_n - x_(n-1)|'])
            # Accept the *previous* x_n (x1)
            return x1, n, df, step_diff

        x0, x1 = x1, x2

# ---------------------------------------------
# Interactive App
# ---------------------------------------------
def root_finding_app():
    # Initial Instructions
    print("\n============================================================")
    print("         NUMERICAL METHODS IN APPROXIMATING ROOTS")
    print("==============================================================\n")
    print("INSTRUCTIONS:")
    print("1. Choose a method")
    print("   a. Newton's Method")
    print("   b. Secant Method")
    print("2. Enter a mathematical function in terms of x.")
    print("   Examples:")
    print("      x**2 - 4")
    print("      x**6 - x - 1")
    print("      math.sin(x) - x/2")
    print("      math.exp(x) - 3*x")
    print()
    print("3. Use '**' for exponents. Example: x**3 + 2*x**2 - 5")
    print("4. Use 'math.' prefix for trig/log/exponential functions:")
    print("   Examples: math.sin(x), math.cos(x), math.log(x), math.exp(x)")
    print("5. For Newton's Method → provide one initial guess (x0).")
    print("6. For Secant Method → provide two initial guesses (x0, x1).")
    print("7. Enter a positive error tolerance (e.g., 0.001).")
    print("8. The program will show a table of iterations and the accepted root.\n")

    # Start the menu loop
    while True:
        print("===================================")
        print("            METHODS")
        print("===================================")
        print("a. Newton's Method")
        print("b. Secant Method")
        print("===================================")

        choice = input("Choose a method (a/b): ").strip().lower()

        if choice == 'a':
            print("\n--- NEWTON'S METHOD ---")
            func_str = input("Enter the function in terms of x: ").strip()
            x0 = float(input("Enter initial guess x0: "))
            tol = float(input("Enter error tolerance: "))

            root, iters, table, diff = newton_method(func_str, x0, tol)
            if root is None:
                retry = input("\nMethod failed. Do you want to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("\nThank you for using the Root-Finding App. Have a great day!")
                    break
                else:
                    continue  # restart loop

            pd.set_option('display.float_format', lambda v: f"{v:.10f}")
            print("\nNewton's Method Iterations:")
            print(table.to_string(index=False))
            print(f"\nAccepted x{iters-1} ≈ {root:.10f} as the root")
            print(f"Since |x{iters} - x{iters-1}| = {diff:.10f} <= ε = {tol}")

        elif choice == 'b':
            print("\n--- SECANT METHOD ---")
            func_str = input("Enter the function in terms of x: ").strip()
            x0 = float(input("Enter first initial guess x0: "))
            x1 = float(