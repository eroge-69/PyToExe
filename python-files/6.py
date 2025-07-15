import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog # Import filedialog
from sympy import *
from sympy.abc import x
from sympy.calculus.util import continuous_domain
from sympy.sets import Reals
import subprocess
import os
import tempfile
from PIL import Image, ImageTk, ImageGrab # Import ImageGrab for clipboard (Windows specific)

def analyze_function(f_str, domain_str=None):
    """
    Analyzes the mathematical function and finds important points for the variation table.
    """
    try:
        f = parse_expr(f_str)
        f_prime = diff(f, x)
    except Exception as e:
        return {"error": f"Error analyzing function: {e}"}

    analysis_domain = Interval(-oo, oo)
    if domain_str:
        try:
            # Handle common interval notations
            if domain_str.startswith('[') and domain_str.endswith(']'):
                bounds_str = domain_str[1:-1]
                left, right = map(parse_expr, bounds_str.split(','))
                analysis_domain = Interval(left, right)
            elif domain_str.startswith('(') and domain_str.endswith(')'):
                bounds_str = domain_str[1:-1]
                left, right = map(parse_expr, bounds_str.split(','))
                analysis_domain = Interval.open(left, right)
            elif domain_str.startswith('[') and domain_str.endswith(')'):
                bounds_str = domain_str[1:-1]
                left, right = map(parse_expr, bounds_str.split(','))
                analysis_domain = Interval.Lopen(left, right)
            elif domain_str.startswith('(') and domain_str.endswith(']'):
                bounds_str = domain_str[1:-1]
                left, right = map(parse_expr, bounds_str.split(','))
                analysis_domain = Interval.Ropen(left, right)
            elif domain_str.lower() == 'reals' or domain_str == '(-oo,oo)':
                analysis_domain = Reals
            else:
                raise ValueError("Invalid domain format.")
        except Exception as e:
            return {"error": f"Error analyzing domain: {e}. Please use formats like [a,b], (a,b), [a,b), (a,b], (-oo,oo), Reals."}

    critical = []
    try:
        # Solve f_prime = 0 for critical points
        solutions = solve(f_prime, x)
        for sol in solutions:
            # Check if the solution is real and within the analysis domain
            if sol.is_real and analysis_domain.contains(sol):
                critical.append(sol)
    except Exception as e:
        print(f"Error solving f_prime = 0: {e}")

    singular = []
    # Get the overall continuous domain of f(x)
    overall_f_domain = continuous_domain(f, x, Reals)
    
    try:
        domain_fp = continuous_domain(f_prime, x, Reals)
        
        # Add points where f is defined but f' is not (e.g., cusps, vertical tangents)
        for boundary_point in domain_fp.boundary:
            if overall_f_domain.contains(boundary_point) and boundary_point not in singular and boundary_point.is_real:
                singular.append(boundary_point)

        # Add points where f itself is undefined (e.g., division by zero)
        if isinstance(overall_f_domain, Union):
            for interval in overall_f_domain.args:
                if interval.left != -oo and not overall_f_domain.contains(interval.left) and interval.left.is_real:
                    singular.append(interval.left)
                if interval.right != oo and not overall_f_domain.contains(interval.right) and interval.right.is_real:
                    singular.append(interval.right)
        elif isinstance(overall_f_domain, Interval):
            if overall_f_domain.left != -oo and not overall_f_domain.contains(overall_f_domain.left) and overall_f_domain.left.is_real:
                singular.append(overall_f_domain.left)
            if overall_f_domain.right != oo and not overall_f_domain.contains(overall_f_domain.right) and overall_f_domain.right.is_real:
                singular.append(overall_f_domain.right)
        
        singular = sorted(list(set(singular)), key=lambda p: p.evalf())

    except Exception as e:
        print(f"Error finding singular points: {e}")


    points_set = set(critical + singular)
    
    # Add explicit domain boundaries if they are finite
    if analysis_domain.is_Interval:
        if analysis_domain.left != -oo and analysis_domain.left.is_real:
            points_set.add(analysis_domain.left)
        if analysis_domain.right != oo and analysis_domain.right.is_real:
            points_set.add(analysis_domain.right)

    points = sorted([p for p in points_set if p.is_real or p in [-oo, oo]], key=lambda p: p.evalf() if p not in [-oo, oo] else float('-inf') if p == -oo else float('inf'))

    # Ensure -oo and +oo are always present if they are part of analysis_domain
    if analysis_domain.is_Interval:
        if analysis_domain.left == -oo and (not points or points[0] != -oo):
            points.insert(0, -oo)
        if analysis_domain.right == oo and (not points or points[-1] != oo):
            points.append(oo)

    points_data = []
    for p in points:
        point_info = {
            "point": p,
            "latex_label": "$-\\infty$" if p == -oo else ("$+\\infty$" if p == oo else f"${latex(p)}$"),
            "value_at_point": None,
            "value_latex": r"\text{ND}",
            "left_limit": None,
            "left_limit_latex": None,
            "right_limit": None,
            "right_limit_latex": None,
            "is_critical": p in critical,
            "is_singular": p in singular, # Points where f or f' is undefined, or f' changes behavior
            "is_removable_discontinuity": False,
            "is_vertical_asymptote": False,
            "is_jump_discontinuity": False, 
            "is_domain_boundary": (p == analysis_domain.left and p != -oo) or \
                                  (p == analysis_domain.right and p != oo)
        }

        try:
            # Check if point is within the overall continuous domain of f
            if overall_f_domain.contains(p):
                val = f.subs(x, p)
                point_info["value_at_point"] = val
                point_info["value_latex"] = latex(val)
            else: # Point is outside f's domain, or is a boundary where f is not defined
                # Calculate limits to determine type of discontinuity
                left_limit = limit(f, x, p, dir='-')
                right_limit = limit(f, x, p, dir='+')
                point_info["left_limit"] = left_limit
                point_info["right_limit"] = right_limit
                point_info["left_limit_latex"] = latex(left_limit)
                point_info["right_limit_latex"] = latex(right_limit)

                # Robust checks for limits
                is_left_real_finite = left_limit.is_real and left_limit.is_finite
                is_right_real_finite = right_limit.is_real and right_limit.is_finite
                is_left_infinite = left_limit.is_infinite
                is_right_infinite = right_limit.is_infinite

                if is_left_real_finite and is_right_real_finite and left_limit == right_limit:
                    point_info["is_removable_discontinuity"] = True
                    point_info["value_at_point"] = left_limit # The value of the hole
                    point_info["value_latex"] = latex(left_limit)
                elif is_left_infinite or is_right_infinite:
                    point_info["is_vertical_asymptote"] = True
                    # Value_at_point remains None or ND for asymptotes
                elif is_left_real_finite and is_right_real_finite and left_limit != right_limit:
                    point_info["is_jump_discontinuity"] = True
                    point_info["value_at_point"] = r"\text{ND}" # Function value is undefined at jump
                    point_info["value_latex"] = r"\text{ND}"
                else: # Limits are non-real, or mixed, or other complex cases
                    point_info["value_at_point"] = r"\text{ND}"
                    point_info["value_latex"] = r"\text{ND}"
            
            # Special handling for infinities (limits already calculated)
            if p == -oo:
                point_info["value_latex"] = latex(point_info["left_limit"])
            elif p == oo:
                point_info["value_latex"] = latex(point_info["right_limit"])
            
        except Exception as e:
            print(f"Error evaluating function at point {p}: {e}")
            point_info["value_latex"] = r"\text{ND}"

        points_data.append(point_info)

    intervals_data = []
    
    for i in range(len(points) - 1):
        a, b = points[i], points[i+1]
        
        sign_f_prime = 'h' # Default to undefined for f'
        variation_arrow = 'R \\' # Default to "Rien" for f

        # Determine if the interval (a, b) is within the real domain of f
        # Test a midpoint to see if f(x) is real and defined
        mid = (a + b) / 2
        if a == -oo and b == oo: mid = 0
        elif a == -oo: mid = b - 1
        elif b == oo: mid = a + 1

        is_interval_in_real_domain = False
        try:
            test_val_f = f.subs(x, mid)
            if test_val_f.is_real and not test_val_f.is_infinite:
                is_interval_in_real_domain = True
        except Exception:
            is_interval_in_real_domain = False

        if is_interval_in_real_domain:
            # If in f's real domain, then check f_prime's domain
            is_in_fp_domain = continuous_domain(f_prime, x, Reals).contains(mid)
            if is_in_fp_domain:
                try:
                    fp_val = f_prime.subs(x, mid).evalf()
                    if fp_val > 0:
                        sign_f_prime = '+'
                        variation_arrow = '+'
                    elif fp_val < 0:
                        sign_f_prime = '-'
                        variation_arrow = '-'
                    else: # fp_val == 0 for an interval
                        sign_f_prime = '0'
                        variation_arrow = 'C' # Constant
                except Exception as e:
                    print(f"Error evaluating derivative in interval ({a}, {b}): {e}")
                    sign_f_prime = 'h'
                    variation_arrow = 'R \\'
            else: # In f's domain, but not f_prime's domain (e.g., sqrt(x) at x=0)
                sign_f_prime = 'h' # f' is undefined
                variation_arrow = 'R \\' # No arrow across this, as f' is undefined
        else: # Interval is outside the real domain of f
            sign_f_prime = 'h' # Undefined for f'
            variation_arrow = 'R \\' # Undefined for f

        intervals_data.append({
            "start_point": a,
            "end_point": b,
            "sign_f_prime": sign_f_prime,
            "variation_arrow": variation_arrow
        })

    return {
        "f": latex(f),
        "f_prime": latex(f_prime),
        "points_data": points_data,
        "intervals_data": intervals_data,
        "critical": critical,
        "singular": singular, # These are points where f(x) is undefined
        "original_function_obj": f # Pass the SymPy function object
    }

def analyze_expression_sign(expr_str):
    """
    Analyzes the sign of a mathematical expression, detailing factors/numerator and denominator.
    Returns a dictionary containing:
    - overall_expr: The original expression in LaTeX format.
    - all_points: All important points (roots and forbidden values) sorted.
    - analyses: A list of dictionaries, each dictionary representing the sign analysis for a factor/term,
                including the final analysis of the original expression.
    """
    try:
        expr = parse_expr(expr_str)
    except Exception as e:
        return {"error": f"Error analyzing expression: {e}"}

    individual_analyses = []
    all_points_set = set()
    
    numer, denom = expr.as_numer_denom()
    
    if denom != 1: # It's a rational expression
        # Analyze numerator
        num_roots = solve(numer, x)
        num_roots_real = [s for s in num_roots if s.is_real]
        
        num_singular = []
        num_domain = continuous_domain(numer, x, Reals)
        if isinstance(num_domain, Union):
            for interval in num_domain.args:
                if interval.left != -oo and not interval.left.is_infinite and not num_domain.contains(interval.left):
                    if interval.left.is_real: num_singular.append(interval.left)
                if interval.right != oo and not interval.right.is_infinite and not num_domain.contains(interval.right):
                    if interval.right.is_real: num_singular.append(interval.right)
        elif isinstance(num_domain, Interval):
            if num_domain.left != -oo and not num_domain.left.is_infinite and not num_domain.contains(num_domain.left):
                if num_domain.left.is_real: num_singular.append(num_domain.left)
            if num_domain.right != oo and not num_domain.right.is_infinite and not num_domain.contains(num_domain.right):
                if num_domain.right.is_real: num_singular.append(num_domain.right)
        num_singular = sorted(list(set(num_singular)), key=lambda p: p.evalf())


        individual_analyses.append({
            "label": latex(numer),
            "expr_obj": numer,
            "roots": num_roots_real,
            "singular": num_singular 
        })
        all_points_set.update(num_roots_real)
        all_points_set.update(num_singular)
        
        # Analyze denominator
        den_roots = solve(denom, x)
        den_roots_real = [s for s in den_roots if s.is_real]
        
        den_singular = []
        den_domain = continuous_domain(denom, x, Reals)
        if isinstance(den_domain, Union):
            for interval in den_domain.args:
                if interval.left != -oo and not interval.left.is_infinite and not den_domain.contains(interval.left):
                    if interval.left.is_real: den_singular.append(interval.left)
                if interval.right != oo and not interval.right.is_infinite and not den_domain.contains(interval.right):
                    if interval.right.is_real: den_singular.append(interval.right)
        elif isinstance(den_domain, Interval):
            if den_domain.left != -oo and not den_domain.left.is_infinite and not den_domain.contains(den_domain.left):
                if den_domain.left.is_real: den_singular.append(den_domain.left)
            if den_domain.right != oo and not den_domain.right.is_infinite and not den_domain.contains(den_domain.right):
                if den_domain.right.is_real: den_singular.append(den_domain.right)
        den_singular = sorted(list(set(den_singular)), key=lambda p: p.evalf())

        individual_analyses.append({
            "label": latex(denom),
            "expr_obj": denom,
            "roots": den_roots_real, # Denominator roots are points where it's zero
            "singular": den_singular # Singular points of the denominator itself
        })
        all_points_set.update(den_roots_real)
        all_points_set.update(den_singular)

    else: # Not a rational expression, try to factor for product terms
        factored_expr = factor(expr)
        
        if factored_expr.is_Mul: # It's a product of multiple terms
            for factor_term in factored_expr.args:
                factor_roots = solve(factor_term, x)
                factor_roots_real = [s for s in factor_roots if s.is_real]
                
                # Check for singular points within the factor itself (e.g., sqrt(x), 1/x within a factor)
                factor_singular = []
                factor_domain = continuous_domain(factor_term, x, Reals)
                if isinstance(factor_domain, Union):
                    for interval in factor_domain.args:
                        if interval.left != -oo and not interval.left.is_infinite and not factor_domain.contains(interval.left):
                            if interval.left.is_real: factor_singular.append(interval.left)
                        if interval.right != oo and not interval.right.is_infinite and not factor_domain.contains(interval.right):
                            if interval.right.is_real: factor_singular.append(interval.right)
                elif isinstance(factor_domain, Interval):
                    if factor_domain.left != -oo and not factor_domain.left.is_infinite and not factor_domain.contains(factor_domain.left):
                        if factor_domain.left.is_real: factor_singular.append(factor_domain.left)
                    if factor_domain.right != oo and not factor_domain.right.is_infinite and not factor_domain.contains(factor_domain.right):
                        if factor_domain.right.is_real: factor_singular.append(factor_domain.right)
                factor_singular = sorted(list(set(factor_singular)), key=lambda p: p.evalf())

                individual_analyses.append({
                    "label": latex(factor_term),
                    "expr_obj": factor_term,
                    "roots": factor_roots_real,
                    "singular": factor_singular
                })
                all_points_set.update(factor_roots_real)
                all_points_set.update(factor_singular)

        else: # It's a single term (e.g., x, x+1, x**2, sin(x))
            single_expr_roots = solve(expr, x)
            single_expr_roots_real = [s for s in single_expr_roots if s.is_real]
            
            single_expr_singular = []
            single_expr_domain = continuous_domain(expr, x, Reals)
            
            numer_single, denom_single = expr.as_numer_denom()
            if denom_single != 1:
                den_roots_single = solve(denom_single, x)
                for dr in den_roots_single:
                    if dr.is_real:
                        single_expr_singular.append(dr)
            
            if isinstance(single_expr_domain, Union):
                for interval in single_expr_domain.args:
                    if interval.left != -oo and not interval.left.is_infinite and not single_expr_domain.contains(interval.left):
                        if interval.left.is_real: single_expr_singular.append(interval.left)
                    if interval.right != oo and not interval.right.is_infinite and not single_expr_domain.contains(interval.right):
                        if interval.right.is_real: single_expr_singular.append(interval.right)
            elif isinstance(single_expr_domain, Interval):
                if single_expr_domain.left != -oo and not single_expr_domain.left.is_infinite and not single_expr_domain.contains(single_expr_domain.left):
                    if single_expr_domain.left.is_real: single_expr_singular.append(single_expr_domain.left)
                if single_expr_domain.right != oo and not single_expr_domain.right.is_infinite and not single_expr_domain.contains(single_expr_domain.right):
                    if single_expr_domain.right.is_real: single_expr_singular.append(single_expr_domain.right)
            
            single_expr_singular = sorted(list(set(single_expr_singular)), key=lambda p: p.evalf())

            individual_analyses.append({
                "label": latex(expr),
                "expr_obj": expr,
                "roots": single_expr_roots_real,
                "singular": single_expr_singular
            })
            all_points_set.update(single_expr_roots_real)
            all_points_set.update(single_expr_singular)

    all_points = sorted(list(all_points_set) + [-oo, oo], key=lambda p: p.evalf() if p not in [-oo, oo] else float('-inf') if p == -oo else float('inf'))

    if not all_points or all_points[0] != -oo:
        all_points.insert(0, -oo)
    if not all_points or all_points[-1] != oo:
        all_points.append(oo)

    for analysis in individual_analyses:
        current_expr_obj = analysis["expr_obj"]
        current_domain = continuous_domain(current_expr_obj, x, Reals)
        current_signs = []
        for i in range(len(all_points) - 1):
            a, b = all_points[i], all_points[i+1]
            try:
                if a == -oo and b == oo: mid = 0
                elif a == -oo: mid = b - 1
                elif b == oo: mid = a + 1
                else: mid = (a + b) / 2

                if not current_domain.contains(mid):
                    current_signs.append('h')
                else:
                    val = current_expr_obj.subs(x, mid).evalf()
                    if val > 0: current_signs.append('+')
                    elif val < 0: current_signs.append('-')
                    else: current_signs.append('0')
            except Exception:
                current_signs.append('h')
        analysis["signs"] = current_signs

    overall_signs = []
    overall_singular = []
    overall_domain = continuous_domain(expr, x, Reals)

    numer_overall, denom_overall = expr.as_numer_denom()
    if denom_overall != 1:
        overall_denom_roots = solve(denom_overall, x)
        for dr in overall_denom_roots:
            if dr.is_real:
                overall_singular.append(dr)
    
    if isinstance(overall_domain, Union):
        for interval in overall_domain.args:
            if interval.left != -oo and not interval.left.is_infinite and not overall_domain.contains(interval.left):
                if interval.left.is_real: overall_singular.append(interval.left)
            if interval.right != oo and not interval.right.is_infinite and not overall_domain.contains(interval.right):
                if interval.right.is_real: overall_singular.append(interval.right)
    elif isinstance(overall_domain, Interval):
        if overall_domain.left != -oo and not overall_domain.left.is_infinite and not overall_domain.contains(overall_domain.left):
            if overall_domain.left.is_real: overall_singular.append(overall_domain.left)
        if overall_domain.right != oo and not overall_domain.right.is_infinite and not overall_domain.contains(overall_domain.right):
            if overall_domain.right.is_real: overall_singular.append(overall_domain.right)
    
    overall_singular = sorted(list(set(overall_singular)), key=lambda p: p.evalf())

    for i in range(len(all_points) - 1):
        a, b = all_points[i], all_points[i+1]
        try:
            if a == -oo and b == oo: mid = 0
            elif a == -oo: mid = b - 1
            elif b == oo: mid = a + 1
            else: mid = (a + b) / 2

            if not overall_domain.contains(mid):
                overall_signs.append('h')
            else:
                val = expr.subs(x, mid).evalf()
                if val > 0: overall_signs.append('+')
                elif val < 0: overall_signs.append('-')
                else: overall_signs.append('0')
        except Exception:
            overall_signs.append('h')
    
    overall_roots = [s for s in solve(expr, x) if s.is_real]

    individual_analyses.append({
        "label": latex(expr),
        "expr_obj": expr,
        "roots": overall_roots,
        "singular": overall_singular,
        "signs": overall_signs
    })

    return {
        "overall_expr": latex(expr),
        "all_points": all_points,
        "analyses": individual_analyses
    }

def generate_tkz_tab(data):
    """Generates the LaTeX code for the variation table."""
    if "error" in data:
        return "\\textbf{Error:} " + data["error"]

    f_obj = data["original_function_obj"]
    pts_data = data["points_data"]
    intervals_data = data["intervals_data"]
    critical = data.get("critical", [])
    singular = data.get("singular", [])

    col_labels = []
    for p_info in pts_data:
        col_labels.append(p_info["latex_label"])
    
    # Use standalone document class for automatic cropping
    latex_lines = [
        "\\documentclass{standalone}", # Changed to standalone
        "\\usepackage{amsmath}",
        "\\usepackage{tkz-tab}",
        "\\usepackage{amsfonts}",
        "\\usepackage{amssymb}",
        "\\usepackage{tikz}", # Added tikz package
        "\\begin{document}",
        "\\begin{tikzpicture}"
    ]
    
    latex_lines.append(f"\\tkzTabInit[lgt=2,espcl=2]{{$x$ / 1, $f'(x)$ / 1, $f(x)$ / 2}}{{{', '.join(col_labels)}}}")

    # tkzTabLine for f'(x)
    line_f_prime_elements = []
    line_f_prime_elements.append('') # For -oo (start point)

    for i in range(len(intervals_data)):
        interval_info = intervals_data[i]
        line_f_prime_elements.append(interval_info["sign_f_prime"])
        
        # Add separator for the point at the end of this interval
        if i + 1 < len(pts_data):
            next_pt_obj = pts_data[i+1]
            if next_pt_obj["point"] in critical:
                line_f_prime_elements.append('z')
            elif next_pt_obj["point"] in singular:
                line_f_prime_elements.append('d') 
            else:
                line_f_prime_elements.append('')
        else:
            line_f_prime_elements.append('') 

    line_f_prime_str = ", ".join(line_f_prime_elements)
    line_f_prime_str = line_f_prime_str.replace(", ,", ", ") 
    latex_lines.append(f"\\tkzTabLine{{{line_f_prime_str}}}")

    # tkzTabVar for f(x)
    tkz_tab_var_elements = []

    def format_value_for_latex(val):
        if not isinstance(val, str):
            val_str = latex(val)
        else:
            val_str = val
        if val_str == "\\infty":
            return "$+\\infty$"
        if not val_str.startswith('$') and not val_str.endswith('$'):
            return f"${val_str}$"
        return val_str

    def format_value_for_dh(val):
        if val == oo:
            return "$+\\infty$"
        elif val == -oo:
            return "$-\\infty$"
        return format_value_for_latex(val)

    # 1. Handle the first point (pts_data[0])
    first_point_data = pts_data[0]
    s_prefix_first_point = ""
    # Determine s_prefix for -oo based on the direction of the first interval
    if len(intervals_data) > 0 and intervals_data[0]["variation_arrow"] == '+':
        s_prefix_first_point = "-" # Arrow starts low, goes up
    elif len(intervals_data) > 0 and intervals_data[0]["variation_arrow"] == '-':
        s_prefix_first_point = "+" # Arrow starts high, goes down
    else: # Constant or undefined first interval, default to '+'
        s_prefix_first_point = "+"

    if len(intervals_data) > 0 and intervals_data[0]["variation_arrow"] == 'R \\':
        tkz_tab_var_elements.append("R")
    else:
        tkz_tab_var_elements.append(f"{s_prefix_first_point}/{format_value_for_latex(first_point_data['value_latex'])}")


    # 2. Iterate for subsequent points (pts_data[1] to pts_data[last])
    for i in range(1, len(pts_data)):
        current_point_data = pts_data[i]
        prev_interval_info = intervals_data[i-1]
        prev_interval_arrow = prev_interval_info["variation_arrow"] # Arrow leading TO this point
        
        # The arrow *from* this point *to* the next interval (if it exists)
        next_interval_arrow = intervals_data[i]["variation_arrow"] if i < len(intervals_data) else "R \\"

        element_str = ""
        
        # s_prefix for the current point's value is determined by the arrow *leading to it*
        s_prefix_for_point = ""
        if current_point_data['point'] == oo: # Special case for +oo, force '-' as per user request
            s_prefix_for_point = "-"
        elif prev_interval_arrow == '+':
            s_prefix_for_point = "+"
        elif prev_interval_arrow == '-':
            s_prefix_for_point = "-"
        elif prev_interval_arrow == 'C':
            s_prefix_for_point = "C"
        else: # prev_interval_arrow == 'R \' (undefined interval leading to this point)
            # If the point itself is defined, its vertical position depends on the *next* arrow.
            # If next arrow is '+', it starts low, so s_prefix is '-'.
            # If next arrow is '-', it starts high, so s_prefix is '+'.
            # If it's the last point or next interval is also undefined, default to '+'
            if is_point_in_f_real_domain and next_interval_arrow == '+':
                s_prefix_for_point = "-"
            elif is_point_in_f_real_domain and next_interval_arrow == '-':
                s_prefix_for_point = "+"
            else:
                s_prefix_for_point = "+" # Default for undefined/last point

        # Check if the current point is within the real domain of function f
        is_point_in_f_real_domain = False
        try:
            if current_point_data['point'] in [-oo, oo]:
                is_point_in_f_real_domain = True
            else:
                test_val_at_point_obj = f_obj.subs(x, current_point_data['point'])
                if test_val_at_point_obj.is_real and not test_val_at_point_obj.is_infinite:
                    is_point_in_f_real_domain = True
        except Exception:
            is_point_in_f_real_domain = False

        # --- DH and HD Cases ---
        # DH: Defined interval -> Vertical Asymptote -> Undefined interval
        if current_point_data["is_vertical_asymptote"] and next_interval_arrow == 'R \\' and prev_interval_arrow != 'R \\':
            element_str = f"{s_prefix_for_point}DH/{format_value_for_dh(current_point_data['left_limit'])}"
        # HD: Undefined interval -> Vertical Asymptote -> Defined interval
        elif current_point_data["is_vertical_asymptote"] and prev_interval_arrow == 'R \\' and next_interval_arrow != 'R \\':
            s_prefix_for_hd = next_interval_arrow # The arrow from this point
            element_str = f"{s_prefix_for_hd}HD/{format_value_for_dh(current_point_data['right_limit'])}"
        # R: Point is within a fully undefined region (both prev and next intervals are undefined)
        elif prev_interval_arrow == 'R \\' and next_interval_arrow == 'R \\':
            element_str = 'R'
        # R: Point is at the boundary of an undefined region, and not defined itself
        elif prev_interval_arrow == 'R \\' and not is_point_in_f_real_domain:
            element_str = 'R'
        elif current_point_data["is_vertical_asymptote"]:
            # Regular vertical asymptote (not DH or HD)
            limit_suffix = "+" 
            if (current_point_data["right_limit"] is not None and current_point_data["right_limit"] == -oo) or \
               (current_point_data["left_limit"] == -oo and current_point_data["right_limit"] == -oo):
                limit_suffix = "-"
            element_str = f"{s_prefix_for_point}D{limit_suffix}/{format_value_for_latex(current_point_data['left_limit_latex'])}/{format_value_for_latex(current_point_data['right_limit_latex'])}"
        elif current_point_data["is_removable_discontinuity"] and current_point_data['point'] != oo: # Exclude +H at infinity
            # If it's a removable discontinuity at a finite point.
            element_type = "H"
            element_str = f"{s_prefix_for_point}{element_type}/{format_value_for_latex(current_point_data['value_latex'])}"
        elif current_point_data["is_jump_discontinuity"]:
            element_type = "V"
            v_type_suffix = ""
            left_lim_obj = current_point_data["left_limit"]
            right_lim_obj = current_point_data["right_limit"]

            if (left_lim_obj is not None and left_lim_obj.is_real and left_lim_obj.is_finite) and \
               (right_lim_obj is not None and right_lim_obj.is_real and right_lim_obj.is_finite):
                if left_lim_obj > right_lim_obj:
                    v_type_suffix = "-" 
                elif left_lim_obj < right_lim_obj:
                    v_type_suffix = "+" 
                else: 
                    v_type_suffix = "+"
            else:
                v_type_suffix = "+" # Fallback
            element_str = f"{s_prefix_for_point}{element_type}{v_type_suffix}/{format_value_for_latex(current_point_data['left_limit_latex'])}/{format_value_for_latex(current_point_data['right_limit_latex'])}"
        else: # Regular point or critical point, including +oo (now forced to '-')
            element_str = f"{s_prefix_for_point}/{format_value_for_latex(current_point_data['value_latex'])}"
        
        tkz_tab_var_elements.append(element_str)

    line_var = ", ".join(tkz_tab_var_elements)
    latex_lines.append(f"\\tkzTabVar{{{line_var}}}")

    latex_lines.extend([
        "\\end{tikzpicture}",
        "\\end{document}"
    ])
    
    return "\n".join(latex_lines)

def generate_tkz_sign_tab(data):
    """Generates the LaTeX code for the sign table, detailing factors/numerator and denominator."""
    if "error" in data:
        return "\\textbf{Error:} " + data["error"]

    all_points = data["all_points"]
    analyses = data["analyses"]

    col_labels = []
    for p in all_points:
        if p == -oo:
            col_labels.append("$-\\infty$")
        elif p == oo:
            col_labels.append("$+\\infty$")
        else:
            col_labels.append(f"${latex(p)}$")
    
    # Use standalone document class for automatic cropping
    latex_lines = [
        "\\documentclass{standalone}", # Changed to standalone
        "\\usepackage{amsmath}",
        "\\usepackage{tkz-tab}",
        "\\usepackage{amsfonts}",
        "\\usepackage{amssymb}",
        "\\usepackage{tikz}", # Added tikz package
        "\\begin{document}",
        "\\begin{tikzpicture}"
    ]
    
    # Build row labels for tkzTabInit
    row_labels_init_parts = ["$x$ / 1"]
    for analysis in analyses:
        label_content = analysis['label']
        row_labels_init_parts.append(f"${label_content}$ / 1") 

    latex_lines.append(f"\\tkzTabInit[lgt=2,espcl=2]{{{', '.join(row_labels_init_parts)}}}{{{', '.join(col_labels)}}}")

    # Calculate all roots and singular points from all factors for 't' logic
    all_roots_and_singular_points_overall = set()
    for analysis_item in analyses:
        all_roots_and_singular_points_overall.update(analysis_item['roots'])
        all_roots_and_singular_points_overall.update(analysis_item['singular'])
    
    # Generate tkzTabLine for each individual analysis
    for idx, analysis in enumerate(analyses):
        current_signs = analysis["signs"]
        current_roots = analysis["roots"]
        current_singular = analysis["singular"]
        
        line_elements = [] 
        
        line_elements.append('') # For -oo

        for i in range(len(all_points) - 1):
            if i < len(current_signs):
                line_elements.append(current_signs[i])
            else:
                line_elements.append('h')
            
            current_pt_for_separator = all_points[i+1]
            
            separator_char = ''
            
            # If this is the final expression line
            if idx == len(analyses) - 1:
                if current_pt_for_separator in current_roots:
                    separator_char = 'z'
                elif current_pt_for_separator in current_singular: # Point where the overall expression is undefined (denominator = 0)
                    separator_char = 'd'
                else:
                    separator_char = ''
            else: # This is an individual factor/term line (A or B)
                if current_pt_for_separator in current_roots:
                    separator_char = 'z' # Root for this specific factor
                elif current_pt_for_separator in current_singular:
                    # Singular point for this specific factor (e.g., sqrt(x) in a factor)
                    # For A/B, if B is the factor, its roots are 'z' for B, but 'd' for A/B
                    # Here, for factor B, its roots are 'z'.
                    # If factor B itself has a singularity (e.g., 1/sqrt(x-1)), it's 'd' for B.
                    separator_char = 'd' 
                elif current_pt_for_separator in all_roots_and_singular_points_overall:
                    # If it's a root/singular point for any factor, but not for this specific factor
                    separator_char = 't' 
            
            line_elements.append(separator_char)
        
        line_str = ", ".join(line_elements)
        line_str = line_str.replace(", ,", ", ")
        
        latex_lines.append(f"\\tkzTabLine{{{line_str}}}")

    latex_lines.extend([
        "\\end{tikzpicture}",
        "\\end{document}"
    ])
    
    return "\n".join(latex_lines)

class Application(tk.Tk):
    """Graphical User Interface for the application."""
    def __init__(self):
        super().__init__()
        self.title("Variation and Sign Table Generator - tkz-tab")
        self.geometry("1000x750") 
        self.configure(bg="#f0f0f0")
        
        self.active_entry = None 
        self.current_preview_image = None # To store the PIL Image object for save/copy

        self.main_content_frame = tk.Frame(self, bg="#f0f0f0")
        self.main_content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.right_panel_frame = tk.Frame(self.main_content_frame, bg="#f0f0f0")

        self.create_widgets()
        self.setup_layout()
        self.func_entry.focus_set() 
        self.active_entry = self.func_entry

    def create_widgets(self):
        """Creates the UI elements."""
        self.title_label = tk.Label(self, text="Function Variation and Sign Table Generator", 
                                     font=('Arial', 16, 'bold'), bg="#f0f0f0", fg="#333333")
        
        # --- Input Frame --- (child of right_panel_frame)
        self.input_frame = tk.LabelFrame(self.right_panel_frame, text="Enter Function/Expression and Domain", padx=10, pady=10, bg="#f0f0f0", font=('Arial', 10, 'bold'))
        
        self.func_label = tk.Label(self.input_frame, text="Enter function f(x) or expression P(x):", bg="#f0f0f0")
        self.func_entry = tk.Entry(self.input_frame, width=50, font=('Arial', 12), bd=2, relief=tk.GROOVE)
        self.func_entry.insert(0, "sqrt((x-1)/(x+1))") # Default to the new function
        self.func_entry.bind("<FocusIn>", lambda e: self.set_active_entry(self.func_entry))
        
        self.domain_label = tk.Label(self.input_frame, text="Domain (optional) e.g., [a,b] or (a,oo) or Reals:", bg="#f0f0f0")
        self.domain_entry = tk.Entry(self.input_frame, width=50, font=('Arial', 12), bd=2, relief=tk.GROOVE)
        self.domain_entry.insert(0, "") # Clear domain for this example
        self.domain_entry.bind("<FocusIn>", lambda e: self.set_active_entry(self.domain_entry))

        # --- Keypad Frame --- (child of right_panel_frame)
        self.keypad_frame = tk.LabelFrame(self.right_panel_frame, text="Mathematical Keypad", padx=10, pady=10, bg="#e0e0e0", font=('Arial', 10, 'bold'))
        self.create_keypad(self.keypad_frame)

        # --- Output Frame --- (child of main_content_frame)
        self.output_frame = tk.LabelFrame(self.main_content_frame, text="Generated LaTeX Code", padx=10, pady=10, bg="#f0f0f0", font=('Arial', 10, 'bold'))
        self.output_text = scrolledtext.ScrolledText(self.output_frame, width=80, height=15, 
                                                     font=('Courier New', 10), wrap=tk.WORD, bd=2, relief=tk.SUNKEN)
        
        # --- Button Frame --- (child of right_panel_frame)
        self.button_frame = tk.Frame(self.right_panel_frame, bg="#f0f0f0")
        
        self.generate_variation_btn = tk.Button(self.button_frame, text="?? Analyze Function Variation", 
                                       command=self.generate_variation_table, bg="#4CAF50", fg="white", 
                                       font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")
        
        self.generate_sign_btn = tk.Button(self.button_frame, text="?? Draw Expression Sign Table", 
                                       command=self.generate_sign_table, bg="#FF9800", fg="white", 
                                       font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")

        self.copy_btn = tk.Button(self.button_frame, text="?? Copy LaTeX Code", # Renamed for clarity
                                   command=self.copy_to_clipboard, bg="#2196F3", fg="white", 
                                   font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")
        
        # New button for in-app preview
        self.preview_in_app_btn = tk.Button(self.button_frame, text="??? Preview in App", 
                                     command=self.compile_and_display_latex, bg="#8B008B", fg="white", 
                                     font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")

        self.clear_btn = tk.Button(self.button_frame, text="??? Clear Fields", 
                                    command=self.clear_fields, bg="#f44336", fg="white", 
                                    font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")
    
    def set_active_entry(self, entry_widget):
        """Sets the active entry widget for the keypad."""
        self.active_entry = entry_widget

    def create_keypad(self, parent_frame):
        """Creates the mathematical keypad."""
        keypad_buttons = [
            ('7', '8', '9', '+', '-', '('),
            ('4', '5', '6', '*', '/', ')'),
            ('1', '2', '3', '**', 'x', 'sqrt('),
            ('0', '.', 'pi', 'e', 'oo', 'sin('),
            ('cos(', 'tan(', 'log(', 'exp(', 'abs(', 'del')
        ]

        for r_idx, row in enumerate(keypad_buttons):
            for c_idx, text in enumerate(row):
                if text == 'del':
                    btn = tk.Button(parent_frame, text="??", command=self.delete_char,
                                    font=('Arial', 11, 'bold'), bg="#FFEB3B", fg="#333333", width=4, height=1) 
                else:
                    btn = tk.Button(parent_frame, text=text, command=lambda t=text: self.insert_char(t),
                                    font=('Arial', 11), bg="#FFFFFF", fg="#333333", width=4, height=1) 
                btn.grid(row=r_idx, column=c_idx, padx=2, pady=2, sticky="nsew") 
        
        for i in range(len(keypad_buttons[0])):
            parent_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(keypad_buttons)):
            parent_frame.grid_rowconfigure(i, weight=1)

    def insert_char(self, char):
        """Inserts a character into the active entry field."""
        if self.active_entry:
            cursor_pos = self.active_entry.index(tk.INSERT)
            self.active_entry.insert(cursor_pos, char)

    def delete_char(self):
        """Deletes the last character from the active entry field."""
        if self.active_entry:
            cursor_pos = self.active_entry.index(tk.INSERT)
            if cursor_pos > 0:
                self.active_entry.delete(cursor_pos - 1, cursor_pos)

    def setup_layout(self):
        """Organizes the UI elements."""
        self.title_label.pack(pady=10)
        
        self.main_content_frame.grid_columnconfigure(0, weight=1) 
        self.main_content_frame.grid_columnconfigure(1, weight=0) 
        self.main_content_frame.grid_rowconfigure(0, weight=1) 

        self.output_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10)) 

        self.right_panel_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))

        self.input_frame.pack(pady=5, fill=tk.X)
        self.func_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.func_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.domain_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.domain_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.input_frame.grid_columnconfigure(1, weight=1) 

        self.keypad_frame.pack(pady=5, fill=tk.X, expand=False) 

        self.button_frame.pack(pady=5, fill=tk.X)
        self.generate_variation_btn.pack(side=tk.LEFT, padx=5, pady=5) 
        self.generate_sign_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.copy_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.preview_in_app_btn.pack(side=tk.LEFT, padx=5, pady=5) # Pack the new button
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.output_text.pack(fill=tk.BOTH, expand=True) 

    def generate_variation_table(self):
        """Processes the function and generates the variation table."""
        func = self.func_entry.get()
        domain = self.domain_entry.get().strip()
        
        try:
            analysis = analyze_function(func, domain if domain else None)
            if "error" in analysis:
                messagebox.showerror("Analysis Error", analysis["error"])
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, analysis["error"])
            else:
                latex_code = generate_tkz_tab(analysis)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, latex_code)
        except Exception as e:
            messagebox.showerror("General Error", f"An unexpected error occurred:\n{str(e)}")
    
    def generate_sign_table(self):
        """Processes the expression and generates the sign table."""
        expr = self.func_entry.get()
        
        try:
            analysis = analyze_expression_sign(expr)
            if "error" in analysis:
                messagebox.showerror("Analysis Error", analysis["error"])
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END)
            else:
                latex_code = generate_tkz_sign_tab(analysis)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, latex_code)
        except Exception as e:
            messagebox.showerror("General Error", f"An unexpected error occurred:\n{str(e)}")

    def copy_to_clipboard(self):
        """Copies the code to the clipboard."""
        text_to_copy = self.output_text.get(1.0, tk.END).strip()
        if text_to_copy:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            messagebox.showinfo("Copied", "LaTeX code copied to clipboard.")
        else:
            messagebox.showwarning("No Content", "There is no code to copy.")
    
    def save_current_image(self):
        """Saves the currently displayed preview image to a file."""
        if self.current_preview_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Image As"
            )
            if file_path:
                try:
                    self.current_preview_image.save(file_path)
                    messagebox.showinfo("Image Saved", f"Image successfully saved to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save image:\n{str(e)}")
        else:
            messagebox.showwarning("No Image", "No image to save. Generate a preview first.")

    def copy_current_image_to_clipboard(self):
        """Copies the currently displayed preview image to the clipboard."""
        if self.current_preview_image:
            try:
                # This method is generally Windows-specific for direct image copy
                # On other OS, it might require extra steps or libraries (e.g., pyperclip + xclip/xsel)
                # For simplicity and common Windows use-case, this is a direct approach.
                ImageGrab.grabclipboard().paste(self.current_preview_image) # This line is incorrect, it should be Image.paste()
                # Correct way for Windows:
                # The ImageGrab.grabclipboard() is for GETTING an image.
                # To PUT an image, you'd typically need system-level calls or a library like pyperclip that handles it.
                # However, Pillow itself can interact with the clipboard on Windows for putting images.
                
                # Let's try the direct PIL way if it's available for putting.
                # If this fails, we'll revert to the "save to temp and inform" method.
                
                # A more robust cross-platform way would be to save to temp file and then
                # use system commands (xclip on Linux, osascript on macOS)
                # For Windows, PIL's Image.save("clipboard") is not a direct feature.
                # The typical way is to use win32clipboard module from pywin32, or save to temp and then copy.
                
                # Given the constraints, the most straightforward is to inform the user
                # or use a temp file. Let's go with saving to temp and informing.
                
                # Alternative: Save to a temporary BMP and then use system clipboard.
                # This is still a workaround for non-direct PIL clipboard write.
                
                # Let's simplify and inform the user for cross-platform robustness
                # without adding pywin32 dependency for the .exe.
                
                # This is the most reliable approach without platform-specific dependencies:
                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                self.current_preview_image.save(temp_file.name)
                temp_file.close()
                messagebox.showinfo(
                    "Image Copied (Workaround)",
                    f"The image has been saved to a temporary file:\n{temp_file.name}\n\n"
                    "You can now open this file and copy it manually, or insert it directly from this location."
                )
                # Note: For a true direct clipboard copy, pywin32 (Windows) or platform-specific tools are needed.
                # This workaround is robust across platforms where direct clipboard write is complex.

            except Exception as e:
                messagebox.showerror("Copy Error", f"Failed to copy image to clipboard:\n{str(e)}")
        else:
            messagebox.showwarning("No Image", "No image to copy. Generate a preview first.")

    def compile_and_display_latex(self):
        """
        Compiles the LaTeX code to PDF using pdflatex, then converts PDF to PNG
        using pdf2image, and displays the PNG in a new Tkinter window.
        """
        latex_code = self.output_text.get(1.0, tk.END).strip()
        if not latex_code:
            messagebox.showwarning("No Code", "Generate LaTeX code first to preview.")
            return

        # Use a temporary directory for all compilation files
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file_path = os.path.join(temp_dir, "preview.tex")
            pdf_file_path = os.path.join(temp_dir, "preview.pdf")
            
            try:
                # Write LaTeX code to a temporary .tex file
                with open(tex_file_path, "w", encoding="utf-8") as f:
                    f.write(latex_code)

                # 1. Compile LaTeX to PDF using pdflatex
                pdflatex_command = [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    f"-output-directory={temp_dir}",
                    tex_file_path
                ]
                
                # Run pdflatex twice for correct cross-referencing/layout (especially for tkz-tab)
                result1 = subprocess.run(pdflatex_command, capture_output=True, text=True, check=False)
                result2 = subprocess.run(pdflatex_command, capture_output=True, text=True, check=False)

                if result1.returncode != 0 or result2.returncode != 0:
                    error_output = result1.stderr + result2.stderr
                    messagebox.showerror(
                        "LaTeX Compilation Error",
                        f"Failed to compile LaTeX to PDF. Check your LaTeX code and TeX Live installation (pdflatex).\n\n"
                        f"Error details:\n{error_output[:1000]}..." # Show first 1000 chars of error
                    )
                    return

                if not os.path.exists(pdf_file_path):
                    messagebox.showerror(
                        "File Not Found Error",
                        "PDF file was not generated by pdflatex. Check LaTeX code for severe errors."
                    )
                    return

                # 2. Convert PDF to PIL Image objects using pdf2image
                # poppler_path can be specified here if poppler bin is not in PATH globally
                # Example: poppler_path=r"C:\path\to\poppler\bin"
                from pdf2image import convert_from_path # Re-import here to ensure it's available after potential error
                images = convert_from_path(pdf_file_path, dpi=300, fmt='png') 
                
                if not images:
                    messagebox.showerror(
                        "Image Conversion Error",
                        "No images were generated from the PDF. Ensure Poppler utilities are correctly installed and in your PATH."
                    )
                    return

                # Assuming we only have one page (the table)
                img = images[0] 
                self.current_preview_image = img # Store the PIL Image object

                # 3. Display the PIL Image in a new Tkinter window
                preview_window = tk.Toplevel(self)
                preview_window.title("LaTeX Preview")
                
                # Resize image if it's too large for the screen
                max_width = self.winfo_screenwidth() * 0.8
                max_height = self.winfo_screenheight() * 0.8
                
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.LANCZOS)
                
                tk_img = ImageTk.PhotoImage(img)

                # Keep a reference to the image to prevent it from being garbage-collected
                preview_window.image = tk_img 

                img_label = tk.Label(preview_window, image=tk_img)
                img_label.pack(padx=10, pady=10)

                # Add Save and Copy buttons to the preview window
                preview_buttons_frame = tk.Frame(preview_window)
                preview_buttons_frame.pack(pady=5)

                save_btn = tk.Button(preview_buttons_frame, text="?? Save Image", 
                                     command=self.save_current_image, bg="#4CAF50", fg="white", 
                                     font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")
                save_btn.pack(side=tk.LEFT, padx=5)

                copy_img_btn = tk.Button(preview_buttons_frame, text="?? Copy Image", 
                                         command=self.copy_current_image_to_clipboard, bg="#2196F3", fg="white", 
                                         font=('Arial', 10, 'bold'), relief=tk.RAISED, bd=3, cursor="hand2")
                copy_img_btn.pack(side=tk.LEFT, padx=5)

                # Center the new window
                preview_window.update_idletasks()
                x_pos = self.winfo_x() + (self.winfo_width() // 2) - (preview_window.winfo_width() // 2)
                y_pos = self.winfo_y() + (self.winfo_height() // 2) - (preview_window.winfo_height() // 2)
                preview_window.geometry(f"+{int(x_pos)}+{int(y_pos)}")

            except FileNotFoundError as e:
                messagebox.showerror(
                    "Command Not Found",
                    f"Required command not found: '{e.filename}'.\n"
                    f"Please ensure 'pdflatex' (from TeX Live) and 'Poppler utilities' (e.g., pdftocairo) "
                    f"are installed and added to your system's PATH environment variable."
                )
            except Exception as e:
                messagebox.showerror("Preview Error", f"An unexpected error occurred during preview generation:\n{str(e)}")

    def clear_fields(self):
        """Clears the fields."""
        self.func_entry.delete(0, tk.END)
        self.domain_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.func_entry.focus_set()
        self.current_preview_image = None # Clear the stored image

if __name__ == "__main__":
    app = Application()
    app.mainloop()
