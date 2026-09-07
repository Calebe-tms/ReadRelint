# ADR-0051: Proteção de Estado Visual com Flag Atômica (`_isTogglingLLM`)

- Status: Aceita
- Data: não registrada

## Contexto
O polling periódico de atualização dos gráficos (a cada 5 segundos) podia sobrescrever o estado visual de carregamento do botão de teste de IA no meio de sua própria operação assíncrona, deixando o botão preso em estado desabilitado após o uso.

## Decisão
Adição de um sistema de bloqueio local no UI para proteger o estado de Loading otimista do botão de IA (`Testando IA...`) contra atropelamentos causados pelo laço de *polling* de 5 segundos dos gráficos. Garante o feedback visual em tempo real ininterrupto e soluciona o bug que travava o botão desabilitado após o uso (`btnLLM.disabled = true/false`).

## Consequências
Elimina o bug de botão travado e garante feedback visual consistente durante a alternância de IA. Introduz mais um estado de flag local que precisa ser corretamente limpo em todos os caminhos de sucesso e erro para não reintroduzir o travamento.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
