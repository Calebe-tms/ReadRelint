# ADR-0042: Reorganização do Monitoramento Web em Sub-Abas com Terminal de Logs na Coluna Direita

- Status: Aceita
- Data: não registrada

## Contexto
O painel de monitoramento acumulava logs e relatório de leitura na mesma área visual, comprimindo ambos e dificultando a leitura contínua do console em sessões longas de processamento.

## Decisão
Reposicionamento do `Console de Logs do Sistema em Tempo Real` para a coluna da direita do painel de monitoramento, expandindo a área do terminal para preenchimento vertical constante. Isolamento do `Relatório de Leitura` em uma sub-aba dedicada em tela cheia com busca em tempo real, filtros de extração (`Ollama` vs `Regex`) e badge de contagem dinâmica.

## Consequências
Melhora a legibilidade do console de logs (agora com altura dedicada) e dá ao relatório de leitura seu próprio espaço com busca e filtros. Aumenta a complexidade estrutural da tela de monitoramento com sub-abas adicionais.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
