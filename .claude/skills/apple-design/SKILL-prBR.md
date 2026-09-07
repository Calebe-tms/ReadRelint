---
name: apple-design
description: A abordagem da Apple para design de interface e movimento físico e fluido, traduzida para a web. Use ao construir ou revisar UI baseada em gestos, animações baseadas em molas (springs), interações de arrastar/deslizar/painéis (sheets), transições com momento e interruptíveis, materiais translúcidos e profundidade, tipografia (dimensionamento óptico, tracking, leading), redução de movimento (reduced-motion), ou os fundamentos de design (feedback, consistência espacial, moderação) por trás das interfaces no estilo Apple.
---

# Design da Apple

Como a Apple constrói interfaces que deixam de parecer um computador e passam a parecer uma extensão sua. Esse conhecimento vem das palestras de design da WWDC da Apple — principalmente *Designing Fluid Interfaces* (WWDC 2018) — destilado e traduzido para a plataforma web (CSS, Pointer Events, `requestAnimationFrame`, bibliotecas de molas/springs como Motion/Framer Motion).

A linha condutora: **uma interface parece viva quando o movimento começa a partir do valor atual na tela, herda a velocidade do usuário, projeta o momento para frente e pode ser agarrado e revertido a qualquer instante.** Molas (springs) são a ferramenta que torna tudo isso natural, porque são inerentemente interruptíveis e sensíveis à velocidade.

## A Ideia Central

> "Quando alinhamos a interface com a forma como pensamos e nos movemos, algo mágico acontece — ela deixa de parecer um computador e começa a parecer uma extensão perfeita de nós."

Uma interface é fluida quando se comporta como o mundo físico: as coisas respondem instantaneamente, movem-se continuamente, carregam momento, resistem nos limites e podem ser redirecionadas no meio do movimento. Tudo abaixo é uma forma de chegar mais perto disso.

A Apple enquadra o design como algo que atende a quatro necessidades humanas: **segurança/previsibilidade, compreensão, realização e alegria (joy).** Toda regra aqui serve a uma delas.

## 1. Resposta — elimine a latência

No momento em que o atraso aparece, a sensação de direcionamento cai drasticamente. A resposta é a fundação sobre a qual todo o resto é construído.

- **Responda no `pointer-down`, não na liberação.** Destaque um botão no instante em que ele é pressionado. Esperar o `click` / levantar do dedo para mostrar feedback faz a interface parecer morta.
- **Seja vigilante sobre qualquer latência.** Audite debounces, timers artificiais, esperas de transição e o atraso de toque de ~300ms. Qualquer coisa no caminho da entrada (input) que não seja essencial é um retrocesso.
- **O feedback deve ser contínuo *durante* a interação, não apenas no final.** Para um arrasto, slider ou gaveta, atualize a UI em uma proporção de 1:1 com o ponteiro durante todo o caminho — nunca anime apenas quando o gesto for concluído.

```css
/* O feedback vive no clique (pressão), e é instantâneo */
.button:active {
  transform: scale(0.97);
  transition: transform 100ms ease-out;
}