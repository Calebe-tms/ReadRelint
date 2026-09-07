# ADR-0040: Botão Dinâmico de Servidor Web e Centralização das Ações Globais na Aba Status

- Status: Aceita
- Data: não registrada

## Contexto
Ações globais de controle do servidor Web estavam espalhadas em abas que deveriam ser dedicadas a outras funções (como monitoramento de diretório), confundindo o modelo mental do usuário sobre onde encontrar cada controle.

## Decisão
Centralização das ações de abrir/fechar o servidor Web FastAPI e encerramento total do sistema na aba `StatusTab`, com botão dinâmico que alterna entre `Iniciar & Abrir Painel Web` (offline) e `Parar Servidor Web` + `Reabrir Dashboard` (online). Limpeza total da aba `ControlPanelTab` para focar estritamente em operações de monitoramento de diretório.

## Consequências
Simplifica a navegação ao concentrar as ações globais em um único lugar coerente (StatusTab), com feedback visual claro do estado atual via botão dinâmico. A aba de controle de pasta fica mais enxuta e focada em sua responsabilidade específica.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
