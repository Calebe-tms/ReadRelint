# ADR-0008: Repositório Universal (Sem Descartes)

- Status: Aceita
- Data: não registrada

## Contexto
Descartar boletins durante a ingestão (por exemplo por não se encaixarem em uma categoria esperada) cria risco de perda silenciosa de dados e dificulta auditar o que foi lido versus o que foi processado.

## Decisão
Nenhum boletim válido lido do diretório deve ser silenciado. Todos devem ir para o banco. A filtragem de "ocorrências indesejadas" ocorre apenas na UI.

## Consequências
Garante rastreabilidade total de tudo que foi lido do diretório monitorado, sem perda silenciosa de boletins. Como efeito colateral, o banco acumula registros que a UI precisa saber filtrar, deslocando essa responsabilidade para a camada de apresentação.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
