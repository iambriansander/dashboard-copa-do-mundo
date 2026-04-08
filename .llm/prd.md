# PRD — Copa do Mundo FIFA Dashboard
**Versão:** 1.0 | **Data:** 2026-04-07

---

## 1. Visão Geral

**Produto:** Dashboard analítico interativo sobre a história da Copa do Mundo FIFA (1930–2014).

**Propósito:** Portfólio técnico pessoal que demonstra habilidades em análise de dados com pandas e visualização de dados com Plotly, em um projeto de dados completo e bem estruturado.

**Plataforma:** Aplicação web Streamlit, hospedada no Streamlit Community Cloud. Responsiva para desktop e mobile.

**Repositório:** github.com/iambriansander/dashboard-copa-do-mundo

---

## 2. Público-Alvo

**Usuário primário:** Recrutadores técnicos, líderes de engenharia e cientistas de dados que avaliam o portfólio do desenvolvedor.

**O que o usuário quer ver:**
- Código limpo, organizado e sem bugs
- Análise de dados real com pandas (limpeza, agregações, transformações)
- Visualizações claras, informativas e interativas com Plotly
- Projeto com estrutura profissional (README, requirements, config)

---

## 3. Objetivos do Produto

| Objetivo | Métrica de Sucesso |
|---|---|
| Zero erros ao carregar | Nenhum `ValueError`, `KeyError` ou exception visível |
| Narrativa clara | Cada bloco tem título + subtítulo explicativo |
| Visualizações corretas | Todos os gráficos renderizam com dados reais |
| Portfólio completo | README com prints + descrição técnica no GitHub |

---

## 4. Fonte de Dados

| Arquivo | Linhas | Conteúdo |
|---|---|---|
| `data/WorldCups.csv` | 20 | Edições: campeão, gols, público, times qualificados |
| `data/WorldCupMatches.csv` | ~4.572 | Partidas: times, gols, fases, estádios |
| `data/WorldCupPlayers.csv` | ~37.784 | Jogadores: nome, eventos (gols `G\d+`, cartões `Y\d+`/`R\d+`) |

**Limpeza necessária:**
- `WorldCups.Attendance`: separador de milhar é `.` (ex: `590.549` = 590.549)
- `WorldCupMatches.Year`: pode ter linhas com NaN — usar `dropna` antes do cast
- `WorldCupPlayers.Event`: regex `(?<![A-Z])G\d+` para excluir gols contra (`OG`)

---

## 5. Estrutura do Dashboard

### Layout
Página única, scroll vertical. Sem sidebar de navegação. Sem tabs.

### Seções (em ordem)

#### Header
- Título: **"Copa do Mundo FIFA"** + subtítulo "Dados históricos · 1930–2014"
- Toggle dark/light mode (canto direito, discreto)

---

#### Bloco 1 — A Evolução do Futebol
> *Narrative: o esporte cresceu muito em 90 anos de Copa*

**KPIs (linha de métricas):**
- Total de edições
- Total de gols marcados
- Total de partidas jogadas
- Maior público de uma edição (ano + país)

**Gráficos:**
- Linha com área: gols por edição ao longo do tempo
- Barras: público total por edição

---

#### Bloco 2 — Quem Dominou a Copa
> *Narrative: poucos países concentram os títulos mundiais*

**KPIs:**
- Seleção mais campeã (+ número de títulos)
- Total de seleções participantes

**Gráficos:**
- Barras horizontais: ranking de campeões (ordenado por títulos)
- Barras horizontais: top 10 seleções por gols marcados (soma mandante + visitante)

---

#### Bloco 3 — Números que Surpreendem
> *Narrative: estatísticas curiosas e os maiores jogadores da história*

**KPIs:**
- Placar mais frequente de todos os tempos
- % de vitórias do time mandante
- Artilheiro histórico (nome + gols)

**Gráficos:**
- Histograma: distribuição de total de gols por partida
- Barras horizontais: top 12 artilheiros históricos
- Barras horizontais: top 10 jogadores com mais convocações (partidas únicas)

---

#### Rodapé — Sobre o Projeto
- **Dados:** Kaggle — FIFA World Cup Dataset · 1930–2014
- **Tecnologias:** Python 3 · Streamlit · pandas · Plotly
- **Autor:** Brian Sander · [github.com/iambriansander](https://github.com/iambriansander)
- Link para o repositório

---

## 6. Design Visual

**Tom:** Profissional e limpo. Sem emojis em títulos de seção.

| Elemento | Valor |
|---|---|
| Fundo | `#f8fafc` (off-white) |
| Cards | `#ffffff` com `box-shadow: 0 2px 8px rgba(0,0,0,0.08)` |
| Cor de destaque | `#0ea5e9` (azul-ciano — Sky 500) |
| Texto principal | `#0f172a` |
| Texto secundário | `#64748b` |
| Border/divisor | `#e2e8f0` |
| Border-radius | `12px` nos cards |
| Dark mode bg | `#0f172a` · cards `#1e293b` |

**Paleta dos gráficos Plotly:**
- Gols/Evolução: `#0ea5e9` (azul)
- Campeões: `#10b981` (verde esmeralda)
- Gols por seleção: `#f59e0b` (âmbar)
- Artilheiros: `#f97316` (laranja)
- Convocações: `#8b5cf6` (violeta)

**Responsividade:**
- CSS `@media (max-width: 768px)`: colunas do `st.columns` colapsam para 1
- KPI cards: `flex-wrap` para empilhar em telas pequenas

---

## 7. Stack Técnica

| Camada | Tecnologia |
|---|---|
| Framework | `streamlit >= 1.32` |
| Análise de dados | `pandas >= 2.0` |
| Gráficos | `plotly >= 5.18` |
| Estilo | CSS injetado via `st.markdown(unsafe_allow_html=True)` |
| Deploy | Streamlit Community Cloud |
| Repositório | GitHub — iambriansander/dashboard-copa-do-mundo |

**Arquivo único:** `dashboard.py`

Estrutura interna:
```
load_data()           → leitura e limpeza dos 3 CSVs (@st.cache_data)
get_colors(dark)      → dict com tokens de cor do tema atual
inject_css(c)         → CSS global injetado no início do render
render_header(dark)   → título + toggle dark mode
render_kpis(...)      → linha de métricas em cards HTML
render_bloco1(...)    → Evolução (linha + barras)
render_bloco2(...)    → Dominância (barras horizontais)
render_bloco3(...)    → Curiosidades (histograma + artilheiros)
render_footer()       → Sobre o projeto
main()                → orquestra tudo
```

---

## 8. Entregáveis

| Entregável | Descrição |
|---|---|
| `dashboard.py` | App Streamlit funcional, sem bugs |
| `requirements.txt` | `streamlit`, `pandas`, `plotly` com versões mínimas |
| `.streamlit/config.toml` | `headless=true`, `layout=wide` |
| `README.md` | Descrição do projeto, prints do dashboard, como rodar localmente, tecnologias |
| Deploy ativo | URL pública no Streamlit Community Cloud |

---

## 9. Fora do Escopo

- Filtros interativos por seleção ou ano
- Comparação entre seleções
- Dados pós-2014
- Autenticação ou área restrita
- Banco de dados (dados são lidos diretamente dos CSVs)
