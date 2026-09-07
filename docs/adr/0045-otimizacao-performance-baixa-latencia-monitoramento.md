# ADR-0045: Otimização de Performance e Baixa Latência no Fluxo de Monitoramento

- Status: Aceita
- Data: não registrada

## Contexto
O endpoint de status de monitoramento, consultado repetidamente pela UI, carregava todos os registros do banco para apenas contar quantos existiam, gerando um padrão clássico de consulta N+1 que degradava a performance conforme o volume de RELINTs crescia.

## Decisão
Eliminação do gargalo N+1 no endpoint `/monitoring/status` com substituição de `db_repo.get_all()` por `get_report_counts()` em 1 query SQL de 0.1ms. Otimização O(1) de varredura de diretórios via `get_all_source_filenames()`, finalização síncrona de `worker_thread` ao pausar e ajuste do timeout do Ollama para 25s.

## Consequências
Reduz drasticamente a latência do endpoint de status, mantendo a UI responsiva mesmo com grande volume de dados. Consolida um conjunto de otimizações pontuais (query agregada, varredura O(1), timeout ajustado) que precisam continuar sendo monitoradas conforme o volume de dados aumenta.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
