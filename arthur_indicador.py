# arthur_indicador.py
import pandas as pd
from pathlib import Path

def carregar_ideb_pop(
    caminho_ideb: str = "tabelas/divulgacao_anos_iniciais_municipios_2023.xlsx",
    caminho_pop: str = "tabelas/POP2020_20220905(Municípios).csv",
    filtro_rede: str = "municipal",
    estados: list[str] | None = None,
) -> pd.DataFrame:
    # ---------- IDEB ----------
    pasta = Path(caminho_ideb).parent
    ideb = pd.read_excel(caminho_ideb, skiprows=9)
    ideb.columns = ideb.columns.str.strip()

    lista_ideb = [f"VL_OBSERVADO_{x}" for x in range(2007, 2025, 2)]
    nomes_ideb = [f"IDEB_{x}" for x in range(2007, 2025, 2)]
    colunas_final = ["CO_MUNICIPIO", "NO_MUNICIPIO", "REDE", "SG_UF"] + lista_ideb

    ideb = ideb[colunas_final]
    ideb = ideb.rename(
        columns={"NO_MUNICIPIO": "MUNICIPIO", **dict(zip(lista_ideb, nomes_ideb))}
    )

    if filtro_rede:
        ideb = ideb[ideb["REDE"].str.strip().str.lower() == filtro_rede.lower()]

    ideb["MUNICIPIO"] = ideb["MUNICIPIO"].str.upper().str.strip()

    # ---------- População ----------
    pop = pd.read_csv(caminho_pop, sep=";", encoding="latin1", skiprows=1)
    pop = pop.rename(columns={"NOME DO MUNICÍPIO": "MUNICIPIO"})
    pop["MUNICIPIO"] = pop["MUNICIPIO"].str.upper().str.strip()
    pop = pop.iloc[:5570, :]
    pop = pop.rename(columns={" POPULAÇÃO ESTIMADA ": "POPULACAO_ESTIMADA"})

    # ---------- Merge ----------
    df = pd.merge(
        ideb,
        pop[["MUNICIPIO", "POPULACAO_ESTIMADA"]],
        on="MUNICIPIO",
        how="left",
    )

    df = df.drop_duplicates(subset=["MUNICIPIO", "SG_UF"], keep="last")

    # ---------- Tratamento das colunas IDEB ----------
    ideb_cols = [c for c in df.columns if c.startswith("IDEB_")]
    if ideb_cols:
        # converter todas as colunas IDEB para numéricas
        df[ideb_cols] = df[ideb_cols].apply(pd.to_numeric, errors="coerce")

        # ordenar e pegar os 2 anos mais recentes
        cols_ordenadas = sorted(ideb_cols, reverse=True)
        anos_recentes = cols_ordenadas[:2]

        # calcular média
        df["MEDIA_IDEB"] = df[anos_recentes].mean(axis=1)

    # ---------- Filtro por estados ----------
    if estados:
        df = df[df["SG_UF"].isin(estados)]

    return df.reset_index(drop=True)
