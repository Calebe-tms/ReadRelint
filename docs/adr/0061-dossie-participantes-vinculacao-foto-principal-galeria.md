# ADR-0061: Dossiê de Participantes & Vinculação de Foto Principal e Galeria

- Status: Aceita
- Data: não registrada

## Contexto
Após decidir não associar fotos automaticamente a participantes (ADR-020), o sistema precisava de um mecanismo manual e centralizado para que o analista pudesse, quando desejasse, vincular fotos já extraídas a uma pessoa específica e consultar seu histórico consolidado.

## Decisão
Implementação do router REST `participants.py` (`participants.py`) e da interface SPA `participants_view.js` (`participants_view.js`). No modal de edição de RELINTs (`relints_view.js`), o revisor pode vincular uma foto extraída do PDF a cada participante. Na aba **Participantes**, a aplicação exibe cards com foto de perfil, busca em tempo real, filtro de reincidentes (`X Ocorrências`) e o modal de **Dossiê do Indivíduo** com galeria de fotos cruzadas e histórico de RELINTs vinculados.

## Consequências
Cria uma visão unificada e investigativa por pessoa, aproveitando a base de dados de pessoas (ADR-004) para revelar reincidência entre RELINTs. Exige manter a integridade da vinculação manual foto-participante ao longo de futuras edições e reprocessamentos.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
