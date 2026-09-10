# ReadRelint — Estado do Projeto

_Última atualização: 2026-09-10_

## Concluído nesta sessão

- **Auditoria pontual de dados faltantes na extração via LLM** (banco local de teste, 28 RELINTs): confirmado que os bugs já corrigidos em 08/09 (placeholders vazando, `location_types` não persistido) continuam corrigidos — nenhuma reincidência. Vazios remanescentes (`coordenadas`, `numero_registro`, `hora_fato`) são esperados por desenho, não bugs.
- **Avatares de participantes na aba `/participantes`** (ADR-0107): API passou a buscar fotos em `pessoa_fotos` (módulo Gerenciador de Pessoas), filtrando por existência real do arquivo em disco. Nova pasta estática `/pessoas_images`.
- **Corrigido bug pré-existente** (já registrado como pendente na ADR-0103): `get_participant_dossier()` não tinha `return` — endpoint de dossiê individual sempre falhava com 500. Corrigido + testado.
- Testes novos em `tests/modulo_pessoas/test_api_participants.py` (dossiê com sucesso, filtragem de fotos ausentes) — 7/7 passando.

## Bugs/gaps conhecidos (não corrigidos, registrados para decisão futura)

1. **~45% das fotos em `pessoa_fotos` (850/1901) referenciam arquivos que nunca existiram em disco** (`CRIMINOSOS_Images/...`, nome de pasta legado da planilha original). Não é bug de código — dado de origem ausente. Resolver exige localizar/reimportar os arquivos originais do App-AJ. Ver `docs/adr/0107-avatares-participantes-gerenciador-pessoas.md`.
2. **Auditoria formal de 08/09 (`docs/proposals/auditoria-pos-reprocessamento-2026-09.md`), Estágio 2**: prompt de auditoria não distingue enum fechado (`grupo_bm`, `tipo_relint`) de campo narrativo — números de inconsistência de `Grupo BM`/`Resumo`/`Fato Principal` (73-82%) estão inflados e não são confiáveis como estão. Correção do prompt foi dispensada pelo usuário na sessão anterior — ainda pendente se algum dia quiserem repetir o Estágio 2.
3. **Os 602 RELINTs de produção não foram reprocessados** com as correções de engine aplicadas em 08/09 (placeholders, `location_types`, `_strip_antecedentes`). O banco local de teste (28 RELINTs) já reflete as correções; a base completa, não — decisão de reprocessar ainda não foi tomada.
4. **`main_fact` nunca é derivado por lógica própria** — é sempre cópia de `summary`. Comportamento aceito, não é um bug a corrigir, só uma limitação de desenho conhecida.

## Ambiente local

- O usuário mantém `painel.py --autostart` rodando permanentemente (portas 8000/5173) como app real de uso diário — **não reiniciar sem avisar**. Para testar mudanças de backend, subir instância temporária em porta alternativa (ex: 8123) e encerrar depois.
- Banco local (`data/relints.db`) tem só 28 RELINTs processados — um subconjunto de teste, não a base de produção completa (602 RELINTs mencionados na auditoria de 08/09).

## Por onde continuar na próxima sessão

- Se o usuário voltar a perguntar sobre fotos/avatares faltando: já é esperado que participantes só extraídos de RELINT (sem contraparte no App-AJ) não tenham foto — não investigar de novo, ver achado 1 acima.
- Se for decidido reprocessar os 602 RELINTs de produção: rodar `python scripts/audit_extracted_fields.py` depois, comparar com o baseline de `docs/proposals/auditoria-pos-reprocessamento-2026-09.md`.
- Nenhuma tarefa em andamento/inacabada foi deixada pendente nesta sessão.
