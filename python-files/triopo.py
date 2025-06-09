
import tkinter as tk
from tkinter import filedialog, ttk
import sys
import io

# Лексический анализатор (токенизатор)
class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.tokens = []
        self.keywords = {
            'IF': 'IF',
            'THEN': 'THEN',
            'ELSE': 'ELSE',
            'ENDIF': 'ENDIF',
            'PRINT': 'PRINT',
            'INPUT': 'INPUT',
            'LET': 'LET'
        }
        self.operators = {
            '+': 'PLUS',
            '-': 'MINUS',
            '*': 'MULTIPLY',
            '/': 'DIVIDE',
            '=': 'EQUALS',
            '<': 'LESS',
            '>': 'GREATER',
            '<=': 'LESS_EQUAL',
            '>=': 'GREATER_EQUAL',
            '<>': 'NOT_EQUAL'
        }

    def tokenize(self):
        while self.pos < len(self.code):
            current_char = self.code[self.pos]
            if current_char.isspace():
                self.pos += 1
                continue
            if current_char.isdigit():
                num = ''
                while self.pos < len(self.code) and self.code[self.pos].isdigit():
                    num += self.code[self.pos]
                    self.pos += 1
                self.tokens.append(('NUMBER', int(num)))
                continue
            if current_char == '"':
                string = ''
                self.pos += 1
                while self.pos < len(self.code) and self.code[self.pos] != '"':
                    string += self.code[self.pos]
                    self.pos += 1
                self.pos += 1
                self.tokens.append(('STRING', string))
                continue
            if current_char.isalpha():
                ident = ''
                while self.pos < len(self.code) and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
                    ident += self.code[self.pos]
                    self.pos += 1
                keyword = self.keywords.get(ident.upper())
                if keyword:
                    self.tokens.append((keyword, ident))
                else:
                    self.tokens.append(('IDENTIFIER', ident))
                continue
            op_found = False
            for op in sorted(self.operators.keys(), key=len, reverse=True):
                if self.code.startswith(op, self.pos):
                    self.tokens.append((self.operators[op], op))
                    self.pos += len(op)
                    op_found = True
                    break
            if op_found:
                continue
            if current_char == '(':
                self.tokens.append(('LPAREN', '('))
                self.pos += 1
                continue
            if current_char == ')':
                self.tokens.append(('RPAREN', ')'))
                self.pos += 1
                continue
            raise SyntaxError(f'Неизвестный символ: {current_char}')
        return self.tokens

# Синтаксический анализатор (парсер)
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = None
        self.next_token()

    def next_token(self):
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            self.pos += 1
        else:
            self.current_token = None
        return self.current_token

    def expect(self, token_type, value=None):
        if (self.current_token and self.current_token[0] == token_type and (value is None or self.current_token[1] == value)):
            token = self.current_token
            self.next_token()
            return token
        expected = f"{token_type} '{value}'" if value else token_type
        found = self.current_token[0] if self.current_token else "конец файла"
        raise SyntaxError(f"Ожидалось {expected}, но найдено {found}")

    def parse(self):
        statements = []
        while self.current_token:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        if not self.current_token:
            return None
        if self.current_token[0] == 'PRINT':
            return self.parse_print()
        elif self.current_token[0] == 'LET' or self.current_token[0] == 'IDENTIFIER':
            return self.parse_assignment()
        elif self.current_token[0] == 'IF':
            return self.parse_if()
        elif self.current_token[0] == 'INPUT':
            return self.parse_input()
        raise SyntaxError(f"Неизвестный оператор: {self.current_token[1]}")

    def parse_print(self):
        self.expect('PRINT')
        expr = self.parse_expression()
        return ('PRINT', expr)

    def parse_input(self):
        self.expect('INPUT')
        var_name = self.expect('IDENTIFIER')
        return ('INPUT', var_name[1])

    def parse_assignment(self):
        if self.current_token[0] == 'LET':
            self.expect('LET')
        var_name = self.expect('IDENTIFIER')
        self.expect('EQUALS', '=')
        expr = self.parse_expression()
        return ('ASSIGN', var_name[1], expr)

    def parse_if(self):
        self.expect('IF')
        condition = self.parse_expression()
        self.expect('THEN')
        then_block = []
        while self.current_token and self.current_token[0] not in ('ELSE', 'ENDIF'):
            then_block.append(self.parse_statement())
        else_block = []
        if self.current_token and self.current_token[0] == 'ELSE':
            self.expect('ELSE')
            while self.current_token and self.current_token[0] != 'ENDIF':
                else_block.append(self.parse_statement())
        if self.current_token and self.current_token[0] == 'ENDIF':
            self.expect('ENDIF')
        return ('IF', condition, then_block, else_block)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.current_token and self.current_token[0] == 'OR':
            op = self.expect('OR')
            right = self.parse_logical_and()
            left = ('BINARY_OP', op[1], left, right)
        return left

    def parse_logical_and(self):
        left = self.parse_comparison()
        while self.current_token and self.current_token[0] == 'AND':
            op = self.expect('AND')
            right = self.parse_comparison()
            left = ('BINARY_OP', op[1], left, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.current_token and self.current_token[0] in ('LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL', 'EQUALS', 'NOT_EQUAL'):
            op = self.current_token
            self.next_token()
            right = self.parse_term()
            left = ('BINARY_OP', op[1], left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token and self.current_token[0] in ('PLUS', 'MINUS'):
            op = self.current_token
            self.next_token()
            right = self.parse_factor()
            left = ('BINARY_OP', op[1], left, right)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.current_token and self.current_token[0] in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token
            self.next_token()
            right = self.parse_unary()
            left = ('BINARY_OP', op[1], left, right)
        return left

    def parse_unary(self):
        if self.current_token and self.current_token[0] == 'MINUS':
            op = self.current_token
            self.next_token()
            expr = self.parse_unary()
            return ('UNARY_OP', op[1], expr)
        return self.parse_primary()

    def parse_primary(self):
        if not self.current_token:
            raise SyntaxError("Ожидалось выражение, но достигнут конец файла")
        token = self.current_token
        if token[0] == 'NUMBER':
            self.next_token()
            return ('NUMBER', token[1])
        elif token[0] == 'STRING':
            self.next_token()
            return ('STRING', token[1])
        elif token[0] == 'IDENTIFIER':
            self.next_token()
            return ('IDENTIFIER', token[1])
        elif token[0] == 'LPAREN':
            self.next_token()
            expr = self.parse_expression()
            self.expect('RPAREN', ')')
            return expr
        raise SyntaxError(f"Неожиданный токен: {token[1]}")

# Семантический анализатор
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = set()

    def analyze(self, ast):
        for node in ast:
            self.analyze_node(node)

    def analyze_node(self, node):
        if not node:
            return
        node_type = node[0]
        if node_type == 'ASSIGN':
            var_name = node[1]
            self.symbol_table.add(var_name)
            self.analyze_node(node[2])
        elif node_type == 'PRINT':
            self.analyze_node(node[1])
        elif node_type == 'IF':
            self.analyze_node(node[1])
            for stmt in node[2]:
                self.analyze_node(stmt)
            for stmt in node[3]:
                self.analyze_node(stmt)
        elif node_type == 'INPUT':
            var_name = node[1]
            self.symbol_table.add(var_name)
        elif node_type == 'BINARY_OP':
            self.analyze_node(node[2])
            self.analyze_node(node[3])
        elif node_type == 'UNARY_OP':
            self.analyze_node(node[2])
        elif node_type == 'IDENTIFIER':
            if node[1] not in self.symbol_table:
                raise NameError(f"Необъявленная переменная: {node[1]}")

# Интерпретатор
class Interpreter:
    def __init__(self):
        self.variables = {}

    def interpret(self, ast):
        for node in ast:
            self.execute_node(node)


    def execute_node(self, node):
        if not node:
            return None
        node_type = node[0]
        if node_type == 'ASSIGN':
            var_name = node[1]
            value = self.evaluate(node[2])
            self.variables[var_name] = value
            return value
        elif node_type == 'PRINT':
            value = self.evaluate(node[1])
            print(value)
            return value
        elif node_type == 'IF':
            condition = self.evaluate(node[1])
            if condition:
                for stmt in node[2]:
                    self.execute_node(stmt)
            else:
                for stmt in node[3]:
                    self.execute_node(stmt)
            return None
        elif node_type == 'INPUT':
            from tkinter import simpledialog
            var_name = node[1]
            value = simpledialog.askstring("Ввод", f"Введите значение для {var_name}:")
            if value is None:
                value = ""
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            self.variables[var_name] = value
            return value
        raise RuntimeError(f"Неизвестный тип узла: {node_type}")


    def evaluate(self, node):
        if not node:
            return None
        node_type = node[0]
        if node_type == 'NUMBER':
            return node[1]
        elif node_type == 'STRING':
            return node[1]
        elif node_type == 'IDENTIFIER':
            var_name = node[1]
            if var_name not in self.variables:
                raise NameError(f"Неопределенная переменная: {var_name}")
            return self.variables[var_name]
        elif node_type == 'BINARY_OP':
            op = node[1]
            left = self.evaluate(node[2])
            right = self.evaluate(node[3])
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '=':
                return left == right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '>=':
                return left >= right
            elif op == '<>':
                return left != right
            elif op == 'AND':
                return left and right
            elif op == 'OR':
                return left or right
            raise RuntimeError(f"Неизвестный оператор: {op}")
        elif node_type == 'UNARY_OP':
            op = node[1]
            expr = self.evaluate(node[2])
            if op == '-':
                return -expr
            raise RuntimeError(f"Неизвестный унарный оператор: {op}")
        raise RuntimeError(f"Неизвестный тип узла для вычисления: {node_type}")

class BasicCompiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.interpreter = Interpreter()

    def compile_and_run(self, code):
        try:
            self.lexer = Lexer(code)
            tokens = self.lexer.tokenize()
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            self.semantic_analyzer.analyze(ast)
            self.interpreter.interpret(ast)
        except Exception as e:
            print(f"Ошибка компиляции: {e}")

class TextRedirector(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class BasicIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Triopo basic")
        self.geometry("800x600")
        self.configure(bg="#1e1e1e")
        self.compiler = BasicCompiler()
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", foreground="#ffffff", background="#444", font=("Consolas", 11), padding=6)
        style.configure("TLabel", foreground="#ffffff", background="#1e1e1e")
        self.text_area = tk.Text(self, wrap=tk.WORD, font=("Consolas", 12), bg="#2e2e2e", fg="#ffffff", insertbackground="white")
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="📂 Открыть файл", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="▶ Запустить", command=self.run_code).pack(side=tk.LEFT)
        self.output_label = ttk.Label(self, text="Вывод:")
        self.output_label.pack(anchor=tk.W, padx=10)
        self.output_area = tk.Text(self, height=10, wrap=tk.WORD, font=("Consolas", 11), bg="#1e1e1e", fg="#00ff00", insertbackground="white")
        self.output_area.pack(fill=tk.BOTH, expand=False, padx=5, pady=(0, 5))

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("BASIC files", "*.basic"), ("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, content)

    def run_code(self):
        code = self.text_area.get("1.0", tk.END)
        self.output_area.delete("1.0", tk.END)
        sys.stdout = TextRedirector(self.output_area)
        sys.stderr = TextRedirector(self.output_area)
        try:
            self.compiler.compile_and_run(code)
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

if __name__ == "__main__":
    app = BasicIDE()
    app.mainloop()
