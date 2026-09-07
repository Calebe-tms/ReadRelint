# ADR-0059: Arquitetura Reativa em Tempo Real via Server-Sent Events (SSE) e Listener EventSource

- Status: Aceita
- Data: não registrada

## Contexto
Sem um canal reativo, o dashboard só refletiria novos RELINTs processados ou atualizados após um recarregamento manual da página ou polling periódico, criando uma experiência defasada em relação ao que o motor de ETL estava produzindo em segundo plano.

## Decisão
Implementação do barramento pub/sub assíncrono `EventBroadcaster` e rota SSE `GET /api/v1/events` (`events.py`). Conectado ao pipeline `EtlService` e ao endpoint de atualização de RELINTs. O listener nativo `EventSource` no frontend (`app.js`) recebe os eventos `relint_created` e `relint_updated`, re-processando os dados da aba ativa (Dashboard de Crimes, Lista de RELINTs, Homicídios, Galeria) em tempo real e exibindo notificações *Toast* flutuantes sem recarregar a página.

## Consequências
Dá ao dashboard uma sensação de atualização ao vivo, sem necessidade de recarregar a página, melhorando significativamente a experiência durante sessões de monitoramento ativo. Introduz a complexidade de manter um barramento pub/sub assíncrono e listeners client-side sincronizados com o estado real do backend.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
