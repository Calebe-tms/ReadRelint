# Diretório de Testes (`tests/`)

Esta pasta contém a **suíte de testes automatizados** da aplicação **ReadRelint**, desenvolvida com `pytest`.

## Suíte de Testes

**API REST (FastAPI, via `TestClient`):**
* [test_api_relints.py](file:///d:/www/ReadRelint/tests/test_api_relints.py) — endpoints de RELINTs (`/api/v1/relints`).
* [test_api_participants.py](file:///d:/www/ReadRelint/tests/test_api_participants.py) — endpoints de Participantes e Dossiês (`/api/v1/participants`).
* [test_api_monitoring.py](file:///d:/www/ReadRelint/tests/test_api_monitoring.py) — endpoints de monitoramento de pastas (`/api/v1/monitoring`).
* [test_api_events.py](file:///d:/www/ReadRelint/tests/test_api_events.py) — endpoint de eventos em tempo real via WebSocket (`/api/v1/events`).

**Persistência (SQLite):**
* [test_sqlite_repo.py](file:///d:/www/ReadRelint/tests/test_sqlite_repo.py) — `SqliteRepo` e `SqlitePersonRepo` (leitura, gravação, migrações automáticas).
* [test_json_processed_registry.py](file:///d:/www/ReadRelint/tests/test_json_processed_registry.py) — `JsonProcessedRegistry` (registro de arquivos já processados).
* [test_entities.py](file:///d:/www/ReadRelint/tests/test_entities.py) — contratos de dados e schemas Pydantic (`IncidentReport` e especialidades).

**Extração — motor determinístico (`backend/engine/extractors/deterministic/`):**
* [test_deterministic_pipeline.py](file:///d:/www/ReadRelint/tests/test_deterministic_pipeline.py) — execução completa do `DeterministicPipeline`.
* [test_deterministic_rules.py](file:///d:/www/ReadRelint/tests/test_deterministic_rules.py) — regras determinísticas por especialidade (`HomicideDeterministicRule`, `DrugTraffickingDeterministicRule`).
* [test_ibge_validator.py](file:///d:/www/ReadRelint/tests/test_ibge_validator.py) — validação de prenomes via Censo IBGE.
* [test_participant_extractor.py](file:///d:/www/ReadRelint/tests/test_participant_extractor.py) — `ParticipantExtractor` (blocos estruturados de participantes).
* [test_role_detector.py](file:///d:/www/ReadRelint/tests/test_role_detector.py) — detecção de papel (Vítima/Testemunha/Autor), vulgo e documento próximo ao nome.
* [test_bm_classifier.py](file:///d:/www/ReadRelint/tests/test_bm_classifier.py) — classificador determinístico de `bm_group`.
* [test_name_parser.py](file:///d:/www/ReadRelint/tests/test_name_parser.py) — `BrazilianNameParser` e `clean_person_name`.

**Extração — motor cognitivo via LLM (`backend/engine/extractors/llm/`):**
* [test_llm_prompts.py](file:///d:/www/ReadRelint/tests/test_llm_prompts.py) — prompts modulares, sanitizador de síntese e gerador de link Google Maps.
* [test_location_extractor.py](file:///d:/www/ReadRelint/tests/test_location_extractor.py) — guardrails determinísticos do `LocationExtractor` (quebra de linha no sinal de coordenadas, conversão DMS, blindagem geográfica do RS, unidade policial, guardrail de rua).
* [test_specialty_extractor.py](file:///d:/www/ReadRelint/tests/test_specialty_extractor.py) — Passo 3 do pipeline multi-pass (`SpecialtyExtractor`): detectores determinísticos e guardrails de enum/evidência textual.
* [test_ollama_client.py](file:///d:/www/ReadRelint/tests/test_ollama_client.py) — `OllamaClient` com mock das requisições HTTP.
* [test_base_rule.py](file:///d:/www/ReadRelint/tests/test_base_rule.py) — contrato abstrato `IncidentRule` (`backend/engine/extractors/llm/rules/base_rule.py`).
* [test_rules.py](file:///d:/www/ReadRelint/tests/test_rules.py) — `RelintRule` e orquestração do `EtlService.process_file()` (skip por registro/banco já existente, fluxo de save).

**Camadas transversais:**
* [test_pdf_reader.py](file:///d:/www/ReadRelint/tests/test_pdf_reader.py) — `PdfReader` com mocks do PyMuPDF (`fitz`).
* [test_text_cleaner.py](file:///d:/www/ReadRelint/tests/test_text_cleaner.py) — higienização de texto e remoção de cabeçalhos institucionais.
* [test_folder_watcher.py](file:///d:/www/ReadRelint/tests/test_folder_watcher.py) — monitoramento de pastas e disparo de eventos.

## Como Executar os Testes

No terminal, na raiz do projeto:
```bash
pytest
```
