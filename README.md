# Administrador de RELINTs (Ollama)

Este projeto é um software local para Windows desenvolvido para monitorar e processar relatórios de inteligência policial e boletins de ocorrência (**RELINTs**) em formato PDF.

## 🚀 Principais Funcionalidades
* **Processamento Cognitivo Local (Offline):** extração multi-pass via LLM local (**Ollama**, ex: `llama3.1`) — síntese, localização/georreferenciamento, apreensões, participantes e classificação de especialidade, cada uma em um pass dedicado com guardrails determinísticos.
* **Motor Determinístico de Fallback (100% sem IA):** pipeline em camadas (blocos estruturados, NER via spaCy, validação por Censo IBGE, detecção de papéis, filtros negativos) que assume automaticamente quando o Ollama está indisponível, sem perda de funcionalidade.
* **Zero Envio para Nuvem:** garante sigilo e privacidade total (LGPD), processando 100% dos dados na máquina local.
* **Monitoramento Automático de Pastas:** observa diretórios configurados via `watchdog` para processar automaticamente novos PDFs adicionados.
* **Dashboard Web (FastAPI + SvelteKit):** interface Master-Detail para busca, dossiês por especialidade criminal, cruzamento de vínculos entre participantes, galeria de anexos e atualização em tempo real via WebSocket.
* **Persistência Relacional (SQLite/WAL):** banco embutido local, sem dependência de servidores externos.
* **Painel Desktop (PyQt6):** hub central para ligar/desligar o monitoramento de pastas, o backend e o dashboard web.

## 🏗️ Arquitetura e Estrutura
O projeto adota rigorosamente o padrão **Clean Architecture (Ports & Adapters)**. Para entender a estrutura física de arquivos e diretórios, o modelo de dados, o fluxo de processamento e as decisões arquiteturais, veja a documentação completa em [`docs/`](./docs/README.md).

## 📜 Regra de Idioma do Projeto
* **Código-fonte:** Estritamente em **Inglês** (nomes de variáveis, funções, classes, arquivos, chaves JSON).
* **Documentação, Comentários, Logs e UI:** Estritamente em **Português do Brasil (pt-BR)**.
