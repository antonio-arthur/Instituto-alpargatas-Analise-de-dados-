# Instituto Alpargatas – Análise de Dados

[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/antonio-arthur/Instituto-alpargatas-Analise-de-dados)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()

## Visão geral

Repositório com análises de dados para o Instituto Alpargatas. O objetivo é organizar, tratar e analisar bases de dados institucionais para gerar indicadores, visualizações e relatórios que apoiem a tomada de decisão.

## Sumário

- [Objetivos](#objetivos)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e execução](#instalação-e-execução)
- [Notebooks e scripts principais](#notebooks-e-scripts-principais)
- [Como contribuir](#como-contribuir)
- [Boas práticas e observações](#boas-práticas-e-observações)
- [Membros / Autores](#membros--autores)
- [Licença](#licença)

## Objetivos

- Centralizar e documentar os processos de limpeza e transformação das bases de dados.
- Gerar indicadores quantitativos e qualitativos sobre os projetos do Instituto.
- Produzir análises exploratórias e visualizações reproduzíveis (notebooks).
- Fornecer scripts reutilizáveis para processamento e geração de tabelas.

## Estrutura do repositório

```
Instituto-alpargatas-Analise-de-dados/
├─ database/         # bases brutas e/ou processadas (não versionar dados sensíveis)
├─ nbs/              # notebooks, análises exploratórias e pipelines em Jupyter
├─ src/              # módulos e funções reutilizáveis em python
├─ tabelas/          # tabelas geradas (outputs)
├─ indicadores.ipynb # notebook de indicadores
├─ arquivo_teste.py  # script de exemplo / testes iniciais
├─ requirements.txt  # dependências do projeto
└─ readme.md         # documentação do projeto (este arquivo)
```

> Observação: ajuste caminhos e nomes de pastas conforme sua conveniência local.

## Pré-requisitos

- Python 3.8 ou superior
- Git
- Recomendado: ambiente virtual (`venv`, `conda`)

## Instalação e execução

1. Clone o repositório

```bash
git clone https://github.com/antonio-arthur/Instituto-alpargatas-Analise-de-dados.git
cd Instituto-alpargatas-Analise-de-dados
```

2. Crie e ative um ambiente virtual

Linux / macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Executar notebooks

Inicie o Jupyter Lab ou Notebook:

```bash
jupyter lab
# ou
jupyter notebook
```

Abra `nbs/` ou `indicadores.ipynb` para explorar as análises.

5. Executar scripts Python

Para rodar scripts simples (ex.: `arquivo_teste.py`):

```bash
python arquivo_teste.py
```

## Notebooks e scripts principais

- `indicadores.ipynb` — notebook com análise dos indicadores principais.
- `nbs/` — notebooks de experimentação e etapas de limpeza/transformação.
- `src/` — funções utilitárias (funções de leitura, transformação, agregação).
- `tabelas/` — saídas tabulares geradas pelas análises.

Se algum notebook acessar bases grandes ou dados sensíveis, execute localmente e não inclua dados confidenciais no repositório.

## Boas práticas e observações

- Não versionar dados sensíveis ou grandes bases diretamente no repositório — use `.gitignore` e coloque apenas amostras quando necessário.
- Documente pré-processamentos e transformações importantes dentro dos notebooks ou com arquivos `README` nas pastas.
- Use `requirements.txt` (já presente) ou `environment.yml` para reprodutibilidade.

## Membros / Autores

- Antonio Arthur de Souza Cardoso
- Felipe Emidio de Medeiros Neto
- Ryann Pedro Minervino das Neves Felix
- Kaylane Pereira Francelino
