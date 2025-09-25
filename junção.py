# app_ideb_unificado.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path
from itertools import cycle, islice
import unicodedata, re

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(page_title="IDEB — Unificado", page_icon="📊", layout="wide")

# ==============================
# PARÂMETROS / PASTAS
# ==============================
CSV_INSTITUTO = Path("database/ideb_municipios_instituto_por_id.csv")
LOGO_LOCAL = Path("static/logo.png")
LOGO_ALT = Path("/mnt/data/logo.png")
CSV_PB = Path("tabelas/divulgacao_anos_iniciais_municipios_2023.xlsx")
POP_PB = Path("tabelas/POP2020_20220905(Municípios).csv")

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def norm_text(s):
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', s).strip().upper()

def make_colors(base_palette, n):
    if not base_palette:
        return []
    if len(base_palette) >= n:
        return base_palette[:n]
    return list(islice(cycle(base_palette), n))

def find_col_like(dfcols, patterns):
    lc = {c.lower(): c for c in dfcols}
    for pat in patterns:
        rx = re.compile(pat, flags=re.I)
        for k, orig in lc.items():
            if rx.search(k):
                return orig
    return None

# ==============================
# TAB 2: PB / Comparativo ±10%
# ==============================
@st.cache_data(show_spinner="Carregando dados PB...")
def carregar_dados_pb():
    from arthur_indicador import carregar_ideb_pop
    df = carregar_ideb_pop(str(CSV_PB), str(POP_PB), filtro_rede="municipal")
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")
    df.columns = (df.columns.str.strip()
                  .str.upper()
                  .str.replace(" ", "_")
                  .str.replace("Á","A")
                  .str.replace("Í","I")
                  .str.replace("É","E"))
    return df

def comparar_municipio(df, municipio, uf="PB", coluna="MEDIA_IDEB"):
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df["POPULACAO_ESTIMADA"] = pd.to_numeric(df["POPULACAO_ESTIMADA"], errors="coerce")
    df_mun = df[(df["MUNICIPIO"] == municipio) & (df["SG_UF"] == uf)]
    if df_mun.empty:
        return None, None, None, pd.DataFrame()
    valor_mun = df_mun[coluna].squeeze()
    pop_mun = df_mun["POPULACAO_ESTIMADA"].squeeze()
    limite_inferior = pop_mun * 0.9
    limite_superior = pop_mun * 1.1
    df_similares = df[(df["SG_UF"]==uf) &
                      (df["MUNICIPIO"] != municipio) &
                      (df["POPULACAO_ESTIMADA"]>=limite_inferior) &
                      (df["POPULACAO_ESTIMADA"]<=limite_superior)].copy()
    ufs_nordeste = ["AL","BA","CE","MA","PB","PE","PI","RN","SE"]
    media_nordeste = df.loc[df["SG_UF"].isin(ufs_nordeste), coluna].mean()
    media_brasil = df[coluna].mean()
    return valor_mun, media_nordeste, media_brasil, df_similares

# ==============================
# LER CSV INSTITUTO
# ==============================
if not CSV_INSTITUTO.exists():
    st.warning(f"Arquivo CSV do Instituto não encontrado: {CSV_INSTITUTO}")
    df_instituto, year_cols = pd.DataFrame(), []
else:
    df_instituto = pd.read_csv(CSV_INSTITUTO)
    if "ds_mun" not in df_instituto.columns:
        st.error(f"Coluna 'ds_mun' não encontrada no CSV do Instituto. Colunas: {df_instituto.columns.tolist()}")
        df_instituto, year_cols = pd.DataFrame(), []
    else:
        year_cols = [c for c in df_instituto.columns if str(c).isdigit()]
        year_cols = sorted(year_cols, key=lambda x:int(x))
        for y in year_cols:
            df_instituto[y] = pd.to_numeric(df_instituto[y], errors="coerce")

# ==============================
# LISTA DE MUNICÍPIOS DESTAQUE PB
# ==============================
cidades_destacadas = [
    "ALAGOA NOVA","BAIA DA TRAICAO","BANANEIRAS","CABACEIRAS","CAMPINA GRANDE",
    "CATURITE","GUARABIRA","INGA","ITATUBA","JOAO PESSOA","LAGOA SECA","MOGEIRO",
    "QUEIMADAS","SANTA RITA","SERRA REDONDA"
]

# ==============================
# CONFIGURAÇÕES CSS LEVES
# ==============================
st.markdown("""
<style>
.header-title { font-size:26px; font-weight:700; margin:0; }
.header-sub { color: #6b7280; margin-top:4px; margin-bottom:6px; }
.metric-card { padding:6px 10px; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# ==============================
# ABAS UNIFICADAS
# ==============================
tabs = st.tabs(["🏢 Instituto Alpargatas", "🏘 PB — Comparativo Municípios", "🗺️ Mapa da PB"])

# ==============================
# TAB 1 — INSTITUTO ALPARGATAS
# ==============================
with tabs[0]:
    st.subheader("IDEB — Municípios do Instituto Alpargatas")
    cols = st.columns([1,4,1])
    with cols[0]:
        LOGO = LOGO_LOCAL if LOGO_LOCAL.exists() else (LOGO_ALT if LOGO_ALT.exists() else None)
        if LOGO:
            st.image(str(LOGO), width=110)
    with cols[1]:
        st.markdown('<p class="header-title">IDEB — Municípios do Instituto Alpargatas</p>', unsafe_allow_html=True)
        st.markdown('<p class="header-sub">Visualizações: evolução, ranking e crescimento do IDEB</p>', unsafe_allow_html=True)
    with cols[2]:
        if not df_instituto.empty:
            n_munis = df_instituto['ds_mun'].nunique()
            ultimo_ano = year_cols[-1]
            ideb_medio_ult = df_instituto[ultimo_ano].mean(skipna=True)
            st.markdown(f'<div class="metric-card">🔢 <b>Municípios (IA)</b><div>{n_munis}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card">📅 <b>Último ano</b><div>{ultimo_ano}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card">📈 <b>IDEB médio ({ultimo_ano})</b><div>{ideb_medio_ult:.2f}</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    st.sidebar.header("Opções Instituto")
    palette_choice = st.sidebar.selectbox("Paleta de cores", ["Colorida (Plotly)","D3 (vibrante)","Pastel (Set3)"])
    exclude_sp = st.sidebar.checkbox("Excluir São Paulo (por nome)", value=False)
    default_topn = st.sidebar.slider("Top N padrão", 5, 30, 15)
    color_palettes = {
        "Colorida (Plotly)": px.colors.qualitative.Plotly,
        "D3 (vibrante)": px.colors.qualitative.D3,
        "Pastel (Set3)": px.colors.qualitative.Set3 if hasattr(px.colors.qualitative,"Set3") else px.colors.qualitative.Pastel
    }
    base_pal = color_palettes.get(palette_choice, px.colors.qualitative.Plotly)

    df_work = df_instituto.copy()
    if exclude_sp:
        mask_sp = df_work['ds_mun'].astype(str).str.upper().str.contains(r"\bSAO PAULO\b|\bSÃO PAULO\b")
        df_work = df_work[~mask_sp].copy()

    tab1_tabs = st.tabs(["📈 Evolução por Município","🏆 Ranking (Top N)","📊 Crescimento (Δ)","📉 IDEB Médio"])

    # ---------------- Evolução
    with tab1_tabs[0]:
        st.subheader("📈 Evolução IDEB por Município")
        municipio_sel = st.selectbox("Escolha o município:", sorted(df_work['ds_mun'].unique()))
        if municipio_sel:
            df_m = df_work[df_work['ds_mun'] == municipio_sel]
            df_long = df_m.melt(id_vars='ds_mun', value_vars=year_cols,
                                var_name="Ano", value_name="IDEB")
            fig = px.line(df_long, x="Ano", y="IDEB", color="ds_mun",
                          title=f"Evolução IDEB — {municipio_sel}",
                          markers=True)
            fig.update_layout(yaxis=dict(title="IDEB"), xaxis=dict(title="Ano"))
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- Ranking
    with tab1_tabs[1]:
        st.subheader(f"🏆 Ranking — Top {default_topn}")
        ultimo_ano = year_cols[-1]
        df_rank = df_work[['ds_mun', ultimo_ano]].dropna().sort_values(by=ultimo_ano, ascending=False)
        df_rank = df_rank.head(default_topn)
        fig = px.bar(df_rank, x=ultimo_ano, y="ds_mun", orientation="h",
                     text=ultimo_ano, color="ds_mun", color_discrete_sequence=make_colors(base_pal, len(df_rank)))
        fig.update_layout(xaxis_title="IDEB", yaxis_title="Município")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Crescimento Δ
    with tab1_tabs[2]:
        st.subheader("📊 Crescimento (Δ)")
        df_growth = df_work[['ds_mun', year_cols[0], year_cols[-1]]].dropna()
        df_growth['Delta'] = df_growth[year_cols[-1]] - df_growth[year_cols[0]]
        df_growth = df_growth.sort_values(by='Delta', ascending=False).head(default_topn)
        fig = px.bar(df_growth, x='Delta', y='ds_mun', orientation="h",
                     text='Delta', color="ds_mun", color_discrete_sequence=make_colors(base_pal, len(df_growth)))
        fig.update_layout(xaxis_title="Δ IDEB", yaxis_title="Município")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- IDEB Médio
    with tab1_tabs[3]:
        st.subheader("📉 IDEB Médio por Ano")
        df_mean = df_work[year_cols].mean(skipna=True).reset_index()
        df_mean.columns = ['Ano','IDEB médio']
        fig = px.line(df_mean, x="Ano", y="IDEB médio", markers=True,
                      title="IDEB Médio dos Municípios do Instituto")
        st.plotly_chart(fig, use_container_width=True)

# ==============================
# TAB 2 — PB COMPARATIVO (INTERATIVO)
# ==============================
with tabs[1]:
    st.subheader("📊 Comparativo IDEB — Municípios PB")
    df_pb = carregar_dados_pb()

    municipio = st.selectbox("Selecione o município:", cidades_destacadas)

    if municipio:
        valor_mun, media_nordeste, media_brasil, similares = comparar_municipio(df_pb, municipio)

        df_comparacao = pd.DataFrame({
            'MUNICIPIO': [
                f'{municipio} (PB)',
                'SIMILARES (±10%)',
                'NORDESTE',
                'BRASIL'
            ],
            'MEDIA_IDEB': [
                valor_mun,
                similares["MEDIA_IDEB"].mean() if not similares.empty else 0,
                media_nordeste,
                media_brasil
            ],
            'Grupo': [
                "Selecionado",
                "Similares",
                "Nordeste",
                "Brasil"
            ]
        })

        cores = {
            "Selecionado": "red",
            "Similares": "gray",
            "Nordeste": "blue",
            "Brasil": "green"
        }

        fig = px.bar(
            df_comparacao,
            x="MEDIA_IDEB",
            y="MUNICIPIO",
            orientation="h",
            color="Grupo",
            color_discrete_map=cores,
            text="MEDIA_IDEB"
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition="outside")
        fig.update_layout(
            title=f"Comparação IDEB: {municipio} vs Similares, Nordeste e Brasil",
            xaxis_title="Média IDEB (2021–2023)",
            yaxis_title="",
            bargap=0.4,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela de similares
        if not similares.empty:
            st.subheader(f"🏘 Municípios similares (±10% população) na PB")
            st.dataframe(
                similares[['MUNICIPIO', 'POPULACAO_ESTIMADA', 'MEDIA_IDEB']]
                .sort_values(by='MEDIA_IDEB', ascending=False)
            )
        else:
            st.info("Nenhum município similar encontrado dentro da faixa populacional ±10%.")
            
with tabs[2]:
    st.subheader("🗺️ Mapa do IDEB — Municípios da Paraíba (Rede Pública, Fundamental)")

    csv_path = Path("database/br_inep_ideb_municipio_filtrado.csv")
    geo_path = Path("geo/pb_municipios.json")

    if not csv_path.exists():
        st.error(f"CSV não encontrado: {csv_path}")
    elif not geo_path.exists():
        st.error(f"GeoJSON não encontrado: {geo_path}")
    else:
        # ------------------ Carregar dados ------------------
        df = pd.read_csv(csv_path)
        df = df[(df["rede"].str.lower() == "publica") & (df["ensino"].str.lower() == "fundamental")]

        # Cidades atendidas pelo projeto
        cidades_projeto = [
            "Alagoa Nova", "Bananeiras", "Baía da Traição", "Cabaceiras",
            "Campina Grande", "Carpina", "Caturité", "Guarabira", "Ingá",
            "Itatuba", "João Pessoa", "Lagoa Seca", "Mogeiro", "Montes Claros",
            "Queimadas", "Santa Rita", "Serra Redonda"
        ]

        # Filtro de cidades
        filtro_modo = st.radio(
            "Exibir dados de:",
            ["Todas as cidades", "Apenas cidades atendidas pelo projeto"],
            index=0,
            key="filtro_mapa"
        )
        if filtro_modo != "Todas as cidades":
            df = df[df["nome"].isin(cidades_projeto)]

        # Seleção de ano
        anos = sorted(df["ano"].unique())
        ano_sel = st.selectbox("Selecione o ano:", anos, index=len(anos)-1, key="ano_mapa")
        df_temp = df.query("ano == @ano_sel")

        # ------------------ Calcular métricas ------------------
        df_mun = (
            df_temp.groupby("nome")["ideb"]
            .agg(
                ideb_media="mean",
                ideb_mediana="median",
                ideb_desvio="std",
                perc_acima5=lambda x: (x >= 5).mean() * 100,
            )
            .reset_index()
            .round({"ideb_media": 3, "ideb_mediana": 3, "ideb_desvio": 3, "perc_acima5": 1})
            .fillna({"ideb_desvio": 0})
        )

        # ------------------ Carregar GeoJSON ------------------
        import json
        from plotly import graph_objects as go

        with open(geo_path, "r", encoding="utf-8") as f:
            geojson_pb = json.load(f)

        df_geo = pd.DataFrame({"nome": [f["properties"]["name"] for f in geojson_pb["features"]]})
        df_map = df_geo.merge(df_mun, on="nome", how="left")
        df_com_dado, df_sem_dado = df_map.dropna(subset=["ideb_media"]), df_map[df_map["ideb_media"].isna()]

        # ------------------ Plotar mapa ------------------
        ideb_min, ideb_max = 1.8, 6
        fig = go.Figure()

        def add_choropleth(data, z, colorscale, name, **kwargs):
            fig.add_trace(go.Choropleth(
                geojson=geojson_pb,
                locations=data["nome"],
                z=z,
                featureidkey="properties.name",
                colorscale=colorscale,
                name=name,
                **kwargs
            ))

        if not df_sem_dado.empty:
            add_choropleth(
                df_sem_dado, [0]*len(df_sem_dado),
                [[0, "lightgrey"], [1, "lightgrey"]],
                "Sem dado",
                showscale=False,
                hoverinfo="location"
            )

        if not df_com_dado.empty:
            add_choropleth(
                df_com_dado, df_com_dado["ideb_media"],
                "YlGnBu", "Com dado",
                zmin=ideb_min, zmax=ideb_max,
                colorbar_title="IDEB (média)",
                marker_line_width=0.5,
                marker_line_color="black",
                hovertemplate="<b>%{location}</b><br>" +
                              "Média: %{z:.2f}<br>" +
                              "Mediana: %{customdata[0]:.2f}<br>" +
                              "Desvio: %{customdata[1]:.2f}<br>" +
                              "≥5.0: %{customdata[2]:.1f}%<extra></extra>",
                customdata=df_com_dado[["ideb_mediana", "ideb_desvio", "perc_acima5"]].values
            )

        fig.update_layout(
            geo=dict(fitbounds="locations", visible=False),
            height=650,
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title=f"IDEB (Rede Pública - Fundamental) — {ano_sel} ({filtro_modo})",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------------ Mostrar tabela ------------------
        st.dataframe(df_map.sort_values("ideb_media", ascending=False).reset_index(drop=True))













