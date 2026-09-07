# ADR-0086: Bypass de CORS em Transmissão SSE no SvelteKit

- Status: Aceita
- Data: não registrada

## Contexto
O navegador trata `127.0.0.1` e `localhost` como origens diferentes para fins de CORS, mesmo apontando para o mesmo host físico; como o app desktop abria o navegador em um domínio e o `EventSource` estava hardcoded para o outro, a conexão SSE (ADR-059) era bloqueada silenciosamente sem erro visível claro.

## Decisão
Identificado bloqueio silencioso do navegador de política de segurança (CORS) devido ao mismatch entre `127.0.0.1` (servidor nativo PyQt) e `localhost` na url hardcoded da inicialização do `EventSource` no frontend SPA. Solucionado através do uso de URL Base Relativa (`/api/v1`) em todo o ecossistema Svelte, eliminando travamentos de socket cross-domain.

## Consequências
Elimina um bug sutil e difícil de diagnosticar de bloqueio de CORS, restaurando a confiabilidade do canal de eventos em tempo real. O uso de URLs relativas em vez de absolutas torna o frontend mais portável entre ambientes, reduzindo o risco de mismatches de origem futuros.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
