# ADR-0068: Thread-Safety de Atualizações de Progresso do ETL via `pyqtSignal` (`StatsEmitter`)

- Status: Aceita
- Data: não registrada

## Contexto
O `MainController` roda a extração de RELINTs em threads de trabalho separadas da UI; atualizar widgets Qt diretamente a partir dessas threads viola o modelo de thread-safety do Qt (que exige que widgets sejam tocados apenas pela main thread), com risco de corrupção de estado ou crash.

## Decisão
Encapsulamento das notificações de contadores e barras de progresso do `MainController` através de um `QObject` com `pyqtSignal` (`stats_updated = pyqtSignal()`). Garante que modificações em widgets da interface sejam despachadas com segurança para o event loop principal do Qt, mantendo a janela 100% responsiva durante a extração contínua e intensiva de relatórios.

## Consequências
Garante atualizações de progresso seguras e responsivas durante processamento intensivo em segundo plano, seguindo o padrão correto de sinais/slots do Qt. Exige que qualquer nova métrica de progresso passe pelo mesmo padrão de `pyqtSignal` para não reintroduzir acesso inseguro a widgets.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
