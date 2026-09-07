---
description: Início de sessão — sincroniza .agents/.claude, lê o histórico de decisões (ADR) e resume o que foi trabalhado na última sessão. Use quando o usuário digitar /init.
disable-model-invocation: true
---

Início de sessão de trabalho. Execute os passos na ordem.

## 1. Sincronizar `.agents/` ↔ `.claude/` (rules e skills)

Mesmo procedimento de `/end-quality`: `.agents/rules/` ↔ `.claude/rules/`
e `.agents/skills/` ↔ `.claude/skills/` ficam com conteúdo idêntico por
arquivo, o mais recentemente modificado vencendo em caso de conflito.

1. Garanta que as 4 pastas existem (crie vazias se faltar alguma).
2. Liste os caminhos relativos (recursivo) de cada lado.
3. Caminho que existe só de um lado: copie pro outro.
4. Caminho que existe dos dois lados: compare data de modificação (ou
   conteúdo) e copie a versão mais nova por cima da mais antiga.
5. Nunca apague um arquivo que existe só de um lado.
6. Não inclua `.claude/settings.json`/`.claude/settings.local.json`.

## 2. Ler o histórico de decisões

Leia `docs/adr/README.md` (índice) e, ao menos por cima, o conteúdo de
cada ADR listada ali — principalmente as mais recentes — pra ter o
contexto de arquitetura atualizado antes de começar a trabalhar.

## 3. Resumir a última sessão

Rode `git log --oneline -10` e `git status` pra ver o que foi feito
recentemente e se há algo pendente sem commit. Com base nisso (commits
recentes, arquivos alterados, ADRs novas encontradas no passo 2), escreva
um resumo **curto e direto** (poucas frases) do que foi trabalhado na
última sessão — não é pra listar tudo em detalhe, é uma orientação rápida
de "onde paramos".

## 4. Ler as rules e dizer quais estão em vigor

Liste os arquivos em `.claude/rules/` (já sincronizado no passo 1) e leia
cada um. Para cada arquivo, olhe o front matter YAML (entre `---` no topo)
procurando o campo `trigger`:

- `trigger: always_on` → regra sempre em vigor nesta sessão.
- Outro valor de `trigger` (ex.: `glob`, `manual`, `model_decision`) →
  regra condicional; diga qual é a condição, não assuma que está em vigor
  agora sem checar.
- Sem front matter, ou arquivo chamado `claude.md`/`CLAUDE.md` → carregado
  automaticamente pelo Claude Code como instrução permanente, independente
  de qualquer `trigger`.

Reporte pro usuário uma lista curta — um item por arquivo — com o nome, o
tipo de trigger e se está em vigor agora (e por quê).
