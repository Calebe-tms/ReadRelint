# ADR-0060: Design Responsivo e Adaptável (Mobile, Tablet e Desktop)

- Status: Aceita
- Data: não registrada

## Contexto
A interface web havia sido construída com foco em telas desktop, e o acesso remoto via Cloudflare Tunnel (ADR-019) criou a necessidade real de usuários acessarem o dashboard a partir de tablets e smartphones em campo.

## Decisão
Implementação de sistema completo de `@media` queries e layout adaptável em `main.css` (`main.css`), botão hambúrguer mobile e fundo overlay com desfoque (*backdrop-filter blur*) em `index.html` (`index.html`). As telas se ajustam dinamicamente: sidebars convertem-se em *drawer* deslizante em telas menores que 992px, cartões KPI e gráficos re-arranjam de 4 para 2 e 1 colunas, e janelas modais passam a ocupar 94vw/96vw com scroll suave nos formulários.

## Consequências
Torna o dashboard utilizável em qualquer tamanho de tela, ampliando os cenários de uso em campo. Aumenta a superfície de CSS responsivo a manter e testar a cada nova funcionalidade de UI adicionada.

---
_Nota: Contexto e Consequências foram reconstruídos a partir do registro original resumido (uma única frase de decisão + motivo). Revisar se necessário._
