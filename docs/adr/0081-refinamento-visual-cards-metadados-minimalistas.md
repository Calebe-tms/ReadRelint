# ADR-0081: Refinamento Visual de Cards e Metadados Minimalistas

- Status: Aceita
- Data: não registrada

## Contexto
Os cards da lista e a barra de metadados do dossiê acumulavam informação textual densa, dificultando a leitura rápida do essencial (identificação, especialidade, status) ao percorrer vários RELINTs em sequência.

## Decisão
Reestruturação visual dos cards da lista lateral (`RelintListPane.svelte`) destacando número puro (`RELINT X`), ícone de PDF, chips de especialidades e status de revisão agrupados. No `RelintDetailPane.svelte`, simplificação da barra de metadados com ícones discretos para data, município e método de extração por ícones com tooltips (`Sparkle` para Ollama IA e `Cpu` para Regex), além do reposicionamento do alerta de pendência de revisão logo abaixo do botão de edição.

## Consequências
Melhora a escaneabilidade da lista e do dossiê, priorizando ícones e chips compactos sobre texto extenso. A substituição de texto por ícones com tooltip exige garantir acessibilidade e clareza do significado de cada ícone para novos usuários.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
