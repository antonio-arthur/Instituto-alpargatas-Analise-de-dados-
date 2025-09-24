# app_ideb_munis_styled_with_logo.py
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import re
from itertools import cycle, islice

# ====== Configuração da página ======
st.set_page_config(page_title="IDEB — Instituto Alpargatas", page_icon="📊", layout="wide")

# ====== Parâmetros / caminho do CSV e logo ======
CSV_PATH = Path("database/ideb_municipios_instituto_por_id.csv")  # ajuste se necessário
LOGO_LOCAL = Path("static/logo.png")             # preferencial: adicione static/logo.png no repo
LOGO_ALT = Path("/mnt/data/logo.png")            # fallback: ambiente do notebook já contém essa imagem

# ====== Estilos leves via CSS ======
st.markdown(
    """
    <style>
      .header-title { font-size:26px; font-weight:700; margin:0; }
      .header-sub { color: #6b7280; margin-top:4px; margin-bottom:6px; }
      .metric-card { padding:6px 10px; border-radius:8px; }
    </style>
    """, unsafe_allow_html=True
)

# ====== Leitura simples do CSV (falha rápido se não existir) ======
if not CSV_PATH.exists():
    st.error(f"Arquivo não encontrado: {CSV_PATH}. Coloque o CSV no diretório do app.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# ====== Verificações mínimas ======
if "ds_mun" not in df.columns:
    st.error("Coluna 'ds_mun' não encontrada no CSV. Renomeie a coluna ou ajuste o arquivo.")
    st.write("Colunas disponíveis:", df.columns.tolist())
    st.stop()

# detectar colunas de ano como strings (ex.: '2005','2007',...)
year_cols = [c for c in df.columns if str(c).isdigit()]
if not year_cols:
    st.error("Não foram detectadas colunas-ano (ex.: '2005','2007'). Verifique o CSV.")
    st.stop()
year_cols = sorted(year_cols, key=lambda x: int(x))

# garantir numericidade das colunas de ano
for y in year_cols:
    df[y] = pd.to_numeric(df[y], errors="coerce")

# ====== Header: logo + título + métricas ======
cols = st.columns([1, 4, 1])
with cols[0]:
    # escolhe logo: prioridade static/logo.png; senão fallback para /mnt/data/logo.png se existir
    LOGO = LOGO_LOCAL if LOGO_LOCAL.exists() else (LOGO_ALT if LOGO_ALT.exists() else None)
    if LOGO:
        st.image(str(LOGO), width=110)
with cols[1]:
    st.markdown('<p class="header-title">IDEB — Municípios do Instituto Alpargatas</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Visualizações: evolução, ranking e crescimento do IDEB</p>', unsafe_allow_html=True)
with cols[2]:
    n_munis = df['ds_mun'].nunique()
    ultimo_ano = year_cols[-1]
    ideb_medio_ult = df[ultimo_ano].mean(skipna=True)
    st.markdown(f'<div class="metric-card">🔢 <b>Municípios (IA)</b><div>{n_munis}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card">📅 <b>Último ano</b><div>{ultimo_ano}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card">📈 <b>IDEB médio ({ultimo_ano})</b><div>{ideb_medio_ult:.2f}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ====== Sidebar controls: palette, exclude São Paulo, topN defaults ======
st.sidebar.header("Opções")
palette_choice = st.sidebar.selectbox("Paleta de cores", ["Colorida (Plotly)", "D3 (vibrante)", "Pastel (Set3)"])
exclude_sp = st.sidebar.checkbox("Excluir São Paulo (por nome)", value=False)
default_topn = st.sidebar.slider("Top N padrão", min_value=5, max_value=30, value=15)

# ====== Função utilitária: expande paleta para N cores ======
def make_colors(base_palette, n):
    """Retorna lista de n cores, repetindo a paleta base se necessário."""
    if not base_palette:
        return []
    if len(base_palette) >= n:
        return base_palette[:n]
    # repete o ciclo da paleta até alcançar n
    return list(islice(cycle(base_palette), n))

# definir paletas base mais coloridas
color_palettes = {
    "Colorida (Plotly)": px.colors.qualitative.Plotly,
    "D3 (vibrante)": px.colors.qualitative.D3,
    "Pastel (Set3)": px.colors.qualitative.Set3 if hasattr(px.colors.qualitative, "Set3") else px.colors.qualitative.Pastel
}

base_pal = color_palettes.get(palette_choice, px.colors.qualitative.Plotly)

# ====== aplicar exclusão São Paulo se desejado ======
df_work = df.copy()
if exclude_sp:
    mask_sp = df_work['ds_mun'].astype(str).str.upper().str.contains(r"\bSAO PAULO\b|\bSÃO PAULO\b")
    df_work = df_work[~mask_sp].copy()

# ====== Tabs ======
tabs = st.tabs(["📈 Evolução por Município", "🏆 Ranking (Top N)", "📊 Crescimento (Δ)", "📉 IDEB Médio"])

# -------- Tab 1: Evolução por Município (cada município com cor distinta) --------
with tabs[0]:
    st.subheader("Evolução do IDEB — selecione municípios")
    mun_options = sorted(df_work['ds_mun'].dropna().unique().tolist())
    default_sel = mun_options[:6] if len(mun_options) > 6 else mun_options
    selected = st.multiselect("Municípios (opcional — deixe vazio para todos):", mun_options, default=default_sel)

    if selected:
        df_sel = df_work[df_work['ds_mun'].isin(selected)].copy()
    else:
        df_sel = df_work.copy()

    dfm = df_sel.melt(id_vars=["ds_mun"], value_vars=year_cols, var_name="year", value_name="ideb").dropna(subset=["ideb"])
    if dfm.empty:
        st.info("Sem dados para os municípios selecionados.")
    else:
        dfm["year_int"] = dfm["year"].astype(int)
        # construir sequência de cores suficiente para o número de municípios
        n_munis_sel = df_sel['ds_mun'].nunique()
        color_sequence = make_colors(base_pal, max(8, n_munis_sel))  # garante ao menos 8 cores
        fig = px.line(dfm, x="year_int", y="ideb", color="ds_mun", markers=True,
                      labels={"year_int":"Ano", "ideb":"IDEB", "ds_mun":"Município"},
                      title="Evolução do IDEB — municípios selecionados",
                      color_discrete_sequence=color_sequence)
        fig.update_xaxes(tickmode="array", tickvals=[int(y) for y in year_cols])
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_sel[["ds_mun"] + year_cols].reset_index(drop=True))
        st.download_button("Baixar dados filtrados (CSV)", df_sel[["ds_mun"] + year_cols].to_csv(index=False).encode("utf-8"),
                           file_name="ideb_municipios_filtrados.csv", mime="text/csv")

# -------- Tab 2: Top N por nota --------
with tabs[1]:
    st.subheader("Ranking — Top N por IDEB em um ano")
    top_n = st.number_input("Top N (quantos mostrar)", min_value=3, max_value=50, value=default_topn, step=1)
    ano_rank = st.selectbox("Ano para ranking", options=year_cols, index=len(year_cols)-1)

    dfr = df_work[["ds_mun", ano_rank]].copy()
    dfr[ano_rank] = pd.to_numeric(dfr[ano_rank], errors="coerce")
    dfr = dfr.dropna(subset=[ano_rank]).sort_values(by=ano_rank, ascending=False).head(int(top_n))

    if dfr.empty:
        st.info("Sem dados para o ano selecionado.")
    else:
        # cores para barras (repete se necessário)
        colors_bar = make_colors(base_pal, len(dfr))
        fig_rank = px.bar(dfr, x=ano_rank, y="ds_mun", orientation="h",
                          labels={ano_rank:"IDEB", "ds_mun":"Município"},
                          title=f"Top {len(dfr)} — IDEB {ano_rank}",
                          color_discrete_sequence=colors_bar)
        fig_rank.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
        st.plotly_chart(fig_rank, use_container_width=True)
        st.dataframe(dfr.reset_index(drop=True))
        st.download_button("Baixar ranking (CSV)", dfr.to_csv(index=False).encode("utf-8"),
                           file_name=f"top_{top_n}_ideb_{ano_rank}.csv", mime="text/csv")

# -------- Tab 3: Crescimento (Δ) --------
with tabs[2]:
    st.subheader("Top N — Crescimento (Δ IDEB entre dois anos)")
    start = st.selectbox("Ano inicial (start)", options=year_cols, index=0, key="start")
    end = st.selectbox("Ano final (end)", options=year_cols, index=len(year_cols)-1, key="end")
    top_n_delta = st.number_input("Top N (crescimento)", min_value=3, max_value=50, value=default_topn, step=1, key="topdelta")

    if int(start) >= int(end):
        st.error("Escolha um ano final maior que o inicial.")
    else:
        dft = df_work[["ds_mun", start, end]].copy()
        dft[start] = pd.to_numeric(dft[start], errors="coerce")
        dft[end] = pd.to_numeric(dft[end], errors="coerce")
        dft["delta"] = dft[end] - dft[start]
        dfr_delta = dft.dropna(subset=[start, end, "delta"]).sort_values("delta", ascending=False).head(int(top_n_delta))
        if dfr_delta.empty:
            st.info("Não há dados suficientes para o intervalo selecionado.")
        else:
            colors_delta = make_colors(base_pal, len(dfr_delta))
            figd = px.bar(dfr_delta, x="delta", y="ds_mun", orientation="h",
                          labels={"delta":"Δ IDEB", "ds_mun":"Município"},
                          title=f"Top {len(dfr_delta)} — Δ IDEB ({start} → {end})",
                          color_discrete_sequence=colors_delta)
            figd.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(figd, use_container_width=True)
            st.dataframe(dfr_delta)
            st.download_button("Baixar Δ (CSV)", dfr_delta.to_csv(index=False).encode("utf-8"),
                               file_name=f"top_delta_{start}_{end}.csv", mime="text/csv")

# -------- Tab 4: IDEB médio --------
with tabs[3]:
    st.subheader("IDEB médio — evolução (média dos municípios do Instituto)")
    mean_vals = df_work[year_cols].mean()
    years_int = [int(y) for y in year_cols]
    df_mean = pd.DataFrame({"Ano": years_int, "IDEB_medio": mean_vals.values})

    figm = px.line(df_mean, x="Ano", y="IDEB_medio", markers=True,
                   title="Evolução do IDEB médio — Municípios do Instituto",
                   labels={"IDEB_medio":"IDEB médio", "Ano":"Ano"},
                   color_discrete_sequence=[base_pal[0]] if base_pal else None)
    figm.update_xaxes(tickmode="array", tickvals=years_int)
    st.plotly_chart(figm, use_container_width=True)
    st.dataframe(df_mean)
    st.download_button("Baixar IDEB médio (CSV)", df_mean.to_csv(index=False).encode("utf-8"),
                       file_name="ideb_medio.csv", mime="text/csv")

# ====== Rodapé ======
st.markdown("---")
st.caption("IDEB — Instituto Alpargatas · Visualização gerada com Streamlit + Plotly. Ajustes: paleta e exclusões na barra lateral.")

# -----------------------------
# Seção: Comparação IDEB 2023
# Cole após carregar 'df' (ou troque df -> df_work se for o caso)
# -----------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata, re

# --- Configurações rápidas ---
YEAR = "2023"   # usar string pois as colunas no CSV costumam ser strings
df_local = df.copy()   # troque para df_work se for o caso: df_local = df_work.copy()

# --- Funções utilitárias ---
def norm_text(s):
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', s).strip().upper()

def find_col_like(dfcols, patterns):
    """Busca na lista dfcols um nome que case com algum regex em patterns (case-insensitive)."""
    lc = {c.lower(): c for c in dfcols}
    for pat in patterns:
        rx = re.compile(pat, flags=re.I)
        for k, orig in lc.items():
            if rx.search(k):
                return orig
    return None

# --- Detectar colunas relevantes (robusto) ---
cols = df_local.columns.tolist()
col_ds_mun = find_col_like(cols, [r'\bds?_?mun(ic|icip)?\b', r'\bmunicipio\b', r'\bcidades?\b', r'\bnome.*municipio\b'])
col_sg_uf  = find_col_like(cols, [r'\bsg[_ ]?uf\b', r'\buf\b', r'\bsigla[_ ]?uf\b'])
col_ds_uf  = find_col_like(cols, [r'\b(ds_)?uf\b', r'\bnome[_ ]?estado\b', r'\bestado\b'])
col_ds_rgi = find_col_like(cols, [r'\brgi\b', r'\bregiao\b', r'regiao_intermediaria', r'regiao_imediata'])

# quick diagnostic if YEAR exists
if YEAR not in df_local.columns:
    st.warning(f"Aviso: coluna '{YEAR}' não encontrada entre as colunas do dataset. Colunas detectadas: {list(df_local.columns)[:30]}")
    st.stop()

# minimal checks
if not col_ds_mun:
    st.error("Não encontrei coluna de nome do município no dataset (procure por 'ds_mun' ou 'CIDADES').")
    st.stop()

# preparar: garantir numericidade da coluna YEAR
df_local[YEAR] = pd.to_numeric(df_local[YEAR], errors='coerce')

# normalizar colunas auxiliares (se existirem)
if col_sg_uf:
    df_local['_sg_uf_norm'] = df_local[col_sg_uf].astype(str).map(norm_text)
else:
    df_local['_sg_uf_norm'] = ""

if col_ds_uf:
    df_local['_ds_uf_norm'] = df_local[col_ds_uf].astype(str).map(norm_text)
else:
    df_local['_ds_uf_norm'] = ""

if col_ds_rgi:
    df_local['_rgi_norm'] = df_local[col_ds_rgi].astype(str).map(norm_text)
else:
    df_local['_rgi_norm'] = ""

# mapa simples nome_estado -> sigla (fallback)
estado_map = {
    "ACRE":"AC","ALAGOAS":"AL","AMAPA":"AP","AMAZONAS":"AM","BAHIA":"BA","CEARA":"CE",
    "DISTRITO FEDERAL":"DF","ESPIRITO SANTO":"ES","GOIAS":"GO","MARANHAO":"MA","MATO GROSSO":"MT",
    "MATO GROSSO DO SUL":"MS","MINAS GERAIS":"MG","PARA":"PA","PARAIBA":"PB","PARANA":"PR",
    "PERNAMBUCO":"PE","PIAUI":"PI","RIO DE JANEIRO":"RJ","RIO GRANDE DO NORTE":"RN","RIO GRANDE DO SUL":"RS",
    "RONDONIA":"RO","RORAIMA":"RR","SANTA CATARINA":"SC","SAO PAULO":"SP","SERGIPE":"SE","TOCANTINS":"TO"
}
nordeste_siglas = {"MA","PI","CE","RN","PB","PE","AL","SE","BA"}

# --- Interface do usuário ---
with st.expander("🔎 Comparação IDEB 2023 (Município vs Similares / Nordeste / Brasil)", expanded=True):
    st.write("Comparação fixa no ano 2023. Escolha um município (lista extraída dos municípios do Instituto).")
    muni_options = sorted(df_local[col_ds_mun].dropna().unique().tolist())
    muni_sel = st.selectbox("Escolha o município", options=[""] + muni_options)
    if not muni_sel:
        st.info("Escolha um município para ver a comparação.")
    else:
        # recuperar valor do município
        row = df_local[df_local[col_ds_mun] == muni_sel]
        if row.empty:
            st.error("Município selecionado não encontrado nos dados.")
        else:
            muni_val = pd.to_numeric(row[YEAR].iloc[0], errors='coerce')

            # --- Similares: prioriza rgi, senão UF (sigla), senão UF por nome (mapeado) ---
            similares_mean = np.nan
            similares_label = "Similares (não disponível)"
            try:
                # tenta RGI se existir
                if col_ds_rgi and row.iloc[0].get(col_ds_rgi) and not pd.isna(row.iloc[0].get(col_ds_rgi)):
                    rgi_val = norm_text(row.iloc[0].get(col_ds_rgi))
                    mask = df_local['_rgi_norm'] == rgi_val
                    similares_mean = df_local.loc[mask, YEAR].mean()
                    similares_label = f"Similares (rgi: {row.iloc[0].get(col_ds_rgi)})"
                # se pouco dado, tenta por sigla UF
                if (pd.isna(similares_mean) or mask.sum() <= 1) and col_sg_uf:
                    sg = norm_text(row.iloc[0].get(col_sg_uf))
                    if sg:
                        mask2 = df_local['_sg_uf_norm'] == sg
                        similares_mean = df_local.loc[mask2, YEAR].mean()
                        similares_label = f"Similares (UF: {sg})"
                # por último, mapear nome do estado para sigla e usar
                if (pd.isna(similares_mean) or ( (mask.sum() <= 1) and col_ds_uf )) and col_ds_uf:
                    dsuf = norm_text(row.iloc[0].get(col_ds_uf))
                    sig = estado_map.get(dsuf)
                    if sig:
                        mask3 = df_local['_sg_uf_norm'] == sig
                        similares_mean = df_local.loc[mask3, YEAR].mean()
                        similares_label = f"Similares (UF: {sig})"
            except Exception as e:
                st.warning("Erro ao calcular 'similares': " + str(e))

            # --- Nordeste ---
            nordeste_mean = np.nan
            # se temos sigla col_sg_uf use-a
            if col_sg_uf:
                mn = df_local[df_local['_sg_uf_norm'].isin(nordeste_siglas)]
                if not mn.empty:
                    nordeste_mean = mn[YEAR].astype(float).mean()
            # fallback: mapear por nome do estado
            if pd.isna(nordeste_mean) and col_ds_uf:
                # tentar detectar nomes do nordeste na coluna ds_uf
                nord_names = set(["MARANHAO","PIAUI","CEARA","RIO GRANDE DO NORTE","PARAIBA","PERNAMBUCO","ALAGOAS","SERGIPE","BAHIA"])
                maskn = df_local['_ds_uf_norm'].apply(lambda x: any(n in x for n in nord_names))
                if maskn.any():
                    nordeste_mean = df_local.loc[maskn, YEAR].astype(float).mean()

            # --- Brasil (média geral) ---
            brasil_mean = df_local[YEAR].astype(float).mean()

            # construir DataFrame de comparação
            comp = [
                ("Município", muni_val),
                (similares_label, similares_mean),
                ("Nordeste", nordeste_mean),
                ("Brasil", brasil_mean)
            ]
            comp_df = pd.DataFrame(comp, columns=["comparacao", "ideb"]).dropna(subset=["ideb"]).reset_index(drop=True)

            if comp_df.empty:
                st.error("Sem valores numéricos disponíveis para as comparações em 2023.")
            else:
                # gráfico Plotly
                fig = px.bar(comp_df, x="ideb", y="comparacao", orientation="h",
                             labels={"ideb":"IDEB (2023)", "comparacao":"Comparação"},
                             title=f"Comparação IDEB 2023 — {muni_sel}",
                             color="comparacao", color_discrete_sequence=px.colors.qualitative.Plotly)
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=420)
                st.plotly_chart(fig, use_container_width=True)

                # tabela + download
                st.table(comp_df.rename(columns={"comparacao":"Comparação","ideb":"IDEB 2023"}))
                st.download_button("Baixar comparação (CSV)", comp_df.to_csv(index=False).encode("utf-8"),
                                   file_name=f"comparacao_ideb_2023_{muni_sel}.csv", mime="text/csv")

            # --- Mensagens diagnósticas (úteis para você depurar) ---
            diag = []
            diag.append(f"Coluna nome município detectada: {col_ds_mun}")
            diag.append(f"Coluna sigla UF detectada: {col_sg_uf}")
            diag.append(f"Coluna nome UF detectada: {col_ds_uf}")
            diag.append(f"Coluna RGI detectada: {col_ds_rgi}")
            st.info("Diagnóstico: " + " | ".join(diag))

            st.write(df_ia_columns.tolist())
