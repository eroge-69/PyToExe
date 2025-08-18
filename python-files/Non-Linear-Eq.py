from sympy import symbols, simplify ,diff
from sympy.core.sympify import SympifyError
import math

def get_non_lin_exp():
    print("----------------------------------------------------------------------------")
    print("First step:")
    print("Please enter a nonlinear expression in terms of 'x'.")
    print("For example: x*cos(x) - 2*x**2 + 3*x - 1")
    while True:
        x = input("Enter the expression: ")
        try:
            expr = simplify(x)
            if 'x' not in str(expr):
                print("The expression must contain the variable 'x'.\nplease try again.")
            return expr
        except SympifyError:
            print("Invalid expression. Please enter a valid nonlinear expression in terms of 'x'.")
        except Exception as e:
            print(f"An error occurred: {e}.")

def get_intervals():
    print("----------------------------------------------------------------------------")
    print("Second step:")
    print("Please enter the interval endpoints, separated by commas (e.g., -2, 2.5, 3e, -1.2, e).")
    print("You can use 'e' for the natural logarithm base.")
    while True:
        x = input("Enter the intervals: ")
        raw_int = [item.strip() for item in x.split(',')]
        parsed_int = []
        is_valid = True
        for i in raw_int:
            if not i:
                continue
            if i.lower() == 'e':
                parsed_int.append(math.e)
                continue
            try:
                if 'e' in i.lower():
                    parsed_int.append(float(i))
                else:
                    parsed_int.append(float(i))
            except ValueError:
                print(f"Invalid input '{i}'. Please enter valid numbers or 'e'.")
                is_valid = False
                break
        if is_valid and len(parsed_int) % 2 != 0:
            print("Error: The number of values must be even to form intervals (e.g., [a, b]). Please enter an even number of values.")
        else:
            intervals = []
            for i in range(0, len(parsed_int), 2):
                a, b = parsed_int[i], parsed_int[i + 1]
                if a > b:
                    intervals.append((b, a))
                else:
                    intervals.append((a, b))
            intervals.sort(key = lambda x: x[0])

            return intervals

def get_tolerance():
    print("----------------------------------------------------------------------------")
    print("Third step:")
    print("Please enter the tolerance for the method.")
    while True:
        try:
            tol = float(input("Enter the tolerance: "))
            if tol <= 0:
                print("Tolerance must be a positive number.")
            else:
                return tol
        except ValueError:
            print("Invalid input. Please enter a positive number.")

def get_rounding():
    print("----------------------------------------------------------------------------")
    print("Fourth step:")
    print("Please enter the number of decimal places for rounding.")
    while True:
        try:
            rounding = int(input("Enter the number of decimal places: "))
            if rounding < 0:
                print("Rounding must be a non-negative integer.")
            else:
                return rounding
        except ValueError:
            print("Invalid input. Please enter a non-negative integer.")

def newton_raphson_method(expr, x0, tol, rounding):
    x = symbols('x')
    f = expr
    f_prime = diff(f, x)
    if f_prime.subs(x, x0) == 0:
        print("Error: The derivative at the initial guess is zero. The method cannot proceed.")
        return None
    iterations = 0
    print(f"Starting Newton-Raphson with initial guess: {x0}")
    while True:
        iterations += 1
        f_value = f.subs(x, x0)
        f_prime_value = f_prime.subs(x, x0)
        if f_prime_value == 0:
            print("Error: The derivative is zero. The method cannot proceed.")
            return None
        x_new = x0 - f_value / f_prime_value
        if abs(x_new - x0) < tol:
            break
        x0 = float(x_new)
    final_root = round(x_new, rounding)
    root = x_new.evalf()
    print(f"Newton-Raphson finished after {iterations} iterations.")
    print(f"The root is approximately {root}")
    print(f"The final rounded result to {rounding}D decimal places is: {final_root}")
    return final_root

def bisection_method(expr, a, b, tol, rounding):
    x = symbols('x')
    fa = expr.subs(x, a)
    fb = expr.subs(x, b)
    if fa * fb >= 0:
        print("Error: The initial interval is invalid. f(a) and f(b) must have opposite signs.")
        return None
    iterations = 0
    while (b - a) >= tol:
        iterations += 1
        c = (a + b) / 2
        fc = expr.subs(x, c)
        if fc == 0:
            a, b = c, c
            break
        elif fa * fc < 0:
            b = c
        else:
            a = c
    root = (a + b) / 2
    final_root = round(root, rounding)
    print(f"Bisection Method finished after {iterations} iterations.")
    print(f"The root is approximately {root}")
    print(f"The final rounded result to {rounding}D decimal places is: {final_root}")
    return final_root

def simple_iteration_method(expr, x0, tol, rounding, max_iter=1000):
    x = symbols('x')
    x_old = float(x0)
    iterations = 0
    print(f"Starting Simple Iteration with initial guess: {x_old}")
    while True:
        iterations += 1
        try:
            x_new = expr.subs(x, x_old)
            if not x_new.is_real:
                print("Error: The iteration resulted in a complex number. The method may not converge with this g(x) or initial guess.")
                return None
            x_new_float = float(x_new)
            if abs(x_new_float - x_old) < tol or iterations >= max_iter:
                break
            x_old = x_new_float
        except Exception as e:
            print(f"An error occurred during iteration: {e}")
            return None
    final_root = round(x_new_float, rounding)
    root = x_new.evalf()
    print(f"Fixed-Point Iteration finished after {iterations} iterations.")
    print(f"The root is approximately {root}")
    print(f"The final rounded result to {rounding}D decimal places is: {final_root}")
    return final_root

def convert_f_to_g(expr):
    x = symbols('x')
    g_expr = x - expr
    g_expr = simplify(g_expr)
    print(f"Converted expression f(x) = {expr} to g(x) = {g_expr}")
    return g_expr

while True:
    while True:
        try:
            print("----------------------------------------------------------------------------")
            method = int(input("1-Newton-Raphson Method\n2-Bisection Method\n3-Simple Iteration Method\nChoose the method(Enter the number): "))
            if method in [1, 2, 3]:
                break
        except ValueError:
            print("Choose 1, 2 or 3 please!")
    if method == 1:
        expr = get_non_lin_exp()
        inter = get_intervals()
        tol = get_tolerance()
        rounding = get_rounding()
        for a, b in inter:
            print(f"--- Testing Interval: [{a}, {b}] ---")
            try:
                x0 = (a + b) / 2
                newton_raphson_method(expr, x0, tol, rounding)
            except Exception as e:
                print(f"An error occurred during Newton-Raphson method: {e}")
    elif method == 2:
        expr = get_non_lin_exp()
        inter = get_intervals()
        tol = get_tolerance()
        rounding = get_rounding()
        for a, b in inter:
            print(f"--- Testing Interval: [{a}, {b}] ---")
            bisection_method(expr, a, b, tol, rounding)
    elif method == 3:
        expr = get_non_lin_exp()
        expr = convert_f_to_g(expr)
        x0 = float(input("Enter the initial guess for the root: "))
        tol = get_tolerance()
        rounding = get_rounding()
        max_iter = int(input("Enter the maximum number of iterations (default is 1000): "))
        print(f"--- Starting Simple Iteration Method with initial guess: {x0} ---")
        simple_iteration_method(expr, x0, tol, rounding, max_iter)