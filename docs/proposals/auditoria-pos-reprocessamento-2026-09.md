# Proposta: Auditoria de Consistência Pós-Reprocessamento (Setembro/2026)

> Status: **Itens 1-5 da seção 4 corrigidos e testados (2026-09-08); item 6 dispensado pelo usuário.** Motivada pelo usuário após vários aprimoramentos no motor e reprocessamento de todos os PDFs: "precisamos validar o que o motor está trazendo". Amostra: **320 dos 602 RELINTs** do banco (auditoria interrompida a pedido antes de completar os 602 — os achados abaixo são estatisticamente representativos, mas não é a base inteira). **As correções não foram retroaplicadas aos 602 RELINTs já no banco** — valem para processamentos novos; reprocessar os existentes é uma decisão separada, ainda não tomada.

---

## 0. Resumo executivo (para quem for repetir esse procedimento)

Esse audit **vai ser rodado de novo** (provavelmente depois de um reprocessamento completo dos PDFs) — este documento é o registro do que foi feito, o que foi encontrado e o que já foi corrigido, para não repetir trabalho nem os mesmos erros de metodologia.

**5 bugs reais encontrados e corrigidos no motor** (seção 4): `location_types` nunca era persistido no banco; placeholder `"Não Informado"` vazando em `hora_fato`; placeholder `"null"` vazando em `município`; placeholder `"Sem informação específica"` vazando em `endereço`; `classify_bm_group()` classificando RELINTs errado quando o texto menciona o histórico criminal do suspeito (antecedentes) em vez do fato atual.

**3 erros de metodologia do próprio script de auditoria, corrigidos durante a análise** (seção 1) — importantes pra quem for rodar de novo não cair nos mesmos: checar `unidade_policial`/`coordenadas`/`endereço` por match literal simples gera falsos positivos em massa (91-98%) porque esses campos legitimamente não precisam de menção literal na maioria dos casos.

**1 limitação conhecida, não corrigida** (seção 3): o prompt de auditoria do Estágio 2 (LLM) não distingue campo de enum fechado (`grupo_bm`, `tipo_relint` — nunca vai ter menção literal tipo "Outros") de campo narrativo — infla artificialmente os números de `Grupo BM`/`Resumo`/`Fato Principal`. Se for repetir o Estágio 2, vale corrigir o prompt primeiro (ver sugestão 6, dispensada desta vez).

**O banco não foi reprocessado** — as correções valem só para processamentos novos. Os 602 RELINTs já salvos continuam com os mesmos bugs até serem reprocessados.

## 1. Metodologia

Dois estágios, script em [`scripts/audit_extracted_fields.py`](../../scripts/audit_extracted_fields.py) (só leitura, não altera o banco):

- **Estágio 1 (determinístico)**: campos com evidência textual esperada (endereço, município, unidade policial, coordenadas, registro, data/hora) — checados por match literal tolerante contra `conteudo` (mesma função `text_contains()` do `LocationExtractor`).
- **Estágio 2 (LLM/Ollama)**: campos narrativos e classificatórios (assunto, resumo, fato principal, grupo BM, tipo de RELINT) e de especialidade (motivação, drogas, veículo etc.) — pedem julgamento semântico, não match literal. Cada RELINT recebeu 1 chamada ao Ollama com o texto + os valores gravados, pedindo veredito por campo.

**3 correções de metodologia feitas durante a análise** (importante ler antes dos números abaixo, senão alguns parecem muito piores do que são de verdade):

1. **`unidade_policial`** é 100% determinístico desde a sessão passada (tabela município→BPM) — "sem menção literal no texto" é o comportamento *esperado* quando o valor vem da tabela por inferência territorial, não um erro. Critério corrigido para "diverge da tabela do município", não "sem evidência literal".
2. **`coordenadas`** frequentemente vêm de um link do Google Maps presente no documento (resolvido para decimal) — o link não é o número decimal, então "sem match literal" não significa hallucinação. Critério corrigido para considerar `map_url` como fonte válida.
3. **`endereço`** é uma string composta ("Rua X, nº N - Bairro, Município - RS") — checar o valor inteiro contra o texto quase nunca bate mesmo quando a rua está certa (o documento nunca escreve nesse formato administrativo). Corrigido para checar a rua isoladamente.

Sem essas 3 correções, os números brutos do Estágio 1 diziam "91% dos endereços" e "98% das coordenadas" sem evidência — números **falsos**, artefato da metodologia, não do motor. Ficam registrados aqui pra não se repetir num próximo audit.

**Uma 4ª limitação, descoberta mas não corrigida ainda** (afeta o Estágio 2): o prompt de auditoria pede "aparece no texto" também pra campos que são **classificação em enum fechado** (`grupo_bm`, `tipo_relint`) — mas um valor como `"Outros"` nunca vai aparecer literalmente no texto por definição (é a categoria "nenhuma das outras 8 serve"). Isso infla artificialmente as inconsistências de `grupo_bm` reportadas pelo Estágio 2 — ver seção 3.

---

## 2. Estágio 1 — Resultados (corrigidos)

| Campo | Preenchidos | Inconsistência real | Observação |
|---|---|---|---|
| `data_fato` | 320/320 (100%) | 0 (0%) | Determinístico, perfeito. |
| `unidade_policial` | 281/320 (88%) | 0 (0%) | 100% batendo com a tabela município→BPM. |
| `coordenadas` | 55/320 (17%) | 0 (0%) | 54/55 resolvidos via link do Maps (esperado); 1 checado direto. |
| `numero_registro`/`orgao_registro`/`ano_registro` | 33-35/320 (~11%) | 0 (0%) | `RegistryExtractor` (pass novo desta sessão) sem nenhum caso sem sustentação. |
| `endereço` | 320/320 (100%) | 18 (6%) | Ver seção 2.1. |
| `município` | 301/320 (94%) | 3 (1%) | Ver seção 2.2. |
| `hora_fato` | 320/320 (100%) | **87 (27%)** | Ver seção 2.3 — achado mais sério do Estágio 1. |
| `location_types` | **0/602 (0%)** | — | **Bug crítico — ver seção 2.4.** |

### 2.1. `endereço` — 18 casos, majoritariamente esperados

16 dos 18 são o fallback `"Interior, <Município> - RS"` (endereço rural sem rua específica — comportamento correto quando o documento não cita uma rua). Os 2 realmente problemáticos:
- id 345: `"Sem informação específica, Cruz Alta - RS"` — **placeholder textual vazando** pro campo endereço (deveria ficar vazio).
- Os demais "Interior, ..." não são erro, é o desenho esperado — sinalizo só pra registro, não como pendência.

### 2.2. `município` — 3 casos, 1 bug confirmado

- id 313: `municipio = "null"` (a **string literal** "null", não vazio) — bug de serialização, provavelmente um `None`/JSON `null` que virou string em algum ponto do pipeline em vez de ficar como valor vazio.
- Os outros 2 são falsos positivos do meu checker (o texto cita o município em um trecho que meu regex não capturou bem) — não investiguei a fundo, baixo risco.

### 2.3. `hora_fato` — 87 casos (27%), todos o mesmo padrão

**100% dos 87 casos têm o valor literal `"Não Informado"`** — não é erro de extração, é um **placeholder vazando pro banco** em vez de ficar vazio. Causa provável: `extract_time_of_fact()` (`text_cleaner.py`) retorna `""` corretamente quando não acha horário, mas o guard em `EtlService.process_file()` (`if not response_dict.get("time_of_fact")`) só aciona esse fallback determinístico quando o campo vem **vazio** da LLM — se a LLM responder a string não-vazia `"Não Informado"`, o guard considera "já resolvido" e nunca cai no fallback determinístico. Diferente do `address`/`street`, que já tem uma lista `INVALID_PLACEHOLDERS` dedicada (`location_extractor.py`), `time_of_fact` nunca ganhou o mesmo filtro.

### 2.4. `location_types` — bug crítico: campo nunca é persistido

**Nenhum dos 602 RELINTs no banco tem `location_types` preenchido — nem um único.** Investigando: a tabela `relints` **não tem essa coluna** (`PRAGMA table_info(relints)` confirma). O campo foi implementado no `LocationExtractor` nesta mesma sessão (commit `c4d5d5e`, 5 testes unitários passando, verificado ao vivo contra o RELINT 015 real retornando `['Propriedade Rural', 'Via Pública']`) — mas **`SqliteRepo` nunca foi atualizado pra persistir esse campo novo**: sem coluna no schema, sem `INSERT`/`UPDATE`, sem `SELECT`. O valor é calculado em memória pela LLM e descartado silenciosamente na hora de salvar. Isso não é uma inconsistência de dado — é um recurso inteiro que nunca chegou a funcionar de ponta a ponta, só nos testes isolados.

---

## 3. Estágio 2 — Resultados (LLM), com ressalva de confiabilidade

**Achado confirmado manualmente, alta confiança:**
- **RELINT 599** ("Estupro de Vulnerável em Iraí - RS") está classificado com `grupo_bm = "Homicídio"`. O texto não menciona homicídio nenhum — é um caso de estupro. Classificação de especialidade errada, e carrega campos de homicídio (`fact_type`, `motivation`) sem sentido pro caso real.

**Números brutos do Estágio 2** (ver ressalva abaixo antes de usar):

| Campo | Avaliados | "Inconsistente" (bruto) | % |
|---|---|---|---|
| Resumo | 315 | 254 | 81% |
| Grupo BM | 308 | 252 | 82% |
| Fato Principal | 315 | 230 | 73% |
| Motivação (Homicídio) | 45 | 21 | 47% |
| Tipo de Fato (Homicídio) | 44 | 11 | 25% |
| Quantidade de Drogas | 23 | 10 | 43% |
| Tipo de RELINT | 313 | 22 | 7% |
| Assunto | 315 | 4 | 1% |

**Ressalva importante**: amostrando manualmente ~15 casos de `Grupo BM` marcados "inconsistente", a maioria é **ruído do prompt de auditoria**, não erro real do motor — o auditor reclama que `"Outros"` "não aparece no texto", mas `Outros` é a categoria "nenhuma das 8 específicas serve", nunca deveria aparecer literalmente por definição (mesmo problema que corrigi pra `unidade_policial` no Estágio 1, mas não deu tempo de corrigir aqui). Amostrando `Fato Principal`, boa parte das reclamações são sobre o campo **repetir o Assunto sem acrescentar nada** (queixa de qualidade real, não de fato inventado) ou **omitir um detalhe secundário** (ex: "não menciona o nome da segunda vítima") — isso é diferente de "inventou/trocou um fato", que era o critério que pedi no prompt.

**Conclusão**: os números de `Grupo BM`/`Resumo`/`Fato Principal` acima **superestimam bastante** o problema real. Não dá pra confiar neles como estão — precisam de um prompt de auditoria refeito (deixando claro que `Outros`/enums fechados não precisam de menção literal, e separando "omissão" de "contradição factual") rodado de novo, ou revisão manual de uma amostra menor. `Motivação`/`Tipo de Fato`/`Quantidade de Drogas` (campos de especialidade, não enum fechado tipo "Outros") são mais confiáveis nesse sentido, mas também não revisei caso a caso.

---

## 4. Sugestões de Melhoria — status

1. ✅ **[Alta prioridade] Persistir `location_types` de verdade** — coluna `tipos_local` (TEXT, JSON) adicionada em `relints` (`_init_db()`, `ALTER TABLE ... ADD COLUMN`), incluída no `INSERT`/`ON CONFLICT UPDATE`/`_build_report_from_row()` de `SqliteRepo`. Teste: `tests/dashboard/test_sqlite_repo.py::test_location_types_persiste_no_banco`.
2. ✅ **[Média] Filtrar placeholder `"Não Informado"` em `time_of_fact`** — causa real era mais simples do que o suposto: `EtlService.process_file()` fazia `extract_date_of_fact(...) or "Não Informado"`/`extract_time_of_fact(...) or "Não Informado"`, substituindo deliberadamente vazio pelo placeholder. Removida a substituição — campo fica genuinamente vazio quando não há data/hora no texto. Teste: `tests/motor_regex/test_etl_service_deterministic_phase.py::test_fase_b_nao_grava_placeholder_nao_informado_quando_data_hora_vazias`.
3. ✅ **[Média] `municipio = "null"` literal** — causa: `LocationExtractor` aceitava qualquer string não-vazia de `raw_response.get("municipality")` com mais de 2 caracteres, incluindo a LLM respondendo a string literal `"null"` (não o JSON `null`). `INVALID_PLACEHOLDERS` promovido para constante do módulo (antes só local dentro de `format_google_standard_address`) e reaplicado nesse ponto. Teste: `tests/motor_llm/test_location_extractor.py::test_extract_discards_literal_null_string_from_llm_municipality`.
4. ✅ **[Baixa] Placeholder `"Sem informação específica"` vazando pro endereço** — adicionado a `INVALID_PLACEHOLDERS`. Teste: `tests/motor_llm/test_location_extractor.py::test_format_address_discards_sem_informacao_especifica_placeholder`.
5. ✅ **[Investigação] `grupo_bm = Homicídio` pra caso de estupro** — causa raiz encontrada: a Passada 2 de `classify_bm_group()` (busca de fallback no conteúdo inteiro) pegou a menção **"Rodrigo de Souza possui antecedentes por homicídio..."** — o histórico criminal do suspeito, não o fato relatado agora. Corrigido: trechos `"antecedentes por ..."` são removidos do texto antes da Passada 2 (`_strip_antecedentes()`, `bm_classifier.py`). Afeta potencialmente outros RELINTs: **31/602** no banco têm essa frase. Testes: `tests/motor_regex/test_bm_classifier.py::test_ignora_homicidio_mencionado_apenas_nos_antecedentes` (não classifica errado) e `test_ainda_classifica_homicidio_quando_e_o_fato_relatado` (não deixa de classificar homicídio de verdade).
6. **Dispensado pelo usuário** — não refazer o prompt do Estágio 2 nem continuar a auditoria nos 282 RELINTs restantes.

**199 testes passando** (193 + 6 novos) após as correções.

---

## 4.1. Achado adicional (2026-09-08, fora da amostra original): `município` capturando texto corrido

Usuário encontrou no RELINT 001 (id 631): `municipio = "Face De Policial Militar Em Serviço Em Panambi"`. Causa: `extract_municipality_from_context()` usava um prefixo de regex preguiçoso (`.*?`) antes de `\bem\s+` — quando o Assunto tem mais de um "em" antes do nome da cidade (ex: "...em face de policial militar em serviço em Panambi - RS"), o regex ancorava no primeiro "em" em vez do último, capturando tudo pelo caminho até o único "- RS" do texto.

**Corrigido em duas camadas:**
1. Trocado `.*?` (preguiçoso) por `.*` (guloso) — faz o backtracking pegar o último "em" antes de "- RS", não o primeiro. Vale tanto pro Assunto quanto pro nome do arquivo (mesmo bug nos dois).
2. **Novo guardrail `validate_municipality()`**, regra confirmada com o usuário: compara o candidato primeiro contra os 41 municípios com BPM territorial conhecido (`MUNICIPALITY_TO_BATTALION`), depois contra a lista completa dos 497 municípios do RS (`backend/engine/extractors/deterministic/resources/municipios_rs.json`, baixada da API oficial do IBGE — `servicodados.ibge.gov.br`), e se não bater com nenhum dos dois, descarta (fica vazio) em vez de manter o texto capturado por engano. Aplicado tanto no resultado do regex determinístico quanto na resposta da LLM.

RELINT 001 (id 631) corrigido em memória (`municipio = "Panambi"`), sem reprocessar. Nenhum outro RELINT dos 28 atualmente no banco tinha esse padrão. Testes: `tests/motor_llm/test_location_extractor.py` (6 novos: regex do assunto, regex do filename, `validate_municipality` aceitando os 41, aceitando RS fora dos 41, rejeitando texto lixo, e fim-a-fim via `LocationExtractor.extract()`).

## 5. Dados brutos

Resultado completo (320 RELINTs, ambos estágios) salvo em `data/audit_results.json` — **gitignored**, não vai pro repositório (contém trechos de texto de RELINTs).

---

## 6. Como repetir esse procedimento

Os 2 scripts continuam no repositório, prontos pra reuso:

```bash
# Estágio 1 + 2 completos, todos os RELINTs do banco (Ollama precisa estar rodando)
python scripts/audit_extracted_fields.py

# Teste rápido antes de rodar tudo (recomendado — o Estágio 2 é ~8s/RELINT)
python scripts/audit_extracted_fields.py --limit 5

# Só Estágio 1 (determinístico, sem custo de LLM, roda em segundos)
python scripts/audit_extracted_fields.py --skip-llm

# Agrega data/audit_results.json em tabelas/estatísticas (roda depois do audit)
python scripts/analyze_audit_results.py
```

**Antes de confiar nos números do próximo run**, relembrar as 3 correções de metodologia da seção 1 (`unidade_policial`, `coordenadas`, `endereço`) — o script já tem essas correções aplicadas no código atual, mas se `analyze_audit_results.py` for reescrito do zero, não esquecer delas. A limitação do Estágio 2 (enum fechado vs. narrativo, seção 3) **não** está corrigida no prompt — se for rodar o Estágio 2 de novo, considerar corrigi-la antes (sugestão 6) pra não gerar números inflados de novo em `grupo_bm`/`tipo_relint`.

**Se o próximo run for depois de um reprocessamento completo dos 602 PDFs**: os 5 bugs desta rodada já estão corrigidos no motor, então o esperado é que os números de `location_types`, `hora_fato`, `município` e a classificação de `grupo_bm` (casos tipo RELINT 599) apareçam bem melhores. Se ainda aparecerem, é sinal de que a correção não pegou ou de que existe uma variante do bug não coberta pelos testes de regressão adicionados (ver seção 4).
