import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Função para carregar e limpar os dados
@st.cache_data
def load_data(path):
    df = pd.read_excel(
        path,
        sheet_name="Controle",
        header=5  # Cabeçalho real está na linha 6
    )
    
    # Remover colunas "Unnamed"
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Garantir que 'Status' seja numérico
    df['Status'] = pd.to_numeric(df['Status'], errors='coerce')

    # Mapear status numérico para texto + emoji
    status_map = {
        3: "✅ Finalizado",
        2: "⚠️ Pendente Implementação",
        1: "❌ Aguardando Disposição"
    }
    df['Status'] = df['Status'].map(status_map)

    # Converter coluna de data
    df['Data da Emissão'] = pd.to_datetime(df['Data da Emissão'], errors='coerce')

    # Criar colunas auxiliares para mês
    df['Mês_Num'] = df['Data da Emissão'].dt.month

    # Mapear o número do mês para o nome do mês (abreviado)
    meses = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df['Mês'] = df['Mês_Num'].map(meses)

    return df

# Gráfico de status pequeno
def grafico_status_rncs(df_filtrado):
    # Contar RNCs por status
    status_counts = df_filtrado['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Quantidade']

    # Gráfico de barras horizontal
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=status_counts['Quantidade'],
        y=status_counts['Status'],
        orientation='h',
        text=status_counts['Quantidade'],
        textposition='auto',
        marker=dict(color='lightblue')  # Azul claro
    ))

    fig.update_layout(
        title="📊 Status dos RNCs",
        xaxis_title="Quantidade de RNCs",
        yaxis_title="Status",
        template="plotly_dark",
        height=300  # Gráfico pequeno
    )

    st.plotly_chart(fig, use_container_width=True)

# Gráfico de tendência por mês (Visão Geral)
def grafico_rncs_abertos(df_filtrado):
    df_mes = df_filtrado.groupby(['Mês_Num', 'Mês']).size().reset_index(name='count')

    meses_ordenados = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df_mes['Mês'] = pd.Categorical(df_mes['Mês'], categories=meses_ordenados, ordered=True)
    df_mes = df_mes.sort_values('Mês')

    fig = go.Figure()

    # Linha de RNCs
    fig.add_trace(go.Scatter(
        x=df_mes['Mês'],
        y=df_mes['count'],
        mode='lines+markers+text',
        text=df_mes['count'],
        textposition='top center',
        line=dict(color='lightblue'),  # Azul claro
        marker=dict(size=8),
        name="RNCs por Mês"
    ))

    # Linha de tendência
    x = df_mes['Mês_Num']
    y = df_mes['count']
    coef = np.polyfit(x, y, 1)
    poly1d_fn = np.poly1d(coef)

    fig.add_trace(go.Scatter(
        x=df_mes['Mês'],
        y=poly1d_fn(x),
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Tendência'
    ))

    # Exibir o número total de RNCs
    total_rncs = df_mes['count'].sum()

    fig.update_layout(
        title=f'📈 RNCs Abertos por Mês  |  Total: {total_rncs}',
        xaxis_title='Mês',
        yaxis_title='Quantidade de RNCs',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

# Gráfico mensal por setor (Indicadores)
def numero_rncs_por_setor(df_filtrado):
    setores_interesse = ['FORNECEDOR', 'CALDEIRARIA', 'ENGENHARIA', 'PCP', 'PREPARAÇÃO']
    df_setor = df_filtrado[df_filtrado['Setor responsável'].isin(setores_interesse)]
    df_agrupado = df_setor.groupby(['Mês', 'Setor responsável']).size().reset_index(name='count')

    meses_ordenados = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df_agrupado['Mês'] = pd.Categorical(df_agrupado['Mês'], categories=meses_ordenados, ordered=True)
    df_agrupado = df_agrupado.sort_values('Mês')

    fig = go.Figure()

    for setor in setores_interesse:
        df_setor_mes = df_agrupado[df_agrupado['Setor responsável'] == setor]
        fig.add_trace(go.Bar(
            x=df_setor_mes['Mês'],
            y=df_setor_mes['count'],
            name=setor,
            text=df_setor_mes['count'],
            textposition='outside'
        ))

    fig.update_layout(
        title='📊 Número de RNCs por Principal Setor Responsável',
        xaxis_title='Mês',
        yaxis_title='Quantidade de RNCs',
        barmode='group',
        template='plotly_dark',
        legend_title="Setores"
    )

    st.plotly_chart(fig, use_container_width=True)

# NOVO GRÁFICO GERAL POR SETOR (horizontal)
def rncs_por_setor_geral(df_filtrado):
    df_setor = df_filtrado['Setor responsável'].value_counts().reset_index()
    df_setor.columns = ['Setor responsável', 'Quantidade']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_setor['Quantidade'],
        y=df_setor['Setor responsável'],
        orientation='h',
        text=df_setor['Quantidade'],
        textposition='auto',
        marker=dict(color='lightblue')  # Azul claro
    ))

    fig.update_layout(
        title='📊 Número de RNCs Abertos por Setor Responsável',
        xaxis_title='Quantidade de RNCs',
        yaxis_title='Setores',
        template='plotly_dark',
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

# Função principal
def main():
    st.set_page_config(page_title="Dashboard RNC 2025", layout="wide")
    st.title("📊 Controle de Números de RNC's - Dashboard 2025")

    caminho_excel = r"P:\00. SGT Docs\07 - Controle de RNCs\2025\01 - Controle de RNCs - CSC\Controle de Número de RNC's.xlsx"
    df = load_data(caminho_excel)

    # Filtros na barra lateral
    st.sidebar.header("🧯 Filtros")

    setor_opcoes = df['Setor responsável'].dropna().unique().tolist()
    status_opcoes = df['Status'].dropna().unique().tolist()
    mes_opcoes = df['Mês'].dropna().unique().tolist()

    setor_filtrado = st.sidebar.multiselect("Setor responsável", sorted(setor_opcoes), default=sorted(setor_opcoes))
    status_filtrado = st.sidebar.multiselect("Status", sorted(status_opcoes), default=sorted(status_opcoes))
    mes_filtrado = st.sidebar.multiselect("Mês", sorted(mes_opcoes, key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x)), default=sorted(mes_opcoes, key=lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x)))

    # Aplicar todos os filtros
    df_filtrado = df[
        (df['Setor responsável'].isin(setor_filtrado)) & 
        (df['Status'].isin(status_filtrado)) & 
        (df['Mês'].isin(mes_filtrado))
    ]

    # Navegação entre abas
    menu = st.sidebar.radio("Escolha uma visualização:", ("Visão Geral", "Indicadores"))

    if menu == "Visão Geral":
        # Exibir o gráfico pequeno de status
        grafico_status_rncs(df_filtrado)

        grafico_rncs_abertos(df_filtrado)
        st.subheader("📋 Tabela de RNCs")
        st.dataframe(df_filtrado, use_container_width=True)

    elif menu == "Indicadores":
        numero_rncs_por_setor(df_filtrado)
        st.markdown("---")
        rncs_por_setor_geral(df_filtrado)

if __name__ == "__main__":
    main()
