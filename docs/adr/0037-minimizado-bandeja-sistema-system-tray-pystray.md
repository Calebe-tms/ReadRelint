# ADR-0037: Minimizado para a Bandeja do Sistema (System Tray) via `pystray`

- Status: Aceita
- Data: não registrada

## Contexto
Fechar a janela do app desktop não deveria encerrar o monitoramento de pastas nem o servidor Web, já que ambos precisam continuar rodando em segundo plano mesmo sem a interface visível.

## Decisão
Interceptação do protocolo `WM_DELETE_WINDOW` para ocultar a janela (`withdraw`) e manter o monitoramento de pastas e o servidor Web em segundo plano com suporte a menu de contexto no tray.

## Consequências
O usuário pode fechar a janela sem interromper os serviços essenciais, mantendo o sistema disponível via bandeja do sistema. Isso exige gerenciar corretamente o ciclo de vida do processo para evitar que ele fique invisível e difícil de encerrar de fato quando necessário.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
