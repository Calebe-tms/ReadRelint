# ADR-0024: Classificação Determinística por Regex (`bm_classifier.py`)

- Status: Aceita
- Data: não registrada

## Contexto
Depender exclusivamente do LLM para classificar o grupo de boletim (`bm_group`) introduz variabilidade e risco de erro de classificação, especialmente quando o vocabulário do assunto/nome de arquivo já é formulaico o suficiente para um regex resolver com precisão.

## Decisão
Adição de uma camada de segurança determinística pós-LLM que classifica o `bm_group` baseado em padrões de texto no nome do arquivo, assunto e conteúdo ordenados por especificidade.

## Consequências
Aumenta a confiabilidade da classificação ao remover a dependência de julgamento probabilístico da IA para uma tarefa essencialmente padronizada. Exige, em contrapartida, manter e evoluir um conjunto de padrões regex ordenados por especificidade conforme novos formatos de boletim aparecem.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
