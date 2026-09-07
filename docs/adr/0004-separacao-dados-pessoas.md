# ADR-0004: Separação de Dados de Pessoas

- Status: Aceita
- Data: não registrada

## Contexto
Sem uma entidade própria para pessoas, cada RELINT armazenaria participantes de forma isolada, impossibilitando identificar rapidamente que a mesma pessoa aparece em múltiplos boletins.

## Decisão
Criação da tabela e domínio independente de `Person` no SQLite (`persons`). Garante dossiês hiper-velozes e cruzamento de vínculos de pessoas através dos RELINTs.

## Consequências
Permite montar dossiês individuais e cruzar reincidências entre RELINTs com consultas diretas. Introduz a necessidade de lógica de deduplicação/vínculo entre participantes extraídos e registros de pessoa já existentes.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
