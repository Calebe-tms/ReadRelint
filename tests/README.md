# Diretório de Testes (`tests/`)

Esta pasta contém a **suíte de testes automatizados** da aplicação **ReadRelint**, desenvolvida com `pytest`.

## Estrutura por Área

Os testes são organizados em subpastas por área do sistema, para permitir rodar **só o que foi afetado** por uma mudança (ver `.claude/rules/rules.md` — minimizar execução de testes) em vez da suíte inteira a cada alteração.

### `tests/motor_llm/` — motor cognitivo via LLM (`backend/engine/extractors/llm/`)
* [test_llm_prompts.py](file:///d:/www/ReadRelint/tests/motor_llm/test_llm_prompts.py) — prompts modulares, sanitizador de síntese e gerador de link Google Maps.
* [test_location_extractor.py](file:///d:/www/ReadRelint/tests/motor_llm/test_location_extractor.py) — guardrails determinísticos do `LocationExtractor` (coordenadas, DMS, blindagem RS, unidade policial, `location_types`).
* [test_specialty_extractor.py](file:///d:/www/ReadRelint/tests/motor_llm/test_specialty_extractor.py) — Pass 3 (`SpecialtyExtractor`): detectores determinísticos e guardrails de enum/evidência textual.
* [test_registry_extractor.py](file:///d:/www/ReadRelint/tests/motor_llm/test_registry_extractor.py) — `RegistryExtractor` (registro policial em outro órgão) e `classify_registry_digits`.
* [test_ollama_client.py](file:///d:/www/ReadRelint/tests/motor_llm/test_ollama_client.py) — `OllamaClient` com mock das requisições HTTP.
* [test_base_rule.py](file:///d:/www/ReadRelint/tests/motor_llm/test_base_rule.py) — contrato abstrato `IncidentRule`.
* [test_rules.py](file:///d:/www/ReadRelint/tests/motor_llm/test_rules.py) — `RelintRule` e orquestração do `EtlService.process_file()` no caminho LLM.

```bash
pytest tests/motor_llm/
```

### `tests/motor_regex/` — motor determinístico (`backend/engine/extractors/deterministic/`, `text_cleaner.py`, `bm_classifier.py`)
* [test_deterministic_pipeline.py](file:///d:/www/ReadRelint/tests/motor_regex/test_deterministic_pipeline.py) — execução completa do `DeterministicPipeline`.
* [test_deterministic_rules.py](file:///d:/www/ReadRelint/tests/motor_regex/test_deterministic_rules.py) — regras por especialidade (`HomicideDeterministicRule`, `DrugTraffickingDeterministicRule`).
* [test_ibge_validator.py](file:///d:/www/ReadRelint/tests/motor_regex/test_ibge_validator.py) — validação de prenomes via Censo IBGE.
* [test_participant_extractor.py](file:///d:/www/ReadRelint/tests/motor_regex/test_participant_extractor.py) — `ParticipantExtractor` (blocos estruturados de participantes, fallback regex).
* [test_role_detector.py](file:///d:/www/ReadRelint/tests/motor_regex/test_role_detector.py) — detecção de papel (Vítima/Testemunha/Autor), vulgo e documento próximo ao nome.
* [test_bm_classifier.py](file:///d:/www/ReadRelint/tests/motor_regex/test_bm_classifier.py) — `classify_bm_group()` e `classify_relint_type()`.
* [test_name_parser.py](file:///d:/www/ReadRelint/tests/motor_regex/test_name_parser.py) — `BrazilianNameParser` e `clean_person_name`.
* [test_text_cleaner.py](file:///d:/www/ReadRelint/tests/motor_regex/test_text_cleaner.py) — higienização de texto, remoção de cabeçalhos institucionais, `extract_date_of_fact`/`extract_time_of_fact`.
* [test_etl_service_deterministic_phase.py](file:///d:/www/ReadRelint/tests/motor_regex/test_etl_service_deterministic_phase.py) — garantia de que a "Fase B" (incondicional, os dois motores) nunca sobrescreve/recalcula o que já foi resolvido.

```bash
pytest tests/motor_regex/
```

### `tests/modulo_pessoas/` — Gerenciador de Pessoas (dossiês, participantes, App-AJ)
* [test_api_participants.py](file:///d:/www/ReadRelint/tests/modulo_pessoas/test_api_participants.py) — endpoints de Participantes e Dossiês (`/api/v1/participants`).
* [test_pessoas_models.py](file:///d:/www/ReadRelint/tests/modulo_pessoas/test_pessoas_models.py) — models SQLModel (`Pessoa`/`dados_aj` livre, `PessoaFoto`, `Qrb`, `GrupoCriminoso`/`GrupoFamiliar`, pivots) contra um SQLite temporário criado via `SQLModel.metadata.create_all()`.
* [test_migration_schema.py](file:///d:/www/ReadRelint/tests/modulo_pessoas/test_migration_schema.py) — roda `alembic upgrade head` de verdade contra um arquivo temporário e confere o schema resultante, incluindo coexistência com o bootstrap legado do motor de RELINT.

> Ver [`docs/proposals/gerenciador-pessoas-app-aj.md`](file:///d:/www/ReadRelint/docs/proposals/gerenciador-pessoas-app-aj.md) para o estado da importação de dados e os itens em aberto (endpoints REST/UI, passo 3 de participantes no motor LLM).

```bash
pytest tests/modulo_pessoas/
```

### `tests/dashboard/` — API REST, persistência e monitoramento
* [test_api_relints.py](file:///d:/www/ReadRelint/tests/dashboard/test_api_relints.py) — endpoints de RELINTs (`/api/v1/relints`).
* [test_api_monitoring.py](file:///d:/www/ReadRelint/tests/dashboard/test_api_monitoring.py) — endpoints de monitoramento de pastas (`/api/v1/monitoring`).
* [test_api_events.py](file:///d:/www/ReadRelint/tests/dashboard/test_api_events.py) — endpoint de eventos em tempo real via WebSocket (`/api/v1/events`).
* [test_sqlite_repo.py](file:///d:/www/ReadRelint/tests/dashboard/test_sqlite_repo.py) — `SqliteRepo`/`SqlitePersonRepo` (leitura, gravação, migrações automáticas, regressão de listagem completa no dashboard).
* [test_json_processed_registry.py](file:///d:/www/ReadRelint/tests/dashboard/test_json_processed_registry.py) — `JsonProcessedRegistry` (registro de arquivos já processados).
* [test_folder_watcher.py](file:///d:/www/ReadRelint/tests/dashboard/test_folder_watcher.py) — monitoramento de pastas e disparo de eventos.

```bash
pytest tests/dashboard/
```

### Raiz de `tests/` — compartilhado entre motores/módulos
* [test_entities.py](file:///d:/www/ReadRelint/tests/test_entities.py) — contratos de dados e schemas Pydantic (`IncidentReport`, `Person`, especialidades) — usado pelos dois motores, sem dono único.
* [test_pdf_reader.py](file:///d:/www/ReadRelint/tests/test_pdf_reader.py) — `PdfReader` com mocks do PyMuPDF (`fitz`) — parsing compartilhado, roda antes de qualquer motor.

## Como Executar os Testes

Suíte inteira (evitar — usar só quando a mudança afeta múltiplas áreas):
```bash
pytest
```

Escopo alvo (preferir — rodar só a(s) pasta(s) afetada(s) pela mudança):
```bash
pytest tests/motor_llm/
pytest tests/motor_regex/
pytest tests/modulo_pessoas/
pytest tests/dashboard/
```
