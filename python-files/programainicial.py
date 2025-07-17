import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import serial
import serial.tools.list_ports
from threading import Thread
import mysql.connector
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
from PIL import Image, ImageDraw, ImageFont
import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import sys

class BancoDeDados:
    def __init__(self):
        self.cursor = None  # evita erro se conexão falhar
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                port=3307
            )
            self.cursor = self.conn.cursor(buffered=True)
            self.criar_base_e_tabelas()
            print("[OK] Conectado ao banco de dados.")
        except mysql.connector.Error as e:
            print(f"[ERRO] Falha ao conectar: {e}")

    def criar_base_e_tabelas(self):
        if not self.cursor:
            return
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_rotinas CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        self.cursor.execute("USE sistema_rotinas")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS caixas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero_caixa VARCHAR(20),
                rotina INT,
                data_criacao DATETIME,
                esta_cheia BOOLEAN NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pecas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_caixa INT,
                numero_peca BIGINT,
                nome VARCHAR(100),
                codigo VARCHAR(50),
                FOREIGN KEY (id_caixa) REFERENCES caixas(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                chave VARCHAR(50) PRIMARY KEY,
                valor VARCHAR(50) NOT NULL
            )
        """)

        self.cursor.execute("""
            INSERT IGNORE INTO config (chave, valor) VALUES ('ultima_caixa', '0')
        """)

        self.conn.commit()

    def obter_ultima_caixa(self):
        if not self.cursor:
            return 0
        self.cursor.execute("SELECT valor FROM config WHERE chave = 'ultima_caixa'")
        resultado = self.cursor.fetchone()
        return int(resultado[0]) if resultado else 0

    def atualizar_ultima_caixa(self, nova_valor):
        if not self.cursor:
            return
        self.cursor.execute("UPDATE config SET valor = %s WHERE chave = 'ultima_caixa'", (str(nova_valor),))
        self.conn.commit()

    def obter_ultima_caixa_incompleta(self):
        if not self.cursor:
            return None
        self.cursor.execute("""
            SELECT id, numero_caixa, rotina FROM caixas
            WHERE esta_cheia = FALSE
            ORDER BY id DESC LIMIT 1
        """)
        return self.cursor.fetchone()

    def marcar_caixa_como_cheia(self, id_caixa):
        if not self.cursor:
            return
        self.cursor.execute("UPDATE caixas SET esta_cheia = TRUE WHERE id = %s", (id_caixa,))
        self.conn.commit()

    def salvar_caixa(self, caixa):
        if not self.cursor:
            return None
        self.cursor.execute("""
            INSERT INTO caixas (numero_caixa, rotina, data_criacao, esta_cheia)
            VALUES (%s, %s, %s, %s)
        """, (caixa.numero, caixa.rotina_ativa, datetime.now(), False))
        self.conn.commit()
        return self.cursor.lastrowid

    def salvar_peca(self, id_caixa, numero_peca, nome, codigo):
        if not self.cursor:
            return
        self.cursor.execute("""
            INSERT INTO pecas (id_caixa, numero_peca, nome, codigo)
            VALUES (%s, %s, %s, %s)
        """, (id_caixa, numero_peca, nome, codigo))
        self.conn.commit()

class GestorDeRotinas:
    def __init__(self, master, numeros_validos):
        self.top = tk.Toplevel(master)
        self.top.title("Editar Rotinas")
        self.numeros_validos = numeros_validos

        ttk.Label(self.top, text="Editar códigos das rotinas").grid(row=0, column=0, columnspan=3, pady=10)

        self.entries = {}
        for i in range(1, 5):
            ttk.Label(self.top, text=f"Rotina {i}:").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(self.top)
            entry.insert(0, str(self.numeros_validos[i][0]))
            entry.grid(row=i, column=1, padx=5)
            self.entries[i] = entry

        ttk.Button(self.top, text="Salvar", command=self.salvar).grid(row=5, column=0, columnspan=3, pady=10)

    def salvar(self):
        for i in range(1, 5):
            try:
                valor = int(self.entries[i].get())
                self.numeros_validos[i] = [valor]
            except ValueError:
                messagebox.showerror("Erro", f"Código inválido para Rotina {i}")
                return
        messagebox.showinfo("Sucesso", "Rotinas atualizadas com sucesso!")



class CognexDM8600:
    def __init__(self, app):
        self.app = app
        self.serial_port = None
        self.baudrate = 9600
        self.connect_serial()

    def connect_serial(self):
        try:
            self.serial_port = serial.Serial(
            port='COM4',
            baudrate=self.baudrate,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
            )
            Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao conectar: {str(e)}")


    def read_serial(self):
        buffer = ""
        while True:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting).decode('ascii')
                buffer += data
                if '\r\n' in buffer:
                    codes = buffer.split('\r\n')
                    for code in codes[:-1]:
                        self.process_code(code.strip())
                    buffer = codes[-1]

    def process_code(self, code):
        if code:
            self.app.entry_numero.delete(0, 'end')
            self.app.entry_numero.insert(0, code)
            self.app.processar_peça()

    def close(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

class Peça:
    def __init__(self, id_peça, número_peça):
        self.id = f"{id_peça:06d}"
        self.número_peça = número_peça
        self.nome = self._obter_nome_peça(número_peça)
    
    def _obter_nome_peça(self, número):
        prefixo = int(str(número)[:8])  # pega os primeiros 8 dígitos como inteiro
        mapeamento = {
            28865644: "Retainer",
            28865636: "Audio cover",
            28869058: "Main cover A",
            28869059: "Main cover B"
        }
        return mapeamento.get(prefixo, "")

class Caixa:
    def __init__(self, numero_caixa, rotina_ativa):
        self.numero = f"#{numero_caixa:06d}"
        self.peças = []
        self.rotina_ativa = rotina_ativa
        self.data_criação = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def adicionar_peça(self, peça):
        if len(self.peças) >= 4:
            raise ValueError("Caixa cheia (máx. 4 peças)!")
        self.peças.append(peça)

    def está_cheia(self):
        return len(self.peças) == 4

class SistemaRotinasGUI:
    def __init__(self, root, banco):
        self.root = root
        self.banco = banco
        self.root.title("Sistema de Rotinas")
        # Verifica se existe uma caixa incompleta ao iniciar
        ultima_incompleta = self.banco.obter_ultima_caixa_incompleta()
        if ultima_incompleta:
            id_db, numero_str, rotina = ultima_incompleta
            self.contador_caixas = int(numero_str.strip('#'))
            self.caixa_atual = Caixa(self.contador_caixas, rotina)
            self.caixa_atual.id_db = id_db
            self.rotina_ativa = rotina
            self.status_var = tk.StringVar(value=f"Rotina {rotina} ativa (retomada)")
        else:
            self.contador_caixas = self.banco.obter_ultima_caixa()
            self.status_var = tk.StringVar(value="Nenhuma rotina ativa")

        self.todas_peças = []
        self.caixas = []
        self.caixa_atual = None
        self.contador_peças = 0
        self.rotina_ativa = None
        self.números_válidos = {
            1: [28865644], 2: [28865636], 3: [28869058], 4: [28869059]
        }
        self.serial_number = 1
        self.data_atual = datetime.now().strftime("%d%m%y")
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        self.setup_ui()


    def ao_fechar(self):
        self.root.destroy()
    
    def abrir_editor_rotinas(self):
        GestorDeRotinas(self.root, self.números_válidos)


    def setup_ui(self):
        mainframe = ttk.Frame(self.root, padding="10")
        mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Button(mainframe, text="Editar Rotinas", command=self.abrir_editor_rotinas).grid(row=6, column=0, columnspan=7, pady=10)

        ttk.Label(mainframe, text="Rotinas:").grid(row=0, column=0, sticky=tk.W)
        for i in range(1, 6):
            ttk.Button(mainframe, text=f"Rotina {i}", command=lambda num=i: self.ativar_rotina(num)).grid(row=0, column=i, padx=5, pady=5)

        ttk.Button(mainframe, text="Listar Caixas", command=self.listar_caixas).grid(row=1, column=6, padx=5, pady=5)
        ttk.Button(mainframe, text="Limpar Caixa", command=self.limpar_caixa).grid(row=0, column=6, padx=5)




        ttk.Label(mainframe, text="Número da Peça:").grid(row=1, column=0, sticky=tk.W)
        self.entry_numero = ttk.Entry(mainframe, width=15)
        self.entry_numero.grid(row=1, column=1, columnspan=3, sticky=tk.W)

        ttk.Button(mainframe, text="Processar Peça", command=self.processar_peça).grid(row=1, column=4, padx=5)

        self.status_var = tk.StringVar()
        self.status_var.set("Nenhuma rotina ativa")
        ttk.Label(mainframe, textvariable=self.status_var).grid(row=2, column=0, columnspan=7, pady=10)

        self.tree = ttk.Treeview(mainframe, columns=("ID", "Número", "Nome", "Código"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Número", text="Número")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Código", text="Código")
        self.tree.grid(row=3, column=0, columnspan=7, pady=10)

    def gerar_codigo_peça(self):
        nova_data = datetime.now().strftime("%d%m%y")
        if nova_data != self.data_atual:
            self.data_atual = nova_data
            self.serial_number = 1
        codigo = f"PPPPPPPP{self.data_atual}{self.serial_number:04d}"
        self.serial_number += 1
        return codigo

    def ativar_rotina(self, número):
        # Se já houver rotina ativa, limpa a caixa atual
        if self.rotina_ativa is not None:
            if self.caixa_atual and self.rotina_ativa != 5:
                try:
                    self.banco.cursor.execute("DELETE FROM pecas WHERE id_caixa = %s", (self.caixa_atual.id_db,))
                    self.banco.conn.commit()
                except mysql.connector.Error as e:
                    messagebox.showerror("Erro", f"Erro ao limpar a caixa da base de dados: {e}")

            # Limpa visualmente as peças da interface
            self.tree.delete(*self.tree.get_children())

            self.caixa_atual = None
            self.todas_peças.clear()

        # Ativa a nova rotina
        self.rotina_ativa = número
        self.status_var.set(f"Rotina {número} ativa")

        if número != 5:
            self.contador_caixas += 1
            self.caixa_atual = Caixa(self.contador_caixas, número)
            self.caixa_atual.id_db = self.banco.salvar_caixa(self.caixa_atual)
            self.banco.atualizar_ultima_caixa(self.contador_caixas)
            self.caixas.append(self.caixa_atual)
            messagebox.showinfo("Nova Caixa", f"Caixa {self.caixa_atual.numero} criada para Rotina {número}")



    def limpar_caixa(self):
        if not self.caixa_atual or not self.rotina_ativa or self.rotina_ativa == 5:
            messagebox.showwarning("Aviso", "Nenhuma caixa ativa para limpar!")
            return

        # Limpa a lista de peças da caixa atual (em memória)
        self.caixa_atual.peças.clear()

        # Limpa a TreeView
        self.tree.delete(*self.tree.get_children())

        # Remove as peças da base de dados ligadas a esta caixa
        try:
            self.banco.cursor.execute("DELETE FROM pecas WHERE id_caixa = %s", (self.caixa_atual.id_db,))
            self.banco.conn.commit()
        except mysql.connector.Error as e:
            messagebox.showerror("Erro", f"Erro ao limpar a caixa da base de dados: {e}")


    def desativar_rotina(self):
        if self.rotina_ativa is None:
            messagebox.showwarning("Aviso", "Nenhuma rotina está ativa!")
            return
        self.rotina_ativa = None
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Nenhuma rotina ativa")

    def processar_peça(self):
        if self.rotina_ativa is None:
            messagebox.showerror("Erro", "Nenhuma rotina ativa!")
            return

        try:
            número_peça = int(self.entry_numero.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido!")
            return

        # ROTINA 5 – Remoção por código de barras da caixa
        if self.rotina_ativa == 5:
            numero_lido = self.entry_numero.get().strip().lstrip('#')

            try:
                numero_int = int(numero_lido)
            except ValueError:
                messagebox.showerror("Erro", "Código de caixa inválido!")
                return

            try:
                # Buscar a caixa
                self.banco.cursor.execute("""
                    SELECT id FROM caixas
                    WHERE numero_caixa = %s
                """, (f"#{numero_int:06d}",))
                caixa_info = self.banco.cursor.fetchone()

                if not caixa_info:
                    messagebox.showerror("Erro", f"Caixa #{numero_int:06d} não encontrada!")
                    return

                id_caixa = caixa_info[0]

                # Buscar peças da caixa
                self.banco.cursor.execute("""
                    SELECT numero_peca, nome, codigo FROM pecas
                    WHERE id_caixa = %s
                """, (id_caixa,))
                pecas = self.banco.cursor.fetchall()

                # Mostrar peças na Treeview
                self.tree.delete(*self.tree.get_children())
                for idx, (num, nome, cod) in enumerate(pecas, start=1):
                    self.tree.insert("", "end", values=(f"{idx:06d}", num, nome, cod))

                # Eliminar peças
                self.banco.cursor.execute("DELETE FROM pecas WHERE id_caixa = %s", (id_caixa,))

                # Eliminar a caixa
                self.banco.cursor.execute("DELETE FROM caixas WHERE id = %s", (id_caixa,))

                self.banco.conn.commit()

                messagebox.showinfo("Remoção", f"Caixa #{numero_int:06d} e suas peças foram removidas com sucesso!")
                self.entry_numero.delete(0, 'end')
                return

            except mysql.connector.Error as e:
                messagebox.showerror("Erro SQL", f"Ocorreu um erro: {e}")
                return

        # ROTINAS 1–4 – Processamento de peça
        if self.rotina_ativa != 5:
            número_str = str(número_peça)
            codigo_ref = self.números_válidos[self.rotina_ativa][0]
            num_digitos = len(str(codigo_ref))
            número_validacao = int(número_str[:num_digitos])

            if número_validacao not in self.números_válidos[self.rotina_ativa]:
                messagebox.showwarning("Aviso", f"A peça {número_peça} não é válida para a Rotina {self.rotina_ativa}!")
                self.entry_numero.delete(0, 'end')
                return

        self.contador_peças += 1
        nova_peça = Peça(self.contador_peças, número_peça)
        self.todas_peças.append(nova_peça)
        codigo_peça = self.entry_numero.get().strip()

        self.tree.insert("", "end", values=(nova_peça.id, nova_peça.número_peça, nova_peça.nome, codigo_peça))

        try:
            self.caixa_atual.adicionar_peça(nova_peça)
            messagebox.showinfo("Sucesso", f"Peça {nova_peça.id} adicionada à {self.caixa_atual.numero}")

            id_caixa_db = self.caixa_atual.id_db
            self.banco.salvar_peca(
                id_caixa=id_caixa_db,
                numero_peca=nova_peça.número_peça,
                nome=nova_peça.nome,
                codigo=codigo_peça
            )

            if self.caixa_atual.está_cheia():
                self.banco.marcar_caixa_como_cheia(self.caixa_atual.id_db)
                messagebox.showinfo("Caixa Cheia", f"Caixa {self.caixa_atual.numero} pronta para etiqueta!")

                caixa_cheia = self.caixa_atual
                self.contador_caixas += 1
                self.caixa_atual = Caixa(self.contador_caixas, self.rotina_ativa)
                self.caixa_atual.id_db = self.banco.salvar_caixa(self.caixa_atual)
                self.caixas.append(self.caixa_atual)
                self.banco.atualizar_ultima_caixa(self.contador_caixas)

                self.imprimir_etiqueta(caixa_cheia)

        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            self.entry_numero.delete(0, 'end')
            return

        # Limpa o campo de entrada após processar a peça
        self.entry_numero.delete(0, 'end')

    def imprimir_etiqueta(self, caixa):
        if not caixa or not caixa.peças:
            messagebox.showerror("Erro", "Nenhuma caixa ativa ou vazia!")
            return

        try:
            modelo_impressora = 'QL-810W'
            porta_impressora = 'usb://0x4f9:0x209c'
            tamanho_etiqueta = '62x29'

            largura = 696
            altura = 271
            imagem = Image.new('L', (largura, altura), 255)  # fundo branco
            draw = ImageDraw.Draw(imagem)

            try:
                fonte = ImageFont.truetype("arial.ttf", 24)
            except:
                fonte = ImageFont.load_default()

            y_pos = 5
            draw.text((5, y_pos), f"Caixa: {caixa.numero}", font=fonte, fill=0)
            y_pos += 30
            draw.text((5, y_pos), f"Rotina: {caixa.rotina_ativa}", font=fonte, fill=0)
            y_pos += 30
            draw.text((5, y_pos), f"Data: {caixa.data_criação}", font=fonte, fill=0)
            y_pos += 30
            draw.text((5, y_pos), "Peças:", font=fonte, fill=0)
            y_pos += 50

            for peça in caixa.peças:
                draw.text((30, y_pos), f"{peça.id} - {peça.nome} ({peça.número_peça})", font=fonte, fill=0)
                y_pos += 25

            # Gerar código de barras do número da caixa (sem o #)
            numero_sem_hash = caixa.numero.strip('#')
            CODE128 = barcode.get_barcode_class('code128')
            barcode_obj = CODE128(numero_sem_hash, writer=ImageWriter())

            buffer = BytesIO()
            barcode_obj.write(buffer, {
                'module_width': 0.3,
                'module_height': 15,
                'font_size': 10,
                'text_distance': 1,
                'write_text': False  # remove o texto do código de barras
            })
            buffer.seek(0)
            img_codigo = Image.open(buffer).convert('L')

            # Colar código de barras no canto inferior direito
            pos_x = largura - img_codigo.width - 10
            pos_y = altura - img_codigo.height - 130
            imagem.paste(img_codigo, (pos_x, pos_y))

            # Ajustar crop para não cortar fundo branco e evitar barra preta
            imagem = imagem.crop((0, 0, largura, altura))

            # Preparar e enviar para impressão
            qlr = BrotherQLRaster(modelo_impressora)
            instrucoes = convert(
                qlr=qlr,
                images=[imagem],
                label=tamanho_etiqueta,
                orientation='standard',
                threshold=70,
                dither=False,
                compress=False,
                cut=True
            )

            send(
                instructions=instrucoes,
                printer_identifier=porta_impressora,
                backend_identifier='pyusb'
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao imprimir: {str(e)}")
    
    def listar_caixas(self):
        janela = tk.Toplevel(self.root)
        janela.title("Caixas Registradas")
        janela.geometry("800x500")

        colunas = ("Número", "Rotina", "Peças", "Cheia")
        tree = ttk.Treeview(janela, columns=colunas, show="headings")
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=180 if col == "Peças" else 100)

        tree.pack(fill=tk.BOTH, expand=True)

        # Buscar todas as caixas
        self.banco.cursor.execute("SELECT id, numero_caixa, rotina FROM caixas ORDER BY id DESC")
        caixas = self.banco.cursor.fetchall()

        caixas_unicas = {}
        for id_caixa, numero_bruto, rotina in caixas:
            numero = f"#{int(numero_bruto.strip('#')):06d}"

            # Se já vimos esse número de caixa, ignoramos duplicados
            if numero in caixas_unicas:
                continue

            # Buscar peças associadas a esta caixa
            self.banco.cursor.execute("SELECT nome, numero_peca FROM pecas WHERE id_caixa = %s", (id_caixa,))
            pecas = self.banco.cursor.fetchall()

            lista_pecas = ", ".join(f"{nome} ({num})" for nome, num in pecas) if pecas else "Nenhuma"
            cheia = "Sim" if len(pecas) >= 4 else "Não"

            caixas_unicas[numero] = (rotina, lista_pecas, cheia)

        for numero, (rotina, lista_pecas, cheia) in caixas_unicas.items():
            tree.insert("", "end", values=(numero, rotina, lista_pecas, cheia))

# Execução
if __name__ == "__main__":
    root = tk.Tk()
    banco = BancoDeDados()
    if not banco.cursor:
        messagebox.showerror("Erro", "Falha ao conectar ao banco de dados.")
        sys.exit(1)

    app = SistemaRotinasGUI(root, banco)
    leitor = CognexDM8600(app)
    root.mainloop()