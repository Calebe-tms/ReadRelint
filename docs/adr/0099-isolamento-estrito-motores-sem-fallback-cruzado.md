# ADR-0099: Isolamento Estrito entre os Motores LLM e Determinístico — Sem Fallback Cruzado (por Enquanto)

- Status: Aceita
- Data: 2026-09-07

## Contexto

Durante a remoção do Pass 1 legado ([ADR-0096](./0096-eliminacao-total-pass1-legado-passes-dedicados-proposta.md)), uma auditoria em `backend/task_manager/etl/etl_service.py` encontrou dois pontos onde o motor determinístico (regex) era acionado como rede de segurança mesmo quando o sistema estava rodando no modo Ollama (IA), sem que isso fosse refletido no campo `extraction_method` salvo no banco:

1. **`participants`**: se a resposta da LLM não trouxesse participantes, o código caía silenciosamente em `extract_fallback_participants()` (regex), mesmo em modo IA.
2. **`summary`**: se a síntese da LLM viesse vazia, o código caía em `extract_fallback_summary()` (regex), mesmo em modo IA — ainda que, na prática, o `SummaryExtractor` já tivesse seu próprio guardrail interno tornando esse caminho quase sempre inalcançável.

Isso contraria o desacoplamento estrito já decidido na [ADR-0085](./0085-desacoplamento-arquitetural-motores-llm-regex.md) ("no modo LLM, a extração é 100% orientada pelo modelo Ollama sem nenhum fallback silencioso de regex sobrepondo campos") — os dois pontos acima eram exatamente esse tipo de fallback silencioso, só que não pegos na auditoria original daquela ADR.

## Decisão

Os dois fallbacks foram removidos do caminho Ollama (IA):
- `participants` fica vazio (`[]`) no modo IA quando não há pass dedicado que o preencha.
- `summary` fica vazio no modo IA no caso extremo em que até o guardrail interno do `SummaryExtractor` falhar.

Ambos os fallbacks continuam ativos, sem alteração, no modo 100% Regex (Sem IA) — lá, cair em `extract_fallback_participants`/`extract_fallback_summary` é o comportamento correto e esperado, não um cruzamento indevido.

**Decisão de princípio para o momento:** enquanto o motor determinístico não estiver com todos os extratores dedicados (participantes, síntese e os demais campos redistribuídos do Pass 1 legado — ver [`../proposals/eliminacao-pass1-legado.md`](../proposals/eliminacao-pass1-legado.md)) maduros e completos, **não haverá nenhum mecanismo de recall/fallback cruzado entre os dois motores**. Um campo sem cobertura no motor ativo fica em branco — isso é aceitável e intencional, não um bug a ser mascarado silenciosamente.

## Direção futura (não implementada agora)

Quando o motor determinístico estiver pronto — com extratores dedicados e maduros para os campos que hoje dependiam do Pass 1 legado —, o plano é inverter a relação de segurança: em vez do modo Ollama recorrer silenciosamente ao regex (como acontecia antes desta ADR), o motor determinístico passa a ser a base primária, com uma **chamada de segurança para a LLM** como rede de segurança nos casos em que o regex não conseguir extrair um campo com confiança suficiente. Essa chamada de segurança precisa ser explícita e rastreável (refletida em `extraction_method` ou em um campo equivalente), nunca silenciosa como os dois casos corrigidos por esta ADR. O desenho detalhado dessa chamada de segurança fica para quando o motor determinístico atingir esse estágio de maturidade — não faz parte do escopo desta decisão.

## Consequências

Positivas: comportamento previsível e auditável — o campo `extraction_method` salvo no banco passa a refletir com precisão de onde cada dado realmente veio, sem mistura silenciosa entre os dois motores. Facilita medir, campo a campo, a real cobertura de cada motor antes de decidir se/quando vale a pena reintroduzir um mecanismo de segurança.

Negativas (temporárias, aceitas conscientemente): RELINTs processados em modo Ollama (IA) enquanto os campos redistribuídos do Pass 1 legado não forem reconstruídos ficam com `participants`, `date_of_fact`, `time_of_fact`, `registry_number`/`registry_agency`/`registry_year`, `relint_type`, `location_types` e `main_fact` em branco — sem nenhum dado de reserva. Isso é uma perda de cobertura visível na UI (`TabGeneral.svelte`) até cada campo ser reconstruído seguindo os novos moldes (determinismo onde formulaico, pass LLM dedicado onde há julgamento genuíno).
