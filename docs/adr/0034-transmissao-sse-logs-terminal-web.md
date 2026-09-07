# ADR-0034: Transmissão SSE de Logs do Terminal para a Web

- Status: Aceita
- Data: não registrada

## Contexto
Os logs do motor de processamento são gerados no processo Python local; para que a interface web os exiba em tempo real sem polling constante, é necessário um canal de push assíncrono do servidor para o navegador.

## Decisão
Uso de buffer circular in-memory (`recent_logs`) no `MainController` exposto via SSE (`/api/v1/monitoring/events`) para popular a caixa de log do terminal web em tempo real.

## Consequências
O terminal web passa a refletir os logs do sistema em tempo real com baixa latência, sem sobrecarregar o backend com requisições repetidas de polling. O buffer em memória, por ser circular, descarta logs mais antigos e não serve como histórico permanente.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
