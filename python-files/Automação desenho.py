import tkinter as tk
from tkinter import ttk, messagebox
import xlwings as xw
import os
import itertools

class TubeDesignerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Desenhador de Tubos")
        
        # Caminho do arquivo Excel com o layout
        self.excel_file = r'C:\Users\s-Pablo.Souza\OneDrive - Vallourec\Desktop\Automações\Projeto desenho tubo padrão\Codigo\código V2\Layout - tubo padrão.xlsx'
        
        # Abre o arquivo Excel
        try:
            self.wb = xw.Book(self.excel_file)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo Excel: {e}")
            self.master.destroy()
            return
        
        # Define as planilhas
        self.sheet_layout = self.wb.sheets['Layout']
        self.sheet_defeitos = self.wb.sheets['defeitos']
        
        self.tube_length_mm = None
        # Armazena defeitos como tuplas: (defect_name, new_shape, posicao_mm, angle_value)
        self.placed_shapes = []
        self.current_cota_y = None
        
        # 1) Painel para definir o tamanho do tubo
        self.frame_tubo = ttk.Frame(master)
        self.frame_tubo.pack(padx=10, pady=10, fill="x")
        ttk.Label(self.frame_tubo, text="Tamanho do tubo (mm):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_tamanho = ttk.Entry(self.frame_tubo, width=10)
        self.entry_tamanho.grid(row=0, column=1, padx=5, pady=5)
        self.btn_definir_tamanho = ttk.Button(self.frame_tubo, text="Definir", command=self.definir_tamanho)
        self.btn_definir_tamanho.grid(row=0, column=2, padx=5, pady=5)
        
        # 2) Painel para adicionar defeitos
        # Inicialmente não empacotado; será exibido no definir_tamanho
        self.frame_defeitos = ttk.Frame(master)
        
        # 3) Lista interativa de defeitos
        self.frame_lista_defeitos = ttk.Frame(master)
        self.frame_lista_defeitos.pack(fill="x", padx=10, pady=10)
        
        # 4) Botão de finalizar
        self.btn_finalizar = ttk.Button(master, text="Finalizar", command=self.finalizar)
        self.btn_finalizar.pack(padx=10, pady=10)
        
        # Opções de defeitos e ângulo
        self.defeito_options = [
            "Transversal Interno",
            "Transversal externo",
            "Longitudinal Interno",
            "Longitudinal externo",
            "Solda",  # Tratado de forma especial na tabela
            "FBH",
            "Wall reduction",
            "Drill hole"
        ]
        self.angulo_options = ["0°", "90°", "180°", "270°"]

    def definir_tamanho(self):
        try:
            tamanho = float(self.entry_tamanho.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido para o tamanho do tubo.")
            return
        self.tube_length_mm = tamanho
        messagebox.showinfo("Info", f"Tamanho do tubo definido como {tamanho} mm.\nEste valor será usado como referência para posicionar os defeitos.")
        
        # Agora exibimos o frame de defeitos (2) somente após definir o tamanho
        self.frame_defeitos.pack(padx=10, pady=10, fill="x")
        
        # Linha para selecionar o defeito e sua posição
        ttk.Label(self.frame_defeitos, text="Defeito:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_defeito = ttk.Combobox(self.frame_defeitos, values=self.defeito_options, state="readonly")
        self.combo_defeito.grid(row=0, column=1, padx=5, pady=5)
        self.combo_defeito.current(0)
        
        ttk.Label(self.frame_defeitos, text="Posição (mm):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_posicao = ttk.Entry(self.frame_defeitos, width=10)
        self.entry_posicao.grid(row=0, column=3, padx=5, pady=5)
        
        # Nova linha para seleção do ângulo
        ttk.Label(self.frame_defeitos, text="Ângulo:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_angulo = ttk.Combobox(self.frame_defeitos, values=self.angulo_options, state="readonly")
        self.combo_angulo.grid(row=1, column=1, padx=5, pady=5)
        self.combo_angulo.current(0)
        
        self.btn_adicionar_defeito = ttk.Button(self.frame_defeitos, text="Adicionar Defeito", command=self.adicionar_defeito)
        self.btn_adicionar_defeito.grid(row=0, column=4, rowspan=2, padx=5, pady=5)
        
        # Debug: lista os shapes na planilha "defeitos"
        for sh in self.sheet_defeitos.api.Shapes:
            print("Shape disponível:", sh.Name)

           
    def adicionar_defeito(self):
        """
        Adiciona um defeito à planilha de layout, posicionando-o de forma que o subshape "Eixo"
        fique exatamente na posição desejada, calculada a partir do valor (em mm) fornecido pelo usuário.
        
        Procedimento:
          1. Copia o shape correspondente (conforme shapes_map) da planilha "defeitos" e cola-o no layout.
          2. Calcula a posição desejada em pontos (P_desired) com base no valor digitado.
          3. Dentro do grupo recém-colado, localiza o subshape "Eixo" e calcula seu centro relativo (em relação ao grupo).
          4. Ajusta o Left do grupo para que: new_shape.Left + rel_eixo = P_desired.
          5. Aplica o deslocamento vertical (angular) aos itens do grupo:
                - Se o item for o subshape "Defeito" ou tiver um TextFrame cujo texto, após strip(), seja "X",
                  o item é deslocado verticalmente de acordo com o ângulo selecionado.
        """
        if self.tube_length_mm is None:
            messagebox.showerror("Erro", "Defina primeiro o tamanho do tubo.")
            return

        shapes_map = {
            "Transversal Interno": "Transversal Interno",
            "Transversal externo": "Transversal externo",
            "Longitudinal Interno": "Longitudinal Interno",
            "Longitudinal externo": "Longitudinal externo",
            "Solda": "Solda",
            "FBH": "FBH",
            "Wall reduction": "Wall reduction",
            "Drill hole": "Drill hole"
        }

        defect_name = self.combo_defeito.get()
        shape_name = shapes_map.get(defect_name)
        if not shape_name:
            messagebox.showerror("Erro", f"Shape não encontrado para o defeito '{defect_name}'")
            return

        try:
            posicao_mm = float(self.entry_posicao.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um valor numérico válido para a posição.")
            return

        if posicao_mm < 10:
            posicao_mm += 20
        elif posicao_mm > (self.tube_length_mm - 10):
            posicao_mm -= 20
        posicao_mm = max(0, min(posicao_mm, self.tube_length_mm))

        try:
            defect_shape = self.sheet_defeitos.api.Shapes(shape_name)
            defect_shape.Copy()
            self.sheet_layout.api.Paste()
            shapes = self.sheet_layout.api.Shapes
            new_shape = shapes(shapes.Count)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar o defeito: {e}")
            return

        try:
            try:
                tube_shape = self.sheet_layout.api.Shapes("Tubo")
            except Exception:
                tube_shape = self.sheet_layout.api.Shapes("Rectangle 50")
            tube_left = tube_shape.Left
            tube_width = tube_shape.Width

            P_desired = tube_left + (posicao_mm / self.tube_length_mm) * tube_width
            print(f"[DEBUG] P_desired = {P_desired:.2f} pts (pos_mm = {posicao_mm})")

            new_shape.Left = tube_left + (posicao_mm / self.tube_length_mm) * tube_width
            new_shape.Top = tube_shape.Top + (tube_shape.Height - new_shape.Height) / 2

            # Ajusta o grupo para que o subshape "Eixo" fique em P_desired.
            eixo_found = False
            rel_eixo = 0
            try:
                group_items = new_shape.GroupItems
                for idx in range(1, group_items.Count + 1):
                    item = group_items.Item(idx)
                    print(f"[DEBUG] {defect_name} - Item {idx}: Name={item.Name}, Left={item.Left:.2f}, Width={item.Width:.2f}")
                    if item.Name == "Eixo":
                        rel_eixo = (item.Left + (item.Width / 2)) - new_shape.Left
                        eixo_found = True
                        print(f"[DEBUG] 'Eixo' encontrado: rel_eixo = {rel_eixo:.2f}")
                        break
                if not eixo_found:
                    rel_eixo = new_shape.Width / 2
                    print(f"[DEBUG] 'Eixo' não encontrado, usando centro do grupo: rel_eixo = {rel_eixo:.2f}")
            except Exception as e:
                print(f"[ERRO] Ao buscar 'Eixo' em '{defect_name}': {e}")
                rel_eixo = new_shape.Width / 2

            delta = P_desired - (new_shape.Left + rel_eixo)
            print(f"[DEBUG] delta = {delta:.2f}")
            new_shape.Left += delta
            print(f"[DEBUG] new_shape.Left ajustado para {new_shape.Left:.2f} para alinhar 'Eixo' em {P_desired:.2f}")

            # Aplica o deslocamento vertical (angular).
            angulo_selecionado = self.combo_angulo.get()
            deslocamento_vertical_cm = {
                "0°": 0.0,
                "180°": 0.0,
                "90°": -0.75,
                "270°": 0.75
            }
            if angulo_selecionado in deslocamento_vertical_cm:
                deslocamento_pts = deslocamento_vertical_cm[angulo_selecionado] * 28.35
                try:
                    group_items = new_shape.GroupItems
                    for idx in range(1, group_items.Count + 1):
                        item = group_items.Item(idx)
                        if item.Name == "Defeito":
                            item.Top += deslocamento_pts
                            print(f"[DEBUG] Subshape 'Defeito' deslocado {deslocamento_vertical_cm[angulo_selecionado]} cm para {angulo_selecionado}.")
                        else:
                            try:
                                if hasattr(item, 'TextFrame'):
                                    texto = item.TextFrame.Characters().Text.strip()
                                    if texto == "X":
                                        item.Top += deslocamento_pts
                                        print(f"[DEBUG] Caixa de texto com 'X' deslocada {deslocamento_vertical_cm[angulo_selecionado]} cm para {angulo_selecionado}.")
                            except Exception as e_text:
                                print(f"[DEBUG] Erro ao verificar item para 'X': {e_text}")
                except Exception as e:
                    print(f"[ERRO] Ao acessar os itens do grupo: {e}")

            angle_value = self.combo_angulo.get()
            self.placed_shapes.append((defect_name, new_shape, posicao_mm, angle_value))
            # Atualiza a lista interativa:
            self.atualizar_lista_defeitos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao posicionar o defeito: {e}")


    def atualizar_lista_defeitos(self):
        """
        Atualiza a lista interativa de defeitos exibida na interface.
        Cada linha exibe:
          - Para defeitos normais: Descrição, Entrada para posição (mm), Combobox para ângulo e botão "Remover".
          - Para "Solda": Exibe "Weld" na descrição, entrada para posição, Combobox para ângulo e botão "Remover".
        As alterações feitas pelo usuário serão atualizadas nos métodos atualizar_defeito_pos e atualizar_defeito_angle.
        """
        for widget in self.frame_lista_defeitos.winfo_children():
            widget.destroy()
        
        desc_map = {
            "Longitudinal externo": "External Longitudinal Notch (L OD)",
            "Longitudinal Interno": "Internal Longitudinal Notch (L ID)",
            "Transversal externo": "External Transverse Notch (T OD)",
            "Transversal Interno": "Internal Transverse Notch (T ID)",
            "FBH": "Flat Bottom Hole (FBH ID)",
            "Wall reduction": "Wall Reduction (WR ID)",
            "Drill hole": "Through Drill Hole (TDH)"
        }
        
        sorted_defects = sorted(self.placed_shapes, key=lambda tup: tup[2])
        for idx, (d_name, d_shape, pos, angle) in enumerate(sorted_defects):
            row = idx
            if d_name == "Solda":
                lbl = ttk.Label(self.frame_lista_defeitos, text="Weld")
            else:
                lbl = ttk.Label(self.frame_lista_defeitos, text=desc_map.get(d_name, d_name))
            lbl.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            ent_pos = ttk.Entry(self.frame_lista_defeitos, width=10)
            ent_pos.insert(0, str(pos))
            ent_pos.grid(row=row, column=1, padx=5, pady=2)
            ent_pos.bind("<FocusOut>", lambda event, i=idx: self.atualizar_defeito_pos(i, event.widget.get()))
            
            cmb_angle = ttk.Combobox(self.frame_lista_defeitos, values=self.angulo_options, state="readonly", width=6)
            cmb_angle.set(angle)
            cmb_angle.grid(row=row, column=2, padx=5, pady=2)
            cmb_angle.bind("<<ComboboxSelected>>", lambda event, i=idx: self.atualizar_defeito_angle(i, event.widget.get()))
            
            btn_remover = ttk.Button(self.frame_lista_defeitos, text="Remover", command=lambda i=idx: self.remover_defeito(i))
            btn_remover.grid(row=row, column=3, padx=5, pady=2)
            
    def atualizar_defeito_pos(self, i, novo_val):
        try:
            novo_val = float(novo_val)
        except ValueError:
            return
        sorted_defects = sorted(self.placed_shapes, key=lambda tup: tup[2])
        d_name, d_shape, pos, angle = sorted_defects[i]
        sorted_defects[i] = (d_name, d_shape, novo_val, angle)
        self.placed_shapes = sorted_defects
        self.atualizar_posicao_defeito(d_shape, novo_val, angle)
        self.atualizar_lista_defeitos()
        
    def atualizar_defeito_angle(self, i, novo_angle):
        sorted_defects = sorted(self.placed_shapes, key=lambda tup: tup[2])
        d_name, d_shape, pos, old_angle = sorted_defects[i]
        # Atualiza a tupla com o novo ângulo
        sorted_defects[i] = (d_name, d_shape, pos, novo_angle)
        self.placed_shapes = sorted_defects
        # Chama atualizar_posicao_defeito passando o ângulo antigo e o novo
        self.atualizar_posicao_defeito(d_shape, pos, old_angle, novo_angle)
        self.atualizar_lista_defeitos()

        
    def remover_defeito(self, i):
        sorted_defects = sorted(self.placed_shapes, key=lambda tup: tup[2])
        d_name, d_shape, pos, angle = sorted_defects[i]
        try:
            d_shape.Delete()  # Exclui o shape diretamente
        except Exception as e:
            print(f"[DEBUG] Erro ao deletar o shape: {e}")
        sorted_defects.pop(i)
        self.placed_shapes = sorted_defects
        self.atualizar_lista_defeitos()
        
    def atualizar_posicao_defeito(self, shape, posicao_mm, old_angle, new_angle):
        try:
            try:
                tube_shape = self.sheet_layout.api.Shapes("Tubo")
            except Exception:
                tube_shape = self.sheet_layout.api.Shapes("Rectangle 50")
            tube_left = tube_shape.Left
            tube_width = tube_shape.Width

            P_desired = tube_left + (posicao_mm / self.tube_length_mm) * tube_width
            shape.Left = tube_left + (posicao_mm / self.tube_length_mm) * tube_width
            shape.Top = tube_shape.Top + (tube_shape.Height - shape.Height) / 2

            eixo_found = False
            rel_eixo = 0
            try:
                group_items = shape.GroupItems
                for idx in range(1, group_items.Count + 1):
                    item = group_items.Item(idx)
                    if item.Name == "Eixo":
                        rel_eixo = (item.Left + (item.Width / 2)) - shape.Left
                        eixo_found = True
                        break
                if not eixo_found:
                    rel_eixo = shape.Width / 2
            except Exception:
                rel_eixo = shape.Width / 2

            delta = P_desired - (shape.Left + rel_eixo)
            shape.Left += delta

            # Calcular o deslocamento vertical considerando a mudança de ângulo:
            if new_angle in {"0°", "180°"}:
                deslocamento_vertical_cm = 0.0
            elif new_angle == "90°":
                # Se a mudança foi de 270° para 90°, desloca -1,5; caso contrário, -0.75.
                deslocamento_vertical_cm = -1.5 if old_angle == "270°" else -0.75
            elif new_angle == "270°":
                # Se a mudança foi de 90° para 270°, desloca 1.5; caso contrário, 0.75.
                deslocamento_vertical_cm = 1.5 if old_angle == "90°" else 0.75
            else:
                deslocamento_vertical_cm = 0.0

            deslocamento_pts = deslocamento_vertical_cm * 28.35
            try:
                group_items = shape.GroupItems
                for idx in range(1, group_items.Count + 1):
                    item = group_items.Item(idx)
                    if item.Name == "Defeito":
                        item.Top += deslocamento_pts
                    else:
                        try:
                            if hasattr(item, 'TextFrame'):
                                texto = item.TextFrame.Characters().Text.strip()
                                if texto == "X":
                                    item.Top += deslocamento_pts
                        except Exception:
                            pass
                # Opcional: imprimir debug
                print(f"[DEBUG] Deslocamento vertical aplicado: {deslocamento_vertical_cm} cm ({deslocamento_pts:.2f} pts)")
            except Exception:
                pass
        except Exception as e:
            print(f"[ERRO] Ao atualizar posição do defeito: {e}")


    def numerar_defeitos(self):
        """
        Ordena as tuplas (defect_name, shape, posicao_mm, angle_value) de self.placed_shapes
        da esquerda para a direita e substitui o texto 'X' pelo número sequencial (1, 2, 3, ...),
        ignorando os defeitos do tipo "Solda".
        """
        sorted_placed = sorted(self.placed_shapes, key=lambda tup: tup[1].Left)
        num = 1
        for defect_type, shape, pos_mm, *rest in sorted_placed:
            if defect_type == "Solda":
                print(f"Ignorando defeito 'Solda' no shape {shape.Name}.")
                continue
            atualizado = False
            try:
                group_items = shape.GroupItems
                for idx in range(1, group_items.Count + 1):
                    item = group_items.Item(idx)
                    if hasattr(item, 'TextFrame'):
                        text_content = item.TextFrame.Characters().Text
                        if text_content.strip() == 'X':
                            item.TextFrame.Characters().Text = str(num)
                            atualizado = True
            except Exception as e:
                try:
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        text_content = shape.TextFrame.Characters().Text
                        if text_content.strip() == 'X':
                            shape.TextFrame.Characters().Text = str(num)
                            atualizado = True
                except Exception as e2:
                    print(f"Aviso: não foi possível acessar o TextFrame do shape '{defect_type}'. Detalhes: {e2}")
            if atualizado:
                print(f"Defeito '{defect_type}' numerado como {num}.")
            else:
                print(f"Aviso: Nenhuma caixa de texto 'X' encontrada para o defeito '{defect_type}'.")
            num += 1


    def criar_cotas(self):
        """
        Cria as cotas para cada grupo de defeitos que compartilham a mesma posição longitudinal (pos_mm).
        Cada cota é baseada no shape "Cota" (um grupo contendo:
          - Uma seta horizontal,
          - Uma caixa de texto com Name "Texto",
          - E uma linha vertical com Name "Cota fim").
        A seta horizontal se estende desde a extremidade direita de "Side A" até o ponto definido pelo 
        subshape "Eixo" do defeito (para o grupo, usa-se o maior valor encontrado). Em seguida, a linha
        vertical ("Cota fim") é ajustada para que sua altura seja fixa (aumentando somente para cima) conforme:
          - Para defeitos normais: 1ª cota = 0,5 cm, 2ª = 0,82 cm, 3ª = 1,14 cm, etc.
          - Para defeito "Solda": acrescenta 0,43 cm ao valor normal.
        As cotas são empilhadas verticalmente, iniciando 0,32 cm abaixo do tubo, com espaçamento de 0,32 cm entre elas.
        """
        try:
            sideA = self.sheet_layout.api.Shapes("Side A")
            sideA_right = sideA.Left + sideA.Width
            print(f"[DEBUG] Side A: Left={sideA.Left:.2f}, Width={sideA.Width:.2f}, sideA_right={sideA_right:.2f}")

            try:
                tubo_shape = self.sheet_layout.api.Shapes("Tubo")
            except Exception as e:
                print(f"[DEBUG] 'Tubo' não encontrado, usando 'Rectangle 50': {e}")
                tubo_shape = self.sheet_layout.api.Shapes("Rectangle 50")
            tube_bottom = tubo_shape.Top + tubo_shape.Height
            print(f"[DEBUG] Tubo: Top={tubo_shape.Top:.2f}, Height={tubo_shape.Height:.2f}, tube_bottom={tube_bottom:.2f}")

            spacing = 0.4 * 28.35  
            current_y = tube_bottom + spacing
            print(f"[DEBUG] Offset vertical inicial = {spacing:.2f} pts, current_y = {current_y:.2f}")

            sorted_defects = sorted(self.placed_shapes, key=lambda tup: tup[2])
            print(f"[DEBUG] Total de defeitos a cotar: {len(sorted_defects)}")

            groups = []
            for key, group in itertools.groupby(sorted_defects, key=lambda tup: tup[2]):
                groups.append(list(group))
            print(f"[DEBUG] Total de grupos de defeitos: {len(groups)}")

            for i, group in enumerate(groups, start=1):
                pos_mm = group[0][2]
                defect_name = group[0][0]
                print(f"\n[DEBUG] Processando grupo {i} com pos_mm={pos_mm:.0f} (ex.: '{defect_name}')")

                group_defect_eixo_x = -float('inf')
                group_eixo_bottom = -float('inf')
                for (d_name, d_shape, d_pos, *rest) in group:
                    try:
                        group_items = d_shape.GroupItems
                        defect_eixo_x_tmp = None
                        eixo_bottom_tmp = None
                        for idx in range(1, group_items.Count + 1):
                            item = group_items.Item(idx)
                            if item.Name == "Eixo":
                                defect_eixo_x_tmp = item.Left + (item.Width / 2)
                                eixo_bottom_tmp = d_shape.Top + item.Top + item.Height
                                break
                        if defect_eixo_x_tmp is None:
                            defect_eixo_x_tmp = d_shape.Left + (d_shape.Width / 2)
                            eixo_bottom_tmp = d_shape.Top + d_shape.Height
                    except Exception as e:
                        print(f"[ERRO] Ao buscar 'Eixo' em '{d_name}': {e}")
                        defect_eixo_x_tmp = d_shape.Left + (d_shape.Width / 2)
                        eixo_bottom_tmp = d_shape.Top + d_shape.Height

                    group_defect_eixo_x = max(group_defect_eixo_x, defect_eixo_x_tmp)
                    group_eixo_bottom = max(group_eixo_bottom, eixo_bottom_tmp)
                print(f"[DEBUG] Grupo {i}: group_defect_eixo_x={group_defect_eixo_x:.2f}, group_eixo_bottom={group_eixo_bottom:.2f}")

                try:
                    self.sheet_defeitos.api.Shapes("Cota").Copy()
                    self.sheet_layout.api.Paste()
                    print(f"[DEBUG] 'Cota' copiado e colado com sucesso para grupo {i}.")
                except Exception as e:
                    print(f"[ERRO] Ao copiar 'Cota' para grupo {i}: {e}")
                    continue

                shapes = self.sheet_layout.api.Shapes
                new_cota = shapes(shapes.Count)
                print(f"[DEBUG] Novo shape 'Cota' para grupo {i} obtido: Top={new_cota.Top:.2f}, Left={new_cota.Left:.2f}")

                new_cota.Left = sideA_right
                new_cota.Top = current_y
                print(f"[DEBUG] Cota do grupo {i} posicionada em: Left={new_cota.Left:.2f}, Top={new_cota.Top:.2f}")

                cota_width = group_defect_eixo_x - sideA_right
                if cota_width < 0:
                    cota_width = 0
                new_cota.Width = cota_width
                print(f"[DEBUG] Largura da cota do grupo {i}: cota_width={cota_width:.2f}")

                try:
                    if hasattr(new_cota, "GroupItems"):
                        group_items_cota = new_cota.GroupItems
                        replaced = False
                        for idx in range(1, group_items_cota.Count + 1):
                            item_sub = group_items_cota.Item(idx)
                            print(f"[DEBUG] Cota do grupo {i} - Item {idx}: Name={item_sub.Name}")
                            if item_sub.Name == "Texto":
                                item_sub.TextFrame.Characters().Text = f"{pos_mm:.0f}"
                                replaced = True
                                print(f"[DEBUG] Texto da cota do grupo {i} substituído por: {pos_mm:.0f}")
                        if not replaced:
                            print(f"[AVISO] Caixa de texto 'Texto' não encontrada na cota do grupo {i}.")
                    else:
                        print(f"[DEBUG] Shape 'Cota' do grupo {i} não é um grupo; não foi possível ajustar o texto.")
                except Exception as e:
                    print(f"[ERRO] Ao ajustar o texto da cota do grupo {i}: {e}")

                try:
                    if hasattr(new_cota, "GroupItems"):
                        group_items_cota = new_cota.GroupItems
                        for idx in range(1, group_items_cota.Count + 1):
                            item_sub = group_items_cota.Item(idx)
                            if item_sub.Name == "Cota fim":
                                bottom_abs = new_cota.Top + item_sub.Top + item_sub.Height
                                if defect_name == "Solda":
                                    desired_length_cm = 0.5 + (i - 1) * 0.32 + 0.43
                                else:
                                    desired_length_cm = 0.5 + (i - 1) * 0.32
                                desired_length_pts = desired_length_cm * 28.35
                                print(f"[DEBUG] Cota do grupo {i} ('{defect_name}'): desired_length_cm={desired_length_cm:.2f} cm, desired_length_pts={desired_length_pts:.2f} pts")
                                new_absolute_top = bottom_abs - desired_length_pts
                                new_relative_top = new_absolute_top - new_cota.Top
                                if new_relative_top < item_sub.Top:
                                    item_sub.Top = new_relative_top
                                    item_sub.Height = desired_length_pts
                                    print(f"[DEBUG] 'Cota fim' do grupo {i} ajustado: novo Top relativo = {new_relative_top:.2f}, nova Height = {desired_length_pts:.2f}")
                                else:
                                    print(f"[DEBUG] 'Cota fim' do grupo {i} não necessita ajuste.")
                                break
                except Exception as e:
                    print(f"[ERRO] Ao ajustar 'Cota fim' na cota do grupo {i}: {e}")

                current_y += spacing
                print(f"[DEBUG] Próxima cota será posicionada em current_y = {current_y:.2f}")

            self.current_cota_y = current_y

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar as cotas: {e}")

    def criar_cota_tubo(self):
        """
        Cria uma cota final que liga as linhas "Side A" e "Side B", representando
        o tamanho total do tubo. Essa cota é baseada no shape "Cota" (um grupo contendo:
          - Uma seta horizontal,
          - Uma caixa de texto com Name "Texto",
          - E uma linha vertical com Name "Cota fim").
        A cota é posicionada horizontalmente de modo que seu Left seja a extremidade direita de "Side A"
        e sua largura seja a distância até a extremidade esquerda de "Side B".
        O texto da cota é substituído pelo tamanho total do tubo (sem unidade).
        Essa cota é posicionada abaixo da última cota dos defeitos, utilizando self.current_cota_y.
        """
        try:
            sideA = self.sheet_layout.api.Shapes("Side A")
            sideB = self.sheet_layout.api.Shapes("Side B")
            sideA_right = sideA.Left + sideA.Width
            sideB_left = sideB.Left
            print(f"[DEBUG] Cota Tubo: Side A right = {sideA_right:.2f}, Side B left = {sideB_left:.2f}")

            try:
                self.sheet_defeitos.api.Shapes("Cota 1").Copy()
                self.sheet_layout.api.Paste()
                print("[DEBUG] 'Cota' copiado e colado para cota do tubo com sucesso.")
            except Exception as e:
                print(f"[ERRO] Ao copiar shape 'Cota' para cota do tubo: {e}")
                return

            shapes = self.sheet_layout.api.Shapes
            new_cota = shapes(shapes.Count)
            print(f"[DEBUG] Novo shape 'Cota' para tubo obtido: Top={new_cota.Top:.2f}, Left={new_cota.Left:.2f}")

            extra_offset = 0.5 * 28.35  # 0,5 cm em pontos
            new_cota.Left = sideA_right
            new_cota.Top = self.current_cota_y
            print(f"[DEBUG] Cota do tubo posicionada em: Left={new_cota.Left:.2f}, Top={new_cota.Top:.2f}")

            cota_width = sideB_left - sideA_right
            if cota_width < 0:
                cota_width = 0
            new_cota.Width = cota_width
            print(f"[DEBUG] Cota do tubo: Width definida = {cota_width:.2f}")

            try:
                if hasattr(new_cota, "GroupItems"):
                    group_items_cota = new_cota.GroupItems
                    replaced = False
                    for idx in range(1, group_items_cota.Count + 1):
                        item_sub = group_items_cota.Item(idx)
                        print(f"[DEBUG] Cota Tubo - Item {idx}: Name={item_sub.Name}")
                        if item_sub.Name == "Texto":
                            item_sub.TextFrame.Characters().Text = f"{self.tube_length_mm:.0f}"
                            replaced = True
                            print(f"[DEBUG] Texto da cota do tubo substituído por: {self.tube_length_mm:.0f}")
                    if not replaced:
                        print("[AVISO] Caixa de texto com Name 'Texto' não encontrada na cota do tubo.")
                else:
                    try:
                        new_cota.TextFrame.Characters().Text = f"{self.tube_length_mm:.0f}"
                        print(f"[DEBUG] Texto ajustado diretamente na cota do tubo: {self.tube_length_mm:.0f}")
                    except Exception as e:
                        print(f"[ERRO] Ao ajustar o texto diretamente na cota do tubo: {e}")
            except Exception as e:
                print(f"[ERRO] Ao ajustar o texto da cota do tubo: {e}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar a cota do tubo: {e}")

    def numerar_defeitos(self):
        """
        Ordena as tuplas (defect_name, shape, posicao_mm, angle_value) armazenadas em self.placed_shapes
        da esquerda para a direita e substitui o texto 'X' pelo número do defeito (1, 2, 3, ...),
        ignorando os defeitos do tipo "Solda".
        """
        sorted_placed = sorted(self.placed_shapes, key=lambda tup: tup[1].Left)
        num = 1
        for defect_type, shape, pos_mm, *rest in sorted_placed:
            if defect_type == "Solda":
                print(f"Ignorando defeito 'Solda' no shape {shape.Name}.")
                continue

            atualizado = False
            try:
                group_items = shape.GroupItems
                for idx in range(1, group_items.Count + 1):
                    item = group_items.Item(idx)
                    if hasattr(item, 'TextFrame'):
                        text_content = item.TextFrame.Characters().Text
                        if text_content.strip() == 'X':
                            item.TextFrame.Characters().Text = str(num)
                            atualizado = True
            except Exception as e:
                try:
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        text_content = shape.TextFrame.Characters().Text
                        if text_content.strip() == 'X':
                            shape.TextFrame.Characters().Text = str(num)
                            atualizado = True
                except Exception as e2:
                    print(f"Aviso: não foi possível acessar o TextFrame do shape '{defect_type}'. Detalhes: {e2}")

            if atualizado:
                print(f"Defeito '{defect_type}' numerado como {num}.")
            else:
                print(f"Aviso: Nenhuma caixa de texto 'X' encontrada para o defeito '{defect_type}'.")
            num += 1

    def preencher_tabela(self):
        """
        Preenche a tabela que se encontra abaixo do desenho do tubo com as descrições dos defeitos.
        
        Regras:
          - A tabela ocupa as linhas 30 a 62 da planilha de layout.
          - O número de linhas finais será o mesmo do número de defeitos posicionados.
          - Para defeitos normais:
                Coluna A: Número do defeito (sequencial)
                Coluna B: Descrição do defeito conforme o mapeamento:
                      • External Longitudinal Notch (L OD)
                      • Internal Longitudinal Notch (L ID)
                      • External Transverse Notch (T OD)
                      • Internal Transverse Notch (T ID)
                      • Flat Bottom Hole (FBH ID)
                      • Wall Reduction (WR ID)
                      • Through Drill Hole (TDH)
                Coluna R: Posição angular do defeito
                Coluna S: Distância do entalhe à extremidade A (valor digitado)
                Coluna T: Distância do entalhe à extremidade B (tamanho do tubo - valor digitado)
          - Para o defeito "Solda":
                Coluna A: em branco
                Coluna B: "Weld"
                Colunas S e T: conforme acima
                A linha inteira receberá fundo com a cor "#d9d9d9" e somente bordas externas.
        """
        desc_map = {
            "Longitudinal externo": "External Longitudinal Notch (L OD)",
            "Longitudinal Interno": "Internal Longitudinal Notch (L ID)",
            "Transversal externo": "External Transverse Notch (T OD)",
            "Transversal Interno": "Internal Transverse Notch (T ID)",
            "FBH": "Flat Bottom Hole (FBH ID)",
            "Wall reduction": "Wall Reduction (WR ID)",
            "Drill hole": "Through Drill Hole (TDH)"
        }
        ws = self.sheet_layout

        # Filtra os defeitos a partir de self.placed_shapes.
        defect_data = []
        for tup in self.placed_shapes:
            if len(tup) >= 4:
                d_name, d_shape, pos, angle = tup
            else:
                d_name, d_shape, pos = tup
                angle = ""
            defect_data.append((d_name, pos, angle))
        n = len(defect_data)
        print(f"[DEBUG] Total de defeitos para tabela: {n}")

        table_start = 30
        table_end = 62
        current_table_rows = table_end - table_start + 1

        ws.range(f"{table_start}:{table_end}").clear_contents()

        if n < current_table_rows:
            ws.range(f"{table_start + n}:{table_end}").delete()
            print(f"[DEBUG] Excluídas {current_table_rows - n} linhas da tabela.")
        elif n > current_table_rows:
            ws.range(f"{table_end + 1}:{table_end + (n - current_table_rows)}").insert()
            print(f"[DEBUG] Inseridas {n - current_table_rows} linhas na tabela.")

        for i, (d_name, pos, angle) in enumerate(defect_data, start=1):
            row = table_start + i - 1
            if d_name == "Solda":
                ws.range(f"A{row}").value = ""
                ws.range(f"B{row}").value = "Weld"
            else:
                ws.range(f"A{row}").value = i
                description = desc_map.get(d_name, "")
                ws.range(f"B{row}").value = description
            ws.range(f"R{row}").value = angle
            ws.range(f"S{row}").value = pos
            ws.range(f"T{row}").value = self.tube_length_mm - pos
            print(f"[DEBUG] Linha {row}: A={ws.range(f'A{row}').value}, B={ws.range(f'B{row}').value}, R={ws.range(f'R{row}').value}, S={pos}, T={self.tube_length_mm - pos}")

            if d_name == "Solda":
                rng = ws.range(f"A{row}:T{row}")
                rng.color = "#d9d9d9"
                for edge in [7, 8, 9, 10]:
                    rng.api.Borders(edge).LineStyle = 1
                    rng.api.Borders(edge).Weight = 2
                rng.api.Borders(11).LineStyle = -4142
                rng.api.Borders(12).LineStyle = -4142
                print(f"[DEBUG] Linha {row} formatada para Solda (fundo #d9d9d9, bordas externas).")

    def finalizar(self):
        if self.placed_shapes:
            self.numerar_defeitos()
            self.criar_cotas()
            self.criar_cota_tubo()
            self.preencher_tabela()
        try:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            final_path = os.path.join(desktop, "desenho_tubo_final.xlsx")
            self.wb.save(final_path)
            messagebox.showinfo("Finalizado", f"Arquivo salvo em: {final_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TubeDesignerApp(root)
    root.mainloop()
