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
# Função comparativa
# ==============================
def comparar_municipio(df, municipio, uf="PB", coluna="MEDIA_IDEB"):
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    df_filtrado = df[df["MUNICIPIO"].isin(cidades_destacadas)]

    # Nota município
    valor_mun = df_filtrado.loc[
        (df_filtrado["MUNICIPIO"] == municipio) & (df_filtrado["SG_UF"] == uf),
        coluna
    ].mean()

    # Médias regionais/nacional
    ufs_nordeste = ["AL","BA","CE","MA","PB","PE","PI","RN","SE"]
    media_nordeste = df.loc[df["SG_UF"].isin(ufs_nordeste), coluna].mean()
    media_brasil = df[coluna].mean()

    # Outras cidades destacadas (similares ±10%)
    similares = df_filtrado[(df_filtrado["MUNICIPIO"] != municipio) & (df_filtrado["SG_UF"] == uf)]
    similares = similares[(similares[coluna] >= valor_mun * 0.9) & (similares[coluna] <= valor_mun * 1.1)]

    return valor_mun, media_nordeste, media_brasil, similares

# ==============================
# App Streamlit
# ==============================
st.title("📊 Comparativo IDEB - Municípios PB")

municipio = st.selectbox("Selecione o município:", cidades_destacadas)

if municipio:
    valor_mun, media_nordeste, media_brasil, similares = comparar_municipio(df, municipio)

    st.subheader("📈 Gráfico Comparativo")

    # Resumo para o gráfico
    resumo = pd.DataFrame({
        "Categoria": [
            f"{municipio} (PB)",
            "SIMILARES (±10%)",
            "NORDESTE",
            "BRASIL"
        ],
        "MEDIA_IDEB": [
            valor_mun,
            similares["MEDIA_IDEB"].mean() if not similares.empty else 0,
            media_nordeste,
            media_brasil
        ]
    })

    # Definir cores
    cores = {
        "BRASIL": "green",
        "NORDESTE": "blue",
        "SIMILARES (±10%)": "gray",
        f"{municipio} (PB)": "red"
    }
    resumo["Cor"] = resumo["Categoria"].map(cores)

    # Plot horizontal
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(resumo["Categoria"], resumo["MEDIA_IDEB"], color=resumo["Cor"])

    # Adicionar valores ao lado
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.05, bar.get_y() + bar.get_height()/2,
                f"{width:.2f}", va="center", fontsize=10, fontweight="bold")

    ax.set_xlabel("Média IDEB (2021–2023)")
    ax.set_title(f"Comparação IDEB: {municipio} vs Similares, Nordeste e Brasil")
    plt.tight_layout()
    st.pyplot(fig)
