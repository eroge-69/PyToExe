from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd
import time

# Data de hoje no formato 'dd/mm/yyyy'
hoje = datetime.today().strftime('%d/%m/%Y')

# Iniciar o navegador
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # opcional: corre sem abrir janela
driver = webdriver.Chrome(options=options)

try:
    # Ir para o site
    driver.get("https://publicacoes.mj.pt/Pesquisa.aspx")

    # Esperar pelo dropdown
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ddlTipoCaderno")))

    # Selecionar o tipo de publicação
    tipo_caderno = Select(driver.find_element(By.ID, "ddlTipoCaderno"))
    tipo_caderno.select_by_visible_text("Publicação de Atos de Registo Comercial e de Registo de Fundações")

    # Inserir a data
    data_inicio = driver.find_element(By.ID, "txtDataInicio")
    data_fim = driver.find_element(By.ID, "txtDataFim")
    data_inicio.clear()
    data_inicio.send_keys(hoje)
    data_fim.clear()
    data_fim.send_keys(hoje)

    # Clicar em Pesquisar
    driver.find_element(By.ID, "btnPesquisar").click()

    # Esperar pelos resultados
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gvResult")))

    # Extrair os dados
    rows = driver.find_elements(By.CSS_SELECTOR, "#gvResult tr")
    dados = []

    for row in rows[1:]:  # Ignorar cabeçalho
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 3:
            dados.append({
                "Data": cols[0].text.strip(),
                "Nome do Negócio": cols[1].text.strip(),
                "Morada": cols[2].text.strip()
            })

    # Exportar para Excel
    df = pd.DataFrame(dados)
    nome_ficheiro = f"Registos_{datetime.today().strftime('%Y-%m-%d')}.xlsx"
    df.to_excel(nome_ficheiro, index=False)

    print(f"Exportado com sucesso para {nome_ficheiro}!")

finally:
    driver.quit()
