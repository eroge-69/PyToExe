import pandas as pd
import glob
import os

def processar_curva_carga(ficheiro):
    try:
        df = pd.read_csv(ficheiro, header=None, names=["Consumo_kWh"])
        
        n_registos = len(df)
        if n_registos == 35040:
            date_rng = pd.date_range(start="2023-01-01", end="2023-12-31 23:45", freq="15min")
        elif n_registos == 35136:
            date_rng = pd.date_range(start="2024-01-01", end="2024-12-31 23:45", freq="15min")
        else:
            raise ValueError(f"O ficheiro '{ficheiro}' tem {n_registos} registos. Apenas são aceites 35040 ou 35136.")

        df["Datetime"] = date_rng
        df["Consumo_MWh"] = df["Consumo_kWh"] / 1000 / 4

        perfil_mensal = df.groupby(df["Datetime"].dt.month)["Consumo_MWh"].sum()
        perfil_mensal.index = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        perfil_mensal = perfil_mensal.reset_index()
        perfil_mensal.columns = ["Coluna1", "CPE 1"]

        perfil_semanal = df.groupby(df["Datetime"].dt.dayofweek)["Consumo_MWh"].sum()
        perfil_semanal.index = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
        perfil_semanal = perfil_semanal.reset_index()
        perfil_semanal.columns = ["Coluna1", "CPE 1"]

        perfil_diario = df.groupby(df["Datetime"].dt.hour)["Consumo_MWh"].sum()
        perfil_diario.index = perfil_diario.index + 1
        perfil_diario = perfil_diario.reset_index()
        perfil_diario.columns = ["Coluna1", "CPE 1"]

        nome_saida = os.path.splitext(ficheiro)[0] + "_perfis.xlsx"
        
        with pd.ExcelWriter(nome_saida) as writer:
            perfil_mensal.to_excel(writer, sheet_name="Mensal", index=False)
            perfil_semanal.to_excel(writer, sheet_name="Semanal", index=False)
            perfil_diario.to_excel(writer, sheet_name="Diario", index=False)

        print(f"✅ Perfis exportados para {nome_saida}")

    except Exception as e:
        print(f"Ocorreu um erro ao processar o ficheiro '{ficheiro}':")
        print(f"Detalhes: {e}")

# === Loop para processar todos os ficheiros ===
for ficheiro in glob.glob("*[Cc]urva*de*carga*.csv"):
    processar_curva_carga(ficheiro)

# === Adiciona uma pausa no final para ver a mensagem de erro ===
print("\nProcessamento concluído. Pressione ENTER para fechar a janela...")
input()