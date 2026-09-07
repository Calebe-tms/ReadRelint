# ADR-0029: Duas Barras de Progresso e Inspecção Instantânea de Diretório

- Status: Aceita
- Data: não registrada

## Contexto
Uma única barra de progresso misturava o total histórico de arquivos já lidos com o progresso da leitura em andamento, dificultando ao usuário entender quanto falta processar na sessão atual.

## Decisão
Inspecção imediata no `MainController.inspect_folder()` ao selecionar o diretório via `filedialog`. Separação em Barra 1 (`Arquivos Lidos na Pasta`) atualizada em tempo real a cada leitura concluída, e Barra 2 (`Progresso da Leitura Atual`) monitorando a fila ativa da sessão.

## Consequências
Dá ao usuário visibilidade clara e imediata tanto do volume total da pasta quanto do avanço da leitura corrente. Exige manter dois estados de progresso sincronizados na interface em vez de um único contador.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
