# ADR-0078: Monitoramento Silencioso de Portas via Sockets TCP e Travas de Transição no PyQt6

- Status: Aceita
- Data: não registrada

## Contexto
Mesmo após mover a checagem de serviços para background (ADR-070), o uso de `subprocess` chamando `netstat` no Windows abria uma janela de console visível momentaneamente, um efeito colateral visualmente incômodo, além de o polling contínuo poder sobrescrever o estado visual de botões em transição de estado.

## Decisão
Substituição total de chamadas a `subprocess` (`netstat`) por verificações de conectividade nativas via `socket.connect_ex` no Python. Elimina completamente as piscadas de console/CMD no Windows durante o polling do `ServiceWatcher`. Implementação de flags atômicas de transição (`_is_transitioning_backend`, `_is_transitioning_frontend`, `_is_transitioning_dashboard`) para impedir que a thread de polling sobrescreva o estado transitório dos botões antes que os serviços concluam a inicialização ou parada.

## Consequências
Elimina completamente o incômodo visual das janelas de console piscando no Windows, usando checagem de socket nativa e silenciosa. As flags atômicas de transição adicionam estado que precisa ser corretamente resetado ao final de cada operação para não travar os botões permanentemente em estado de transição.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
