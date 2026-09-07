# ADR-0046: Otimização de E/S em Disco no Início do Monitoramento (`remove_records_bulk`)

- Status: Aceita
- Data: não registrada

## Contexto
O registro de curadoria humana (`processed_registry.json`, ADR-006) era reescrito em disco individualmente para cada arquivo removido durante o início do monitoramento, um padrão de I/O ineficiente que crescia linearmente com o número de arquivos a remover.

## Decisão
Eliminação do gargalo de ~5 segundos no método `start_monitoring()`. A implementação anterior executava `remove_record()` síncrono para cada PDF não cadastrado, relendo e re-escrevendo o arquivo JSON `processed_registry.json` em disco N vezes consecutivas. Introdução da remoção em lote `remove_records_bulk()`, reduzindo o tempo de execução do comando de 5.000ms para 0.00ms.

## Consequências
Torna o início do monitoramento praticamente instantâneo, eliminando um gargalo perceptível pelo usuário. A operação em lote exige que `remove_records_bulk()` seja mantida como o único caminho correto de remoção múltipla, evitando regressão para o padrão antigo.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
