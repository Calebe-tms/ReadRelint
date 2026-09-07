# Documentação do ReadRelint

O **ReadRelint** é um software local para Windows que monitora uma pasta de documentos de inteligência policial (RELINTs) em formato PDF. Ele extrai e limpa o texto desses documentos, utiliza uma LLM local (Ollama) ou um pipeline determinístico ultra-rápido (spaCy + Censo IBGE + Regex) para estruturar os dados, e os armazena em um banco de dados relacional embutido (SQLite). O sistema oferece um Painel de Controle Desktop (PyQt6) para gerenciar os serviços e um Dashboard Web (FastAPI + SvelteKit) para curadoria e cruzamento de inteligência.

Esta pasta reúne a documentação completa do projeto, organizada no padrão [Diátaxis](https://diataxis.fr/) (referência técnica + explicação de arquitetura), sucedendo a antiga pasta `.ai_context/` (removida após a conclusão desta migração — seu conteúdo vive integralmente aqui).

## Estrutura da documentação

- [`architecture/`](./architecture/) — Visão geral do sistema, regras de ouro, stack tecnológica, fluxo de dados completo (pipeline ETL) e estrutura de diretórios.
  - [`architecture/overview.md`](./architecture/overview.md) — visão geral e regras de ouro do projeto.
  - [`architecture/data-flow.md`](./architecture/data-flow.md) — o pipeline ETL completo, do PDF ao dashboard.
  - [`architecture/folder-structure.md`](./architecture/folder-structure.md) — árvore de diretórios do repositório.
  - [`architecture/history/`](./architecture/history/) — specs de UI superadas, mantidas como registro histórico de design.
- [`database/`](./database/) — modelo de dados relacional (SQLite).
  - [`database/schema.md`](./database/schema.md) — explicação em prosa do schema.
  - [`database/schema.dbml`](./database/schema.dbml) — desenho formal do schema em DBML.
- [`api/`](./api/) — referência da API REST e WebSocket.
  - [`api/endpoints.md`](./api/endpoints.md) — todos os endpoints, agrupados por router.
- [`extractors/`](./extractors/) — como cada motor de extração funciona por dentro.
  - [`extractors/llm-pipeline.md`](./extractors/llm-pipeline.md) — motor cognitivo via LLM (Ollama), arquitetura multi-pass.
  - [`extractors/deterministic-pipeline.md`](./extractors/deterministic-pipeline.md) — motor 100% determinístico (sem IA).
- [`adr/`](./adr/) — Architecture Decision Records (ADRs), registros imutáveis de decisões arquiteturais já tomadas.
- [`proposals/`](./proposals/) — propostas técnicas em avaliação ou parcialmente implementadas, ainda não formalizadas em ADR.
- [`project-state.md`](./project-state.md) — estado atual do projeto e backlog (documento vivo, atualizado continuamente).

## Por onde começar

Se você é novo no projeto, a leitura recomendada é, nesta ordem:

1. [`architecture/overview.md`](./architecture/overview.md) — entenda o que o sistema faz e as regras de ouro que orientam qualquer mudança.
2. [`architecture/data-flow.md`](./architecture/data-flow.md) — entenda o caminho completo de um documento, do PDF ao dashboard.
3. [`database/schema.md`](./database/schema.md) e [`api/endpoints.md`](./api/endpoints.md) — entenda o modelo de dados e como ele é exposto.
4. [`adr/`](./adr/) — para entender *por que* certas decisões foram tomadas (e quais ainda valem).
5. [`project-state.md`](./project-state.md) — para saber o que já foi feito e o que está no backlog agora.

## Prompt Inicial Recomendado

Sempre que reiniciar contexto com um agente de IA para trabalhar neste projeto, use:

```text
Olá! Vamos trabalhar no Administrador de RELINTs. Leia estritamente a documentação em `docs/` (comece por `docs/README.md`, depois `docs/project-state.md` e `docs/adr/`) para absorver a arquitetura e entender em que passo estamos.
```
