# arthur_app_streamlit.py
import streamlit as st
import pandas as pd
import plotly.express as px

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

# ==============================
# Função comparativa
# ==============================
def comparar_municipio(df, municipio, uf="PB", coluna="MEDIA_IDEB", intervalo=0.1):
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")

    df_filtrado = df[df["MUNICIPIO"].isin(cidades_destacadas)]

    # Nota município
    valor_mun = df_filtrado.loc[
        (df_filtrado["MUNICIPIO"] == municipio) & (df_filtrado["SG_UF"] == uf),
        coluna
    ].mean()

    # População do município
    pop_mun = df_filtrado.loc[
        (df_filtrado["MUNICIPIO"] == municipio) & (df_filtrado["SG_UF"] == uf),
        "POPULACAO_ESTIMADA"
    ].mean()

    # Médias regionais/nacional
    ufs_nordeste = ["AL","BA","CE","MA","PB","PE","PI","RN","SE"]
    media_nordeste = df.loc[df["SG_UF"].isin(ufs_nordeste), coluna].mean()
    media_brasil = df[coluna].mean()

    # Intervalo de população
    limite_inferior = pop_mun * (1 - intervalo)
    limite_superior = pop_mun * (1 + intervalo)

    similares = df_filtrado[
        (df_filtrado["MUNICIPIO"] != municipio) &
        (df_filtrado["SG_UF"] == uf) &
        (df_filtrado["POPULACAO_ESTIMADA"].between(limite_inferior, limite_superior))
    ]

    return valor_mun, media_nordeste, media_brasil, similares, pop_mun, limite_inferior, limite_superior

# ==============================
# App Streamlit
# ==============================
st.title("📊 Comparativo IDEB - Municípios PB")

municipio = st.selectbox("Selecione o município:", cidades_destacadas)

# Slider para ajustar intervalo de população
intervalo = st.slider("Defina o intervalo de população (±%)", 5, 50, 10) / 100

if municipio:
    valor_mun, media_nordeste, media_brasil, similares, pop_mun, li, ls = comparar_municipio(df, municipio, intervalo=intervalo)

    st.subheader("📈 Gráfico Comparativo")

    # Resumo para o gráfico
    resumo = pd.DataFrame({
        "Categoria": [
            f"{municipio} (PB)",
            "SIMILARES (±população)",
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
        "SIMILARES (±população)": "gray",
        f"{municipio} (PB)": "red"
    }
    resumo["Cor"] = resumo["Categoria"].map(cores)

    # Gráfico interativo
    fig = px.bar(
        resumo,
        x="MEDIA_IDEB",
        y="Categoria",
        orientation="h",
        color="Categoria",
        color_discrete_map=cores,
        text="MEDIA_IDEB"
    )

    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        xaxis_title="Média IDEB (2021–2023)",
        yaxis_title="",
        title=f"Comparação IDEB: {municipio} vs Similares, Nordeste e Brasil",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostrar dados de debug
    with st.expander("🔍 Detalhes do cálculo"):
        st.write(f"📊 População {municipio}: {pop_mun:.0f}")
        st.write(f"🔎 Intervalo: {li:.0f} - {ls:.0f}")
        st.write(f"Encontrados: {len(similares)} similares")

    # Extra: mostrar municípios similares
    if not similares.empty:
        st.subheader("🏘️ Municípios similares")
        st.dataframe(similares[["MUNICIPIO", "SG_UF", "POPULACAO_ESTIMADA", "MEDIA_IDEB"]])
