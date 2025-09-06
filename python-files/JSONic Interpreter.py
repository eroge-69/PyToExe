import json
import sys
import os
import math


class ReturnSignal(Exception):
    """Used internally to return early from function calls"""
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self):
        self.global_env = {}
        self.env_stack = [self.global_env]
        self.functions = {}

        # Built-in functions
        self.builtins = {
            # I/O
            "print": self.builtin_print,
            "input": self.builtin_input,
            "read_file": self.builtin_read_file,
            "write_file": self.builtin_write_file,

            # Type and general
            "len": self.builtin_len,
            "type": self.builtin_type,
            "contains": self.builtin_contains,

            # Math
            "abs": abs,
            "min": min,
            "max": max,
            "pow": pow,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,

            # String manipulation
            "upper": lambda s: str(s).upper(),
            "lower": lambda s: str(s).lower(),
            "strip": lambda s: str(s).strip(),
            "split": lambda s, delim=" ": str(s).split(delim),
            "join": lambda delim, lst: str(delim).join(map(str, lst)),
            "replace": lambda s, old, new: str(s).replace(old, new)
        }

    def current_env(self):
        return self.env_stack[-1]

    def eval(self, expr):
        if isinstance(expr, (int, float, bool)):
            return expr

        if isinstance(expr, str):
            env = self.current_env()
            if expr in env:
                return env[expr]
            return expr  # string literal

        if isinstance(expr, list):
            return [self.eval(e) for e in expr]

        if isinstance(expr, dict):
            # --- Comments (ignored during execution) ---
            if "comment" in expr:
                # Accept either string or list of strings
                return None

            # Variable assignment
            if "let" in expr:
                var, value_expr = expr["let"]
                value = self.eval(value_expr)
                self.current_env()[var] = value
                return value

            # Arrays
            if "get" in expr:
                arr = self.eval(expr["get"][0])
                index = self.eval(expr["get"][1])
                return arr[index]
            if "set" in expr:
                arr = self.eval(expr["set"][0])
                index = self.eval(expr["set"][1])
                value = self.eval(expr["set"][2])
                arr[index] = value
                return None
            if "push" in expr:
                arr = self.eval(expr["push"][0])
                value = self.eval(expr["push"][1])
                arr.append(value)
                return None
            if "len" in expr:
                return self.builtin_len(self.eval(expr["len"]))

            # Arithmetic
            if "add" in expr:
                return self.eval(expr["add"][0]) + self.eval(expr["add"][1])
            if "sub" in expr:
                return self.eval(expr["sub"][0]) - self.eval(expr["sub"][1])
            if "mul" in expr:
                return self.eval(expr["mul"][0]) * self.eval(expr["mul"][1])
            if "div" in expr:
                return self.eval(expr["div"][0]) / self.eval(expr["div"][1])
            if "mod" in expr:
                return self.eval(expr["mod"][0]) % self.eval(expr["mod"][1])

            # Comparison
            if "eq" in expr:
                return self.eval(expr["eq"][0]) == self.eval(expr["eq"][1])
            if "neq" in expr:
                return self.eval(expr["neq"][0]) != self.eval(expr["neq"][1])
            if "gt" in expr:
                return self.eval(expr["gt"][0]) > self.eval(expr["gt"][1])
            if "lt" in expr:
                return self.eval(expr["lt"][0]) < self.eval(expr["lt"][1])
            if "gte" in expr:
                return self.eval(expr["gte"][0]) >= self.eval(expr["gte"][1])
            if "lte" in expr:
                return self.eval(expr["lte"][0]) <= self.eval(expr["lte"][1])

            # Logic
            if "and" in expr:
                return self.eval(expr["and"][0]) and self.eval(expr["and"][1])
            if "or" in expr:
                return self.eval(expr["or"][0]) or self.eval(expr["or"][1])
            if "not" in expr:
                return not self.eval(expr["not"])

            # Output
            if "print" in expr:
                val = self.eval(expr["print"])
                print(val)
                return val

            # Input
            if "input" in expr:
                prompt = self.eval(expr["input"])
                return input(str(prompt))

            # Return
            if "return" in expr:
                val = self.eval(expr["return"])
                raise ReturnSignal(val)

            # If
            if "if" in expr:
                cond = self.eval(expr["if"]["condition"])
                if cond:
                    return self.eval(expr["if"]["then"])
                else:
                    return self.eval(expr["if"]["else"])

            # While
            if "while" in expr:
                while self.eval(expr["while"]["condition"]):
                    self.eval(expr["while"]["do"])
                return None

            # Block
            if "do" in expr:
                result = None
                for stmt in expr["do"]:
                    result = self.eval(stmt)
                return result

            # Function def
            if "def" in expr:
                name = expr["def"]["name"]
                params = expr["def"]["params"]
                body = expr["def"]["body"]
                self.functions[name] = {
                    "params": params,
                    "body": body
                }
                return None

            # Function call
            if "call" in expr:
                func_name = expr["call"][0]
                args_exprs = expr["call"][1:]
                arg_values = [self.eval(arg) for arg in args_exprs]

                # Built-in
                if func_name in self.builtins:
                    return self.builtins[func_name](*arg_values)

                # User-defined
                if func_name not in self.functions:
                    raise Exception(f"Function not found: {func_name}")

                func = self.functions[func_name]
                params = func["params"]
                body = func["body"]

                if len(params) != len(arg_values):
                    raise Exception("Argument count mismatch")

                local_env = dict(zip(params, arg_values))
                self.env_stack.append(local_env)

                try:
                    result = self.eval(body)
                except ReturnSignal as r:
                    result = r.value
                finally:
                    self.env_stack.pop()

                return result

        raise Exception(f"Unknown expression: {expr}")

    # --- Built-in Function Implementations ---

    def builtin_len(self, val):
        if isinstance(val, (list, str, dict)):
            return len(val)
        raise Exception(f"len() not supported on {type(val)}")

    def builtin_type(self, val):
        return type(val).__name__

    def builtin_print(self, *args):
        print(*args)
        return None

    def builtin_input(self, prompt=""):
        return input(str(prompt))

    def builtin_contains(self, collection, value):
        return value in collection

    def builtin_read_file(self, filepath):
        filepath = str(filepath)
        if not os.path.isfile(filepath):
            raise Exception(f"File not found: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def builtin_write_file(self, filepath, content):
        filepath = str(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return None


def run_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        program = json.load(f)

    interpreter = Interpreter()
    if isinstance(program, list):
        for stmt in program:
            interpreter.eval(stmt)
    else:
        interpreter.eval(program)


def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py program.json")
        return
    run_file(sys.argv[1])


if __name__ == "__main__":
    main()
