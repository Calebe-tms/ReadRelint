# Motor de Extração Determinístico (100% Sem IA)

Este documento descreve como o motor de extração 100% determinístico (sem nenhuma chamada à LLM) funciona, com base no código real em `backend/engine/extractors/deterministic/`. É o caminho usado como fallback gracioso sempre que o modo IA está desativado ou o Ollama está indisponível.

## Orquestração

`DeterministicPipeline` (`backend/engine/extractors/deterministic/pipeline.py`) coordena a extração completa de um RELINT sem qualquer chamada de rede, em 5 etapas sequenciais dentro de `extract()`:

1. **Assunto**: `extract_subject_fallback()` (`backend/engine/cleaners/text_cleaner.py`).
2. **Síntese/Resumo**: `extract_fallback_summary()`, a partir do assunto já resolvido.
3. **Participantes**: delegado ao `ParticipantExtractor` (pipeline especialista de 5 camadas, detalhado abaixo).
4. **Classificação de Grupo BM**: `classify_bm_group()` (`backend/engine/cleaners/bm_classifier.py`) — mesma função usada também no caminho com IA.
5. **Coordenadas e Mapa**: `resolve_coordinates_and_map_info()` (`text_cleaner.py`).

Cada etapa é isolada em `try/except` própria, emitindo um `ExtractionAlert` de warning/error em caso de falha, sem interromper as etapas seguintes. O resultado final é marcado com `extraction_method = "Regex (Sem IA)"`.

## Estrutura de pastas do motor determinístico

```text
backend/engine/extractors/deterministic/
├── pipeline.py                    # DeterministicPipeline — orquestrador
├── rules/                         # Classes Rule por especialidade (mesma observação do motor LLM: legado)
│   ├── base_rule.py
│   ├── drug_trafficking_rule.py
│   └── homicide_rule.py
└── participants/                  # Pipeline especialista de extração de participantes (5 camadas)
    ├── participant_extractor.py   # Coordenador das 5 camadas
    ├── structured_parser.py       # Camada 1 — blocos verticais e seções formais
    ├── spacy_ner.py                # Camada 2 — spaCy NER
    ├── ibge_validator.py           # Camada 3 — validação positiva IBGE
    ├── role_detector.py            # Camada 4 — detecção direcional de papel + docs/vulgo
    └── negative_filters.py         # Camada 5 — filtros negativos (blacklist)
```

## As 5 camadas de extração de participantes

O `ParticipantExtractor.extract_participants()` (`participant_extractor.py`) combina, nesta ordem:

### Camada 1 — Blocos estruturados (`structured_parser.py`, `extract_structured_blocks()`)
Reconhece 4 padrões textuais formais via regex:
1. **Bloco vertical formal**: `NOME: ...` seguido opcionalmente de `RG:`, `CPF:` e `ALCUNHA:` em linhas subsequentes.
2. **Padrão inline com documento**: `"NOME COMPLETO, RG: 123456"` ou `"NOME - CPF 123456"`.
3. **Seções do boletim**: `"VÍTIMA(S): NOME..."`, `"ACUSADO(S): NOME..."`, `"TESTEMUNHA(S): NOME..."` — cada seção já define o papel diretamente.
4. **Padrão narrativo com qualificadores**: nomes em maiúsculas precedidos por termos como `"menor"`, `"vítima"`, `"acusado"`, `"identificado como"`, `"senhor"`.

Cada participante encontrado nesta camada já recebe um papel (via seção, ou via `detect_participation_role()` para os padrões 1, 2 e 4).

### Camada 2 — spaCy NER (`spacy_ner.py`, `extract_person_entities_spacy()`)
Roda o modelo `pt_core_news_sm` do spaCy (carregado em cache singleton) e coleta todas as entidades reconhecidas como `PER` (pessoa). Se o spaCy ou o modelo não estiverem instalados no ambiente, emite um `ExtractionAlert` de warning e retorna lista vazia — o pipeline degrada graciosamente para as camadas 1/4/5 apenas.

### Camada 3 — Validação positiva via Censo IBGE (`ibge_validator.py`, `is_valid_brazilian_name()`)
Para cada candidato do spaCy, valida em O(1) (consulta a um `set` em memória, carregado de `resources/ibge_names.json`) se o nome tem pelo menos 2 palavras e se o primeiro nome existe na base de prenomes do Censo IBGE (normalizado sem acento/caixa). Candidatos que falham nessa validação são descartados — este é o principal filtro anti-falso-positivo do NER genérico do spaCy.

### Camada 4 — Detecção direcional de papel e enriquecimento (`role_detector.py`)
Para cada candidato validado, três funções analisam o contexto textual ao redor da citação do nome (janela de ~150 caracteres antes/depois):
- `detect_participation_role()`: rankeia padrões de papel (`Vítima`, `Testemunha`, `Autor/Suspeito`) por proximidade física ao nome e especificidade da expressão, com regras específicas para não confundir "vítima" referente a um policial (`"PM vítima"`) com o participante civil. Retorna `"Autor/Suspeito"` como default quando nenhum padrão é encontrado.
- `extract_nickname()`: procura vulgos/alcunhas próximos ao nome (`"vulgo X"`, `"conhecido como X"`, ou entre aspas).
- `extract_document_near_name()`: procura CPF/RG na vizinhança imediata (~80 caracteres) do nome.

Resultados da Camada 2/3 são mesclados com os da Camada 1 por nome normalizado (chave upper-case), enriquecendo entradas já existentes (preenchendo vulgo/documento vazios) sem duplicar participantes.

### Camada 5 — Filtros negativos estritos (`negative_filters.py`, `is_blacklisted_name()`)
Aplicado tanto durante a extração (Camadas 1 e 3) quanto como filtro final antes de retornar a lista, descarta qualquer nome que caia em uma das listas negras normalizadas (sem acento, maiúsculas):
- `MILITARY_KEYWORDS`: patentes e termos de guarnição (SD, SGT, CB, CAP, TEN, CEL, "BRIGADA MILITAR" etc.) — garante que nenhum policial entre no dossiê de pessoas investigadas.
- `INSTITUTION_KEYWORDS`: órgãos públicos, hospitais, delegacias, secretarias.
- `LOCATION_KEYWORDS`: tipos de via/logradouro (quando o nome começa com um desses termos).
- `OBJECT_KEYWORDS`: marcas de veículos e armas.
- `CRIME_KEYWORDS`: títulos de seções e termos de ocorrência.
- `CIVIL_POLICE_KEYWORDS`: policiais civis, delegados, peritos.

## Documentação relacionada

- Fluxo ETL completo: [`../architecture/data-flow.md`](../architecture/data-flow.md)
- Motor via LLM (Ollama): [`llm-pipeline.md`](./llm-pipeline.md)
- Roadmap de modularização deste motor (Fase 2, ainda não implementada): [`../project-state.md`](../project-state.md)
