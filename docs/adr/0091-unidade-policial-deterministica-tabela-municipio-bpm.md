# ADR-0091: Unidade Policial 100% Determinística via Tabela Município → BPM (Substitui Extração por LLM)

- Status: Aceita
- Data: não registrada

## Contexto
Uma auditoria dos dados extraídos revelou viés de ancoragem do LLM: mais da metade dos registros era preenchida com o mesmo batalhão ("39º BPM"), a maioria sem qualquer menção literal a essa unidade no texto do boletim, indicando que o modelo estava "chutando" a opção mais frequente em vez de extrair um dado real.

## Decisão
Resolução de `police_unit` sai do prompt da LLM (eliminava viés de âncora identificado em auditoria — 56% dos registros preenchidos com "39º BPM", 70% deles sem sustentação textual) e passa a ser 100% determinística: tabela fixa de 41 municípios cobertos pelos 3 batalhões da região, com regra de mão dupla — 1 menção literal de BPM no texto vence sobre a tabela (cobre apoio mútuo entre batalhões); 0 ou múltiplas menções ambíguas caem para a tabela; município fora da tabela e sem menção fica vazio. Detalhamento completo em [`../proposals/melhorias-extracao-geo.md`](../proposals/melhorias-extracao-geo.md).

## Consequências
Elimina o viés de ancoragem observado, substituindo uma inferência probabilística pouco confiável por uma regra determinística auditável e testável. Introduz uma tabela de mapeamento município-batalhão que precisa ser mantida e atualizada caso a divisão territorial dos batalhões mude no futuro.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
