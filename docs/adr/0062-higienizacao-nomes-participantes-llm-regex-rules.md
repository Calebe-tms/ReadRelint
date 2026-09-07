# ADR-0062: Higienização de Nomes de Participantes (LLM & Regex Rules)

- Status: Aceita
- Data: não registrada

## Contexto
Tanto a extração via LLM quanto o fallback determinístico por Regex tendiam a capturar nomes de participantes junto com fragmentos narrativos do texto policial (frases de contexto que precedem o nome), poluindo o cadastro de pessoas usado nos dossiês (ADR-004/ADR-061).

## Decisão
Adicionada a função `clean_person_name` (`text_cleaner.py`) e aprimoradas as instruções do prompt no `OllamaClient` (`ollama_client.py`). Elimina prefixos narrativos e ruídos de contexto policial (ex: "Posteriormente Identificado Como Johnny Schroeder" → "Johnny Schroeder", "Estavam João Witor..." → "João Witor...", "momento em que foi feito contato com Mariane" → "Mariane") tanto no processamento via IA quanto na extração de fallback por Regex (`extract_fallback_participants`). Todos os registros legados da tabela `pessoas` do SQLite foram migrados e sanitizados.

## Consequências
Melhora significativamente a qualidade dos nomes cadastrados, tornando o cruzamento de pessoas entre RELINTs mais confiável. A migração retroativa dos registros legados evita que o problema persista apenas em dados novos, mas exige validação cuidadosa para não truncar nomes legítimos de forma incorreta.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
