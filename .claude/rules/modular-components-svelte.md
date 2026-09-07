## Regra de Ouro
**Nunca** insira lógica de UI, navegação, listas de itens, estados ou estilos complexos diretamente em `+layout.svelte`. O layout deve conter apenas o esqueleto do grid global (< 30 linhas).

## Diretrizes de Modularização
1. **Isolamento de Componentes:** Todo elemento funcional de interface (Sidebar, Header, Menus, Modais, Dropdowns) deve ser extraído para arquivos dedicados em `frontend/src/lib/components/`.
2. **Uso do Svelte 5:** Utilize runas modernas (`$state`, `$derived`) e propriedades bidirecionais (`bindable`) para comunicação limpa entre o componente e o layout pai.
3. **Responsabilidades:**
   - **`+layout.svelte`:** Orquestração do grid e slots globais (`{@render children()}`).
   - **Componente (ex: `Sidebar.svelte`):** Gerenciamento interno de estado, animações, rotas ativas, submenus e persistência (`localStorage`).

## Checklist da IA
- Pediu UI/navegação? **Crie um componente separado em `$lib/components/`**.
- `+layout.svelte` deve apenas importar e renderizar o componente.