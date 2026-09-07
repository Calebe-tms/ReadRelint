# ADR-0082: Aba Síntese em Destaque e Campos de Metadados em Modo Leitura Pura

- Status: Aceita
- Data: não registrada

## Contexto
A aba geral do dossiê exibia campos de metadados sempre como controles de formulário editáveis, mesmo em modo de leitura, o que adicionava ruído visual de bordas e caixas de input quando o usuário apenas queria consultar a informação, sem editar.

## Decisão
Na visualização de dossiês (`TabGeneral.svelte`), a aba foi renomeada para **Síntese** e o bloco de síntese cognitiva foi promovido ao topo com tipografia expandida (15px) e destaque visual âmbar. Os campos de metadados (*Assunto*, *Data*, *Registro*, *Órgão*, *Ano*) passaram a ser renderizados como texto puro em modo leitura, eliminando ruído visual de formulário e renderizando caixas de `<Input>` apenas ao acionar o botão `EDITAR`.

## Consequências
Prioriza a leitura fluida da síntese cognitiva (o resumo mais importante do boletim) e reduz ruído visual de formulário fora do momento de edição. Introduz uma alternância explícita entre modo leitura e modo edição que precisa manter os dois estados visuais consistentes.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
