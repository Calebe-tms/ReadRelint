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
```

## 2. Manipulação direta — rastreamento 1:1

> "Toque e conteúdo devem se mover juntos."

Quando o usuário arrasta algo, esse elemento deve ficar "colado" ao dedo — e respeitar o deslocamento (offset) de *onde foi agarrado*. Centralizar o elemento no dedo instantaneamente ao agarrar quebra a ilusão imediatamente.

- Use Pointer Events com `setPointerCapture` para que o rastreamento continue mesmo quando o ponteiro sair dos limites do elemento.
- Rastreie um curto **histórico de velocidade/posição** (últimos eventos `pointermove`), não apenas o ponto atual — você precisará da velocidade no momento em que o usuário soltar o elemento.

```js
el.addEventListener('pointerdown', (e) => {
  el.setPointerCapture(e.pointerId);
  const grabOffset = e.clientY - el.getBoundingClientRect().top; // respeite onde foi agarrado
  // ...rastreie a posição + histórico de timestamp para velocidade
});
```

## 3. Interruptibilidade — o princípio mais importante

> "O pensamento e o gesto acontecem em paralelo."

Toda animação deve ser interruptível e redirecionável a qualquer momento. Um usuário deve poder agarrar um elemento em movimento no meio do caminho e revertê-lo sem esperar a animação terminar. Um modal se fechando que o usuário agarra novamente deve seguir o dedo — não terminar de fechar primeiro, para depois reabrir.

- **Nunca bloqueie a entrada (input) durante uma transição.**
- **Sempre anime a partir do valor *apresentado* (atual), nunca do valor alvo.** Ao interromper, leia a transformação real na tela do elemento e inicie a nova animação a partir dali. Começar do valor lógico/alvo causa um "pulo" visual.
- **Evite transições CSS e `@keyframes` para qualquer coisa controlada por gestos** — elas não podem ser suavemente agarradas e revertidas durante a execução. Molas animam do valor atual por padrão, que é exatamente o que a interrupção precisa.
- **Quando um gesto é revertido, misture a velocidade — não a corte bruscamente.** Substituir uma animação por outra em uma reversão cria uma descontinuidade de velocidade, como bater numa "parede de tijolos". Bibliotecas de molas que mantêm a velocidade durante um redirecionamento evitam isso. (É isso que as *animações aditivas* do iOS fazem nativamente; na web, escolha uma biblioteca de molas que redirecione a partir da velocidade atual).
- **Decomponha o movimento 2D em molas X e Y independentes.** Uma única mola em uma distância 2D perde a sincronia quando X e Y têm velocidades diferentes.

## 4. Comportamento acima da animação — use molas (springs)

> "Pense na animação como uma conversa entre você e o objeto, não algo prescrito pela interface."

Uma animação pré-escrita de duração fixa não pode responder a novos inputs. Uma mola pode — um novo input apenas muda o alvo, e o movimento continua de forma fluida. Prefira molas para qualquer coisa que o usuário possa tocar.

A Apple substituiu deliberadamente o trio físico (massa/rigidez/amortecimento) por dois parâmetros amigáveis para designers. Pense nestes termos:

- **Taxa de amortecimento (Damping ratio)** — controla o exagero (overshoot). `1.0` = criticamente amortecido, sem salto, assentamento suave. `< 1.0` = ultrapassa e oscila. Menor = mais elástico (bouncy).
- **Resposta (Response)** — quão rapidamente o valor atinge o alvo, em segundos. Menor = mais ágil (snappy). **Isso não é "duração"** — uma mola não tem duração fixa; seu tempo de assentamento emerge dos parâmetros.

**Padrões:**
- Inicie a maioria das UIs com **damping `1.0`** (criticamente amortecido) — elegante e não distrai.
- Adicione salto (**damping ~`0.8`**) **apenas quando o próprio gesto carregar momento** (um movimento brusco, um arremesso, uma soltura de arrasto). Um overshoot em um menu que apenas apareceu em fade-in parece errado; overshoot em um card que você "arremessou" parece certo.

**Valores concretos que a Apple usa:**

| Interação | Amortecimento (Damping) | Resposta (Response) |
| --- | --- | --- |
| Mover / reposicionar (ex: PiP) | `1.0` | `0.4` |
| Rotação | `0.8` | `0.4` |
| Gaveta (Drawer) / Painel (Sheet) | `0.8` | `0.3` |

**Mapeamento para Web (Motion / Framer Motion):** a API de mola `bounce` + `duration` mapeia de perto o amortecimento + resposta da Apple. Uma base segura é usar molas com `damping: 1.0` em todos os lugares por padrão; reserve o `bounce` para interações físicas impulsionadas por momento.

```js
import { animate } from 'motion';

// Padrão criticamente amortecido (sem overshoot)
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });

// Interação com momento — um pouco de bounce, apenas porque um movimento rápido precedeu
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4 });
```

## 5. Transferência de velocidade (Velocity handoff) — a costura entre arrastar e animar

Quando um gesto termina, a animação deve **continuar na velocidade exata do dedo**, para que não haja emenda visível entre arrastar e animar. Esse é o detalhe que mais separa o "fluido" do "ok".

Passe a velocidade de liberação do ponteiro como a velocidade inicial da mola. Algumas APIs de mola querem a velocidade **relativa** — normalize-a pela distância restante até o alvo:

```
velocidadeRelativa = velocidadeDoGesto / (valorAlvo − valorAtual)
```

Exemplo: elemento em `y=50`, alvo `y=150` (faltam 100px), dedo movendo a 50px/s → velocidade inicial da mola = `50 / 100 = 0.5`. O Framer Motion / Motion assumem a velocidade absoluta em px/s diretamente (opção `velocity`), então você geralmente fornece o valor bruto.

## 6. Projeção de momento — anime para onde o gesto *está indo*

> "Pegue um pequeno input e transforme-o em um grande output."

Não force o encaixe (snap) na borda mais próxima a partir do *ponto de liberação*. Use a velocidade para **projetar a posição de repouso** — exatamente como a desaceleração de rolagem (scroll) — e depois faça o encaixe (snap) no alvo mais próximo daquele ponto projetado. É isso que faz um "flick" (arremesso) parecer que jogou o elemento.

A função de projeção exata da Apple (do código de amostra *Designing Fluid Interfaces*):

```js
// decelerationRate ≈ 0.998 para sensação de scroll normal; 0.99 para mais ágil
function project(initialVelocity /* px/s */, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}

const projectedEndpoint = currentPosition + project(releaseVelocity);
const target = nearestSnapPoint(projectedEndpoint);   // escolha o alvo da projeção
animateSpringTo(target, { velocity: releaseVelocity }); // depois transfira a velocidade (§5)
```

Nota: a fórmula típica de livro de física `v²/(2·decel)` *não* é o que a Apple usa — use a forma de decaimento exponencial acima. Esse é o comportamento padrão em bons bottom-sheets e carrosséis (Vaul, Embla).

## 7. Consistência espacial — caminhos simétricos, origens ancoradas

> "Se algo desaparece de uma maneira, esperamos que emerja de onde veio."

- **Entre e saia pelo mesmo caminho.** Um painel que desliza da direita deve ser dispensado para a direita. Entrar pela direita / sair por baixo parece desconectado e confuso.
- **Ancore as interações à sua origem.** Um menu, popover ou painel deve se originar do elemento que o acionou — defina o `transform-origin` para o acionador, para que a relação espacial entre o botão e o conteúdo seja óbvia.
- **Espelhe o "easing" (curva) em transições reversíveis** para que o caminho de saída corresponda ao caminho de retorno (use pontos de controle cubic-bézier inversos para as duas direções).

## 8. Dê dicas na direção do gesto

Humanos preveem o estado final a partir de uma trajetória. Movimentos intermediários devem sinalizar para onde as coisas estão indo — os módulos do Centro de Controle "crescem e se projetam em direção ao seu dedo". Faça os frames intermediários apontarem para o resultado final, não apenas interpola-los cegamente até ele.

## 9. Efeito elástico (Rubber-banding) — limites suaves

Em uma borda, resista progressivamente em vez de parar abruptamente. Uma parada brusca parece "congelado"; a resistência contínua soa como "está responsivo, mas não há mais nada aqui". Aplique um amortecimento que aumenta quanto mais além do limite o usuário arrasta.

```js
// Quanto mais além do limite, menos o elemento segue — coisas reais desaceleram antes de parar
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

## 10. Detalhes de design de gestos (o checklist de "sensação")

- **Toque (Tap):** destaque no toque (para baixo, instantâneo), confirme na liberação (para cima). Adicione ~10px de margem (hysteresis) ao redor do alvo, e permita cancelar ao arrastar para longe e retornar.
- **Arrastar/deslizar:** exija um pequeno limite de movimento (hysteresis, ~10px) antes de confirmar uma direção, e então rastreie 1:1.
- **Detecte todos os gestos plausíveis em paralelo desde o primeiro movimento**, então cancele confiantemente os "perdedores" assim que a intenção for clara. Evite reconhecedores que só reportam o estado *final* (eventos tipo `swipeleft`) — eles descartam o rastreamento contínuo necessário para o feedback.
- **Minimize atrasos de desambiguação.** Detectar clique-duplo (double-tap) atrasa inevitavelmente cliques simples; pague esse preço apenas onde o duplo clique realmente existir.

## 11. Suavidade no nível do frame

Suavidade é sobre *o que está nos frames*, não apenas a taxa de quadros (frame rate).

- Mantenha a mudança posicional por quadro abaixo do limite de percepção para evitar efeito estroboscópico.
- Para movimentos muito rápidos, um sutil **desfoque/alongamento de movimento (motion blur)** codifica velocidade e é mais bem lido que um rastro duro e nítido.
- `requestAnimationFrame` é o relógio sincronizado da tela na web (a Apple usa `CADisplayLink`). Anime apenas propriedades amigáveis ao compositor (compositor-friendly) — `transform` e `opacity` — e dê dicas com `will-change` onde o movimento for iminente.

## 12. Materiais e profundidade — translucidez transmite hierarquia

A Apple usa materiais translúcidos como uma camada flutuante funcional que traz estrutura sem roubar o foco. Na web, aproxime isso com `backdrop-filter`.

- **Construa navbars/toolbars/painéis como camadas translúcidas** (`backdrop-filter: blur()` + um fundo semi-transparente) com o conteúdo rolando por baixo — e não barras opacas.
- **O peso do material codifica a hierarquia:** materiais mais escuros/pesados separam regiões estruturais (barras laterais); materiais mais leves chamam a atenção para elementos interativos (botões). **Nunca empilhe uma superfície translúcida clara sobre outra** — a legibilidade desmorona.
- **Superfícies maiores devem parecer mais grossas:** desfoque mais forte + uma sombra mais profunda que chips pequenos. Considere a sombra ciente do contexto — mais forte sobre conteúdo denso/texto para separação, mais clara sobre fundos simples.
- **Escureça para focar, separe para manter o fluxo.** Uma tarefa modal pareia a superfície com uma tela escurecedora (scrim) e empurra o fundo para trás/para baixo. Um painel não bloqueante paralelo usa translucidez e deslocamento *sem* escurecer o fundo, para que o fluxo não seja quebrado.
- **A vivacidade (vibrancy) mantém o texto legível sobre fundos que mudam.** Sobre superfícies borradas/translúcidas, não use texto cinza plano — use maior contraste, um peso ligeiramente maior, e um pequeno aumento no espaçamento entre letras. Coloque cor em uma camada sólida, não no primeiro plano translúcido.
- **Efeitos nas bordas de rolagem, não divisórias duras.** Em vez de uma borda de 1px sob um cabeçalho fixo, fade uma pequena máscara de desfoque/gradiente onde o conteúdo encontra o cromo flutuante — apenas onde a UI flutuante realmente se sobrepõe ao conteúdo.
- **Materialize, não faça apenas fade.** Para superfícise de vidro/blur, anime o raio de desfoque e a escala juntos na entrada/saída, para que a superfície pareça um material real chegando, em vez de um simples fade de opacidade.

```css
.toolbar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.4); /* borda superior brilhante = luz batendo no material */
}
```

## 13. Feedback multimodal — movimento + som + haptics

Três regras para combinar sentidos (de *Designing Audio-Haptic Experiences*):

1. **Causalidade** — deve ser óbvio o que causou o feedback. Acione-o no evento causal real (o botão alternando, o item se encaixando) e combine seu caráter com a fisicalidade da ação.
2. **Harmonia** — o visual, o som e o haptic (tátil) devem ser disparados no **mesmo frame**. A latência entre eles destrói a ilusão. Não deixe uma transição CSS atrasar o áudio/haptic (API de Vibração).
3. **Utilidade** — adicione feedback apenas onde ele merecer. Reserve haptics/som para momentos significativos (sucesso, erro, confirmação, encaixe). Feedback em excesso treina os usuários a ignorar tudo.

## 14. Movimento reduzido e acessibilidade

Movimento reduzido (Reduced motion) não significa *nenhum* feedback — significa um equivalente mais gentil e não vestibular. Responda a três sinais independentes e os incorpore em seus componentes:

- **`prefers-reduced-motion: reduce`** — substitua deslizamentos/molas/paralaxe por **fades curtos de opacidade ou transições estáticas**. Abandone elásticos/overshoot. Mantenha mudanças de opacidade/cor que ajudem a compreensão.
- **`prefers-reduced-transparency: reduce`** — torne superfícies translúcidas mais foscas/sólidas: aumente a opacidade do fundo, diminua o blur.
- **`prefers-contrast: more`** — fundos quase sólidos com uma borda contrastante definida.

Além disso: evite fundos em movimento na tela inteira, oscilações longas e lentas (perto de 0.2 Hz / um ciclo a cada 5s), e saltos abruptos de brilho (suavize mudanças entre tema escuro↔claro). Torne grandes objetos em movimento semitransparentes enquanto viajam, e oculte superfícies grandes durante um grande reposicionamento, voltando-as quando assentarem.

```css
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 200ms ease; transform: none !important; }
}
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
```

## 15. Tipografia — dimensionamento óptico, tracking, entrelinha

A Apple desenha o tipo para mudar de forma conforme o tamanho; a mesma disciplina se aplica à web. (De *The Details of UI Typography*, WWDC 2020.)

- **Tracking (espaçamento de letras) é específico ao tamanho — nunca um único valor para todos os tamanhos.** Textos grandes de display exigem tracking *negativo* (as letras parecem muito espaçadas conforme crescem); textos pequenos exigem tracking ligeiramente *positivo* para legibilidade. Um `letter-spacing` fixo estará errado em algum lugar. Aperte títulos, deixe o corpo do texto perto de `0`.
- **Leading (entrelinha) acompanha o tamanho de forma inversa.** Apertado em grandes títulos, mais solto no corpo do texto. Aumente para fontes com ascedentes/descendentes altos; aperte para UI densa e carregada de informações.
- **Construa hierarquia a partir de peso + tamanho + entrelinha como um conjunto**, não apenas tamanho. Destaque com o peso — isso adiciona presença sem tomar mais espaço.
- **Respeite a configuração de tamanho de texto do usuário** (Dynamic Type). Escale o layout *com* o texto — espaçamentos em `rem`/`em`, não px fixo — para que uma fonte maior não quebre o layout.
- **Prefira a fonte de sistema da plataforma** antes de uma fonte customizada; ela já vem com dimensionamento óptico, tabelas de tracking e ajustes de legibilidade. Substitua apenas por um bom motivo.

```css
:root { font: 100%/1.5 system-ui, sans-serif; } /* corpo: fonte do sistema, entrelinha confortável */

.display {
  font-size: clamp(2rem, 5vw, 4rem);
  line-height: 1.05;        /* entrelinha apertada para texto grande */
  letter-spacing: -0.02em;  /* tracking negativo conforme cresce */
  font-optical-sizing: auto;
}
```

## 16. Fundamentos de design — os oito princípios

O movimento e o ofício acima servem aos oito princípios de design da Apple (*Principles of Great Design*, WWDC 2026). Use-os como a base das suas decisões:

1. **Propósito.** Faça com intenção; decida o que *não* construir. Cada feature pede tempo, atenção e confiança do usuário — gaste esse orçamento apenas onde compensar.
2. **Autonomia (Agency).** Mantenha as pessoas no controle: ofereça escolhas, não force um único caminho. Apoie com tolerância a erros (perdão) — desfazer fácil para deslizes, diálogos de confirmação apenas para ações genuinamente destrutivas e irreversíveis (use com moderação).
3. **Responsabilidade.** Aja no interesse do usuário. Privacidade: peça no momento certo, de forma transparente. Segurança: antecipe mau uso e danos — especialmente com IA.
4. **Familiaridade.** Construa sobre o que as pessoas já conhecem. Use metáforas (uma lata de lixo significa apagar) e honre a física delas. Seja consistente.
5. **Flexibilidade.** Projete para diferentes contextos, dispositivos e para toda a gama de habilidades.
6. **Simplicidade — não minimalismo.** Remova o desnecessário para que o propósito central brilhe; enterrar tudo em um único lugar parece minimalista, mas não é simples.
7. **Ofício (Craft).** A atenção intransigente aos detalhes cria confiança. Tipografia bonita, cores que se adaptam à luz/sombra, iconografia clara e animações responsivas.
8. **Alegria (Delight).** O resultado de acertar os outros sete, não confete jogado por cima.

Regras táticas que servem a estes princípios:
- **Feedback em quatro tipos:** status, conclusão, aviso, erro.
- **Navegação (Wayfinding).** Cada tela deve responder: Onde estou? Para onde posso ir? O que há aqui? Como saio? Nunca prenda o usuário.
- **Agrupamento e mapeamento.** Proximidade implica relação.
- **Rótulos diretos e específicos.** Nomeie itens pela sua função, não com guarda-chuvas genéricos. Especificidade gera previsibilidade.

## 17. Processo

- **Protótipo interativo — vale "um milhão de designs estáticos."** Você descobre a interface construindo e brincando com ela.
- **Projete interação e visual juntos.** "Você não deveria conseguir dizer onde um termina e o outro começa". O movimento não é uma camada adicionada depois dos pixels.
- **Teste com pessoas reais no contexto real** e revise o movimento frame a frame.

## Referência Rápida

| Necessidade | Técnica | Valor Concreto |
| --- | --- | --- |
| Mola de UI padrão | Criticamente amortecida, sem overshoot | `damping 1.0`, `response 0.3–0.4` |
| Mola para momento / flick | Subamortecida, leve salto | `damping ~0.8`, `response 0.3–0.4` |
| Gesto → velocidade da mola | Transfira a velocidade de liberação | `gestureVelocity / (target − current)` se normalizado |
| Ponto de aterrissagem | Projetar momento | `current + (v/1000)·d/(1−d)`, `d ≈ 0.998` |
| Interromper de forma limpa | Começar a partir do valor (ativo) apresentado | leia o `transform` da tela |
| Evitar "parede de tijolos" ao reverter | Manter a velocidade no re-alvo (re-target) | mola que mistura a velocidade |
| Transição reversível | Espelhar a curva (easing curve) | inverse cubic-bézier |
| Arrastar 1:1 | Pointer Events + capture | respeite o deslocamento (offset) do agarre |
| Feedback | No `pointer-down`, contínuo | nunca apenas no final |
| Limite | Efeito elástico (rubber-band), não parada dura | resistência progressiva |
| Cromo translúcido | camada `backdrop-filter` | conteúdo rola por baixo |
| Tracking tipográfico | Específico do tamanho | diminua em texto grande (`-0.02em`), corpo perto de `0` |
| Redução de movimento | Cross-fade, sem slides/molas | `@media (prefers-reduced-motion)` |
