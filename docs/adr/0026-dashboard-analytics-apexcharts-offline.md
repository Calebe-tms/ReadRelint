# ADR-0026: Dashboard Analytics com ApexCharts Offline

- Status: Aceita
- Data: não registrada

## Contexto
O sistema roda localmente sem garantia de conectividade com a internet, então qualquer biblioteca de visualização usada no dashboard precisa estar disponível offline para não quebrar a experiência do usuário.

## Decisão
Adição do módulo `crimes_view.js` com KPIs dinâmicos, gráficos interativos de distribuição e linha do tempo usando **ApexCharts** mantido totalmente offline em `assets/vendor/`.

## Consequências
Garante que os gráficos analíticos funcionem independentemente de conexão com a internet. Exige manter a biblioteca vendorizada localmente e atualizá-la manualmente em vez de depender de um CDN.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
