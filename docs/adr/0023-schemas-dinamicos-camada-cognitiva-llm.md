# ADR-0023: Schemas Dinâmicos na Camada Cognitiva (LLM)

- Status: Aceita
- Data: não registrada

## Contexto
Com a introdução de especialidades polimórficas (ADR-022), a IA precisa ser instruída a preencher diferentes conjuntos de campos dependendo do tipo de ocorrência identificado, sem hardcodear um único schema fixo no cliente Ollama.

## Decisão
O `ILlmProcessor` e `OllamaClient` passam a aceitar `schema_model: Optional[type]`, permitindo que cada regra (`IncidentRule`) defina via `get_schema_model()` qual estrutura Pydantic a IA deve preencher.

## Consequências
A camada de IA torna-se extensível: novas especialidades podem definir seu próprio schema sem alterar o cliente Ollama. Isso acopla a qualidade da extração à corretude de cada `get_schema_model()` implementado por regra.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
