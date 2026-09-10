# ReadRelint — Decisões e Fluxo de Trabalho da Sessão (2026-09-10)

## Decisões técnicas

- **Fonte de avatares de participantes**: usar `pessoa_fotos` (Gerenciador de Pessoas) em vez de `relint_participantes.caminho_foto` — o segundo é sempre vazio por desenho (ADR-0020: fotos extraídas de PDF não são auto-associadas a um participante). Registrado em ADR-0107.
- **Filtrar por existência real em disco**: em vez de normalizar cegamente qualquer prefixo de pasta salvo no banco, a API só expõe uma foto se o arquivo realmente existir em `data/pessoas_Images/` — evita ícones de imagem quebrada quando o dado de origem está incompleto (achado do ~45% de fotos `CRIMINOSOS_Images` ausentes).
- **Escopo do Gerenciador de Pessoas confirmado com o usuário**: só criminosos/vítimas; militares nunca são cadastrados, em nenhum caso (nem como citados, nem como autores). Isso significa que um RELINT sem nenhum participante extraído, quando o único envolvido é um PM, **não é um bug de extração** — é o comportamento correto do filtro anti-PM (`is_blacklisted_name`).

## Bloqueios superados

- **`get_participant_dossier()` sem `return`** (ADR-0103, já registrada como pendente numa sessão anterior): corrigida nesta sessão porque a mesma função precisava ser tocada para incluir as fotos — não foi scope creep, era pré-requisito para o dossiê individual funcionar de qualquer forma.
- **Tabela `pessoa_fotos` pode não existir** em bancos de teste criados via `SqlitePersonRepo` (ela é criada só pela migração Alembic do módulo Gerenciador de Pessoas, ADR-0102) — a consulta de fotos verifica a existência da tabela antes (`sqlite_master`) para não quebrar esses ambientes.
- **Verificação sem interromper o app do usuário**: `painel.py --autostart` já ocupava as portas 8000/5173 quando tentei validar a mudança. Em vez de matar esse processo, subi uma instância temporária do backend numa porta separada (8123) só para validar via curl + screenshot, e encerrei depois. O usuário reiniciou o `painel.py` por conta própria depois para ver a mudança valendo de verdade.

## Mudanças de rota

- Nenhuma mudança de rota nesta sessão — o plano original (montar pasta estática, expor via API, sem tocar o Svelte) foi confirmado e seguido sem alteração.

## Processo/workflow

- Comando `python start_web.py` (citado no skill `run`) não existe mais na raiz do projeto — hoje o backend é subido via `uvicorn backend.api.app:app` diretamente ou pelo próprio `painel.py`. Vale atualizar o skill `run`/`.claude/launch.json` numa próxima sessão se isso continuar causando fricção.
