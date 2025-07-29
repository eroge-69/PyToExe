# Re-executing the updated XMInterpreter with full features due to kernel reset

import random
import math
import re
import time
from typing import Any

# Special marker for uninitialized variables
class Uninitialized:
    def __repr__(self):
        return "<Uninitialized>"

# Exception classes
class BreakLoop(Exception): pass
class EndProgram(Exception): pass
class JumpTo(Exception):
    def __init__(self, line): self.line = line
class CatchBlock(Exception): pass

class XMInterpreter:
    def __init__(self):
        self.global_vars = {}
        self.vars = self.global_vars
        self.last_result = 0
        self.lines = []
        self.line_ptr = 0
        self.functions = {}
        self.running = True
        self.call_stack = []

    def _parse_value(self, val: str) -> Any:
        val = val.strip()
        if val in self.vars:
            value = self.vars[val]
            if isinstance(value, Uninitialized):
                raise Exception(f"Variable '{val}' is uninitialized")
            return value
        if val.startswith("[") and val.endswith("]"):
            return eval(val)
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        try: return int(val)
        except: pass
        try: return float(val)
        except: pass
        return val

    def _evaluate_expr(self, expr: str) -> Any:
        expr = expr.replace("~", str(self.last_result))
        if expr.startswith(("+(", "-(", "*(", "/(")):
            return self._calc(expr)
        return self._parse_value(expr)

    def _calc(self, expr: str) -> Any:
        op = expr[0]
        inside = expr[2:-1]
        a, b = map(self._parse_value, inside.split(",", 1))
        result = {
            "+": a + b,
            "-": a - b,
            "*": a * b,
            "/": a / b if b != 0 else 0,
        }[op]
        self.last_result = result
        return result

    def _interpolate(self, s: str) -> str:
        def repl(m):
            var = m.group(1)
            if "[" in var and "]" in var:
                arr, idx = var[:-1].split("[")
                return str(self.vars.get(arr, [])[int(idx)])
            return str(self.vars.get(var, f"<{var}>"))
        return re.sub(r'<(.*?)>', repl, s)

    def _eval_condition(self, cond: str) -> bool:
        for op in ["==", "!=", ">", "<"]:
            if op in cond:
                l, r = map(self._parse_value, cond.split(op))
                return {
                    "==": l == r, "!=": l != r,
                    ">": l > r, "<": l < r
                }[op]
        return False

    def _eval_bool_expr(self, expr: str) -> bool:
        tokens = expr.replace("True", "1").replace("False", "0").split()
        stack = []
        for token in tokens:
            if token in self.vars:
                stack.append(bool(self.vars[token]))
            elif token == "1": stack.append(True)
            elif token == "0": stack.append(False)
            elif token in {"AND", "OR", "XOR", "NAND", "XNOR"}:
                b, a = stack.pop(), stack.pop()
                stack.append({
                    "AND": a and b,
                    "OR": a or b,
                    "XOR": a != b,
                    "NAND": not (a and b),
                    "XNOR": a == b
                }[token])
            elif token == "NOT":
                a = stack.pop()
                stack.append(not a)
        return stack[-1]

    def _exec_block(self, block: str):
        if block.startswith("{") and block.endswith("}"):
            lines = block[1:-1].split(";")
            for l in lines:
                self.exec_line(l.strip())
        else:
            self.exec_line(block.strip())

    def exec_line(self, line: str):
        line = line.split("#")[0].strip()
        if not line: return

        # Handle declarations with Max and Round
        if any(line.startswith(prefix) for prefix in ["Max.", "-Max.", "Round.", "Max.Round.", "-Max.Round."]):
            self._handle_declaration(line)
            return

        if line.startswith(".Print"):
            content = line.split(" ", 1)[1].strip().strip('"')
            print(self._interpolate(content))
        elif line.startswith(".Input"):
            msg, var = re.findall(r'"(.*?)"\s*->\s*\((.*?)\)', line)[0]
            val = input(msg + " ")
            self.vars[var] = val
        elif line.startswith(".Write"):
            fname, data = re.findall(r'"(.*?)",\s*"(.*?)"', line)[0]
            with open(fname, "w") as f: f.write(data)
        elif line.startswith(".Read"):
            fname, var = re.findall(r'"(.*?)"\s*->\s*\((.*?)\)', line)[0]
            with open(fname) as f: self.vars[var] = f.read()
        elif line.startswith(".Wait"):
            time.sleep(int(re.findall(r'\((\d+)\)', line)[0]) / 1000)
        elif line.startswith(".Func"):
            name = re.findall(r'\.Func\((.*?)\)', line)[0]
            block = self._collect_block()
            self.functions[name] = block
        elif line.startswith(".Call"):
            name = re.findall(r'\.Call\((.*?)\)', line)[0]
            self._exec_block(self.functions.get(name, ""))
        elif line.startswith(".If("):
            cond, rest = line[4:].split("):", 1)
            if self._eval_condition(cond): self._exec_block(rest)
        elif line.startswith(".Elif("):
            cond, rest = line[6:].split("):", 1)
            if self._eval_condition(cond): self._exec_block(rest)
        elif line.startswith(".Else:"):
            self._exec_block(line[6:].strip())
        elif line.startswith("Bool.If("):
            cond, rest = line[8:].split("):", 1)
            if self._eval_bool_expr(cond): self._exec_block(rest)
        elif line.startswith(".While("):
            cond, rest = line[7:].split("):", 1)
            while self._eval_condition(cond): self._exec_block(rest)
        elif line.startswith("Bool.While("):
            cond, rest = line[11:].split("):", 1)
            while self._eval_bool_expr(cond): self._exec_block(rest)
        elif line.startswith(".Loop"):
            while True: self._exec_block(line[5:].strip())
        elif line.startswith(".Try{"):
            try:
                self._exec_block(line[4:].strip())
            except:
                raise CatchBlock()
        elif line.startswith(".Catch{"):
            try: self._exec_block(line[7:].strip())
            except: pass
        elif line.startswith("BREAK"): raise BreakLoop()
        elif line.startswith("END"): raise EndProgram()
        elif line.startswith("JUMP("):
            raise JumpTo(int(line[5:-1]))
        elif line.startswith("Random.("):
            var, lo, hi = re.findall(r'\((.*?),\s*(\d+),\s*(\d+)\)', line)[0]
            self.vars[var.strip()] = random.randint(int(lo), int(hi))
        elif line.startswith("Random.Bool.("):
            var = line[13:-2]
            self.vars[var.strip()] = random.choice([True, False])
        elif line.startswith("Bool.("):
            var = line[6:-2].strip()
            self.vars[var] = False
        elif line.startswith("STR.("):
            var = line[5:-2].strip()
            self.vars[var] = ""
        elif "++" in line:
            var = line.strip("();+ ")
            self.vars[var] += 1
        elif "--" in line:
            var = line.strip("();- ")
            self.vars[var] -= 1
        elif line.startswith("(") and ") =" in line:
            var, val = line.split("=", 1)
            var = var.strip("() ").strip()
            val = val.strip()
            self.vars[var] = self._evaluate_expr(val)
        elif line.startswith("(") and line.endswith(");"):
            var = line.strip("(); ").strip()
            self.vars[var] = Uninitialized()

    def _handle_declaration(self, line: str):
        line = line.rstrip(";")
        match = re.match(r'(-?Max\.Round\.|Max\.Round\.|-?Max\.|Round\.)(\((.*)\))', line)
        if not match:
            return
        modifier, inner = match.group(1), match.group(3)
        parts = inner.split(",")
        var = parts[0].strip()
        value = int(parts[1]) if len(parts) > 1 else None
        if "Round." in modifier:
            direction = parts[2] if len(parts) > 2 else "up"
            if var in self.vars:
                self.vars[var] = math.ceil(self.vars[var]) if direction == "up" else math.floor(self.vars[var])
        if "Max." in modifier or "-Max." in modifier:
            if var in self.vars and value is not None:
                if "-" in modifier:
                    self.vars[var] = max(self.vars[var], value)
                else:
                    self.vars[var] = min(self.vars[var], value)

    def _collect_block(self):
        self.line_ptr += 1
        block = ""
        while self.line_ptr < len(self.lines):
            line = self.lines[self.line_ptr].strip()
            if line == "}":
                break
            block += line + ";"
            self.line_ptr += 1
        return "{" + block + "}"

    def run(self, code: str):
        self.lines = code.strip().splitlines()
        self.line_ptr = 0
        try:
            while self.line_ptr < len(self.lines):
                try:
                    self.exec_line(self.lines[self.line_ptr])
                    self.line_ptr += 1
                except JumpTo as j:
                    self.line_ptr = j.line - 1
                except BreakLoop:
                    break
                except CatchBlock:
                    while not self.lines[self.line_ptr].strip().startswith(".Catch{"):
                        self.line_ptr += 1
        except EndProgram:
            return

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python xm_runner.py your_program.xm")
    else:
        try:
            with open(sys.argv[1], "r") as f:
                code = f.read()
                xm = XMInterpreter()
                xm.run(code)
        except Exception as e:
            print("Runtime error:", e)


