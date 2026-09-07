# Proposta: Termômetro de Certeza Generalizado por Campo

> Status: **Proposta em revisão** — nada aqui foi implementado ainda. Complementa [`melhorias-extracao-geo.md`](./melhorias-extracao-geo.md) (sugestão #7).

---

## 1. Motivação

Hoje o único campo com noção de confiabilidade é a geolocalização (`geo_precision`: Alta/Média/Baixa — ver ADR-007 e ADR-090 item 9). Todos os outros campos extraídos pela LLM (`unidade_policial`, `street`/`endereco`, `municipality`, etc.) são tratados como "certos ou errados" sem grau intermediário — e a auditoria mostrou que isso mascara um problema real: **47% das unidades policiais preenchidas não têm nenhuma evidência no texto** (ver proposta de melhorias, seção 2.2).

A regra de ouro pedida pelo usuário:
> "Quando não tiver certeza, a LLM deve deixar em branco. Isso se aplica a todos os campos."

O termômetro é o mecanismo que **decide objetivamente** o que conta como "certeza suficiente para preencher" vs. "deve ficar em branco" — generalizando o modelo que já existe para coordenadas.

---

## 2. Os 3 Níveis (reaproveitando o padrão visual já existente)

| Nível | Cor/Badge | Critério |
|---|---|---|
| 🟢 **Alta** | Verde | O valor tem **evidência literal direta** no texto bruto (`conteudo`) — match por regex/substring tolerante (case-insensitive, sem acento, tolerante a quebra de linha). |
| 🔵 **Média** | Azul | O valor **não tem match literal exato**, mas passa em uma validação indireta de plausibilidade (lista fechada de valores conhecidos, correspondência fuzzy, ou herança de um campo estrutural confiável do próprio documento). |
| ⚪ **Sem confiança → Campo vazio** | (sem badge) | Nenhuma evidência literal nem indireta. **O campo não é preenchido** — fica `""`/`null`, nunca um placeholder textual tipo "Não informado". |

Diferente do `geo_precision` atual (que sempre mostra algo, mesmo em "Baixa" — endereço só textual, sem coordenada), aqui **não existe um "Baixa" que ainda populado**: se a confiança cai abaixo do nível Média, o campo é limpo. Isso implementa literalmente a regra "quando não tiver certeza, deixe em branco".

---

## 3. Critérios por Campo

### 3.1. `unidade_policial` — *(atualizado: campo agora é 100% determinístico, não passa mais pela LLM — ver `melhorias-extracao-geo.md`, seção 6)*

Regra "via de mão dupla" confirmada com o usuário em 2026-09-03: a tabela município → BPM (41 municípios cobertos pelos 3 batalhões) é a fonte primária; a menção literal no texto funciona como validador que ajusta a confiança, não como fonte concorrente.

- **Alta**: exatamente 1 batalhão citado literalmente no texto (regex `\b(\d{1,2})[º°]?\s*BPM\b`) **e** ele bate com o valor da tabela para o município do RELINT.
- **Média**: qualquer um dos casos abaixo — o valor final ainda é preenchido, mas sinalizado para revisão:
  - Exatamente 1 batalhão citado no texto, mas **diverge** da tabela (usa o valor do texto — cobre apoio mútuo entre batalhões — só que com confiança reduzida).
  - Zero menções literais → usa o valor da tabela (inferência territorial pura, sem confirmação textual).
  - Mais de uma menção literal (texto ambíguo, cita mais de um batalhão) → usa o valor da tabela como desempate.
- **Vazio**: município fora da tabela de 41 cobertos **e** sem menção literal única no texto → descarta e deixa em branco (é o que deveria ter acontecido nos 187 casos de "39º BPM" sem sustentação, identificados na auditoria).

### 3.2. `street` / `endereco`
- **Alta**: nome da rua (normalizado: sem acento, case-insensitive, espaços colapsados) aparece literalmente no `conteudo`.
- **Média**: não há match exato, mas o fallback determinístico (`extract_street_and_number_fallback`) encontra um logradouro no texto com similaridade alta (ex.: distância de Levenshtein / `difflib.SequenceMatcher` ≥ 0.85) em relação ao valor da LLM — cobre casos de abreviação (`Av.` vs `Avenida`) ou pequena variação ortográfica.
- **Vazio**: sem match nem candidato fuzzy plausível → descarta (evita repetir o caso "Rua General Osório" cravada em 10 registros sem relação nenhuma com o texto).

### 3.3. `municipality`
- **Alta**: valor da LLM bate com a extração determinística do cabeçalho `ASSUNTO: ... EM [CIDADE] - RS` (já existe em `extract_municipality_from_context`).
- **Média**: valor da LLM não bate com o Assunto, mas aparece literalmente em outro trecho do corpo do texto.
- **Vazio**: nenhuma correspondência → força o valor do Assunto (comportamento determinístico que já existe hoje) ou deixa vazio se o Assunto também não tiver cidade.

### 3.4. `coordinates` (referência — já implementado, só formalizando no mesmo modelo)
- **Alta**: coordenadas decimais/DMS encontradas literalmente no texto.
- **Média**: coordenadas resolvidas a partir de um link do Google Maps presente no documento.
- **Vazio** *(hoje chamado de "Baixa" e ainda gera link de busca por endereço)*: sem coordenada nem link — mantém o comportamento atual (gera link de busca), pois aqui o "vazio" já é o próprio comportamento esperado.

---

## 4. Armazenamento Proposto

Nova coluna JSON na tabela `relints` (nome em pt-BR, seguindo a convenção do schema):

```sql
ALTER TABLE relints ADD COLUMN confianca_campos TEXT DEFAULT '{}';
```

Formato do JSON (chaves = nomes de coluna em pt-BR, valores = `"alta"` | `"media"`; ausência de chave = sem confiança/vazio):

```json
{
  "unidade_policial": "alta",
  "endereco": "media",
  "municipio": "alta"
}
```

- Segue o padrão de auto-migração já usado em `_init_db()` do `SqliteRepo` (`ALTER TABLE ... ADD COLUMN`), sem quebrar bancos existentes.
- `coordenadas` continua usando a lógica de precisão já existente (não duplicar em `confianca_campos`, a menos que se decida unificar tudo em um só lugar futuramente).

---

## 5. Onde Aplicar (UI)

Reaproveitar o componente de badge de precisão que já existe em `TabLocation.svelte` (3 cores) e replicar para:
- `unidade_policial` — provavelmente na aba **Especialidade** ou **Geral**.
- `street`/`endereco` — já convive com o badge de `geo_precision`; pode usar o mesmo badge ou um selo secundário menor.

Tooltip sugerido: *"Confiança: Alta — confirmado no texto original"* / *"Confiança: Média — inferido, revisão recomendada"*.

---

## 6. Vantagem Extra: Backfill sem reprocessar com a LLM

Como os critérios de Alta/Média são **puramente determinísticos** (regex + comparação de string contra o `conteudo` já salvo), é possível calcular `confianca_campos` retroativamente para os 562 registros existentes **sem precisar rodar o Ollama de novo** — um script único de backfill resolve isso, inclusive já aproveitando para zerar os campos que caírem em "vazio" pelos novos critérios (ex.: os 187 casos de "39º BPM" sem evidência).

---

## 7. Próximos Passos Sugeridos

- [ ] Confirmar se `confianca_campos` deve cobrir só `unidade_policial`/`street`/`municipality`, ou também `neighborhood`/`number`.
- [ ] Decidir o threshold de similaridade fuzzy para o nível Média em `street` (proposto: 0.85).
- [ ] Implementar o validador determinístico compartilhado (pode virar uma função utilitária única reaproveitada pelos 3 campos, em vez de lógica duplicada).
- [ ] Escrever o script de backfill único para os 562 registros existentes.
