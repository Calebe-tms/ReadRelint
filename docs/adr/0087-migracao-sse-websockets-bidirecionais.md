# ADR-0087: Migração de SSE para WebSockets Bidirecionais (Concluída)

- Status: Aceita
- Data: não registrada

## Contexto
O SSE (ADR-059) resolvia bem a necessidade de push do servidor para o cliente, mas é um protocolo estritamente unidirecional; funcionalidades futuras que exigem o frontend enviar dados de volta em tempo real (sem depender exclusivamente de requisições REST) precisavam de um canal bidirecional.

## Decisão
Substituição do fluxo unidirecional EventSource (SSE) por conexões WebSockets nativas no FastAPI (`@router.websocket`) e SvelteKit (`eventsService.js`). Habilitado o método `.send()` no frontend para pavimentar futuras edições e comunicações em tempo real da interface Web de volta para o backend, garantindo resiliência e auto-reconexão inteligente.

## Consequências
Abre caminho para comunicação bidirecional em tempo real entre frontend e backend, além de trazer auto-reconexão mais resiliente. Substitui a infraestrutura de eventos já construída sobre SSE (ADR-059/ADR-086), exigindo que toda a lógica de listeners e broadcast seja portada para o novo protocolo WebSocket.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
