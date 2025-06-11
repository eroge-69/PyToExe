import csv
import os
import win32com.client as win32
from tkinter import Tk, filedialog

def selecionar_arquivo(titulo, tipos):
    root = Tk()
    root.withdraw()  # Oculta a janela principal
    caminho = filedialog.askopenfilename(title=titulo, filetypes=tipos)
    return os.path.abspath(os.path.normpath(caminho)) if caminho else None

def ler_nomes_csv(caminho_csv):
    nomes = []
    with open(caminho_csv, encoding="utf-8") as f:
        reader = csv.reader(f)
        for linha in reader:
            if linha:
                nome = linha[0].strip()
                if nome:
                    nomes.append(nome)
    return nomes

def destacar_nomes_no_word(caminho_docx, nomes):
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = True  # Coloque False para não abrir o Word visualmente

    doc = word.Documents.Open(caminho_docx)

    for nome in nomes:
        encontrar_e_destacar(word, nome)

    doc.Save()
    doc.Close()
    word.Quit()

    print("Todos os nomes foram destacados com sucesso.")

def encontrar_e_destacar(word, nome):
    find = word.Selection.Find
    word.Selection.HomeKey(Unit=6)  # wdStory

    find.Text = nome
    find.Forward = True
    find.Wrap = 1  # wdFindContinue
    find.Format = True
    find.MatchCase = False
    find.MatchWholeWord = True

    while find.Execute():
        word.Selection.Range.HighlightColorIndex = 7  # wdYellow
        word.Selection.MoveRight()

def main():
    print("Selecione o arquivo do Word (.docx)")
    caminho_docx = selecionar_arquivo("Selecione o arquivo .docx", [("Documentos do Word", "*.docx")])
    if not caminho_docx:
        print("Arquivo Word não selecionado.")
        return

    print("Selecione o arquivo CSV com os nomes")
    caminho_csv = selecionar_arquivo("Selecione o arquivo CSV", [("Arquivos CSV", "*.csv")])
    if not caminho_csv:
        print("Arquivo CSV não selecionado.")
        return

    nomes = ler_nomes_csv(caminho_csv)
    if not nomes:
        print("Nenhum nome encontrado no CSV.")
        return

    destacar_nomes_no_word(caminho_docx, nomes)

if __name__ == "__main__":
    main()
