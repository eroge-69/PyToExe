# The Newton's Method and Secant Method are numerical techniques for finding the roots of an equation.
# Unlike the Bisection Method, they do not require the root to be bracketed within an interval,
# but they do require a good initial guess for convergence.

# Import all functions from the 'math' library.
from math import *
# Import necessary functions from SymPy for symbolic differentiation.
from sympy import symbols, diff

def print_description(method_choice):
    """
    This function prints a description of the chosen method.
    """
    if method_choice == '1':
        print("\n\t\t\t***** NEWTON'S METHOD *****")
        print("The formula is: x_{n+1} = x_n - (f(x_n)/f'(x_n))")
    elif method_choice == '2':
        print("\n\t\t\t***** SECANT METHOD *****")
        print("The formula is: x_{n+1} = x_n - f(x_n) * ((x_n - x_{n-1}) / (f(x_n) - f(x_{n-1})))")

def f(fx, x):
    """
    Evaluates the user's mathematical function for a given value of x.
    """
    try:
        return eval(fx)
    except (ZeroDivisionError, NameError, SyntaxError, ValueError):
        print("Error: The function is undefined at this point, or you used a wrong function name/syntax!")
        return None

def newton_method(fx, x0, e, dfx_str):
    """
    Implements Newton's Method.
    dfx_str is the string representation of the derivative function.
    """
    print('\n\n***** TABLE OF ITERATES - NEWTON\'S METHOD *****')
    print('\n n \t\t\t x_n \t\t\t\t\t f(x_n) \t\t\t\t|x_n - x_{n-1}|')

    n = 0       # Iteration count
    x_n = x0    # Current value of x
    x_prev = x_n + 1 # Initialize x_prev for the first iteration

    while True:
        f_xn = f(fx, x_n)
        if f_xn is None:
            return
            
        f_prime_xn = f(dfx_str, x_n)
        if f_prime_xn is None or f_prime_xn == 0:
            print("\nError: The derivative is zero or undefined at this point, cannot proceed.")
            return

        # Calculate the absolute difference for the new column
        error = abs(x_n - x_prev)
            
        # Print current iteration data
        print(f" {n} \t\t\t {x_n:0.9f} \t\t\t {f_xn:0.9f} \t\t\t{error:0.9f}")

        if error <= e:
            break

        x_prev = x_n
        
        # Newton's Methos formula
        x_n = x_n - (f_xn / f_prime_xn)         #x_n on the right hand side is the x_prev
        
        n += 1      # adds 1 to the counter

    print(f"\nAccept x_{n-1} = {x_prev:0.9f} as the root of f(x) = {fx} since |x_{n} - x_{n-1}| < ε")

def secant_method(fx, x0, x1, e):
    """
    Implements the Secant Method with the updated table format.
    """
    print('\n\n***** TABLE OF ITERATES - SECANT METHOD *****')
    print('\n n \t\t\t x_n \t\t\t\t\tf(x_n) \t\t\t\t|x_n - x_{n-1}|')

    # Initial row for n=0
    f_x0 = f(fx, x0)
    print(f" {0} \t\t\t {x0:0.9f} \t\t\t {f_x0:0.9f}")

    x_prev = x0
    x_n = x1
    n = 1
    
    while True:
        f_xn = f(fx, x_n)               #f(x1)
        f_x_prev = f(fx, x_prev)        #f(x0)
            
        if f_xn is None:
            return
        if f_xn == f_x_prev:
            print("\nError: The function values at the two points are the same, cannot proceed.")
            return
            
        error = abs(x_n - x_prev)

        print(f" {n} \t\t\t {x_n:0.9f} \t\t\t {f_xn:0.9f} \t\t\t{error:0.9f}")
            
        if error <= e:
            break
                
        # Secant Method formula
        x_next = x_n - f_xn * ((x_n - x_prev) / (f_xn - f_x_prev))
        
        x_prev = x_n
        x_n = x_next            # Calculates iteration values using the formula
        n += 1

    print(f"\nAccept x_{n-1} = {x_prev:0.9f} as the root of f(x) = {fx} since |x_{n} - x_{n-1}| < ε")

if __name__ == '__main__':
    print("\t\t\t***** NEWTON'S AND SECANT METHODS *****")
    
    print("\n\n\t\t\t***** NEWTON'S METHOD *****")
    print("Newton's Method uses the tangent line at an initial value of x to approximate the root.")
    print("The formula is: x_{n+1} = x_n - (f(x_n)/f'(x_n))")
    print("\nConditions that need to be satisfied:")
    print("\t\t\t1. f(x) is continuous and differentiable on an interval containing the root.")
    print("\t\t\t2. f'(x) is not equal to 0 at the initial value of x or intermediate steps.")
    print("\t\t\tAdditionally, the initial value of x (x_0) should be close to the actual root for fast convergence.")
    
    print("\n\n\t\t\t***** SECANT METHOD *****")
    print("The Secant Method is similar to Newton's Method but uses a secant line (a line through two points) to approximate the root.")
    print("It avoids the need for a derivative.")
    print("The formula is: x_{n+1} = x_n - f(x_n) * ((x_n - x_{n-1}) / (f(x_n) - f(x_{n-1})))")
    print("\nConditions that need to be satisfied:")
    print("\t\t\t1. f(x) is continuous on an interval containing the root.")
    print("\t\t\tAdditionally, the initial values of x (x_0, x_1) should be close to the actual root for fast convergence.")
    
    while True:
        while True:
            choice = input("\nChoose a method:\n1 for Newton's Method\n2 for Secant Method\nYour choice:\t")
            if choice in ['1', '2']:
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
                    
        print_description(choice)
        
        print("\nNote:\tUse ** for exponent, * for multiplication, log(x) for ln x, exp() for e^x, and log10(x) for base-10 log(x)")
        print('\t\tExample: x^3-5x-9 -> x**3-5*x-9')
        print('\t\tUse small letter x only')
        print('\t\tOmit blank space between terms')
        print('\t\tUse sin(x), cos(x), tan(x), and pi, and sqrt(x) if needed')
        
        fx = input("\nEnter the function f(x):\t")
            
        try:
                
            if choice == '1':
                # SymPy part: Differentiating the function
                x = symbols('x')
                f_expr = eval(fx)
                df_expr = diff(f_expr, x)
                dfx_str = str(df_expr)
                print(f"\nf(x) is differentiable")
                print(f"The derivative of f(x) is: f'(x) = {dfx_str}")
                
                e = float(input('\nEnter the error tolerance (in decimal form):\t'))
                
                x0 = float(input('\nEnter the initial value of x (x_0):\t'))
                newton_method(fx, x0, e, dfx_str)
            else: # Secant Method
                e = float(input('\nEnter the error tolerance (in decimal form):\t'))
                x0 = float(input('\nEnter the first initial value of x (x_0):\t'))
                x1 = float(input('Enter the second initial value of x (x_1):\t'))
                secant_method(fx, x0, x1, e)

        except (ValueError, NameError, SyntaxError) as err:
            print(f"\nInvalid input or function format. Error: {err}")

        ans = input('\nDo you want to run the program again? [Yes/No]: ')
        if ans.lower() != 'yes':
            break
        
        input("\nPress Enter to exit...")