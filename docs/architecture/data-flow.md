# Fluxo de Dados (Pipeline ETL) — do PDF ao Dashboard

Este documento descreve o caminho completo percorrido por um RELINT desde o momento em que o PDF chega na pasta monitorada até o momento em que seus dados aparecem no dashboard web.

## Visão geral em etapas

1. **Monitoramento de pasta** → 2. **Extração de texto (PyMuPDF)** → 3. **Limpeza de texto** → 4. **Decisão IA vs Determinístico** → 5. **Extração estruturada** (multi-pass LLM ou pipeline determinístico) → 6. **Pós-processamento e guardrails** → 7. **Classificação de especialidade** → 8. **Persistência SQLite** → 9. **Consumo via API REST/WebSocket** → 10. **Dashboard SvelteKit**

---

## 1. Monitoramento de pasta

O `FolderWatcher` (`backend/task_manager/watcher/folder_watcher.py`) observa continuamente o diretório configurado pelo usuário em busca de novos arquivos PDF. Novos arquivos (ou reprocessamentos disparados manualmente) são enfileirados para o `ETLService` (`backend/task_manager/etl/etl_service.py`), que orquestra o restante do pipeline. O registro de quais arquivos já foram processados (para evitar releitura) é mantido em `backend/task_manager/registry/` (`processed_registry.py` / `json_processed_registry.py`).

## 2. Extração de texto bruto (PyMuPDF)

Os módulos em `backend/engine/parsers/` (`pdf_reader.py`, `file_parser.py`) usam `PyMuPDF` (fitz) para extrair o texto integral do PDF e recortar as imagens/anexos presentes no documento (salvos em `data/media/`).

## 3. Limpeza e higienização de texto

O texto bruto passa por `clean_relint_text` e demais utilitários de `backend/engine/cleaners/text_cleaner.py`, removendo cabeçalhos/rodapés institucionais e normalizando artefatos de extração (ex.: reconexão do sinal `-` de coordenadas quebrado entre linhas pelo PyMuPDF, conversão DMS → decimal). Outros módulos de `cleaners/` cuidam de responsabilidades específicas: `bm_classifier.py` (classificação determinística de grupo BM), `name_parser.py` (parsing de nomes), `hybrid_cleaner.py`.

## 4. Decisão IA vs Determinístico

O `ETLService`/controlador principal decide, com base no switch de modo IA (ativado no Desktop Hub ou na Web) e na saúde do Ollama (heartbeat), qual motor de extração estruturada usar:

- **Modo IA ativo e Ollama saudável** → `LlmPipeline` (`backend/engine/extractors/llm/pipeline.py`).
- **Modo IA desativado ou Ollama indisponível** → `DeterministicPipeline` (`backend/engine/extractors/deterministic/pipeline.py`), como fallback gracioso.

O método efetivamente usado é gravado no campo `metodo_extracao` do registro (`"Ollama (IA)"` ou `"Regex (Sem IA)"`).

## 5. Extração estruturada

### 5a. Caminho com IA — arquitetura multi-pass (Ollama)

Em vez de uma única chamada monolítica à LLM, o `LlmPipeline` executa múltiplas leituras especializadas, cada uma com schema Pydantic e prompt dedicados e minúsculos:

1. **Pass 1 — Síntese & Assunto** (`extractors/summary_extractor.py`): redige a síntese factual em parágrafo único e extrai o assunto, blindado contra preâmbulos policiais e plágio do título.
2. **Pass 2 — Localização & Georreferenciamento** (`extractors/location_extractor.py`): resolve endereço, bairro, município, unidade BPM (100% determinística via tabela município → BPM) e coordenadas, com guardrails anti-alucinação de GPS e evidência textual literal.
3. **Classificação determinística de `bm_group`** (`cleaners/bm_classifier.py`): roda entre o Pass 2 e o Pass 3, com prioridade para filename+assunto sobre o conteúdo.
4. **Pass 3 — Especialidade** (`extractors/specialty_extractor.py`): campos binários/enum simples são resolvidos por regex (sem LLM); campos livres genuinamente nuançados (motivação, quantidade de droga, modelo de veículo etc.) usam um schema Pydantic minúsculo por especialidade, com guardrail de evidência literal no texto.
5. Um Pass 1 legado monolítico (schema genérico `IncidentReport`, via `rule.get_schema_model()`) ainda roda como base para os campos ainda não migrados para passes dedicados (`registry_number`, `date_of_fact`, `participants` etc.) — ver detalhamento completo em [`../extractors/llm-pipeline.md`](../extractors/llm-pipeline.md) e a proposta de eliminação total em [`../proposals/eliminacao-pass1-legado.md`](../proposals/eliminacao-pass1-legado.md).

Descrição completa da arquitetura multi-pass (5 leituras): ver [`../extractors/llm-pipeline.md`](../extractors/llm-pipeline.md).

### 5b. Caminho sem IA — pipeline determinístico

O `DeterministicPipeline` (`backend/engine/extractors/deterministic/pipeline.py`) resolve assunto, síntese, participantes, `bm_group` e coordenadas/mapa usando somente regex, spaCy e tabelas estáticas — sem nenhuma chamada de rede. A extração de participantes em si roda em 5 camadas (blocos estruturados → spaCy NER → validação IBGE → detecção direcional de papel → filtros negativos). Detalhamento completo em [`../extractors/deterministic-pipeline.md`](../extractors/deterministic-pipeline.md).

## 6. Pós-processamento e guardrails

Independente do motor, o resultado passa por normalizações e validações adicionais: `clean_person_name`, recuperação de documentos por proximidade (`extract_document_near_name`), normalização de papéis para o trio oficial (`Vítima`, `Testemunha`, `Autor/Suspeito`) e expurgo de falsos positivos de policiais (`negative_filters.py`).

## 7. Classificação determinística de especialidade

O `bm_classifier.py` aplica regras de padrões ordenados por especificidade (Homicídio, Tráfico, Roubos, Furtos) para garantir o `bm_group` correto, rodando sempre — tanto no caminho IA quanto no caminho sem-IA.

## 8. Persistência

As entidades `IncidentReport`/`HomicideReport` (e demais especialidades) e `Person`, validadas por Pydantic, são salvas no SQLite via `backend/database/sqlite_repo.py` e `backend/database/sqlite_person_repo.py`, populando as tabelas `relints`, `pessoas`, `relint_participantes` e as tabelas de detalhe polimórficas (`homicidio_detalhes` etc.). Ver o modelo relacional completo em [`../database/schema.md`](../database/schema.md).

## 9. Consumo via API

O backend FastAPI (`backend/api/`) expõe endpoints REST para listar, buscar e editar RELINTs e participantes, além de um endpoint WebSocket para notificações em tempo real (novo relint processado, relint atualizado). Referência completa em [`../api/endpoints.md`](../api/endpoints.md).

## 10. Dashboard Web

O Painel Web em SvelteKit consome os endpoints REST/WebSocket do FastAPI para cruzar relacionamentos, exibir dossiês por especialidade, estatísticas e KPIs do dashboard, galerias de anexos com lightbox e permitir curadoria humana dos dados (edição que marca `editado_usuario = true`, imunizando o registro contra sobrescritas automáticas em reprocessamentos).
