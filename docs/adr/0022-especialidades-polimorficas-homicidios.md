# ADR-0022: Especialidades Polimórficas (Homicídios)

- Status: Aceita
- Data: não registrada

## Contexto
Diferentes tipos de ocorrência (homicídio, tráfico, roubo etc.) precisam de campos adicionais específicos, mas a maioria dos boletins compartilha a mesma estrutura base — criar uma tabela ou modelo totalmente separado por especialidade duplicaria lógica comum.

## Decisão
Criação de modelos Pydantic estendidos (`HomicideReport` herdando de `IncidentReport`) para suportar dados especializados (motivação, registro policial, unidade BPM) sem alterar a estrutura da tabela SQLite.

## Consequências
Permite reaproveitar toda a lógica genérica de `IncidentReport` enquanto acrescenta campos específicos por especialidade de forma tipada. A modelagem polimórfica, porém, aumenta a complexidade de persistência e leitura, exigindo tratamento por `isinstance()` em vários pontos do código.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
