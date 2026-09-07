# ADR-0092: Correção do Sinal de Coordenadas Perdido em Quebra de Linha do PDF e Blindagem Geográfica do RS

- Status: Aceita
- Data: não registrada

## Contexto
A extração de texto via PyMuPDF (ADR-064) podia introduzir quebras de linha exatamente entre o sinal negativo e o primeiro dígito de uma coordenada, um artefato de baixo nível da extração de PDF que corrompia silenciosamente o valor antes mesmo de chegar aos regex de detecção geográfica.

## Decisão
O PyMuPDF ocasionalmente quebra a linha entre o sinal `-` e o dígito da coordenada (`-\n28.7`), fazendo o sinal negativo se perder na extração. Normalização determinística reconecta o sinal antes de rodar os regex de detecção. Adicionalmente, como 100% dos RELINTs são do Rio Grande do Sul, latitude e longitude são forçadas a negativo e validadas contra a faixa geográfica aproximada do estado — descarta também placeholders textuais ("N/A", "Sem informação", links não resolvidos) que antes vazavam para o banco. Coordenadas em formato DMS agora são genuinamente convertidas para decimal (antes ficavam presas na string bruta, nunca normalizadas).

## Consequências
Recupera coordenadas que antes eram perdidas ou gravadas incorretamente por causa de um artefato de extração de baixo nível, além de reforçar a blindagem geográfica já existente (ADR-089) com validação específica da faixa do RS. A conversão DMS → decimal aumenta a cobertura de formatos de coordenada aceitos, mas exige testes cuidadosos para não converter incorretamente valores já em decimal.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
