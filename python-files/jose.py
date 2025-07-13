# pressionador_corrigido.py
import tkinter as tk
from tkinter import Toplevel, Listbox, Scrollbar, END, Button, messagebox
import pygetwindow as gw
import threading
import time
from pywinauto.application import Application

class KeyPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pressionador de Tecla Corrigido")
        self.root.geometry("300x120")
        self.root.resizable(False, False)

        # Frame para centralizar os botões
        frame = tk.Frame(root)
        frame.pack(expand=True)

        self.start_button = Button(frame, text="Iniciar", command=self.show_window_selection, width=15, height=2)
        self.start_button.pack(pady=5)

        self.stop_button = Button(frame, text="Parar", command=self.stop_pressing, state=tk.DISABLED, width=15, height=2)
        self.stop_button.pack(pady=5)

        self.pressing_thread = None
        self.is_pressing = False

    def show_window_selection(self):
        selection_window = Toplevel(self.root)
        selection_window.title("Selecione as Janelas do Jogo")
        selection_window.geometry("400x350")

        list_frame = tk.Frame(selection_window)
        scrollbar = Scrollbar(list_frame)
        window_listbox = Listbox(list_frame, selectmode=tk.MULTIPLE, exportselection=False)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        window_listbox.pack(expand=True, fill=tk.BOTH)
        
        all_windows = [win for win in gw.getAllWindows() if win.title]
        for win in all_windows:
            window_listbox.insert(END, win.title)

        window_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=window_listbox.yview)
        list_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        def on_confirm():
            selected_indices = window_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Erro", "Nenhuma janela selecionada.", parent=selection_window)
                return

            selected_windows = [all_windows[i] for i in selected_indices]
            selection_window.destroy()
            self.start_pressing(selected_windows)

        confirm_button = Button(selection_window, text="Confirmar e Iniciar", command=on_confirm)
        confirm_button.pack(pady=10)
        
        selection_window.transient(self.root)
        selection_window.grab_set()
        self.root.wait_window(selection_window)

    def start_pressing(self, selected_windows):
        self.is_pressing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.pressing_thread = threading.Thread(target=self.press_key_loop, args=(selected_windows,), daemon=True)
        self.pressing_thread.start()

    def stop_pressing(self):
        if not self.is_pressing:
            return
            
        self.is_pressing = False
        # Espera a thread terminar antes de reativar os botões
        if self.pressing_thread and self.pressing_thread.is_alive():
            self.pressing_thread.join()

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def press_key_loop(self, windows_to_process):
        target_controls = []
        FLASH_CLASS_NAMES = ['MacromediaFlashPlayerActiveX', 'ShockwaveFlash', 'FlashObject']

        for window in windows_to_process:
            try:
                app = Application().connect(handle=window._hWnd, timeout=10)
                win = app.window(handle=window._hWnd)
                
                found_control = None
                for class_name in FLASH_CLASS_NAMES:
                    try:
                        control = win.child_window(class_name=class_name)
                        if control.exists():
                            print(f"Sucesso: Controle '{class_name}' encontrado na janela '{window.title}'!")
                            found_control = control
                            break
                    except Exception:
                        continue

                if found_control:
                    target_controls.append(found_control)
                else:
                    print(f"Aviso: Nenhum controle Flash encontrado em '{window.title}'. Usando a janela principal como alvo.")
                    target_controls.append(win)
            except Exception as e:
                print(f"Erro ao conectar ou processar a janela '{window.title}': {e}")
        
        if not target_controls:
            print("Nenhum alvo válido foi encontrado. Parando a execução.")
            self.is_pressing = False # Define a flag para parar
        else:
             print("\n--- Pressionamento de teclas iniciado! ---")

        while self.is_pressing:
            if not target_controls:
                break # Sai do loop se a lista de alvos estiver vazia
            
            for control in list(target_controls): # Itera sobre uma cópia da lista
                try:
                    control.send_keystrokes('d')
                except Exception:
                    # Se uma janela for fechada, o controle se torna inválido
                    print(f"Um controle se tornou inválido (janela fechada?) e foi removido.")
                    target_controls.remove(control)
            time.sleep(0.1)
        
        print("--- Pressionamento de teclas parado. ---")
        # A LINHA PROBLEMÁTICA FOI REMOVIDA DAQUI. O CONTROLE AGORA RETORNA
        # CORRETAMENTE PARA A FUNÇÃO stop_pressing.

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyPresserApp(root)
    root.mainloop()