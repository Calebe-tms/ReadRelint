# ADR-0105: "Limpar Base & Reprocessar Tudo" Nunca Mais Afeta o Módulo Gerenciador de Pessoas

- Status: Aceita
- Data: 2026-09-08

## Contexto

O botão "🧹 Limpar Base & Re-processar Tudo" do painel desktop (`desktop/controllers/main_controller.py::reset_and_reprocess_all()`) foi desenhado antes do módulo Gerenciador de Pessoas existir, numa época em que a tabela `pessoas` só continha gente derivada de participantes de RELINTs — fazia sentido zerá-la junto com os RELINTs. Duas chamadas explícitas apagavam essa tabela: `SqliteRepo.clear_all()` (que já fazia `DELETE FROM relints;` e também `DELETE FROM pessoas;`) e, redundantemente, `SqlitePersonRepo.clear_all()` logo em seguida.

Com o Gerenciador de Pessoas (ADR-0101/0102), `pessoas` passou a ser a base de dados reais e valiosos importados de uma planilha externa (App-AJ: 1693 pessoas, com `dados_aj`, grupos criminosos/familiares, veículos e QRBs vinculados) — dados completamente independentes de qualquer RELINT. Clicar no botão apagaria essa importação inteira sem aviso nenhum, exigindo reimportar a planilha do zero pra recuperar.

## Decisão

`reset_and_reprocess_all()` passa a limpar **estritamente** os dados de leitura de RELINTs, nunca `pessoas` nem qualquer tabela do módulo Gerenciador de Pessoas:
1. `SqliteRepo.clear_all()`: removida a linha `DELETE FROM pessoas;`. Só `DELETE FROM relints;` — como `relint_participantes`, `relint_imagens` e as 6 tabelas `*_detalhes` de especialidade têm `FOREIGN KEY ... ON DELETE CASCADE` para `relints.id` (e o app já roda com `PRAGMA foreign_keys = ON`), elas são limpas automaticamente em cascata. `pessoas` não é filha de `relints` — nunca é tocada.
2. A chamada redundante `self.person_repo.clear_all()` foi removida de `main_controller.py` por completo.
3. Texto do diálogo de confirmação (`desktop/ui/pyqt_app.py::_reset_etl_data`) reescrito pra descrever com precisão o que de fato acontece, deixando explícito que o Gerenciador de Pessoas não é afetado.

A limpeza de `data/media/` (fotos extraídas de RELINTs) permanece intacta e continua segura: as fotos do Gerenciador de Pessoas vivem em `data/pessoas_Images/`, uma pasta irmã fora de `data/media/`, então nunca são apagadas por este fluxo.

`SqlitePersonRepo.clear_all()` (o método em si) fica no código, sem nenhum chamador em produção agora — não foi deletado por não ser o foco desta correção, mas é um candidato claro a cleanup futuro caso nenhuma outra necessidade surja pra ele.

## Consequências

Reprocessar RELINTs do zero não corre mais o risco de apagar acidentalmente os dados importados do Gerenciador de Pessoas. Teste de regressão adicionado em `tests/dashboard/test_sqlite_repo.py::test_clear_all_wipes_relints_but_never_touches_pessoas`, travando esse comportamento contra reintrodução futura do bug.
