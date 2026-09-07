# Visão Geral da Arquitetura

O **ReadRelint** é um software local para Windows que monitora uma pasta de documentos de inteligência policial (RELINTs) em formato PDF. Ele extrai e limpa o texto desses documentos, utiliza uma LLM local (Ollama) ou um pipeline determinístico ultra-rápido (spaCy + Censo IBGE + Regex) para estruturar os dados, e os armazena em um banco de dados relacional embutido (SQLite).

O sistema tem duas frentes de interface:

- **Painel de Controle Desktop:** interface moderna em PyQt6 (Qt6 nativo) atuando como *Service Launcher & Status Hub* ultraleve para gerenciar os serviços (Monitor de Pastas, Servidor Web FastAPI, Frontend SvelteKit e IA Ollama), com interface thread-safe e QSS moderno.
- **Dashboard Web de Curadoria:** um dashboard interativo (FastAPI backend + SvelteKit SPA em tema escuro baseado no Resend Design System) para buscar, cruzar vínculos de participantes, exibir dossiês por especialidade, fotos/anexos com visualizador lightbox, métricas de inteligência e curadoria humana dos dados.

## Regras de Ouro (Core Principles)

1. **Privacidade e Segurança:** nenhum dado pode ser enviado para a nuvem sem cifragem. O processamento é 100% offline por padrão.
2. **Arquitetura Limpa:** padrão Ports and Adapters rigorosamente aplicado e organizado em módulos especializados (`backend/engine`, `backend/task_manager`, `backend/api` etc.).
3. **Idioma (Padrão Híbrido):** o código-fonte (nomes, classes, variáveis) é estritamente em **Inglês**. A documentação, comentários e UI são em **Português do Brasil (pt-BR)**.
4. **Portabilidade:** sem instalações de servidores complexos. SQLite embutido em modo WAL (`data/relints.db`).
5. **Single Source of Truth:** cada documento processado corresponde a um único registro no banco relacional.
6. **Especialidades Polimórficas:** suporte a modelos estendidos por tipo de crime (ex.: Homicídios, Tráfico, Roubos e Furtos) preservando um esquema relacional limpo e extensível via JSON.
7. **Processamento Híbrido (IA vs Determinístico):** o sistema opera tanto com LLM local (Ollama) enriquecido por guardrails determinísticos quanto em modo 100% determinístico sem IA, registrando explicitamente o método de extração utilizado (`"Ollama (IA)"` vs `"Regex (Sem IA)"`).
8. **Classificação Tripla de Participantes:** padronização estrita em 3 papéis exclusivos: **`Vítima`**, **`Testemunha`** e **`Autor/Suspeito`**.

## Stack Tecnológica

- **Base:** Python 3.10+
- **Leitura de PDF:** `PyMuPDF` (fitz) para extração limpa de texto bruto e recorte de imagens/anexos (galeria).
- **Motor NLP Local:** `Ollama` local com JSON Schemas Pydantic estruturados e prompts com regras estritas anti-PM.
- **Motor Determinístico:** pipeline em 5 camadas (`backend/engine/extractors/deterministic/`):
  1. Blocos verticais estruturados e padrões inline com idade/documento.
  2. Reconhecimento de entidades nomeadas via `spaCy` (`pt_core_news_sm`).
  3. Validação positiva de prenomes brasileiros via Censo IBGE em O(1).
  4. Detecção direcional de papéis e especificidade léxica (`role_detector.py`).
  5. Filtros negativos estritos contra patentes militares, órgãos públicos e termos veiculares.
- **Persistência:** `SQLite` em modo WAL (`relints.db`).
- **Interfaces:**
  - `Desktop Hub`: Python PyQt6 (Qt6 nativo, em `desktop/ui/pyqt_app.py`).
  - `Web Dashboard`: SvelteKit SPA (adapter-static) + Svelte 5 Runes (Resend Dark/Light Theme com ícones Phosphor).

## Documentação relacionada

- Fluxo completo de dados, do PDF ao dashboard: [`data-flow.md`](./data-flow.md)
- Estrutura de diretórios do repositório: [`folder-structure.md`](./folder-structure.md)
- Motor de extração via LLM: [`../extractors/llm-pipeline.md`](../extractors/llm-pipeline.md)
- Motor de extração determinístico: [`../extractors/deterministic-pipeline.md`](../extractors/deterministic-pipeline.md)
- Modelo de dados: [`../database/schema.md`](../database/schema.md)
- Decisões arquiteturais formais: [`../adr/`](../adr/)
