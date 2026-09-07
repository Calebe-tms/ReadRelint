# ADR-0007: Geolocalização Visual por 3 Níveis

- Status: Aceita
- Data: não registrada

## Contexto
Nem todo RELINT traz a mesma qualidade de dado geográfico — alguns citam coordenadas GPS exatas, outros apenas um link de mapa, e outros somente um endereço textual reconstruído por fallback. Apresentar todos com o mesmo peso visual esconderia essa diferença de confiança.

## Decisão
Cores indicando precisão da localização no Dashboard: Verde (GPS exato capturado do PDF), Azul (Link explícito capturado), Laranja (Endereço estruturado via fallback).

## Consequências
O analista consegue avaliar rapidamente o quanto confiar em cada ponto no mapa sem abrir o boletim original. Exige, porém, que o pipeline de extração classifique corretamente a origem de cada dado geográfico para não induzir o usuário a erro.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
