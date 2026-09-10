# ReadRelint — Blueprint do Projeto

## O que é

Administrador de RELINTs (Relatórios de Inteligência da Brigada Militar/RS): lê PDFs de boletins, extrai dados estruturados (fato, local, participantes, especialidade do crime) via dois motores paralelos e isolados — LLM local (Ollama) e determinístico (regex/regras) — e disponibiliza os dados num dashboard web para consulta, edição e cruzamento de informações entre RELINTs e pessoas.

## Arquitetura

- **Backend**: FastAPI + SQLite (schema em português). Persistência via SQL puro (`SqlitePersonRepo`/`SqliteRepo`) para as tabelas legadas de RELINTs/participantes, e SQLModel + Alembic (módulo mais novo) para o Gerenciador de Pessoas.
- **Frontend**: SvelteKit (Svelte 5, runas), consumindo a API REST em `/api/v1/*`.
- **Desktop**: app `painel.py` (PyQt6) que hospeda o servidor FastAPI in-process e abre o frontend — é o modo de uso real do usuário no dia a dia (roda com `--autostart`).
- **Extração**: pipeline multi-pass (`backend/engine/extractors/llm/pipeline.py`) — cada campo/grupo de campos tem seu próprio pass dedicado à LLM (resumo, localização, especialidade, registro, participantes), com classificação de grupo/tipo sempre determinística. Motor determinístico paralelo faz o mesmo sem LLM (fallback).
- **Módulos principais**: RELINTs (boletins), Participantes/Dossiês (pessoas cruzadas entre RELINTs), Gerenciador de Pessoas (base mais ampla de criminosos importada do App-AJ, com fotos, veículos, grupos criminosos/familiares, QRBs).

## Documentação

- **Decisões arquiteturais**: `docs/adr/` (formato MADR, imutável — uma vez aceita, uma ADR não é editada retroativamente; mudança de rumo gera nova ADR).
- **Este diretório (`.ai_context/`)**: resumo leve e mutável do estado atual do projeto, para retomada rápida entre sessões — não substitui as ADRs, que continuam sendo o registro formal e detalhado de cada decisão técnica.

## Escopo confirmado com o usuário (regras de negócio, não óbvias no código)

- **Gerenciador de Pessoas**: foco é criminosos e, por consequência, vítimas. **Militares (PMs) nunca são cadastrados**, mesmo citados nominalmente num RELINT (ex: consulta de antecedentes disciplinares) e mesmo quando o próprio militar é o autor/suspeito do fato — regra absoluta, sem exceção.
