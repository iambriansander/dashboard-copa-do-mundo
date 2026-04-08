# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
streamlit run dashboard.py
```

Runs on `http://localhost:8501`. Requires `pip install streamlit pandas plotly`.

## Architecture

Single-file app: everything lives in `dashboard.py`. No modules, no tests.

**Function call chain in `main()`:**
```
load_data()          → reads/cleans 3 CSVs, cached with @st.cache_data
get_colors(dark)     → returns theme dict (bg, card, border, text, muted, shadow, template + palette)
inject_css(c)        → injects CSS (DM Sans + JetBrains Mono fonts, card hover animations)
render_header()      → title + dark/light toggle via st.session_state.dark_mode + st.rerun()
render_hero()        → 6 panoramic KPIs (editions, goals, attendance, teams, champions, players)
render_bloco1()      → "A Evolução do Futebol" — 4 KPIs + 4 charts (goals, attendance, GPM trend, teams)
render_bloco2()      → "Quem Dominou a Copa" — 4 KPIs + 2 charts + Finals table
render_bloco3()      → "Dentro de Campo" — 4 KPIs + donut + bar + Goleadas table
render_bloco4()      → "Os Craques" — 4 KPIs + 3 charts (scorers, caps, yellow cards)
render_footer()      → links para Kaggle e GitHub
```

## Data quirks

Three CSVs in `data/`:

- `WorldCups.csv` — `Attendance` uses `.` as thousands separator (`590.549` = 590,549). Strip dots before casting to float.
- `WorldCupMatches.csv` — `Year` column can have NaN rows; always `dropna(subset=[..., "Year"])` before `.astype(int)`. Goals columns need `pd.to_numeric(..., errors="coerce").fillna(0)`.
- `WorldCupPlayers.csv` — `Event` encodes own goals as `OG40'`. Use `(?<![A-Z])G\d+` (negative lookbehind) to count only regular goals.

## Theming

All Plotly charts use `color_discrete_sequence=["#hex"]` — never `color_continuous_scale`. The continuous scale variant throws `ValueError` when a column has only one unique value (common with small datasets like this one).

Chart backgrounds are always `paper_bgcolor="rgba(0,0,0,0)"` and `plot_bgcolor="rgba(0,0,0,0)"` so they adapt to both light and dark themes via the Streamlit background.

## Deploy

Hosted on Streamlit Community Cloud from `github.com/iambriansander/dashboard-copa-do-mundo`, branch `main`, file `dashboard.py`. Push to main triggers a redeploy (or use "Reboot app" in the dashboard).

## Docs

- `.llm/prd.md` — approved PRD with product goals, visual spec, and scope boundaries
- `docs/superpowers/plans/2026-04-07-dashboard-final.md` — current implementation plan
