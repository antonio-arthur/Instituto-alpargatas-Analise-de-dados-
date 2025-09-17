from os import path
from utils import getdtb

# Configuração Inicial de Diretório
data_dir = '~/database'

# Leitura de Dados DTB
file = path.join(data_dir, "RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls")
print("Lendo o arquivo", file)
df_dtb = getdtb(file)

# Leitura de Dados IA
file = path.join(data_dir,"Projetos de Atuação - IA - 2020 a 2025.xlsx")
table = "2024"
from pandas import read_excel
data = read_excel(file, sheet_name=table, skiprows=5)
print(data.head())
print(data.columns)

data = data[['CIDADES', 'UF', 'Nº \nProjetos.7', 
             'Nº \nInstituições.1', 'Nº \nBeneficiados.4']]

data.columns = ['ds_mun', 'sg_uf', 'nprojetos', 'ninstituicoes', 'nbeneficiados']

def formatar_nome(df, coluna, novo_nome="ds_formatada"):
    df[novo_nome] = (df[coluna].str.upper()
                       .str.replace("[-.!?'`()]", "", regex=True)
                       .str.replace("MIXING CENTER", "")
                       .str.strip()
                       .str.replace(" ", ""))
                       
    return df

df_dtb = formatar_nome(df=df_dtb, coluna="ds_mun")
print("IBGE \n", df_dtb.head())

data = formatar_nome(df=data, coluna="ds_mun")
data['ds_uf'] = data['sg_uf'].map({"PB": "Paraíba", "PE": "Pernambuco",
                                   "MG": "Minas Gerais", "SP": "São Paulo"})
print("IA \n", data.head())
print("IA \n", data.sg_uf.value_counts())

data_m = data.merge(df_dtb, how="inner", on=["ds_formatada", "ds_uf"],
                    suffixes=["_ia", ""], indicator="tipo_merge")
print(data_m.head())
print(data_m["tipo_merge"].value_counts)

# Investigação dos não conectados
x = data_m.query("tipo_merge=='left_only'")
print(x.head())

# IDEB
lista_ideb = [f'VL_OBSERVADO_{x}' for x in range(2005,2025, 2)]
nomes_ideb = [f'ideb_{x}' for x in range(2005,2025, 2)]

ideb = read_excel(path.join(data_dir, 
                            "INEP/IDEB/divulgacao_anos_iniciais_municipios_2023.xlsx"), 
                            skiprows=9, 
                            usecols=['CO_MUNICIPIO', 'REDE'] + lista_ideb,
                            na_values=['-', '--'])
ideb.columns = ['id_mundv', 'rede'] + nomes_ideb
print(ideb.head())
print(ideb.info())

data_final = data_m.merge(ideb, how='left')
print(data_final)
