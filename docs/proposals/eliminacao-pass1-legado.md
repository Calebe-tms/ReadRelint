# Proposta: Eliminação do Pass 1 Legado (Monolítico) e Quebra em Passes Dedicados

> Status: **Parcialmente implementada.** O Pass 1 legado foi removido de `LlmPipeline.extract()` (e a lógica associada de `_strip_superseded_fields`/`SUPERSEDED_LEGACY_FIELDS` em `ollama_client.py`, que ficou morta). Os 6 campos que só ele fornecia (seção 1, abaixo) estão temporariamente sem extração dedicada — todos ficam com os defaults do Pydantic (vazio/`None`/`"Outros"`/`[]`). Decisão adicional confirmada com o usuário e formalizada em [ADR-0099](../adr/0099-isolamento-estrito-motores-sem-fallback-cruzado.md): nenhum campo cai de volta em fallback determinístico enquanto estiver no modo Ollama (IA) — nem `participants` (`extract_fallback_participants`) nem `summary` no caso extremo do próprio guardrail do `SummaryExtractor` falhar (`extract_fallback_summary`). Sem recall entre os dois motores por enquanto; a ADR-0099 documenta o plano de, no futuro (motor determinístico maduro), inverter isso com uma chamada de segurança explícita do regex para a LLM. A redistribuição campo a campo (seção 2) ainda não foi implementada — sendo feita uma de cada vez, em turnos separados.
> Decisão de princípio confirmada com o usuário: **não é objetivo reduzir o número de chamadas à LLM** — o objetivo é quebrar em passes mais especializados para aumentar a qualidade/confiabilidade da extração, usando determinismo (regex) sempre que o campo for formulaico o suficiente, e LLM só onde há julgamento genuíno de contexto.

---

## 1. Contexto

O `LlmPipeline.extract()` (`backend/engine/extractors/llm/pipeline.py`) ainda executa, como sua primeira chamada, um **Pass 1 legado monolítico**: `schema_model = rule.get_schema_model()` (efetivamente `IncidentReport` reduzido, após a remoção dos campos geográficos/`bm_group` já supérfluos — ver ADR-095). Esse pass ainda é a única fonte para:

- `registry_number`, `registry_agency`, `registry_year`
- `date_of_fact`, `time_of_fact`
- `relint_type`
- `location_types`
- `main_fact`
- `participants`

O objetivo desta próxima etapa é **eliminar esse Pass 1 legado por completo**, redistribuindo cada campo para o tratamento mais adequado — nunca reagrupando tudo em um schema genérico de novo.

---

## 2. Redistribuição Campo a Campo

| Campo | Tratamento decidido | Justificativa |
|---|---|---|
| `date_of_fact`, `time_of_fact` | ✅ **Implementado** — 100% determinístico, sem LLM. `extract_date_of_fact`/`extract_time_of_fact` (`backend/engine/cleaners/text_cleaner.py`) agora rodam incondicionalmente em `EtlService.process_file()`, fora do bloco `if extraction_method == "Regex (Sem IA)":` — antes só eram usadas no caminho sem-IA. | Formato do cabeçalho é extremamente formulaico ("Em DD de mês de AAAA, às HHhMMmin"). LLM aqui só adiciona risco sem ganho — mesmo raciocínio já aplicado a `police_unit` e `bm_group` nesta sessão. |
| `relint_type` | **Novo classificador determinístico** — `classify_relint_type()`, mesmo padrão de 2 camadas do `classify_bm_group()` (filename+assunto primeiro, conteúdo como fallback). | Enum fechado de 4 opções (`Ocorrência`, `Disk Denúncia`, `Resposta a PB`, `Outros`) com vocabulário-gatilho previsível no assunto ("DISQUE DENÚNCIA", "RESPOSTA PB..."). |
| `registry_number`, `registry_agency`, `registry_year` | ✅ **Implementado** — novo pass LLM dedicado (`RegistryExtractor`, `backend/engine/extractors/llm/extractors/registry_extractor.py`), com guardrail de evidência literal (`text_contains`, reaproveitado de `location_extractor.py`), busca restrita ao corpo narrativo pós-`ANEXOS:` (nunca o cabeçalho, onde vive o número do próprio RELINT) e reclassificação determinística por contagem de dígitos (órgão ~6 dígitos, ano 4 dígitos, número do registro raramente >4 — heurística fornecida pelo usuário, já que a ORDEM dos 3 números no texto não é confiável). Ver ADR-0100. | Não é formulaico o bastante para regex único (varia por órgão/época, ordem inconsistente), mas é um dado tipo "serial" — fácil de validar contra o texto bruto uma vez isolado o trio de números certo. |
| `location_types` | **Novo pass LLM dedicado** ("Tipos de Local"), schema de 1 campo (lista). | Categorização livre (ex: "Propriedade Rural", "Escolas") sem enum fechado — exige julgamento de contexto genuíno. |
| `main_fact` | **Derivado sem chamada nova**, a partir de `subject` (já resolvido pelo Pass de Síntese) e/ou `bm_group` (já resolvido deterministicamente). | Conceitualmente já é uma combinação do que os outros passes resolvem; uma chamada LLM extra aqui não resolveria ambiguidade real. |
| `participants` | **Removido do Pass 1 legado agora.** Fica sem extração até o desenho dos passes novos de participantes (próxima etapa, fora do escopo desta proposta). | Vai virar seu próprio conjunto de passes dedicados — não faz sentido adivinhar o formato agora. |

---

## 3. Resultado Esperado

O Pass 1 legado deixa de existir. Em seu lugar:

- **3 mecanismos determinísticos** (sem LLM): `date_of_fact`/`time_of_fact` (✅ implementado), `classify_relint_type()` (novo), `classify_bm_group()` (já existente).
- **2 passes LLM novos e minúsculos**: "Dados de Registro" (✅ implementado, `RegistryExtractor`) e "Tipos de Local".
- **1 derivação sem chamada**: `main_fact`.
- **`participants` fica de fora**, pendente de desenho próprio.

Isso aumenta o número de passes LLM (não reduz — decisão deliberada), mas cada um extremamente focado, seguindo a mesma filosofia de guardrails já aplicada em `LocationExtractor` e `SpecialtyExtractor` nesta sessão.

---

## 4. Perguntas em Aberto para a Próxima Sessão

- [ ] Desenho dos passes novos de extração de `participants` (quantos passes? um só ou quebrado por sub-concern, ex: identificação vs. antecedentes/documentos?).
- [ ] Nome/organização dos novos arquivos: seguir o padrão `backend/engine/extractors/llm/extractors/registry_extractor.py`, `location_types_extractor.py`? Ou agrupar em um único arquivo dado o tamanho pequeno de cada schema?
- [ ] Onde colocar `classify_relint_type()` — no mesmo `bm_classifier.py` (renomear?) ou em módulo próprio?
- [ ] Confirmar que `main_fact` realmente não precisa de nenhuma lógica adicional além de reaproveitar `subject`/`bm_group`, ou se merece uma pequena função determinística de formatação.

---

## 5. Próximos Passos

- [ ] Implementar `classify_relint_type()` (determinístico).
- [x] Remover `date_of_fact`/`time_of_fact` do schema da LLM e resolver 100% via `text_cleaner.py` no caminho IA também (antes só usado no caminho sem-IA).
- [x] Criar o pass "Dados de Registro" (schema + extractor + prompt) — `RegistryExtractor`, ver ADR-0100.
- [ ] Criar o pass "Tipos de Local" (schema + extractor + prompt).
- [ ] Resolver `main_fact` por derivação.
- [ ] Remover `participants` do Pass 1 legado (sem substituto ainda).
- [ ] Remover o Pass 1 legado inteiro de `LlmPipeline.extract()` e do `ollama_client.py` (a lógica de `_strip_superseded_fields` fica obsoleta e pode ser removida junto).
- [ ] Atualizar testes (`tests/test_rules.py` hoje assume o schema legado; vai precisar de revisão).
- [ ] Desenhar e implementar os passes novos de `participants` (escopo à parte, a discutir).
