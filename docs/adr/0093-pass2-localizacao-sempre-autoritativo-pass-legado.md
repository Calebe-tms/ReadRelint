# ADR-0093: Pass 2 (Localização) Torna-se Sempre Autoritativo sobre o Pass Legado

- Status: Aceita
- Data: não registrada

## Contexto
A arquitetura multi-pass (ADR-088) introduziu um Pass 2 dedicado e blindado (ADR-089) para localização, mas a lógica de merge entre ele e o pass legado ainda tratava campo vazio do Pass 2 como "sem opinião", permitindo que o valor do pass antigo (sem as mesmas garantias) vazasse para o resultado final justamente quando o Pass 2 corretamente se abstinha por falta de evidência.

## Decisão
Corrigido bug onde o `LlmPipeline` só sobrescrevia o resultado do pass legado (schema `IncidentReport` genérico, sem guardrails) quando o Pass 2 retornava valor não-vazio — deixando vazar placeholders e alucinações do pass antigo sempre que o Pass 2 corretamente abstinha de responder por falta de evidência. Agora o Pass 2 sobrescreve incondicionalmente os campos geográficos (`address`, `municipality`, `neighborhood`, `police_unit`, `coordinates`, `map_url`, `geo_precision`).

## Consequências
Fecha uma brecha real de vazamento de dados não confiáveis, garantindo que as garantias de qualidade do Pass 2 (ADR-089) realmente prevaleçam sobre o pass legado em todos os casos, inclusive quando o Pass 2 não encontra evidência. Reforça a lógica de que abstenção deliberada (campo vazio por falta de evidência) é um resultado válido e deve ser respeitado, não tratado como ausência de decisão.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
