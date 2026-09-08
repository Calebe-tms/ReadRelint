# ADR-0104: `LlmParticipantsExtractor` — Pass Dedicado para Participantes, Dividido por Tipo de Confiança

- Status: Aceita
- Data: 2026-09-08

## Contexto

Depois da remoção do Pass 1 legado ([ADR-0096](./0096-eliminacao-total-pass1-legado-passes-dedicados-proposta.md)), `participants` ficou sem nenhuma extração no modo Ollama (IA) — o único dos 6 campos redistribuídos ainda sem substituto ([ADR-0099](./0099-isolamento-estrito-motores-sem-fallback-cruzado.md)). O motor determinístico (sem IA) já resolve isso com um pipeline especialista maduro de 5 camadas (`backend/engine/extractors/deterministic/participants/`): blocos estruturados, spaCy NER, validação IBGE, detecção direcional de papel/vulgo/documento e uma blacklist anti-PM/instituição/objeto — mas esse pipeline não é reaproveitável como um todo no caminho LLM sem violar o desacoplamento estrito entre os dois motores (ADR-0085/ADR-0099).

## Decisão

Criado `LlmParticipantsExtractor` (`backend/engine/extractors/llm/extractors/llm_participants_extractor.py`), seguindo o mesmo padrão dos extratores já existentes (`RegistryExtractor` como modelo mais recente): schema Pydantic minúsculo (`ParticipantsExtraction`, em `schemas/participants_schema.py`) e prompt dedicado (`PARTICIPANTS_INSTRUCTIONS`, em `prompts/participants_prompt.py`) injetado via `questions={"system_prompt": ...}`.

**Divisão do trabalho por tipo de confiança** (mesmo raciocínio já aplicado a `registry_number`/`police_unit` nesta sessão): em vez de pedir tudo à LLM de uma vez, cada campo vai para quem resolve melhor:
- **LLM decide** `name`, `participation_type` e `background` — exige julgamento narrativo genuíno (quem é a pessoa no contexto do fato, qual o papel, o que se sabe sobre ela).
- **Determinístico resolve** `nickname` e `document` — são "dado serial"/proximidade textual, mais confiável por regex do que por LLM. Reaproveita diretamente `extract_nickname()`/`extract_document_near_name()` (`deterministic/participants/role_detector.py`), aplicados sobre o nome já validado, para cada participante retornado.

**Guardrails aplicados, nessa ordem:**
1. **Evidência literal** (`text_contains()`, reaproveitado de `location_extractor.py`): um nome que a LLM não sustente literalmente no texto é descartado por completo — nunca um participante inventado sobrevive.
2. **Blacklist anti-PM/instituição/objeto** (`is_blacklisted_name()`, reaproveitado de `deterministic/participants/negative_filters.py`): roda por cima da instrução do prompt ("nunca inclua policiais da guarnição"), garantindo o filtro mesmo quando a LLM ignora a instrução.
3. **Fallback de `participation_type`**: se a LLM não retornar um papel, o padrão é `"Autor/Suspeito"` — mesmo default já usado pelo `detect_participation_role()` determinístico e pelo validador `Participant.normalize_participation_type` (`entities.py`), que roda de qualquer forma na construção final da entidade.

**Sobre o reuso de código entre motores**: `is_blacklisted_name()`, `extract_nickname()` e `extract_document_near_name()` são importados diretamente do módulo `deterministic/participants/`. Isso é reuso de utilitários puros e sem estado (não chamam a LLM, não têm efeito colateral), não um mecanismo de recall/fallback entre motores — o tipo de cruzamento que a ADR-0099 proíbe é um motor silenciosamente *substituir o resultado* do outro quando este falha. Aqui não há substituição: o motor LLM continua sendo a única fonte de `name`/`participation_type`/`background`, e as duas funções deterministas importadas seriam, de outro modo, apenas duplicadas — o mesmo raciocínio que já justificou mover `enforce_rs_coordinate_signs`/`dms_to_decimal` para `text_cleaner.py` (ADR-098) para reuso entre os dois motores.

Sem fallback cruzado (ADR-0099 continua valendo): se este pass não retornar ninguém, `participants` fica `[]` — nunca cai de volta em `extract_fallback_participants()` (reservado ao modo 100% sem-IA).

## Consequências

`participants` volta a ser extraído no modo Ollama (IA), fechando o último campo pendente da proposta de eliminação do Pass 1 legado ([`../proposals/eliminacao-pass1-legado.md`](../proposals/eliminacao-pass1-legado.md) — encerrada). A persistência (upsert em `pessoas`/`relint_participantes` via `Person`) não precisou de nenhuma alteração — reaproveita o pipeline já existente em `EtlService.process_file()`, que já operava sobre uma lista de dicionários no mesmo formato (`name`, `nickname`, `document`, `participation_type`, `background`).

Como o campo `document` é resolvido por proximidade textual simples (~80 caracteres ao redor do nome), casos onde o documento de um participante está fisicamente distante da citação do nome no texto continuam retornando vazio — mesma limitação que já existe no motor determinístico, não uma regressão introduzida aqui. `background` não tem guardrail de evidência literal (é uma síntese, não uma citação) — confia na instrução do prompt ("só preencha se houver menção explícita, senão null").
