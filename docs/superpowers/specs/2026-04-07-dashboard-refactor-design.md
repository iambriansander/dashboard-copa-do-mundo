# Dashboard Refactor — Design Spec
**Data:** 2026-04-07

## Objetivo
Refatorar `dashboard.py` de layout multi-página com sidebar para página única moderna, responsiva, com dark/light mode toggle.

## Visual

### Tema padrão: Light
- Background: `#f8fafc`
- Cards: `#ffffff` com `box-shadow: 0 2px 8px rgba(0,0,0,0.08)`
- Texto principal: `#1e293b`
- Acento primário: `#00d4aa` (teal)
- Acento secundário: `#7c6af7` (violeta)
- Acento terciário: `#ff6b35` (laranja)

### Dark mode
- Background: `#0e1117`
- Cards: `#1a1f2e`
- Texto principal: `#e2e8f0`
- Acentos idênticos

### Toggle
- Botão `☀️ / 🌙` no header, canto direito
- Estado mantido em `st.session_state["dark_mode"]` (default: False)

## Layout (página única, scroll vertical)

```
┌─ Header ─────────────────────────────[ ☀️/🌙 ]┐
├─ KPI row ─────────────────────────────────────┤
│  [Copas] [Gols] [Partidas] [Maior Público]    │
├─ Area chart (full width) ─────────────────────┤
│  Gols por Edição (área com gradiente)         │
├─ 2 colunas ───────────────────────────────────┤
│  [Campeões H-bar] │ [Top 10 Gols H-bar]       │
├─ 3 colunas ───────────────────────────────────┤
│  [Histograma] │ [Artilheiros] │ [Convocados]  │
└───────────────────────────────────────────────┘
```

## Responsividade
- `st.columns` nativo para grid
- CSS via `st.markdown()` com `@media (max-width: 768px)`: colunas colapsam para 1
- KPI cards: `flex-wrap` para empilhar em mobile
- Todos os gráficos: `use_container_width=True`

## Implementação
- Arquivo único: `dashboard.py` (reescrita completa)
- CSS injetado via `st.markdown("<style>...</style>", unsafe_allow_html=True)`
- Tema aplicado via variáveis CSS (`--bg`, `--card`, `--text`) trocadas por classe no `body`
- `load_data()` mantida idêntica (já testada e correta)
- Sem sidebar, sem tabs
