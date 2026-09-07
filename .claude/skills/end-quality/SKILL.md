---
description: Finalização completa de sessão — sincroniza .agents/.claude, roda revisão de segurança, atualiza docs/, atualiza ADR se necessário, commita e dá push. Use quando o usuário digitar /end-quality.
disable-model-invocation: true
---

Encerramento completo de sessão de trabalho. Execute os passos na ordem,
sem pular nenhum. É mais lento que `/end-fast` de propósito — é o
encerramento "capricha".

## 1. Sincronizar `.agents/` ↔ `.claude/` (rules e skills)

Objetivo: `.agents/rules/` e `.claude/rules/` ficam com o mesmo conteúdo
por arquivo; o mesmo vale para `.agents/skills/` e `.claude/skills/`.
Regra de conflito: **o arquivo mais recentemente modificado vence** e é
copiado por cima do outro lado.

Procedimento:
1. Garanta que `.agents/rules/`, `.agents/skills/`, `.claude/rules/` e
   `.claude/skills/` existem (crie vazias se faltar alguma).
2. Liste todos os caminhos relativos (recursivo) presentes em
   `.agents/rules/` + `.agents/skills/` e em `.claude/rules/` +
   `.claude/skills/`.
3. Para um caminho relativo que existe só de um lado, copie pro outro
   lado (criando subpastas necessárias).
4. Para um caminho relativo que existe dos dois lados, compare a data de
   modificação (ou conteúdo, se a data não for confiável) e copie a
   versão mais nova por cima da mais antiga, deixando os dois lados
   idênticos.
5. **Nunca apague** um arquivo que existe só de um lado — a operação é
   só de cópia, nunca remoção.
6. Não inclua `.claude/settings.json` nem `.claude/settings.local.json`
   nessa sincronização — não fazem parte do conteúdo espelhado.

## 2. Revisão de segurança

Use a skill `security-review` (já disponível neste ambiente) para revisar
as mudanças pendentes da branch atual. Trate os achados normalmente:
aplique correções que façam sentido, reporte o que não foi corrigido.

## 3. Atualizar documentação em `docs/`

Revise `git diff`/`git log` desde o último commit relevante e atualize os
arquivos afetados em `docs/` para refletir o estado atual do sistema:
`docs/architecture.md`, `docs/folder-structure.md`,
`docs/conventions/*.md`, `docs/components/*.md`, `docs/forms/*.md`. Só
altere o que de fato mudou — não reescreva arquivos sem necessidade.

Se alguma **decisão de arquitetura nova** foi tomada na sessão, crie uma
ADR nova em `docs/adr/` seguindo `docs/adr/template.md` (número sequencial
seguinte, nunca edite uma ADR `accepted` existente — marque como
`superseded by ADR-000Y` se uma decisão antiga mudou) e atualize
`docs/adr/README.md`. Se nada de arquitetura mudou, pule esta parte.

## 4. Commit

- Revise `git log --oneline -10` pra seguir o estilo de mensagem já usado.
- `git status` pra ver tudo que a sincronização + revisão + docs
  produziram; `git add` só o relevante (nunca `-A`/`.` sem revisar).
- Commit com mensagem clara, terminando com:
  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  ```
- Se a árvore estiver limpa (nada mudou em lugar nenhum), informe isso e
  pule commit/push.

## 5. Push

Descubra a branch atual (`git branch --show-current`):
- Upstream já configurado: `git push`.
- Sem upstream: `git push -u origin <branch-atual>`.
- **Nunca force push.** Se falhar, reporte o erro exato e pare.

## 6. Resumir

Feche com um resumo: o que foi sincronizado, o que a revisão de segurança
encontrou (e o que foi corrigido), quais docs foram atualizados, se ADR
nova foi criada, e o resultado do commit/push.
