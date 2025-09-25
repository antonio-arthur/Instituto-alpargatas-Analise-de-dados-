# filtrar_pb.py
import pandas as pd
from pathlib import Path

# Caminhos
CSV_IDEB = Path("database/br_inep_ideb_municipio.csv")
CSV_MUNIC = Path("database/br_bd_diretorios_brasil_municipio.csv")
CSV_SAIDA = Path("database/br_inep_ideb_municipio_filtrado.csv")

# Carregar datasets
df_ideb = pd.read_csv(CSV_IDEB)
df_munic = pd.read_csv(CSV_MUNIC)

# Garantir consistência nos tipos de chave
df_ideb["id_municipio"] = df_ideb["id_municipio"].astype(str)
df_munic["id_municipio"] = df_munic["id_municipio"].astype(str)

# Filtrar municípios da Paraíba (sigla_uf == PB)
df_pb_ids = df_munic[df_munic["sigla_uf"] == "PB"][["id_municipio", "nome"]]

# Fazer merge para trazer os nomes
df_pb = df_ideb.merge(df_pb_ids, on="id_municipio", how="inner")

# Reordenar colunas (opcional)
cols = ["ano", "sigla_uf", "id_municipio", "nome", "rede", "ensino",
        "anos_escolares", "taxa_aprovacao", "indicador_rendimento",
        "nota_saeb_matematica", "nota_saeb_lingua_portuguesa",
        "nota_saeb_media_padronizada", "ideb", "projecao"]
df_pb = df_pb[cols]

# Salvar CSV filtrado
df_pb.to_csv(CSV_SAIDA, index=False, encoding="utf-8")

print(f"✅ Arquivo salvo em {CSV_SAIDA} com {len(df_pb)} linhas e {df_pb['id_municipio'].nunique()} municípios.")
