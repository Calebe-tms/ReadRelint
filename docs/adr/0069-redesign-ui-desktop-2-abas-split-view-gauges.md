# ADR-0069: Redesign da UI Desktop em 2 Abas Estratégicas (Split View & Gauges Circulares Vetoriais)

- Status: Aceita
- Data: não registrada

## Contexto
Após a consolidação em PyQt6 (ADR-066) e a transformação do app em hub minimalista (ADR-049, já no contexto do Tkinter anterior), a nova base Qt permitia reconstruir a interface com um número reduzido de abas focadas, priorizando os fluxos de operação central e diagnóstico.

## Decisão
Reorganização total da interface PyQt6 (`desktop/ui/pyqt_app.py`). A Aba 1 condensa a operação central em Split View 50/50: controles e seletor de pasta, ações rápidas (Modo IA e botão com abertura automática do Dashboard Web), dois medidores circulares estilizados (`CircularGauge` via `QPainter` antialiased estilo Apple Watch) e terminal de logs com altura completa na coluna direita. A Aba 2 agrega o diagnóstico de serviços (Backend FastAPI, Frontend SvelteKit, Monitor) e histórico de relatórios com reprocessamento direto.

## Consequências
Concentra a operação do dia a dia em uma única tela densa e informativa (Aba 1), deixando diagnóstico e histórico isolados (Aba 2). Os medidores circulares customizados via `QPainter` exigem manutenção própria de renderização, ao invés de depender de widgets prontos do framework.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
