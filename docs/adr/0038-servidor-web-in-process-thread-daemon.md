# ADR-0038: Servidor Web In-Process via Thread Daemon (Sincronização Perfeita Tkinter & Web)

- Status: Aceita
- Data: não registrada

## Contexto
Rodar o Uvicorn como subprocesso externo isolava sua memória da instância do `MainController` na janela Tkinter, exigindo mecanismos de sincronização (IPC) entre os dois processos para manter os estados coerentes.

## Decisão
Substituição da execução por subprocesso externo do Uvicorn por uma thread daemon interna compartilhando a mesma memória do `MainController`. Garante que qualquer clique ou alteração de estado feita na Web reflita instantaneamente na interface Tkinter e vice-versa.

## Consequências
Elimina a necessidade de comunicação entre processos, garantindo estado sempre sincronizado entre desktop e web em tempo real. Em troca, um erro fatal no servidor Web passa a poder afetar a mesma memória/processo da aplicação desktop.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
