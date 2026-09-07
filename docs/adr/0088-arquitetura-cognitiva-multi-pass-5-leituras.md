# ADR-0088: Arquitetura Cognitiva Multi-Pass em 5 Leituras Especializadas (Multi-Step Extraction)

- Status: Aceita
- Data: não registrada

## Contexto
Pedir a um único prompt de LLM que preenchesse simultaneamente mais de 15 campos heterogêneos (síntese, localização, apreensões, participantes, classificação) sobrecarregava o modelo, degradando a qualidade de cada campo individual em favor de tentar acertar tudo de uma vez.

## Decisão
Decisão de substituir a extração monolítica da LLM (que tentava inferir 15+ campos em um único JSON pesado) por uma arquitetura em 5 Leituras Cognitivas Especializadas com schemas e prompts ultraleves e focados: Pass 1 (Síntese & Assunto) com redação dedicada da síntese factual e extração do assunto (`SummaryExtractor` com `SummaryExtraction`), blindada contra preâmbulos policiais e plágios do título; Pass 2 (Localização & Georreferenciamento) com resolução de endereço, bairro, município, unidade BPM e coordenadas; Pass 3 (Apreensões) com veículos, armas e drogas estruturadas; Pass 4 (Participantes & Vínculos) com autores, vítimas, testemunhas, antecedentes e exclusão de PMs; Pass 5 (Classificação & Regras Especializadas) com roteamento para as tabelas polimórficas de especialidade.

## Consequências
Cada pass, sendo focado e leve, tende a produzir extrações de qualidade mais alta e mais fáceis de validar/depurar isoladamente. O custo é o aumento do número de chamadas ao LLM por RELINT (5 passes especializados em vez de 1 monolítico), elevando o tempo total de inferência por documento.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
