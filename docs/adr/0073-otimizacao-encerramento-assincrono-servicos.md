# ADR-0073: Otimização de Encerramento Assíncrono de Serviços (Zero Lag UI)

- Status: Aceita
- Data: não registrada

## Contexto
Encerrar a aplicação exigia derrubar subprocessos externos (como o dev server `npm/vite` do SvelteKit), uma operação que, se executada de forma síncrona na main thread ao fechar a janela, causava congelamento perceptível da interface no momento da saída.

## Decisão
Reformulação da Aba 2 no PyQt6 (`desktop/ui/pyqt_app.py`) mantendo cartões estritamente informativos de status (sem botões redundantes). Ocultamento instantâneo da janela (`self.hide()`) e migração do desligamento de subprocessos (`npm/vite`) e servidores para thread secundária em `_force_quit_app()`, eliminando congelamentos de interface na saída do app.

## Consequências
Torna o fechamento do aplicativo instantâneo do ponto de vista do usuário, escondendo a janela imediatamente enquanto o encerramento real dos processos ocorre em segundo plano. Exige garantir que a thread secundária de fato finalize todos os subprocessos antes do processo principal terminar, para não deixar processos órfãos.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
