# ADR-0058: Separação por Linha em Branco (`\n\n`) após o Cabeçalho de ANEXOS no Texto Integral

- Status: Aceita
- Data: não registrada

## Contexto
O texto bruto extraído do PDF não preservava necessariamente uma quebra de parágrafo clara entre o cabeçalho formal do boletim (terminado em `ANEXOS: ...`) e o corpo narrativo do fato, fazendo com que a transcrição exibida na Web concatenasse as duas partes de forma confusa.

## Decisão
Atualização de `normalize_whitespace_and_paragraphs` (`text_cleaner.py`) e `formatTranscriptText` (`app.js`). Garante que o bloco formal do cabeçalho do RELINT (encerrado na linha `ANEXOS: ...`) seja separado do corpo narrativo por uma linha em branco (`\n\n`), evitando que a primeira frase do fato seja concatenada na mesma linha do campo de anexos.

## Consequências
Melhora a legibilidade da transcrição exibida ao usuário, deixando clara a fronteira entre cabeçalho formal e narrativa. A correção precisa ser mantida em sincronia entre a normalização no backend (Python) e a formatação no frontend (JS), que replicam a mesma regra em duas linguagens.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
