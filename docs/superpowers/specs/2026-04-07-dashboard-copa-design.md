# Dashboard Copa do Mundo — Design Spec
**Data:** 2026-04-07

## Objetivo
Dashboard interativo em Streamlit para explorar dados históricos das Copas do Mundo FIFA (1930–2014), com navegação por sidebar e 4 seções: Visão Geral, Seleções, Partidas e Jogadores.

## Dados
| Arquivo | Linhas | Conteúdo |
|---|---|---|
| `data/WorldCups.csv` | 20 | Edições: campeão, gols, público, times qualificados |
| `data/WorldCupMatches.csv` | 4.572 | Partidas: times, gols, fase, estádio, árbitro |
| `data/WorldCupPlayers.csv` | 37.784 | Jogadores: nome, posição, eventos (gols, cartões, subs) |

## Arquitetura

### Arquivo único: `dashboard.py`
- `load_data()` — lê e limpa os 3 CSVs com `@st.cache_data`
- `page_visao_geral(df_cups)` — seção Visão Geral
- `page_selecoes(df_matches)` — seção Seleções
- `page_partidas(df_matches)` — seção Partidas
- `page_jogadores(df_players)` — seção Jogadores
- `main()` — sidebar com `st.radio()` + roteamento para as páginas

### Navegação
Sidebar com `st.radio()` contendo 4 opções em português. O conteúdo principal renderiza a função correspondente à opção selecionada.

### Limpeza de dados (em `load_data`)
- `WorldCupMatches`: remover linhas duplicadas/vazias, converter `Year` para int
- `WorldCupPlayers`: parsear coluna `Event` para extrair gols (`G\d+`), cartões amarelos (`Y\d+`), cartões vermelhos (`R\d+`), e substituições

## KPIs e Visualizações por Seção

### Visão Geral (`df_cups`)
**KPIs (st.metric em 4 colunas):**
- Total de Copas disputadas
- Total de Gols marcados (soma histórica)
- Total de Partidas jogadas
- Maior Público numa edição

**Gráficos:**
- Linha: gols por edição ao longo dos anos
- Barra: público total por edição (Attendance)
- Barra: número de times classificados por edição

### Seleções (`df_matches`)
**KPIs (st.metric em 3 colunas):**
- Seleção mais campeã (+ número de títulos)
- Total de seleções diferentes que participaram
- País sede com mais Copas realizadas

**Gráficos:**
- Barra horizontal: ranking de campeões por número de títulos
- Barra horizontal: Top 10 seleções por gols marcados (soma de gols como mandante + visitante)

### Partidas (`df_matches`)
**KPIs (st.metric em 3 colunas):**
- Média de gols por partida
- Placar mais frequente
- % de vitórias do time mandante

**Gráficos:**
- Histograma: distribuição do total de gols por partida
- Barra: média de gols por fase (Group, Quarter-finals, Semi-finals, Final, etc.)

### Jogadores (`df_players`)
**KPIs (st.metric em 4 colunas):**
- Artilheiro histórico (nome + gols)
- Jogador com mais convocações
- Total de cartões amarelos
- Total de cartões vermelhos

**Gráficos:**
- Barra horizontal: Top 15 artilheiros históricos
- Barra horizontal: Top 10 jogadores com mais convocações (aparições em partidas)

## Stack Técnica
- `streamlit` — framework do dashboard
- `pandas` — leitura e manipulação dos CSVs
- `plotly.express` — todos os gráficos interativos

## Idioma
Todos os textos, títulos, labels e métricas em **português**.
