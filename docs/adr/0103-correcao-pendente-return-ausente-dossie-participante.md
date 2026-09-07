# ADR-0103: Correção Pendente — `get_participant_dossier()` Sem `return` no Caminho de Sucesso

- Status: Proposta
- Data: 2026-09-07

## Contexto

Durante a remoção de `chave_pessoa` ([ADR-0101](./0101-gerenciador-pessoas-schema-importacao-app-aj.md), seção "Segunda correção"), foi encontrado um bug pré-existente (não introduzido nesta sessão) em `get_participant_dossier()` (`backend/api/routers/participants.py`, endpoint `GET /api/v1/participants/{person_id}`): a função monta `linked_relints`/`photos` mas **não tem nenhum `return PersonDossierDTO(...)`** no caminho de sucesso — só o `raise HTTPException(404)` do caminho "não encontrado" retorna algo. Uma chamada bem-sucedida (pessoa existe) hoje retornaria `None` implicitamente, o que o FastAPI rejeitaria contra o `response_model=PersonDossierDTO` declarado (erro 500 em runtime).

Não foi pego antes porque a suíte de testes (`tests/modulo_pessoas/test_api_participants.py`) só cobre o caminho 404 (`test_get_participant_dossier_not_found`) — nenhum teste busca o dossiê de uma pessoa que de fato existe.

## Decisão

Ainda não implementada — usuário pediu para registrar a correção pendente sem aplicá-la agora. Quando for feita, a correção deve:
1. Adicionar `return PersonDossierDTO(...)` ao final do caminho de sucesso de `get_participant_dossier()`, espelhando a construção já feita em `list_participants()` (mesmos campos: `person_id=p_key`, `name`, `nickname`, `document=doc` — já com a blindagem contra chave sintética da ADR-0101 —, `background=bg`, `photo_path=main_photo`, `photos`, `linked_relints_count`, `linked_relints`).
2. Adicionar um teste que busque o dossiê de uma pessoa existente com sucesso (200), cobrindo o caminho hoje não testado.

## Consequências

Enquanto não corrigido, `GET /api/v1/participants/{person_id}` para uma pessoa existente falha em runtime (500), embora `GET /api/v1/participants` (lista) e o 404 funcionem normalmente — o bug só afeta a busca de dossiê individual bem-sucedida.
