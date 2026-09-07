# Proposta: Correção de Inconsistências na Extração de Localização/Unidade

> Status: **Implementado em 2026-09-03** (sugestões #2, #3, #4, #5, #6, #8 e o pré-requisito de município da seção 2.4). Sugestão #1 (rewording de exemplos) foi superada pela solução determinística da seção 6. Sugestão #7 (termômetro de certeza generalizado) segue pendente — ver `termometro-certeza.md`. Gerado a partir de uma varredura no `data/relints.db` (562 RELINTs) cruzando `endereco`, `municipio`, `unidade_policial` e `coordenadas` contra o texto literal (`conteudo`).

---

## 1. Panorama Geral

| Campo | Preenchidos | Inconsistência confirmada |
|---|---|---|
| Coordenadas | 180 / 562 (32%) | 30 (17%) — sinal, formato ou faixa geográfica |
| Unidade policial | 476 / 562 (85%) | 223 (47%) — sem nenhuma menção no texto bruto |
| Endereço/rua | 487 / 562 (87%) | 68 (14%) — rua não encontrada literalmente |
| Município | 562 (derivado do Assunto) | 10 (2%) — diverge do cabeçalho |

---

## 2. Causas-Raiz Identificadas

### 2.1. Coordenadas: sinal "-" perdido por quebra de linha do PDF

O PyMuPDF às vezes extrai o texto quebrando a linha exatamente entre o hífen e o número:

```
id 729: "nas coordenadas geográficas: -\n28.704834, -53.111531"
id 734: "Interior (-\n28.715267, -53.019818)"
id 879: "Bairro Interior (-\n29.026916,-53.235809)"
id 1070: "Rua Procópio Gomes, 0480 – São Miguel (-\n28.630464, -53.601084)"
id 1172: "localidade de Capão Bonito, Interior (-\n29.078116, -53.337400)"
id 1191: "Distrito de Castelinho (-\n27.350343, -53.295869)"
```

O regex em `backend/engine/extractors/llm/extractors/location_extractor.py` (`check_raw_text_geo_sources`, linha ~60, e a normalização final na linha ~356) exige o `-` **imediatamente colado** ao dígito (`-?\d{1,2}\.\d{4,8}`). Como o hífen fica isolado numa linha e o número começa na linha seguinte, o regex captura só o número positivo para a latitude.

Um caso (id 958) é diferente: o próprio documento original nunca escreveu o sinal em nenhum dos dois números — erro de origem, não de extração.

**Sub-problemas relacionados:**
- **DMS nunca convertido para decimal**: 6 registros guardam literalmente `28°34'58.5"S 53°07'10.0"W` como string — o padrão é detectado (linha ~64) mas nunca convertido, e a normalização (linha ~356) só aceita formato decimal.
- **Placeholders textuais em vez de vazio**: 12 registros têm `coordenadas = "N/A"`, `"Sem informação"`, `"Não disponível"`, `"Desconhecida"` ou até uma URL crua não resolvida.

### 2.2. Unidade policial: viés de âncora no exemplo do prompt

**265 dos 476 registros preenchidos (56%) têm valor "39º BPM"** — e **187 desses 265 (70%) não têm nenhuma menção a "39" em lugar nenhum do texto bruto**.

Causa: em `backend/engine/extractors/llm/prompts/address_prompt.py` (linha ~13):
```
'police_unit': Batalhão ou fração da Brigada Militar citada (ex: '39º BPM', '37º BPM', '16º BPM').
```
`'39º BPM'` é o **primeiro exemplo** listado. Modelos locais pequenos (o projeto usa `llama3.1:latest` via Ollama) tendem a ancorar no primeiro exemplo de few-shot quando não têm certeza da resposta real.

**Prova mais forte**: 3 registros têm literalmente `unidade_policial = "16º BPM, 37º BPM, 39º BPM"` — o modelo devolveu a lista de exemplos inteira como resposta.

Diferente de `coordinates`/`map_url`, o prompt **não tem** instrução de "retorne null se não tiver certeza" para `police_unit` (nem para `street`/`number`/`neighborhood`/`municipality`).

### 2.3. Mesmo viés de âncora no campo `street`

`'street'` também lista **"Rua General Osório"** como primeiro exemplo (linha ~11 do mesmo prompt). Resultado: 16 registros têm essa rua extraída, e **10 desses 16 (63%) não têm "Osório" em lugar nenhum do texto** — inclusive em cidades diferentes (Porto Alegre, Novo Tiradentes, Cruz Alta) sem relação entre si.

### 2.4. Município: divergências pontuais (baixo impacto, 10 casos)

Ex.: id 883 — banco diz "Frederico Westphalen" mas o Assunto diz "...em **Seberi** - RS". Provável causa: a herança determinística de município (`extract_municipality_from_context`, linha ~110) às vezes pega a sede/comarca administrativa em vez da cidade real do fato, quando o documento cita mais de uma localidade.

---

## 3. Padrão Comum

Os 3 problemas principais (unidade, rua, coordenadas parcialmente) compartilham a mesma raiz estrutural: **o pipeline não distingue "extraído com evidência textual" de "inferido/adivinhado pela LLM"**. Só `geo_precision` (Alta/Média/Baixa) tem esse conceito hoje, e só para coordenadas.

---

## 4. Sugestões de Melhoria (priorizadas)

1. **Estender a regra "null se incerto" para todos os campos do prompt** (`address_prompt.py`) — hoje só existe para `coordinates`/`map_url`. Adicionar a mesma instrução explícita para `street`, `police_unit`, `municipality`, `neighborhood`.

2. **`police_unit` sai do prompt da LLM — vira 100% determinístico via tabela município → BPM.** Decisão tomada em conjunto com o usuário (substitui a ideia original de só reescrever os exemplos do prompt): como só existem 3 batalhões possíveis e a área de cobertura de cada um é fixa, o campo não precisa mais depender de inferência da LLM. Ver seção 6 para o detalhamento completo da regra e da tabela. Só resta reescrever o exemplo `'Rua General Osório'` do prompt para `street` (esse campo continua com a LLM, pois cada endereço é único).

3. **Validação pós-LLM por evidência literal (guardrail determinístico)** — hoje só existe para coordenadas (linhas ~313-317 do extractor). Criar checagem equivalente para `street`: se o valor devolvido pela LLM não aparecer (nem por regex tolerante) no texto bruto, descartar e deixar em branco. Isso sozinho eliminaria os 10 casos de rua sem sustentação identificados (ex.: "Rua General Osório" cravada em 10 registros sem relação com o texto). Para `police_unit`, a validação equivalente já está coberta pela regra determinística da seção 6.

4. **Tornar a regex de coordenadas tolerante a quebra de linha entre sinal e dígito** — trocar `-?\d{1,2}\.\d{4,8}` por algo como `-?\s*\n?\s*\d{1,2}\.\d{4,8}`, ou normalizar o texto (remover `\n` entre um `-` isolado e um dígito) antes de rodar a regex.

5. **Blindagem geográfica para RS** — como 100% dos RELINTs são do Rio Grande do Sul, forçar deterministicamente o sinal negativo quando o valor absoluto de latitude cair em ~27–34 e longitude em ~49–58 mas vier positivo. Corrige tanto os casos de quebra de linha quanto os de erro do documento original (ex.: id 958).

6. **Converter DMS → decimal de fato**, em vez de guardar a string bruta — ou, no mínimo, não deixar cair em `coordinates` sem passar pela normalização.

7. **Termômetro de certeza generalizado** — ver arquivo dedicado [`termometro-certeza.md`](./termometro-certeza.md).

8. **Banir placeholders textuais na validação de saída** — qualquer resposta da LLM que caia em `{"N/A", "não informado", "não disponível", "desconhecida", "sem informação", "-", "xxx"}` deve virar string vazia, nunca ser persistida como texto. Já existe uma lista `INVALID_PLACEHOLDERS` (linha ~169 do extractor) usada só na formatação final do endereço — precisa ser aplicada antes de salvar `coordenadas`/`unidade_policial` cru no banco.

---

## 6. Classificação Determinística de `police_unit` (Tabela Município → BPM)

**Decisão confirmada com o usuário em 2026-09-03.** Como só existem 3 batalhões possíveis na área coberta por este RELINT, o campo `police_unit` deixa de ser resolvido pela LLM e passa a ser calculado como guardrail determinístico dentro do `LocationExtractor` (mesmo padrão já usado para `fb_muni`/`fb_unit`/anti-alucinação de coordenadas — não fere o desacoplamento do ADR-085, pois continua dentro do pass da LLM, não mistura com o `DeterministicPipeline`).

### 6.1. Achado de código que motivou a mudança

Em [location_extractor.py:263](../backend/engine/extractors/llm/extractors/location_extractor.py#L263) já existe uma extração por regex (`fb_unit`) que busca `"Nº BPM"` literal no texto. O problema: em [location_extractor.py:304-306](../backend/engine/extractors/llm/extractors/location_extractor.py#L304), a resposta da LLM **sobrescreve esse fallback incondicionalmente**, sem checar confiabilidade. A nova regra abaixo substitui esse trecho.

### 6.2. Tabela Município → BPM (fornecida pelo usuário)

| BPM | Municípios cobertos |
|---|---|
| **16º BPM** (11) | Cruz Alta, Boa Vista do Cadeado, Pejuçara, Ibirubá, XV de Novembro, Fortaleza dos Valos, Selbach, Saldanha Marinho, Salto do Jacuí, Boa Vista do Incra, Jacuizinho |
| **37º BPM** (15) | Frederico Westphalen, Caiçara, Seberi, Erval Seco, Palmitinho, Pinheirinho do Vale, Taquaruçu do Sul, Vista Alegre, Planalto, Alpestre, Ametista, Rodeio Bonito, Cristal do Sul, Iraí, Vicente Dutra |
| **39º BPM** (15) | Palmeira das Missões, Panambi, Novo Barreiro, São Pedro das Missões, São José das Missões, Dois Irmãos das Missões, Boa Vista das Missões, Jaboticaba, Cerro Grande, Pinhal, Novo Tiradentes, Lajeado do Bugre, Sagrada Família, Condor, Santa Bárbara do Sul |

Total: 41 municípios mapeados. RELINTs de municípios fora desta lista não têm BPM territorial conhecido pelo sistema.

### 6.3. Regra de Resolução (via de mão dupla — tabela é primária, texto ajusta a confiança)

1. Roda o regex determinístico (`fb_unit`) e coleta **todos** os números de BPM válidos (16/37/39) citados literalmente no texto — não só o primeiro.
2. Resolve o valor da tabela a partir do `municipio` já extraído (com normalização: sem acento, case-insensitive, espaço colapsado).
3. Decide o valor final:
   - **Exatamente 1 batalhão citado literalmente no texto** → o texto vence, independente da tabela (cobre casos reais de apoio mútuo entre batalhões).
     - Se esse valor bater com a tabela → confiança **Alta**.
     - Se divergir da tabela → usa o valor do texto mesmo assim, mas confiança **Média** (sinaliza para revisão humana, já que foge do padrão territorial esperado).
   - **Zero menções literais, ou mais de uma menção (texto ambíguo)** → a tabela vence. Confiança **Média** (inferido, sem confirmação textual direta).
   - **Município fora da tabela E sem menção literal (ou ambígua)** → campo fica **vazio**.

### 6.4. Pré-requisito

A precisão desta regra depende da precisão do campo `municipio` — os 10 casos de divergência município vs. Assunto (seção 2.4) devem ser corrigidos primeiro ou em conjunto, senão o lookup herda o erro (ex.: id 1063, onde o banco tem "Cachoeira do Sul" mas o correto seria "Cruz Alta" — que está na lista do 16º BPM).

### 6.5. Onde deve viver a tabela no código

A tabela em si é dado de referência estático (geografia/organização militar), não lógica de extração. Colocá-la dentro de `llm/extractors/location_extractor.py` funciona para o escopo atual (extração via LLM, foco desta sessão), mas a Fase 2 do roadmap (`02_project_state.md` → Task 2.1, `classifier_extractor.py` do motor determinístico) vai precisar da mesma tabela. Como o projeto eliminou deliberadamente a pasta compartilhada `common/` (ADR-085), a sugestão é definir a tabela em `backend/core/` (já é o local de "configurações e utilitários centrais" segundo `folder_structure.md`) para os dois motores importarem sem recriar uma pasta compartilhada de lógica — **a confirmar quando a Fase 2 começar**.

---

## 7. Próximos Passos Sugeridos

- [x] Sugestões #3, #4, #5, #6, #8 e a seção 6 (tabela município → BPM) implementadas em `location_extractor.py`, `address_prompt.py`, `location_schema.py` e `pipeline.py`.
- [x] Corrigido o pré-requisito de município (seção 2.4) — `ASSUNTO` agora sempre prevalece sobre a resposta da LLM.
- [ ] Decidir se o termômetro de certeza generalizado (ver `termometro-certeza.md`) é implementado agora ou fica pra depois.
- [ ] Rodar reprocessamento nos ~200+ registros já existentes no banco (a correção só vale para novos processamentos até que os antigos sejam reprocessados).
