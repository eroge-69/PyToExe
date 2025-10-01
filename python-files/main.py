# Arquivo: main.py

import sys
from PyQt6.QtWidgets import QApplication, QDialog

# Importa as classes das janelas do módulo gui.
from gui import LoginDialog, MainWindow

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    # 1. Cria a instância da aplicação.
    app = QApplication(sys.argv)

    # 2. Cria e exibe a janela de login.
    login_dialog = LoginDialog()

    # 3. O método .exec() pausa o código aqui até a janela de login ser fechada.
    # Ele retorna um valor que nos diz se o login foi aceito (Accepted) ou não.
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # 4. Se o login foi bem-sucedido, cria e mostra a janela principal.
        window = MainWindow()
        window.show()

        # 5. Inicia o loop de eventos da aplicação.
        sys.exit(app.exec())

    # Se o login falhar ou for cancelado, o programa simplesmente termina.