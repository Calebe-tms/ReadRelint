# ADR-0085: Desacoplamento Arquitetural Estrito dos Motores LLM e Regex

- Status: Aceita
- Data: não registrada

## Contexto
Com o tempo, os caminhos de extração via LLM e via Regex acumularam pontos de mistura implícita (fallbacks silenciosos), dificultando entender e depurar qual método realmente produziu cada campo de um RELINT, contrariando o propósito da rastreabilidade já buscada na ADR-030.

## Decisão
Separação física e lógica em pastas dedicadas (`backend/engine/extractors/llm/` e `backend/engine/extractors/deterministic/`). No modo LLM (`LlmPipeline`), a extração é 100% orientada pelo modelo Ollama sem nenhum fallback silencioso de regex sobrepondo campos; no modo Determinístico (`DeterministicPipeline`), a execução roda 100% offline via Regex e heurísticas puras.

## Consequências
Torna o comportamento de cada pipeline (LLM ou Determinístico) previsível e auditável, sem sobreposição implícita entre os dois. Exige disciplina para não reintroduzir fallbacks cruzados entre as pastas separadas conforme novas extrações forem adicionadas.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
