# ProjEngDados202602-BD

Pipeline de ETL para dados da **PNAD Contínua (IBGE)** referentes a Pernambuco. Os dados são extraídos da API do IBGE (ou de uma coleção MongoDB já carregada), transformados com `pandas` e persistidos em SQLite (e opcionalmente MongoDB/JSON).

## Arquitetura

```
                         ┌────────────────────────┐
                         │   API IBGE (SIDRA)      │
                         │  agregado 4093 / PNADC  │
                         └───────────┬─────────────┘
                                     │ requests.get()
                                     ▼
                         ┌────────────────────────┐
                         │   src/extract.py        │
                         │   classe Extract        │
                         │  - extract_pnadc()      │
                         │  - extract_collection_  │
                         │    from_mongo()         │
                         └───────────┬─────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                  ▼
        ┌────────────────────┐             ┌────────────────────────┐
        │  MongoDB Atlas      │◄───────────►│  JSON local             │
        │  db: IBGE           │  load_mongo  │  (pernambuco.json)      │
        │  coll: PNADC        │  load_json   └────────────────────────┘
        └──────────┬──────────┘
                   │ extract_collection_from_mongo()
                   ▼
        ┌────────────────────────┐
        │   src/transform.py      │
        │   classe Transform      │
        │  - transform_pnadc()    │
        │    normaliza série      │
        │    temporal em          │
        │    DataFrame pandas     │
        └───────────┬─────────────┘
                    ▼
        ┌────────────────────────┐
        │   src/load.py           │
        │   classe Load            │
        │  - load_sqlite()        │
        └───────────┬─────────────┘
                    ▼
        ┌────────────────────────┐
        │   ibge.db (SQLite)      │
        │   tabela: pnadc         │
        └────────────────────────┘
```

**Camadas:**

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| Extract | [src/extract.py](src/extract.py) | Busca os dados na API do IBGE ou em uma coleção MongoDB |
| Transform | [src/transform.py](src/transform.py) | Converte a série retornada em um `DataFrame` (período, valor, ano, trimestre) |
| Load | [src/load.py](src/load.py) | Grava o resultado em SQLite, MongoDB ou JSON |
| Orquestração | [main.py](main.py) | Encadeia as três etapas |

O fluxo padrão executado em [main.py](main.py) hoje é: **MongoDB → Transform → SQLite**. As chamadas para extrair diretamente da API do IBGE e para salvar em JSON/MongoDB estão disponíveis nas classes, mas comentadas no script principal.

## Pré-requisitos

- Python 3.13+
- Conta/URI de acesso a um cluster MongoDB (para as etapas que usam Mongo)

## Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd ProjEngDados202602-BD
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS (bash/zsh):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

**Windows (PowerShell):**

```powershell
copy .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Edite o `.env` gerado:

```
MONGO_URI=<sua-connection-string-do-mongodb>

NEON_DB=<connection-string-opcional-do-neon>
```

## Uso

Com o ambiente virtual ativado e o `.env` configurado, execute:

```bash
python main.py
```

Isso irá:
1. Buscar os documentos da coleção `PNADC` no banco `IBGE` (MongoDB);
2. Transformar a série em um `DataFrame` do pandas;
3. Salvar o resultado na tabela `pnadc` do arquivo `ibge.db` (SQLite).

### Extraindo dados diretamente da API do IBGE

Para buscar os dados diretamente da API pública em vez do MongoDB, descomente em [main.py](main.py) as linhas:

```python
pnadc = extrator.extract_pnadc()
```

### Salvando em JSON ou MongoDB

Descomente as chamadas correspondentes em [main.py](main.py):

```python
loader.load_json("pernambuco", pnadc)
loader.load_mongo(pnadc, "IBGE", "PNADC")
```

## Estrutura do projeto

```
ProjEngDados202602-BD/
├── main.py              # Orquestra o pipeline (extract → transform → load)
├── requirements.txt     # Dependências do projeto
├── .env.example         # Modelo de variáveis de ambiente
├── ibge.db              # Banco SQLite gerado pelo pipeline
├── pernambuco.json       # Exemplo de dado extraído em JSON
├── transform.ipynb       # Notebook de exploração/prototipagem da transformação
└── src/
    ├── extract.py        # Extração (API IBGE / MongoDB)
    ├── transform.py       # Transformação dos dados em DataFrame
    └── load.py            # Persistência (SQLite / MongoDB / JSON)
```

## Notas

- O arquivo `.env` não deve ser versionado (já está no `.gitignore`).
- O banco `ibge.db` é recriado (`if_exists="replace"`) a cada execução do pipeline.
