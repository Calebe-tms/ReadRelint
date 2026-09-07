# Motor de Extração via LLM (Ollama)

Este documento descreve como o motor cognitivo de extração via LLM local (Ollama) funciona, com base no código real em `backend/engine/extractors/llm/`.

## Visão geral: arquitetura multi-pass

Em vez de uma única chamada monolítica pedindo 15+ campos em um só JSON pesado, o `LlmPipeline` (`backend/engine/extractors/llm/pipeline.py`) executa múltiplas leituras especializadas, cada uma com schema Pydantic e prompt dedicados e ultraleves — determinismo (regex) onde o campo é formulaico o suficiente, LLM só onde há julgamento genuíno de contexto:

1. **Pass 1 — Síntese & Assunto** (`extractors/summary_extractor.py`, classe `SummaryExtractor`, schema `SummaryExtraction`): redige a síntese factual em parágrafo único e extrai o assunto, blindado contra preâmbulos policiais e plágio do título (`sanitize_summary`, em `validators/llm_response_validator.py`). Se a resposta da LLM for vazia, curta demais ou plagiar o assunto, cai para um fallback determinístico (`extract_fallback_summary`/`extract_subject_fallback`, em `backend/engine/cleaners/text_cleaner.py`).
2. **Pass 2 — Localização & Georreferenciamento** (`extractors/location_extractor.py`, classe `LocationExtractor`, schema `LocationExtraction`): resolve endereço, número, bairro, município, unidade policial (BPM) e coordenadas. Este pass é **sempre autoritativo**: sobrescreve incondicionalmente os campos geográficos do resultado, mesmo quando retorna vazio, porque tem guardrails próprios (ver seção Guardrails abaixo).
3. **Classificação determinística de `bm_group`** (`backend/engine/cleaners/bm_classifier.py`, `classify_bm_group()`): roda entre o Pass 2 e o Pass 3, sem LLM, priorizando nome do arquivo + assunto sobre o conteúdo completo como fallback.
4. **Pass 3 — Especialidade** (`extractors/specialty_extractor.py`, classe `SpecialtyExtractor`): resolve os campos adicionais da especialidade identificada pelo `bm_group`. Campos binários/enum simples (`injured_victims`, `hostage_victim`, `recovered`, `location_type`) são resolvidos 100% por regex, sem LLM; campos livres genuinamente nuançados usam um schema Pydantic minúsculo específico daquela especialidade (`schemas/specialty_schemas.py`). Especialidades sem nenhum campo livre (`Roubo a Residência`, `Furto Qualificado`, `Outros`) nunca chamam a LLM.

O resultado de cada pass é combinado em `result.data` dentro de `LlmPipeline.extract()`, com os passes 2 e 3 sempre sobrescrevendo incondicionalmente os campos que produzem (mesmo com valor vazio), para que uma resposta sem guardrail nunca vaze quando o pass dedicado corretamente absteve-se por falta de evidência.

> O antigo "Pass 1 legado" (chamada genérica via `rule.get_schema_model()`, tipicamente `IncidentReport`) foi removido. Com isso, `registry_number`/`registry_agency`/`registry_year`, `date_of_fact`/`time_of_fact`, `relint_type`, `location_types`, `main_fact` e `participants` ficam temporariamente sem extração dedicada pela LLM neste pipeline — todos com os defaults do Pydantic (vazio/`None`/`"Outros"`/`[]`) até serem reconstruídos campo a campo, seguindo o plano em [`../proposals/eliminacao-pass1-legado.md`](../proposals/eliminacao-pass1-legado.md). `participants` **não** cai automaticamente no fallback determinístico por regex (`extract_fallback_participants`) — esse fallback em `EtlService` é reservado exclusivamente ao modo 100% sem-IA (`extraction_method == "Regex (Sem IA)"`), para manter as duas chamadas (LLM e determinística) totalmente separadas.

## Estrutura de pastas do motor LLM

```text
backend/engine/extractors/llm/
├── pipeline.py              # LlmPipeline — orquestrador dos passes
├── llm_processor.py         # ILlmProcessor — porta/interface abstrata
├── ollama_client.py         # OllamaClient — adapter concreto que fala com o Ollama local
├── extractors/               # Um extrator por pass (Summary, Location, Specialty)
│   ├── summary_extractor.py
│   ├── location_extractor.py
│   └── specialty_extractor.py
├── schemas/                  # JSON Schemas Pydantic dinâmicos, por pass/especialidade
│   ├── summary_schema.py
│   ├── location_schema.py
│   ├── address_schema.py
│   └── specialty_schemas.py
├── prompts/                   # Prompts especializados por pass
│   ├── system_prompt.py
│   ├── summary_prompt.py
│   ├── address_prompt.py
│   └── specialty_prompts.py
├── validators/
│   └── llm_response_validator.py   # Sanitização e normalização de saída da LLM
└── rules/                     # 7 classes Rule especializadas (HomicideRule etc.) — não usadas
                                # no pipeline ao vivo (ver observação abaixo)
```

A interface `ILlmProcessor` (`llm_processor.py`) define o método `process_text(text, questions=None, schema_model=None, pre_extracted_entities=None) -> dict`, implementado pelo adapter `OllamaClient` (`ollama_client.py`), que conversa com o Ollama local (`http://localhost:11434` por padrão, modelo `llama3.1:latest`).

**Observação sobre `rules/`**: as 7 classes `Rule` especializadas (`HomicideRule`, `DrugTraffickingRule` etc.) definem `get_schema_model()` mas não estão de fato conectadas ao pipeline ao vivo — o controlador principal usa uma regra fixa (`RelintRule()`) que nunca sobrescreve esse método. A extração de especialidade real depende inteiramente de `classify_bm_group()` + `SpecialtyExtractor`, independente de qual `Rule` é passada. As 7 **entidades** Pydantic especializadas (`HomicideReport`, `DrugTraffickingReport` etc., em `backend/core/entities.py`) continuam sendo o caminho vivo de persistência e leitura — não confundir as duas coisas.

## Guardrails determinísticos aplicados dentro dos passes da LLM

Mesmo nos passes que chamam a LLM, uma camada de validação/normalização 100% determinística roda em cima da resposta antes de aceitá-la, implementada dentro dos próprios extractors:

- **Anti-alucinação de GPS (Zero Fake GPS)**: coordenadas retornadas pela LLM só são aceitas se os dígitos existirem literalmente no texto bruto (ou no link de mapa resolvido); caso contrário são descartadas (`LocationExtractor.extract`, checagem contra `text`/`raw_map_url`).
- **Blindagem geográfica do RS**: `enforce_rs_coordinate_signs` (`backend/engine/cleaners/text_cleaner.py`) força sinal negativo em latitude/longitude e valida a faixa aproximada do Rio Grande do Sul, descartando placeholders textuais (`"N/A"`, `"Sem informação"` etc.) e convertendo DMS → decimal.
- **Tabela município → BPM (unidade policial 100% determinística)**: `resolve_police_unit()` em `location_extractor.py` não pergunta mais `police_unit` à LLM — usa uma tabela fixa de 41 municípios cobertos pelos 3 batalhões da região (`MUNICIPALITY_TO_BATTALION`), com regra de mão dupla: exatamente 1 menção literal de BPM no texto vence sobre a tabela; zero ou múltiplas menções ambíguas caem para a tabela; município fora da tabela e sem menção literal fica vazio.
- **Evidência textual literal**: `text_contains()` (`location_extractor.py`) verifica se um valor aparece literalmente no texto (tolerante a acento/caixa/espaçamento) antes de aceitá-lo — usado para descartar `street` sem sustentação e, no Pass 3, para descartar campos livres de especialidade (`drug_quantity`, `vehicle_model`, `license_plate` etc.) sem evidência no documento (`FREE_TEXT_FIELDS`, em `specialty_extractor.py`).
- **Guardrails de enum fechado**: no Pass 3, valores de `fact_type`, `motivation` e `weapon_used` só são aceitos se baterem (tolerante a acento/caixa) com uma lista fechada de opções válidas (`_match_enum()`); fora da lista, o campo é descartado, nunca forçado a um valor.
- **Sanitização de ruídos narrativos**: `sanitize_address_field()` (`location_extractor.py`) trunca links HTTP, expressões de coordenadas no meio da frase, verbos operacionais da BM ("foi acionada a guarnição...", "via telefone 190...") e referências comerciais entre parênteses antes de aceitar um valor de endereço.
- **Detecção por regex com checagem de negação**: no Pass 3, campos binários (`injured_victims`, `hostage_victim`, `recovered`) são resolvidos por regex que verifica se há uma negação ("não", "sem") na mesma oração do termo encontrado, evitando falsos positivos de negação em oração anterior (`_has_negation_nearby()`).

Ver também a especificação exaustiva das 9 camadas de sanitização geográfica em ADR-090 (`docs/adr/`).

## Detalhes por schema/pass

- **`SummaryExtraction`** (`schemas/summary_schema.py`): campos `subject` e `summary`.
- **`LocationExtraction`** (`schemas/location_schema.py`): campos de endereço (`street`, `number`, `neighborhood`, `municipality`, `coordinates`, `map_url`); `police_unit` não é mais perguntado à LLM (100% determinístico).
- **Schemas de especialidade** (`schemas/specialty_schemas.py`): um schema minúsculo por `bm_group` — `HomicideSpecialtyExtraction`, `DrugTraffickingSpecialtyExtraction`, `EstablishmentRobberySpecialtyExtraction`, `VehicleSpecialtyExtraction` (reaproveitado por Roubo e Furto de Veículo), `PedestrianRobberySpecialtyExtraction`.

## Documentação relacionada

- Fluxo ETL completo: [`../architecture/data-flow.md`](../architecture/data-flow.md)
- Motor determinístico (sem IA): [`deterministic-pipeline.md`](./deterministic-pipeline.md)
- ADRs relevantes: ADR-088 (arquitetura multi-pass), ADR-089/090 (blindagem geográfica), ADR-091/092/093 (correções de localização), ADR-094/095 (extração de especialidades em 2 estágios), ADR-096 (próxima etapa) — em `docs/adr/`
