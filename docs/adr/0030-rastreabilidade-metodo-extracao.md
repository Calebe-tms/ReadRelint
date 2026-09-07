# ADR-0030: Rastreabilidade de Método de Extração (`Ollama (IA)` vs `Regex (Sem IA)`)

- Status: Aceita
- Data: não registrada

## Contexto
Como o sistema pode operar tanto com IA local quanto em modo puramente determinístico (regex), é importante que o analista saiba, registro a registro, qual método gerou aquela extração para calibrar sua confiança nos dados.

## Decisão
Adição da coluna `extraction_method` no banco SQLite para identificar a origem da extração de cada documento, permitindo que a aplicação opere com alta velocidade 100% sem LLM ou com IA local, exibindo badges visuais e relatórios atualizados em tempo real.

## Consequências
O usuário ganha transparência total sobre a origem de cada extração, podendo filtrar e priorizar revisão conforme o método. Adiciona uma coluna e lógica de badge que precisam ser mantidas consistentes em toda a UI.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
