import ebooklib
from ebooklib import epub
from googletrans import Translator
import tkinter as tk
from tkinter import filedialog
import os
import time

def read_epub(file_path):
    """Lê o conteúdo de um arquivo EPUB e retorna uma lista de parágrafos de texto."""
    book = epub.read_epub(file_path)
    paragraphs = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_content().decode('utf-8')
        # Extrai texto entre tags <p> ou similar
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        for p in soup.find_all(['p', 'div', 'span']):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
    return paragraphs

def translate_text(texts, batch_size=10, delay=2):
    """Traduz uma lista de textos em lotes, com pausas para respeitar limites da API."""
    translator = Translator()
    translated_texts = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"Traduzindo lote {i // batch_size + 1} de {len(texts) // batch_size + 1}...")
        try:
            translations = translator.translate(batch, src='en', dest='pt')
            translated_texts.extend([t.text for t in translations])
        except Exception as e:
            print(f"Erro na tradução: {e}. Tentando novamente após pausa...")
            time.sleep(10)  # Pausa maior em caso de erro
            translations = translator.translate(batch, src='en', dest='pt')
            translated_texts.extend([t.text for t in translations])
        time.sleep(delay)  # Pausa para evitar limite de requisições
    return translated_texts

def create_translated_epub(original_path, translated_texts):
    """Cria um novo arquivo EPUB com o texto traduzido."""
    book = epub.read_epub(original_path)
    output_path = original_path.replace('.epub', '_pt.epub')
    text_index = 0
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_content().decode('utf-8')
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        for p in soup.find_all(['p', 'div', 'span']):
            if p.get_text(strip=True) and text_index < len(translated_texts):
                p.string = translated_texts[text_index]
                text_index += 1
        item.set_content(str(soup).encode('utf-8'))
    epub.write_epub(output_path, book)
    return output_path

def main():
    # Configura a interface para selecionar arquivo
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo EPUB",
        filetypes=[("Arquivos EPUB", "*.epub")]
    )
    if not file_path:
        print("Nenhum arquivo selecionado. Encerrando.")
        return

    print(f"Arquivo selecionado: {file_path}")
    print("Lendo o arquivo EPUB...")
    paragraphs = read_epub(file_path)
    print(f"{len(paragraphs)} parágrafos encontrados. Iniciando tradução...")

    # Traduz em lotes
    translated_paragraphs = translate_text(paragraphs, batch_size=10, delay=2)

    print("Criando novo arquivo EPUB com texto traduzido...")
    output_path = create_translated_epub(file_path, translated_paragraphs)
    print(f"Arquivo traduzido salvo em: {output_path}")

if __name__ == "__main__":
    main()