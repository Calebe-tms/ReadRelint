# ADR-0070: Desacoplamento Total de UI a 60 FPS com ServiceWatcher e Fila de Logs Typewriter

- Status: Aceita
- Data: não registrada

## Contexto
Mesmo após desacoplar a checagem de rede da LLM (ADR-067), a interface desktop ainda disparava chamadas síncronas a `netstat` para verificar portas de serviço na main thread, além de despejar logs diretamente no `QTextEdit` de forma que podia travar a UI sob alto volume.

## Decisão
Eliminação de qualquer chamada síncrona a processos (`netstat`) na thread principal através de um `ServiceWatcher` rodando em background. Implementação de fila de logs em buffer (`collections.deque`) descarregada via `QTimer` e efeito *Typewriter* inteligente (auto-speed conforme carga) para manter a responsividade da UI, evitar travamentos de QTextEdit e impedir crashes de timeout na aplicação (`QTextCursor.MoveOperation`). Janela livremente redimensionável com a coluna esquerda estritamente fixada em 410px.

## Consequências
Garante 60 FPS consistentes mesmo sob checagem contínua de serviços e alto volume de logs, através de background thread e buffer com descarga controlada. O efeito Typewriter com auto-speed adiciona complexidade de renderização que precisa equilibrar legibilidade com performance sob carga variável.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
