# Estrutura de Pastas - ReadRelint

Este documento apresenta a estrutura de diretórios e arquivos do projeto **ReadRelint**, detalhando o papel de cada pasta na arquitetura Ports and Adapters do sistema.

## Visão Geral da Árvore de Diretórios

```text
ReadRelint/
├── .claude/                    # Customizações, regras e skills de agentes de IA
├── docs/                       # Documentação completa do projeto (padrão Diátaxis)
├── alembic/                    # Migrações versionadas (Alembic) do módulo Gerenciador de Pessoas
│   └── versions/               # Scripts de migration, um por revisão
├── alembic.ini                 # Configuração do Alembic (aponta pra data/relints.db)
├── scripts/                    # Scripts utilitários de execução única (ex: import_app_aj_data.py)
├── backend/                    # Backend API REST em FastAPI e lógica central (Engine)
│   ├── api/                    # Routers REST, endpoints, dependências e WebSocket
│   ├── core/                   # Configurações globais e utilitários centrais
│   ├── database/               # Repositórios SQLite (motor RELINT) + models/repo SQLModel (módulo Pessoas)
│   ├── engine/                 # Processamento de PDF, higienização e motores (Ollama/Regex)
│   └── task_manager/           # Fila de processamento (ETL) e watcher de diretórios
├── data/                       # Dados persistidos, SQLite e mídia extraída (gitignored)
│   ├── relints.db              # Banco de dados SQLite principal
│   ├── media/                  # Fotos de participantes e anexos recortados dos PDFs
│   ├── pessoas_Images/         # Fotos de pessoas do módulo Gerenciador de Pessoas
│   └── app_aj_import/          # CSVs da planilha App-AJ preservados para a migração de dados (PII, nunca vai pro git)
├── desktop/                    # Interface gráfica nativa de controle (PyQt6)
│   ├── controllers/            # Controladores de serviço e MainController
│   └── ui/                     # Interface PyQt6 (painel, console de logs, gauges)
├── frontend/                   # Frontend SPA construído em SvelteKit
│   ├── src/                    # Componentes Svelte, rotas e estilos nativos SvelteKit (app.css / variables.css)
│   ├── static/                 # Ativos estáticos (ex: robots.txt)
│   └── vite.config.js          # Configurações do empacotador Vite
├── tests/                      # Suíte de testes automatizados (pytest), organizada por área:
│   ├── motor_llm/               #   extração via LLM (Ollama)
│   ├── motor_regex/              #   extração determinística (regex/heurísticas)
│   ├── modulo_pessoas/           #   Gerenciador de Pessoas (dossiê, App-AJ)
│   └── dashboard/                #   API REST, persistência e monitoramento
├── painel.py                   # Script de atalho para inicialização do painel PyQt6
├── Iniciar-Painel.bat          # Script de lote do Windows para iniciar o app facilmente
└── requirements.txt            # Dependências Python do projeto
```

## Detalhamento dos Diretórios

### 1. `docs/`

Documentação completa do projeto no padrão Diátaxis, sucessora da pasta `.ai_context/`. Contém `architecture/`, `database/`, `api/`, `extractors/`, `adr/` (Architecture Decision Records), `proposals/` e `project-state.md`. Ver o índice geral em [`../README.md`](../README.md).

### 2. `backend/`

Toda a lógica de negócios e API:
- `api/`: define os endpoints do FastAPI (ex.: `/api/v1/relints`, `/api/v1/events` para WebSocket, `/api/v1/monitoring`).
- `core/`: utilitários compartilhados e configurações da aplicação.
- `database/`: conexão com o SQLite. Motor de RELINT (`sqlite_repo.py`, `sqlite_person_repo.py`) usa SQL puro com auto-migração via `_init_db()`; módulo Gerenciador de Pessoas (`pessoas_models.py`, `pessoas_repo.py`) usa SQLModel + Alembic (`alembic/`) — duas tecnologias coexistindo no mesmo arquivo `.db`, ver ADR-0102.
- `engine/`:
  - `parsers/`: extração de texto cru de PDFs via `PyMuPDF`.
  - `cleaners/`: higienização de texto e nomes (`text_cleaner.py`, `bm_classifier.py`, `name_parser.py`).
  - `extractors/`: motor cognitivo local (Ollama) e motor de Regex determinístico com suporte ao Censo IBGE e spaCy.
- `task_manager/`: gerenciador do ciclo de vida de monitoramento de pastas e o worker assíncrono do ETL.

### 3. `desktop/`

A interface nativa PyQt6 que atua como Hub de monitoramento e ativador dos servidores backend/frontend:
- `controllers/`: gerencia o estado e inicializa threads de logs e serviços de rede sem travar a Main Thread.
- `ui/`: arquivos da interface PyQt6 (`pyqt_app.py`), QSS escuro para customização visual e componentes como medidores circulares de progresso.

### 4. `frontend/`

Painel Web SvelteKit moderno construído seguindo o *Resend Design System* (Tema escuro puro `#000000`):
- `src/`: organizado com rotas e componentes reutilizáveis para exibir dossiês, visualizadores de PDFs/Imagens e estatísticas do dashboard.

### 5. `data/`

Diretório local para persistência de dados:
- `relints.db`: banco relacional SQLite operando em modo WAL para alto desempenho concorrente.
- `media/`: diretório que armazena os arquivos de imagem recortados dos relatórios em PDF para renderização na Web.
