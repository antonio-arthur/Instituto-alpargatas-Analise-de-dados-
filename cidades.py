# arthur_app_streamlit.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from arthur_indicador import carregar_ideb_pop

# ==============================
# Lista de cidades destacadas
# ==============================
cidades_destacadas = [
    "ALAGOA NOVA", "BAÍA DA TRAIÇÃO", "BANANEIRAS", "CABACEIRAS",
    "CAMPINA GRANDE", "CATURITÉ", "GUARABIRA", "INGÁ", "ITATUBA",
    "JOÃO PESSOA", "LAGOA SECA", "MOGEIRO", "QUEIMADAS",
    "SANTA RITA", "SERRA REDONDA"
]

# ==============================
# Carregar dados direto (sem upload)
# ==============================
@st.cache_data(show_spinner="Carregando dados IDEB e População...")
def carregar_dados():
    df = carregar_ideb_pop(
        caminho_ideb="tabelas/divulgacao_anos_iniciais_municipios_2023.xlsx",
        caminho_pop="tabelas/POP2020_20220905(Municípios).csv",
        filtro_rede="municipal"
    )
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")

    # Padronizar nomes de colunas
    df.columns = (
        df.columns.str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("Á", "A")
        .str.replace("Í", "I")
        .str.replace("É", "E")
    )
    return df

df = carregar_dados()

# Mostrar colunas disponíveis (debug)
st.write("🔎 Colunas no DataFrame:", df.columns.tolist())

# ==============================
# Função comparativa com população ±10%
# ==============================
def comparar_municipio(df, municipio, uf="PB", coluna="MEDIA_IDEB"):
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")

    # Filtrar município selecionado
    df_mun = df[(df["MUNICIPIO"] == municipio) & (df["SG_UF"] == uf)]

    if df_mun.empty:
        return None, None, None, pd.DataFrame()

    valor_mun = df_mun[coluna].squeeze()
    pop_mun = df_mun["POPULACAO_ESTIMADA"].squeeze()

    # Intervalo populacional ±10%
    limite_inferior = pop_mun * 0.9
    limite_superior = pop_mun * 1.1

    # Similares na PB por população ±10% (excluindo o próprio município)
    df_similares = df[
        (df["SG_UF"] == uf) &
        (df["MUNICIPIO"] != municipio) &
        (df["POPULACAO_ESTIMADA"] >= limite_inferior) &
        (df["POPULACAO_ESTIMADA"] <= limite_superior)
    ].copy()

    media_similares = df_similares[coluna].mean() if not df_similares.empty else 0

    # Médias regionais/nacional
    ufs_nordeste = ["AL","BA","CE","MA","PB","PE","PI","RN","SE"]
    media_nordeste = df.loc[df["SG_UF"].isin(ufs_nordeste), coluna].mean()
    media_brasil = df[coluna].mean()

    return valor_mun, media_nordeste, media_brasil, df_similares

# ==============================
# App Streamlit
# ==============================
st.title("📊 Comparativo IDEB - Municípios PB")

municipio = st.selectbox("Selecione o município:", cidades_destacadas)

if municipio:
    valor_mun, media_nordeste, media_brasil, similares = comparar_municipio(df, municipio)

    st.subheader("📈 Gráfico Comparativo")

    df_comparacao = pd.DataFrame({
        'MUNICIPIO': [f'{municipio} (PB)', 'SIMILARES (±10%)', 'NORDESTE', 'BRASIL'],
        'MEDIA_IDEB': [
            valor_mun,
            similares["MEDIA_IDEB"].mean() if not similares.empty else 0,
            media_nordeste,
            media_brasil
        ]
    })

    cores = ['red', 'gray', 'blue', 'green']
    fig, ax = plt.subplots(figsize=(8, 5))
    barras = ax.barh(df_comparacao['MUNICIPIO'], df_comparacao['MEDIA_IDEB'], color=cores)
    ax.set_xlabel("Média IDEB (2021–2023)")
    ax.set_title(f"Comparação IDEB: {municipio} vs Similares, Nordeste e Brasil")

    # Adicionar valores ao lado das barras
    for barra in barras:
        largura = barra.get_width()
        ax.text(largura + 0.02,
                barra.get_y() + barra.get_height()/2,
                f"{largura:.2f}",
                va='center', ha='left', fontsize=10, fontweight='bold')

    plt.tight_layout()
    st.pyplot(fig)

    # ==============================
    # Mostrar tabela de municípios similares
    # ==============================
    if not similares.empty:
        st.subheader(f"🏘 Municípios similares (±10% população) na PB")
        st.dataframe(similares[['MUNICIPIO', 'POPULACAO_ESTIMADA', 'MEDIA_IDEB']].sort_values(by='MEDIA_IDEB', ascending=False))
    else:
        st.write("Nenhum município similar encontrado dentro da faixa populacional ±10%.")
