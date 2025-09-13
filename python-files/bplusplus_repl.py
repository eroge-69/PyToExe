#!/usr/bin/env python3
"""
B++ Interpreter with REPL (interactive terminal)

Features:
- say "Hello"
- set x to 10
- add 5 to x / subtract / multiply / divide
- repeat N times: ... end
- if condition: ... end

Usage:
  python3 bpp.py

Then type B++ code directly into the REPL.
"""

import sys

def tokenize(src):
    tokens = []
    for line in src.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens.append(line)
    return tokens

class Env:
    def __init__(self):
        self.vars = {}

    def get(self, name):
        if name not in self.vars:
            raise NameError(f"Variable '{name}' not defined")
        return self.vars[name]

    def set(self, name, value):
        self.vars[name] = value

def _split_outside_quotes(s, sep):
    parts = []
    cur = []
    in_q = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == '"':
            cur.append(ch)
            i += 1
            while i < len(s):
                cur.append(s[i])
                if s[i] == '"' and s[i-1] != '\\':
                    i += 1
                    break
                i += 1
            continue
        if not in_q and s.startswith(sep, i):
            parts.append(''.join(cur).strip())
            cur = []
            i += len(sep)
            continue
        cur.append(ch)
        i += 1
    parts.append(''.join(cur).strip())
    return parts

def eval_expr(expr, env):
    expr = expr.strip()
    if not expr:
        raise SyntaxError("Empty expression")
    if expr.startswith('"') and expr.endswith('"') and len(expr) >= 2:
        return expr[1:-1]
    try:
        if '.' in expr:
            return float(expr)
        return int(expr)
    except ValueError:
        pass
    if expr in env.vars:
        return env.get(expr)
    if '+' in expr:
        parts = _split_outside_quotes(expr, '+')
        values = [eval_expr(p, env) for p in parts]
        if any(isinstance(v, str) for v in values):
            return ''.join(str(v) for v in values)
        total = values[0]
        for v in values[1:]:
            total += v
        return total
    raise SyntaxError(f"Cannot evaluate expression: {expr}")

def run_lines(lines, env):
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue
        if line.startswith("say "):
            expr = line[4:].strip()
            print(eval_expr(expr, env))

        elif line.startswith("set ") and " to " in line:
            parts = line.split(" ", 3)
            if len(parts) == 4:
                _, var, _, val = parts
                env.set(var, eval_expr(val, env))
            else:
                raise SyntaxError(f"Invalid set syntax: {line}")

        elif line.startswith("add ") and " to " in line:
            num, _, var = line[4:].partition(" to ")
            left = var.strip()
            env.set(left, env.get(left) + eval_expr(num.strip(), env))

        elif line.startswith("subtract ") and " from " in line:
            num, _, var = line[9:].partition(" from ")
            left = var.strip()
            env.set(left, env.get(left) - eval_expr(num.strip(), env))

        elif line.startswith("multiply ") and " by " in line:
            var, _, num = line[9:].partition(" by ")
            left = var.strip()
            env.set(left, env.get(left) * eval_expr(num.strip(), env))

        elif line.startswith("divide ") and " by " in line:
            var, _, num = line[7:].partition(" by ")
            left = var.strip()
            divisor = eval_expr(num.strip(), env)
            if isinstance(divisor, (int, float)) and divisor == 0:
                raise ZeroDivisionError("Division by zero")
            env.set(left, env.get(left) / divisor)

        elif line.startswith("repeat ") and line.endswith(" times:"):
            count_expr = line[len("repeat "):-len(" times:")].strip()
            count_val = eval_expr(count_expr, env)
            try:
                count = int(count_val)
            except Exception:
                raise TypeError("repeat count must be an integer")
            block, jump = collect_block(lines, i+1)
            for _ in range(count):
                run_lines(block, env)
            i = jump

        elif line.startswith("if ") and line.endswith(":"):
            cond_expr = line[3:-1].strip()
            cond_val = eval_condition(cond_expr, env)
            block, jump = collect_block(lines, i+1)
            if cond_val:
                run_lines(block, env)
            i = jump

        i += 1

def collect_block(lines, start):
    block = []
    i = start
    depth = 0
    while i < len(lines):
        cur = lines[i]
        stripped = cur.strip()
        if stripped == "end":
            if depth == 0:
                return block, i
            depth -= 1
            block.append(cur)
            i += 1
            continue
        if stripped.endswith(":") and (stripped.startswith("repeat") or stripped.startswith("if")):
            depth += 1
            block.append(cur)
            i += 1
            continue
        block.append(cur)
        i += 1
    raise SyntaxError("Missing 'end'")

def eval_condition(expr, env):
    expr = expr.strip()
    if " is not " in expr:
        left, _, right = expr.partition(" is not ")
        return eval_expr(left.strip(), env) != eval_expr(right.strip(), env)
    if " is " in expr:
        left, _, right = expr.partition(" is ")
        return eval_expr(left.strip(), env) == eval_expr(right.strip(), env)
    return bool(eval_expr(expr, env))

def repl():
    print("B++ REPL - type your code. Use 'end' to close blocks. Ctrl+C to exit.")
    env = Env()
    buffer = []
    block_depth = 0
    while True:
        try:
            prompt = ">>> " if block_depth == 0 else "... "
            line = input(prompt)
            if not line.strip() and buffer and block_depth == 0:
                run_lines(tokenize("\n".join(buffer)), env)
                buffer = []
                continue
            if not line.strip() and not buffer:
                continue
            buffer.append(line)
            stripped = line.strip()
            if stripped.endswith(":") and (stripped.startswith("repeat") or stripped.startswith("if")):
                block_depth += 1
            elif stripped == "end":
                block_depth = max(0, block_depth - 1)
            if block_depth == 0 and not stripped.endswith(":"):
                run_lines(tokenize("\n".join(buffer)), env)
                buffer = []
        except KeyboardInterrupt:
            print("\nExiting B++")
            break
        except Exception as e:
            print("Error:", e)
            buffer = []
            block_depth = 0

if __name__ == "__main__":
    repl()
