# ADR-0005: Exclusão de Guarnições PM e Transcrição Segura

- Status: Aceita
- Data: não registrada

## Contexto
RELINTs citam tanto policiais (guarnições que atenderam a ocorrência) quanto pessoas investigadas. Misturar os dois grupos no dossiê de pessoas comprometeria a utilidade analítica do cruzamento, além de expor dados de agentes públicos desnecessariamente ao pipeline de IA.

## Decisão
Policiais não são adicionados aos dossiês de pessoas investigadas. O histórico literal (`content`) do boletim é extraído via código determinístico (Python/Regex) e ocultado da IA (LLM).

## Consequências
Dossiês de pessoas ficam focados exclusivamente em indivíduos de interesse investigativo. A extração determinística do texto integral reduz a exposição de dados sensíveis ao LLM, mas exige regras de regex mantidas separadamente da lógica de IA.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
