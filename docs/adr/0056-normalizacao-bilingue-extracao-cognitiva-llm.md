# ADR-0056: Normalização Bilíngue (pt-BR / en) da Extração Cognitiva via LLM (`EtlService`)

- Status: Aceita
- Data: não registrada

## Contexto
O LLM, operando sobre texto em português, tende a retornar chaves JSON também em português mesmo quando instruído a usar nomes em inglês, e os modelos de domínio internos usam atributos em inglês — essa divergência causava perda silenciosa de campos quando a resposta do modelo não batia exatamente com o schema esperado.

## Decisão
Implementação do método `_normalize_response_dict` no `EtlService` e aprimoramento das instruções do prompt no `OllamaClient`. Garante que retornos do Ollama em Português (`participantes`, `endereco`, `municipio`, `bairro`, `unidade_policial`, `numero_registro`, `nome`, `alcunha`, `documento`, `antecedentes`, `tipo_participacao`) sejam mapeados automaticamente para os atributos de domínio (`participants`, `address`, `municipality`, `neighborhood`, `police_unit`, `registry_number`, etc.). Adicionalmente, a reconstrução em caso de falha de validação passou a usar `model_construct`, impedindo que campos de localização ou participantes sejam descartados.

## Consequências
Torna a extração resiliente a variação de idioma na resposta do LLM, reduzindo perda de dados por divergência de nomenclatura. O uso de `model_construct` em falhas de validação prioriza preservar dados parciais sobre a garantia estrita de validação do Pydantic, o que exige cautela para não propagar dados malformados adiante.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
