import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ======================
# 1. Carregar CSV
# ======================
csv_path = Path("database/ideb_municipios_instituto_por_id.csv")

if not csv_path.exists():
    st.error(f"❌ Arquivo não encontrado: {csv_path}. "
             "Coloque o CSV no diretório do app.")
    st.stop()

df_ia = pd.read_csv(csv_path)

# ======================
# 2. Validar colunas
# ======================
if "ds_mun" not in df_ia.columns:
    st.error("❌ O CSV não contém a coluna 'ds_mun' (nome do município). "
             "Verifique o arquivo gerado.")
    st.write("Colunas disponíveis:", df_ia.columns.tolist())
    st.stop()

# identificar anos
year_cols = [c for c in df_ia.columns if str(c).isdigit()]
if not year_cols:
    st.error("❌ Não encontrei colunas de anos (ex: 2015, 2017...) no CSV.")
    st.stop()

# ======================
# 3. Interface Streamlit
# ======================
st.title("📊 Evolução do IDEB — Municípios do Instituto Alpargatas")

mun_options = sorted(df_ia["ds_mun"].dropna().unique().tolist())
selected_muns = st.multiselect("Selecione municípios:", mun_options)

if not selected_muns:
    st.warning("👆 Escolha pelo menos um município para visualizar.")
    st.stop()

df_sel = df_ia[df_ia["ds_mun"].isin(selected_muns)]

# ======================
# 4. Gráfico
# ======================
fig, ax = plt.subplots(figsize=(10, 6))
for _, row in df_sel.iterrows():
    vals = [row[y] for y in year_cols]
    ax.plot(year_cols, vals, marker="o", label=row["ds_mun"])

ax.set_xlabel("Ano")
ax.set_ylabel("IDEB")
ax.set_title("Evolução do IDEB nos municípios selecionados")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# ======================
# 5. Tabela de dados
# ======================
st.subheader("📋 Dados filtrados")
st.dataframe(df_sel[["ds_mun"] + year_cols])
