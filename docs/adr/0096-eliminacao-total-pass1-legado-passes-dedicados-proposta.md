# ADR-0096: Próxima Etapa — Eliminação Total do Pass 1 Legado, Quebrado em Passes Dedicados (Proposta, Não Implementada)

- Status: Aceita
- Data: não registrada

## Contexto
Após consolidar o Pass 2 (Localização, ADR-089/093) e o Estágio 2 de Especialidades (ADR-094) como passes dedicados e blindados, o Pass 1 legado — ainda um schema genérico amplo sem os mesmos guardrails — permanece como a última peça monolítica do pipeline cognitivo, e o princípio já validado nessas ADRs (determinismo quando possível, LLM só com julgamento genuíno) ainda não foi aplicado a ele.

## Decisão
Decisão de princípio confirmada com o usuário: o objetivo não é reduzir o número de chamadas à LLM — é quebrar em passes mais especializados para aumentar a qualidade/confiabilidade, usando determinismo sempre que o campo for formulaico o bastante e LLM só onde há julgamento genuíno de contexto. Plano detalhado, campo a campo: `date_of_fact`/`time_of_fact` saem da LLM (100% determinístico via `text_cleaner.py`); `relint_type` ganha classificador determinístico próprio (`classify_relint_type()`); `registry_number`/`registry_agency`/`registry_year` viram um novo pass LLM dedicado com guardrail de evidência literal; `location_types` vira um novo pass LLM dedicado; `main_fact` é derivado de `subject`/`bm_group` já resolvidos, sem chamada nova; `participants` é removido do Pass 1 legado nesta etapa, sem substituto ainda, para virar seu próprio conjunto de passes numa etapa futura. Ao final, o Pass 1 legado deixa de existir por completo.

## Consequências
Formaliza um roteiro concreto, campo a campo, para eliminar por completo o último resquício de extração monolítica do sistema, mantendo a filosofia já validada nas ADRs anteriores. Por ser uma proposta ainda não implementada, não produz nenhuma mudança de comportamento imediata — serve como plano de continuidade para a próxima sessão/etapa de trabalho.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
