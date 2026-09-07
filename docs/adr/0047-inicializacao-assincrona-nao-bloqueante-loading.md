# ADR-0047: Inicialização Assíncrona Não-Bloqueante & Loading Explicativo de Varredura

- Status: Aceita
- Data: não registrada

## Contexto
Iniciar o monitoramento de uma pasta grande envolvia uma varredura inicial que podia levar segundos; rodar isso de forma síncrona dentro da requisição HTTP deixava a UI parecendo travada até a resposta retornar.

## Decisão
Desacoplamento da execução do método `start_monitoring()` do ciclo de vida da requisição HTTP `/monitoring/start`. O endpoint retorna resposta 200 em < 1ms e transfere a varredura inicial da pasta para uma thread daemon em segundo plano (`_async_start_monitoring_task`). No frontend Web, o manipulador `toggleWebMonitoring()` atualiza instantaneamente o estado visual para `Inicializando varredura da pasta...` com ícone de spinner animado, fornecendo feedback tátil e eliminando qualquer sensação de congelamento da interface.

## Consequências
A UI responde instantaneamente ao clique do usuário, com feedback visual claro de que a varredura está em andamento em segundo plano. Introduz um estado transitório de inicialização que a UI precisa representar corretamente até a varredura de fato concluir.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
