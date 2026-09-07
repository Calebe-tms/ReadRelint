# ADR-0066: Migração Definitiva do Painel Desktop para PyQt6 (Qt6 Nativo)

- Status: Aceita
- Data: não registrada

## Contexto
A migração para Flet (ADR-065) revelou instabilidades e bugs de atributos em controles no ambiente Windows, o público-alvo primário da aplicação desktop, motivando a busca por um framework mais maduro e nativo nesse ecossistema.

## Decisão
Substituição do Flet pelo **PyQt6** com ponto de entrada em `painel.py` e interface em `desktop/ui/pyqt_app.py`. Motivo: Maior estabilidade nativa no ecossistema Windows, eliminação de bugs de atributos em controles e total compatibilidade com layouts Qt (QSS escuro moderno, QFileDialog, QTabWidget e QProgressBar). Todos os arquivos e dependências legadas do Flet foram removidos.

## Consequências
Traz estabilidade nativa comprovada no Windows e acesso a um ecossistema maduro de widgets Qt. Encerra o ciclo de trocas de framework desktop (Tkinter → Flet → PyQt6), consolidando PyQt6 como a base definitiva sobre a qual as ADRs seguintes de UI desktop são construídas.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
