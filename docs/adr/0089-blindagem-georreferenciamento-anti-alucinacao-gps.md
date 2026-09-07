# ADR-0089: Blindagem de Georreferenciamento, Anti-Alucinação de GPS e Sanitização de Endereços

- Status: Aceita
- Data: não registrada

## Contexto
A arquitetura multi-pass (ADR-088) isolou a extração de localização em um pass dedicado, mas auditorias revelaram que o LLM ainda podia "alucinar" coordenadas GPS plausíveis porém inexistentes no documento, além de deixar mapas caindo por padrão na capital quando o município não era resolvido corretamente.

## Decisão
Implementação de travas no `LocationExtractor` e `TabLocation.svelte`: Zero Fake GPS (descarte sumário de coordenadas inventadas pela LLM quando os dígitos não existirem literalmente no documento ou em link resolvido); Herança Determinística de Município (captura e injeção compulsória da cidade a partir do `ASSUNTO` ou nome do arquivo para impedir que buscas no mapa caiam na capital, Porto Alegre); Sanitização de Ruídos Narrativos (truncamento e limpeza automática de links `https://`, menções a coordenadas no meio da frase, jargões operacionais da BM e pontos de referência comerciais nos logradouros); Enquadramento Panorâmico sem Balão de Ponto (documentos sem rua abrem a visualização panorâmica da cidade inteira, `z=12`, sem balão/marcador falso); Preservação de Abreviaturas e Zonas Rurais (suporte a iniciais compostas de ruas e normalização automática de rodovias/linhas sem bairro para "Interior").

## Consequências
Reduz drasticamente o risco de exibir no mapa uma localização geográfica fabricada pela IA, protegendo a confiabilidade do indicador visual já estabelecido na ADR-007. As múltiplas camadas de sanitização (links, jargões, referências comerciais) exigem manutenção contínua conforme novos padrões de ruído textual aparecerem nos boletins.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
