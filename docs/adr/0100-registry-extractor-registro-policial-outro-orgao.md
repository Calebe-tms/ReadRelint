# ADR-0100: `RegistryExtractor` — Pass Dedicado para Registro Policial em Outro Órgão

- Status: Aceita
- Data: 2026-09-07

## Contexto

Depois da remoção do Pass 1 legado ([ADR-0096](./0096-eliminacao-total-pass1-legado-passes-dedicados-proposta.md)), `registry_number`, `registry_agency` e `registry_year` ficaram sem nenhuma extração dedicada no modo Ollama (IA). Esses campos registram um eventual **registro policial em outro órgão** (DP, DPPA, Polícia Civil) — informação **desconexa do número do próprio RELINT** (que aparece no cabeçalho do documento, ex: "RELATÓRIO Nº 015/2026/ADJ-INT-CRIM").

Levantamento com o usuário (conhecimento de domínio direto, não inferido do texto) estabeleceu 3 características centrais desse campo:
1. É **raro** — a maioria dos RELINTs não menciona nenhum registro em outro órgão.
2. Aparece **no corpo narrativo, geralmente perto do final do texto**, nunca no título/cabeçalho — e é frequentemente confundido com o número do próprio RELINT se a busca não for restrita ao corpo.
3. O formato é `número-do-registro/número-do-órgão/ano-de-registro`, mas **a ordem dos 3 números no texto não é confiável** (ex: "Registro na DP Nº 26/2026/151641" não segue a ordem número/órgão/ano). O que É confiável: o **tamanho em dígitos** de cada componente — código do órgão quase sempre 6 dígitos, ano sempre 4 dígitos, número do registro raramente passa de 4.

## Decisão

Criado `RegistryExtractor` (`backend/engine/extractors/llm/extractors/registry_extractor.py`), seguindo o mesmo padrão dos extratores já existentes (`SummaryExtractor`, `LocationExtractor`, `SpecialtyExtractor`): schema Pydantic minúsculo (`RegistryExtraction`, em `schemas/registry_schema.py`) e prompt dedicado (`REGISTRY_INSTRUCTIONS`, em `prompts/registry_prompt.py`) injetado via `questions={"system_prompt": ...}` — não adicionado ao builder global `build_extraction_prompt()`, para não poluir o prompt dos outros passes com instruções irrelevantes a eles.

Guardrails determinísticos aplicados, nessa ordem:
1. **Restrição ao corpo narrativo**: a busca (e a validação de evidência) roda só no texto retornado por `extract_history_from_annex()` (pós-`ANEXOS:`), nunca no cabeçalho — elimina estruturalmente a confusão com o número do próprio RELINT, sem precisar de lógica extra de exclusão.
2. **Evidência literal**: cada valor retornado pela LLM só é aceito se os dígitos existirem literalmente no corpo do texto (`text_contains()`, reaproveitado de `location_extractor.py`).
3. **Reclassificação por contagem de dígitos** (`classify_registry_digits()`): depois da validação de evidência, os 3 valores são reordenados por tamanho — exatamente 1 valor de 6 dígitos vira `registry_agency`, exatamente 1 valor de 4 dígitos vira `registry_year`, o restante vira `registry_number`. Se houver ambiguidade (ex: dois valores de 4 dígitos, nenhum jeito de saber qual é o ano), a reclassificação é abortada e a resposta original da LLM é mantida sem alteração — evita "corrigir" para pior quando o tamanho sozinho não decide.
4. **Prompt reforça precisão sobre recall**: instrução explícita para retornar `null` nos 3 campos quando não houver menção clara, dado que o campo é raro — prefere não capturar a capturar errado.

Efeito colateral corrigido: `clean_relint_text()` (`text_cleaner.py`) tinha uma regra que apagava qualquer linha inteira começando com a palavra "Registro" (pensada para remover legendas de foto tipo "REGISTRO FOTOGRÁFICO:"), o que apagava por completo frases legítimas como "Registro na DP Nº 26/2026/151641...". A regra foi corrigida para exigir "DO"/"DE" logo após a palavra-chave ou dois-pontos próximo — mesmo padrão de precisão já usado em `extract_fallback_summary()` para o mesmo grupo de palavras-chave.

## Consequências

`registry_number`/`registry_agency`/`registry_year` voltam a ser extraídos no modo Ollama (IA), com maior confiabilidade que o Pass 1 legado tinha (que não tratava a ordem variável dos 3 números nem restringia a busca ao corpo do texto). Como o campo é intencionalmente conservador (guardrail de evidência + reclassificação que aborta em ambiguidade), o recall continua baixo por natureza — RELINTs onde a menção de registro não segue nenhum padrão reconhecível pelo prompt continuam retornando vazio, consistente com a decisão de precisão sobre recall (ADR-0099).

A correção em `clean_relint_text()` também beneficia, em tese, qualquer outro trecho do pipeline que dependa do corpo narrativo pós-`ANEXOS:` conter frases começando com "Registro"/"Foto"/"Imagem"/"Câmera" sem ser um rótulo de legenda — nenhuma regressão encontrada nos testes existentes (`test_text_cleaner.py`).
