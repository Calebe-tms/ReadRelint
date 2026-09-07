# ADR-0065: Migração do Painel Desktop para Flet (Flutter) e Isolamento na Raiz (/desktop)

- Status: Aceita
- Data: não registrada

## Contexto
O CustomTkinter, apesar de melhorias visuais aplicadas em ADRs anteriores (028, 036), continuava limitado em termos de reatividade e componentes modernos de UI quando comparado a frameworks baseados em Flutter como o Flet.

## Decisão
Substituição do CustomTkinter pelo Flet para a interface desktop. Isso permitiu construir uma UI moderna, reativa, com suporte a seleção de pastas nativa, console de logs interativo e gerenciamento de serviços.

## Consequências
Trouxe uma interface desktop mais moderna e reativa no curto prazo. Essa decisão foi posteriormente revertida (ver ADR-066), o que sugere que o Flet não se mostrou a escolha definitiva para as necessidades de estabilidade do projeto no ecossistema Windows.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
