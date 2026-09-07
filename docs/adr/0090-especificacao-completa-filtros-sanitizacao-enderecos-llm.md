# ADR-0090: Especificação Completa dos Filtros e Camadas de Sanitização na Extração de Endereços por LLM

- Status: Aceita
- Data: não registrada

## Contexto
Após várias iterações de blindagem geográfica (ADR-089), o pipeline de localização acumulou 9 camadas distintas de filtro e normalização aplicadas em sequência, e essa complexidade acumulada precisava ser documentada de forma exaustiva e centralizada para que futuros mantenedores entendessem o pipeline completo.

## Decisão
Documentação exaustiva de todas as 9 camadas de validação, filtragem e normalização aplicadas no pipeline geográfico: (1) Filtro Anti-Alucinação de Coordenadas (Zero Fake GPS) validando latitude/longitude contra o texto bruto ou links `maps.app.goo.gl`, descartando coordenadas inventadas; (2) Filtro de Desambiguação de Local do Crime vs Terceiros, capturando estritamente o local do fato do 1º parágrafo; (3) Filtro e Herança Obrigatória de Município a partir do cabeçalho `ASSUNTO` ou nome do arquivo; (4) Filtro de Ruídos Narrativos e Verbos Operacionais da BM; (5) Filtro de Links HTTP e Expressões de GPS no Meio do Texto; (6) Filtro de Referências Comerciais em Parênteses; (7) Filtro e Normalização de Zona Rural (bairro "Interior"); (8) Filtro de Formatação Padrão Google e Descarte de Placeholders, montando o padrão `Logradouro, nº [ou S/N] - Bairro, Município - RS`; (9) Filtro de Classificação de Confiabilidade no Frontend em 3 cores (Alta/Verde para GPS real, Média/Azul para links diretos, Baixa/Âmbar para apenas endereço textual).

## Consequências
Cria uma referência única e completa do pipeline geográfico, facilitando auditoria e onboarding de novos mantenedores nessa parte crítica do sistema. É primariamente uma decisão de documentação consolidando decisões técnicas já tomadas nas ADRs anteriores de georreferenciamento, sem introduzir comportamento novo por si só.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
