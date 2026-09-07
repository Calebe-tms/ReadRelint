# ADR-0079: Indicadores Reativos de Carregamento e Diagnóstico no Console de Logs

- Status: Aceita
- Data: não registrada

## Contexto
Com várias operações assíncronas em segundo plano (checagem de IA, subida de servidores, reprocessamento), o usuário não tinha um indicador visual unificado e imediato de que algo estava em andamento no console, além dos logs de texto em si.

## Decisão
Adição de badge animado dinâmico com spinner (`⠋ ⠙ ⠹...`) e barra de progresso indeterminada de 3px no cabeçalho do console do PyQt6, refletindo em tempo real atividades em segundo plano (verificação de IA, inicialização de FastAPI/SvelteKit, reindexação e reprocessamento individual de RELINTs).

## Consequências
Dá ao usuário um sinal visual rápido e contínuo de atividade em segundo plano, complementando os logs textuais do console. É um refinamento de feedback visual, sem alterar o comportamento funcional das operações monitoradas.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
