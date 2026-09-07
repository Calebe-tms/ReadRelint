---
description: Finalização rápida de sessão — atualiza ADR se necessário, commita e dá push na branch atual. Use quando o usuário digitar /end-fast.
disable-model-invocation: true
---

Encerramento rápido de sessão de trabalho. Execute os passos na ordem,
sem pular nenhum.

## 1. Levantar o que mudou

Rode `git status` e `git diff` (staged e unstaged) para ver exatamente o
que foi alterado nesta sessão. Se a árvore estiver limpa (nada mudou),
informe isso e pare aqui — não crie ADR nem commit vazio.

## 2. Atualizar ADR (só se necessário)

Se, e somente se, alguma **decisão de arquitetura nova** foi tomada nesta
sessão (não é toda mudança de código que vira ADR — só decisão estrutural:
nova biblioteca, novo padrão, mudança de abordagem), crie uma ADR nova em
`docs/adr/`, seguindo `docs/adr/template.md`:
- Número sequencial seguinte ao último existente em `docs/adr/`.
- **Nunca edite uma ADR já `accepted`.** Se uma decisão antiga mudou, crie
  uma ADR nova e marque a antiga como `superseded by ADR-000Y` (você pode
  editar só a linha de Status da antiga pra isso, não o resto do conteúdo).
- Atualize `docs/adr/README.md` incluindo a nova linha na tabela.

Se nenhuma decisão de arquitetura nova foi tomada, pule este passo.

## 3. Commit

Se há mudanças (do passo 1), monte um commit:
- Revise `git log --oneline -10` pra seguir o mesmo estilo de mensagem já
  usado no repositório.
- `git add` só os arquivos relevantes (nunca `git add -A`/`.` sem revisar).
- Commit com mensagem clara sobre o que mudou e por quê, terminando com:
  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  ```

## 4. Push

Descubra a branch atual (`git branch --show-current`). Dê push nela:
- Se já existe upstream configurado: `git push`.
- Se não existe: `git push -u origin <branch-atual>`.
- **Nunca force push.** Se o push falhar (auth, repositório não encontrado,
  branch protegida, etc.), reporte o erro exato ao usuário e pare — não
  tente contornar com `--force` ou outras opções destrutivas.

## 5. Resumir

Feche com um resumo curto: o que foi commitado, se ADR nova foi criada, e
se o push teve sucesso.
