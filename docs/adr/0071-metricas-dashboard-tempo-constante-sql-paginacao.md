# ADR-0071: Métricas de Dashboard em Tempo Constante O(1) via SQL e Paginação Leve

- Status: Aceita
- Data: não registrada

## Contexto
O cálculo de métricas do dashboard era feito iterando no frontend sobre a lista completa de relatórios carregados, um padrão que degrada linearmente com o crescimento do volume de RELINTs no banco.

## Decisão
Eliminação do processamento pesado no frontend que iterava todos os relatórios completos. Implementação do método `get_dashboard_metrics()` no `SqliteRepo` executando agregação direta via SQL para alimentar o novo endpoint `GET /api/v1/relints/stats` (< 5ms) em conjunto com suporte a `limit` e `offset` para relatórios recentes.

## Consequências
Torna o carregamento de métricas praticamente instantâneo e independente do volume total de dados, delegando a agregação ao SQL. Move a responsabilidade de cálculo de métricas para o backend, exigindo que qualquer nova métrica do dashboard seja implementada como agregação SQL em vez de lógica JS ad-hoc.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
