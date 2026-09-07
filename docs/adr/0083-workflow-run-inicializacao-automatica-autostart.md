# ADR-0083: Workflow `/run` e Inicialização Automática em Primeiro Plano (`--autostart`)

- Status: Aceita
- Data: não registrada

## Contexto
Iniciar o ambiente completo de desenvolvimento/uso (app desktop, backend e frontend) exigia vários passos manuais e cliques sequenciais, um atrito repetido a cada nova sessão de trabalho com o sistema.

## Decisão
Criação do workflow `.agents/workflows/run.md` (`/run`) e suporte à flag `--autostart` no `painel.py` e `desktop/ui/pyqt_app.py`. A inicialização garante foco imediato da janela (`show_and_raise()`) e aciona automaticamente via timer assíncrono o servidor Backend FastAPI (:8000), o dev server SvelteKit (:5173) e a abertura do Dashboard no navegador padrão.

## Consequências
Reduz o atrito de inicialização a um único comando/flag, automatizando um fluxo antes manual e repetitivo. A automação via timer assíncrono precisa lidar corretamente com falhas de inicialização de qualquer um dos serviços para não deixar o sistema em estado parcialmente iniciado sem aviso claro.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
