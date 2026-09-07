# ADR-0048: Eliminação da Oscilação (Flicker/Bounce) do Estado de Monitoramento no Frontend

- Status: Aceita
- Data: não registrada

## Contexto
Inferir o estado de monitoramento a partir do texto exibido na tela (parsing de string) era frágil e causava oscilação visual (o botão piscava entre estados) durante a janela assíncrona entre o clique do usuário e a confirmação do backend introduzida na ADR-047.

## Decisão
Substituição da validação via parsing de string `statusBadge.innerText.includes('Ativo')` por um estado booleano otimista `_isWebMonitoringActive`. Ao clicar no botão de Iniciar Monitoramento, a UI altera o botão para o estilo vermelho de Pausar e fixa o status em `Monitoramento Ativo` com indicador animado de varredura sem reverter ou oscilar durante o fetch inicial.

## Consequências
Elimina o flicker visual, dando ao usuário uma transição de estado suave e previsível ao iniciar o monitoramento. Passa a depender de um estado local otimista que precisa ser corretamente revertido caso o backend efetivamente falhe ao iniciar.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
