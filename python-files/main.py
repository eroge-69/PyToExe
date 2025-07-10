import re
import math
import random
import time

class Interpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}
        self.call_stack = []
        
    def eval_expr(self, expr):
        expr = expr.strip()
        # Replace variables
        for var in self.vars:
            expr = re.sub(rf'\b{var}\b', str(self.vars[var]), expr)
        
        # Add built-in functions to the evaluation context
        context = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'sqrt': math.sqrt, 'abs': abs, 'round': round,
            'max': max, 'min': min, 'sum': sum, 'len': len,
            'int': int, 'float': float, 'str': str,
            'pi': math.pi, 'e': math.e,
            'random': random.random, 'randint': random.randint,
            'range': range, 'list': list,
            'ask': lambda prompt: input(str(prompt))
        }
        
        try:
            return eval(expr, {"__builtins__": {}}, context)
        except Exception as e:
            raise ValueError(f"Invalid expression: {expr} ({e})")
    
    def execute(self, line):
        line = line.strip()
        if not line or line.startswith("#"):
            return
        
        # Handle multiple commands separated by semicolons
        if ';' in line:
            commands = [cmd.strip() for cmd in line.split(';')]
            for cmd in commands:
                if cmd:  # Skip empty commands
                    self.execute(cmd)
            return
            
        # Variable assignment
        if line.startswith("set "):
            parts = line[4:].split("=", 1)
            if len(parts) != 2:
                raise SyntaxError("Syntax error. Use: set x = 5")
            var_name = parts[0].strip()
            expr = parts[1].strip()
            value = self.eval_expr(expr)
            self.vars[var_name] = value
            
        # Print/write command
        elif line.startswith("write(") and line.endswith(")"):
            expr = line[6:-1]
            value = self.eval_expr(expr)
            print(value)
            
        # Read input
        elif line.startswith("read(") and line.endswith(")"):
            var_name = line[5:-1].strip()
            value = input("Enter value: ")
            try:
                # Try to convert to number if possible
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string if not a number
                pass
            self.vars[var_name] = value
            
        # Ask with custom prompt
        elif line.startswith("ask(") and line.endswith(")"):
            content = line[4:-1].strip()
            if content.startswith('"') and content.endswith('"'):
                prompt = content[1:-1]  # Remove quotes
                value = input(prompt)
            else:
                # It's a variable assignment: ask("prompt") -> var
                if " -> " in content:
                    parts = content.split(" -> ", 1)
                    if len(parts) == 2:
                        prompt_part = parts[0].strip()
                        var_name = parts[1].strip()
                        if prompt_part.startswith('"') and prompt_part.endswith('"'):
                            prompt = prompt_part[1:-1]
                        else:
                            prompt = self.eval_expr(prompt_part)
                        value = input(str(prompt))
                        try:
                            # Try to convert to number if possible
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            # Keep as string if not a number
                            pass
                        self.vars[var_name] = value
                        return
                else:
                    # Just ask and return the value
                    if content.startswith('"') and content.endswith('"'):
                        prompt = content[1:-1]
                    else:
                        prompt = str(self.eval_expr(content))
                    value = input(prompt)
            
            # For simple ask("prompt"), just get input but don't store
            try:
                # Try to convert to number if possible
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string if not a number
                pass
            print(value)  # Print the result for simple ask commands
            
        # Conditional execution
        elif line.startswith("maybe "):
            cond, _, code = line[6:].partition(":")
            if not code:
                raise SyntaxError("Syntax error. Use: maybe condition: code")
            cond_value = self.eval_expr(cond)
            if cond_value:
                self.execute(code.strip())
                
        # Otherwise conditional
        elif line.startswith("otherwise:"):
            # This would need to be handled with maybe blocks
            code = line[10:].strip()
            self.execute(code)
            
        # Loop with condition
        elif line.startswith("period "):
            cond, _, code = line[7:].partition(":")
            if not code:
                raise SyntaxError("Syntax error. Use: period condition: code")
            while self.eval_expr(cond):
                self.execute(code.strip())
                
        # For loop
        elif line.startswith("each "):
            parts = line[5:].split(" in ", 1)
            if len(parts) != 2:
                raise SyntaxError("Syntax error. Use: each var in iterable: code")
            var_name = parts[0].strip()
            rest = parts[1].strip()
            if ":" not in rest:
                raise SyntaxError("Syntax error. Use: each var in iterable: code")
            iterable_expr, code = rest.split(":", 1)
            iterable = self.eval_expr(iterable_expr.strip())
            for item in iterable:
                self.vars[var_name] = item
                self.execute(code.strip())
                
        # List operations
        elif line.startswith("append "):
            parts = line[7:].split(" to ", 1)
            if len(parts) != 2:
                raise SyntaxError("Syntax error. Use: append value to list_var")
            value_expr = parts[0].strip()
            list_var = parts[1].strip()
            if list_var not in self.vars:
                self.vars[list_var] = []
            value = self.eval_expr(value_expr)
            self.vars[list_var].append(value)
            
        # Remove from list
        elif line.startswith("remove "):
            parts = line[7:].split(" from ", 1)
            if len(parts) != 2:
                raise SyntaxError("Syntax error. Use: remove value from list_var")
            value_expr = parts[0].strip()
            list_var = parts[1].strip()
            if list_var in self.vars and isinstance(self.vars[list_var], list):
                value = self.eval_expr(value_expr)
                if value in self.vars[list_var]:
                    self.vars[list_var].remove(value)
                    
        # Clear list
        elif line.startswith("clear "):
            var_name = line[6:].strip()
            if var_name in self.vars:
                if isinstance(self.vars[var_name], list):
                    self.vars[var_name].clear()
                else:
                    del self.vars[var_name]
                    
        # Show variables
        elif line == "vars":
            for var, val in self.vars.items():
                print(f"{var} = {val}")
                
        # Show help
        elif line == "help":
            print("""
GatocLang Commands:
  set x = value          - Set variable
  write(expr)            - Print expression
  read(var)              - Read input into variable
  ask("prompt")          - Ask for input with custom prompt
  ask("prompt") -> var   - Ask for input and store in variable
  maybe condition: code  - Conditional execution
  period condition: code - Loop while condition is true
  each var in list: code - For each loop
  append value to list   - Add to list
  remove value from list - Remove from list
  clear list             - Clear list or delete variable
  vars                   - Show all variables
  help                   - Show this help
  exit                   - Quit
  
Built-in functions: sin, cos, tan, sqrt, abs, round, max, min, sum, len, ask
Constants: pi, e

Use semicolons (;) to run multiple commands on one line.
            """)
            
        # Sleep/wait
        elif line.startswith("wait "):
            seconds = self.eval_expr(line[5:])
            time.sleep(seconds)
            
        # Random choice
        elif line.startswith("choose "):
            parts = line[7:].split(" from ", 1)
            if len(parts) != 2:
                raise SyntaxError("Syntax error. Use: choose var from list")
            var_name = parts[0].strip()
            list_expr = parts[1].strip()
            choices = self.eval_expr(list_expr)
            if choices:
                self.vars[var_name] = random.choice(choices)
                
        # Type checking
        elif line.startswith("type "):
            var_name = line[5:].strip()
            if var_name in self.vars:
                print(type(self.vars[var_name]).__name__)
            else:
                print("undefined")
                
        # Function definition
        elif line.startswith("func "):
            parts = line[5:].split(":", 1)
            if len(parts) != 2:
                raise SyntaxError("Syntax error. Use: func name(params): code")
            func_header = parts[0].strip()
            func_body = parts[1].strip()
            
            if "(" not in func_header or ")" not in func_header:
                raise SyntaxError("Function must have parentheses")
                
            func_name = func_header[:func_header.index("(")]
            params_str = func_header[func_header.index("(")+1:func_header.rindex(")")]
            params = [p.strip() for p in params_str.split(",") if p.strip()]
            
            self.functions[func_name] = {"params": params, "body": func_body}
            
        # Function call
        elif any(line.startswith(f"{func}(") for func in self.functions):
            for func_name in self.functions:
                if line.startswith(f"{func_name}(") and line.endswith(")"):
                    args_str = line[len(func_name)+1:-1]
                    args = [self.eval_expr(arg.strip()) for arg in args_str.split(",") if arg.strip()]
                    
                    func_def = self.functions[func_name]
                    if len(args) != len(func_def["params"]):
                        raise ValueError(f"Function {func_name} expects {len(func_def['params'])} arguments, got {len(args)}")
                    
                    # Save current variable state
                    saved_vars = self.vars.copy()
                    
                    # Set parameters
                    for param, arg in zip(func_def["params"], args):
                        self.vars[param] = arg
                    
                    # Execute function body
                    self.execute(func_def["body"])
                    
                    # Restore variables (simple implementation)
                    self.vars = saved_vars
                    break
                    
        else:
            # Evaluate and print result
            value = self.eval_expr(line)
            print(value)

def repl():
    interpreter = Interpreter()
    print("GatocLang v2.0. Type 'help' for commands or 'exit' to quit.")
    while True:
        try:
            line = input(">>> ")
            if line == "exit":
                break
            interpreter.execute(line)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    repl()