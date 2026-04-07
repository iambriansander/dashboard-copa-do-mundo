# Dashboard Copa do Mundo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar `dashboard.py` — dashboard Streamlit com sidebar de navegação e 4 seções (Visão Geral, Seleções, Partidas, Jogadores) usando dados históricos das Copas do Mundo FIFA.

**Architecture:** Arquivo único `dashboard.py` com funções de página separadas e `@st.cache_data` para carregamento de dados. Sidebar com `st.radio()` roteia para cada função de página. Dados lidos dos 3 CSVs em `data/` e processados na inicialização.

**Tech Stack:** Python 3, streamlit, pandas, plotly.express

---

## Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `dashboard.py` | Criar | App completo: load_data, 4 páginas, main |
| `data/WorldCups.csv` | Ler | Edições, campeões, gols, público |
| `data/WorldCupMatches.csv` | Ler | Partidas, gols, fases |
| `data/WorldCupPlayers.csv` | Ler | Jogadores, eventos (gols, cartões) |

---

## Task 1: Estrutura base e carregamento de dados

**Files:**
- Create: `dashboard.py`

- [ ] **Step 1: Criar o arquivo com imports e load_data()**

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Copa do Mundo FIFA",
    page_icon="⚽",
    layout="wide",
)


@st.cache_data
def load_data():
    df_cups = pd.read_csv("data/WorldCups.csv")
    df_matches = pd.read_csv("data/WorldCupMatches.csv")
    df_players = pd.read_csv("data/WorldCupPlayers.csv")

    # Limpar WorldCups
    df_cups["Year"] = df_cups["Year"].astype(int)
    df_cups["Attendance"] = (
        df_cups["Attendance"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    # Limpar WorldCupMatches
    df_matches = df_matches.dropna(subset=["Home Team Name", "Away Team Name"])
    df_matches["Year"] = df_matches["Year"].astype(int)
    df_matches["Home Team Goals"] = pd.to_numeric(
        df_matches["Home Team Goals"], errors="coerce"
    ).fillna(0).astype(int)
    df_matches["Away Team Goals"] = pd.to_numeric(
        df_matches["Away Team Goals"], errors="coerce"
    ).fillna(0).astype(int)
    df_matches["Total Goals"] = df_matches["Home Team Goals"] + df_matches["Away Team Goals"]
    df_matches["Home Team Name"] = df_matches["Home Team Name"].str.strip()
    df_matches["Away Team Name"] = df_matches["Away Team Name"].str.strip()

    # Limpar WorldCupPlayers e parsear eventos
    df_players = df_players.dropna(subset=["Player Name"])
    df_players["goals"] = df_players["Event"].str.count(r"G\d+")
    df_players["yellow_cards"] = df_players["Event"].str.count(r"Y\d+")
    df_players["red_cards"] = df_players["Event"].str.count(r"R\d+")

    return df_cups, df_matches, df_players
```

- [ ] **Step 2: Verificar que o arquivo foi criado corretamente**

```bash
head -5 dashboard.py
```
Esperado: linhas de import visíveis.

---

## Task 2: Página — Visão Geral

**Files:**
- Modify: `dashboard.py`

- [ ] **Step 1: Adicionar função page_visao_geral() após load_data()**

```python
def page_visao_geral(df_cups):
    st.title("⚽ Visão Geral das Copas do Mundo")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Copas", len(df_cups))
    col2.metric("Total de Gols", f"{df_cups['GoalsScored'].sum():,}".replace(",", "."))
    col3.metric("Total de Partidas", f"{df_cups['MatchesPlayed'].sum():,}".replace(",", "."))
    idx_max = df_cups["Attendance"].idxmax()
    melhor = df_cups.loc[idx_max]
    col4.metric(
        "Maior Público (edição)",
        f"{int(melhor['Attendance']):,}".replace(",", "."),
        help=f"{int(melhor['Year'])} — {melhor['Country']}",
    )

    st.divider()

    # Gráfico 1: Gols por edição
    fig1 = px.line(
        df_cups,
        x="Year",
        y="GoalsScored",
        markers=True,
        title="Gols Marcados por Edição",
        labels={"Year": "Ano", "GoalsScored": "Gols"},
    )
    fig1.update_traces(line_color="#00CC96")
    st.plotly_chart(fig1, use_container_width=True)

    col_a, col_b = st.columns(2)

    # Gráfico 2: Público por edição
    fig2 = px.bar(
        df_cups,
        x="Year",
        y="Attendance",
        title="Público Total por Edição",
        labels={"Year": "Ano", "Attendance": "Público"},
        color="Attendance",
        color_continuous_scale="Blues",
    )
    col_a.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3: Times classificados por edição
    fig3 = px.bar(
        df_cups,
        x="Year",
        y="QualifiedTeams",
        title="Times Classificados por Edição",
        labels={"Year": "Ano", "QualifiedTeams": "Times"},
        color="QualifiedTeams",
        color_continuous_scale="Oranges",
    )
    col_b.plotly_chart(fig3, use_container_width=True)
```

---

## Task 3: Página — Seleções

**Files:**
- Modify: `dashboard.py`

- [ ] **Step 1: Adicionar função page_selecoes() após page_visao_geral()**

```python
def page_selecoes(df_cups, df_matches):
    st.title("🏆 Desempenho das Seleções")

    # Calcular campeões
    champions = df_cups["Winner"].value_counts().reset_index()
    champions.columns = ["Seleção", "Títulos"]

    # Calcular gols por seleção (mandante + visitante)
    gols_casa = df_matches.groupby("Home Team Name")["Home Team Goals"].sum().rename("Gols")
    gols_fora = df_matches.groupby("Away Team Name")["Away Team Goals"].sum().rename("Gols")
    gols_total = gols_casa.add(gols_fora, fill_value=0).reset_index()
    gols_total.columns = ["Seleção", "Gols"]
    gols_top10 = gols_total.sort_values("Gols", ascending=False).head(10)

    # Participações únicas por país sede
    sedes = df_cups["Country"].value_counts()

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Seleção mais Campeã", champions.iloc[0]["Seleção"], f"{champions.iloc[0]['Títulos']} títulos")
    total_selecoes = len(
        pd.concat([df_matches["Home Team Name"], df_matches["Away Team Name"]]).unique()
    )
    col2.metric("Seleções Participantes", total_selecoes)
    col3.metric("País Sede com mais Copas", sedes.index[0], f"{sedes.iloc[0]} vez(es)")

    st.divider()

    col_a, col_b = st.columns(2)

    # Gráfico 1: Ranking de campeões
    fig1 = px.bar(
        champions,
        x="Títulos",
        y="Seleção",
        orientation="h",
        title="Ranking de Campeões Mundiais",
        labels={"Títulos": "Número de Títulos", "Seleção": ""},
        color="Títulos",
        color_continuous_scale="Greens",
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"})
    col_a.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Top 10 seleções por gols
    fig2 = px.bar(
        gols_top10,
        x="Gols",
        y="Seleção",
        orientation="h",
        title="Top 10 Seleções por Gols Marcados",
        labels={"Gols": "Total de Gols", "Seleção": ""},
        color="Gols",
        color_continuous_scale="Reds",
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    col_b.plotly_chart(fig2, use_container_width=True)
```

---

## Task 4: Página — Partidas

**Files:**
- Modify: `dashboard.py`

- [ ] **Step 1: Adicionar função page_partidas() após page_selecoes()**

```python
def page_partidas(df_matches):
    st.title("📊 Análise de Partidas")

    # Calcular placar mais frequente
    df_matches["Placar"] = (
        df_matches["Home Team Goals"].astype(str)
        + " x "
        + df_matches["Away Team Goals"].astype(str)
    )
    placar_freq = df_matches["Placar"].value_counts().idxmax()

    # % vitórias mandante
    vitorias_mandante = (df_matches["Home Team Goals"] > df_matches["Away Team Goals"]).sum()
    pct_mandante = vitorias_mandante / len(df_matches) * 100

    # Média de gols por fase
    gols_fase = (
        df_matches.groupby("Stage")["Total Goals"]
        .mean()
        .reset_index()
        .rename(columns={"Stage": "Fase", "Total Goals": "Média de Gols"})
        .sort_values("Média de Gols", ascending=False)
    )

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Média de Gols/Jogo", f"{df_matches['Total Goals'].mean():.2f}")
    col2.metric("Placar mais Frequente", placar_freq)
    col3.metric("Vitórias do Mandante", f"{pct_mandante:.1f}%")

    st.divider()

    col_a, col_b = st.columns(2)

    # Gráfico 1: Histograma de gols por partida
    fig1 = px.histogram(
        df_matches,
        x="Total Goals",
        nbins=15,
        title="Distribuição de Gols por Partida",
        labels={"Total Goals": "Gols na Partida", "count": "Número de Partidas"},
        color_discrete_sequence=["#636EFA"],
    )
    col_a.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Média de gols por fase
    fig2 = px.bar(
        gols_fase,
        x="Média de Gols",
        y="Fase",
        orientation="h",
        title="Média de Gols por Fase",
        labels={"Média de Gols": "Média de Gols", "Fase": ""},
        color="Média de Gols",
        color_continuous_scale="Purples",
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    col_b.plotly_chart(fig2, use_container_width=True)
```

---

## Task 5: Página — Jogadores

**Files:**
- Modify: `dashboard.py`

- [ ] **Step 1: Adicionar função page_jogadores() após page_partidas()**

```python
def page_jogadores(df_players):
    st.title("👤 Estatísticas de Jogadores")

    # Artilheiros: agregar por nome de jogador
    artilheiros = (
        df_players.groupby("Player Name")["goals"]
        .sum()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "goals": "Gols"})
        .sort_values("Gols", ascending=False)
    )
    top_artilheiro = artilheiros.iloc[0]

    # Convocações: número de aparições únicas por partida
    convocacoes = (
        df_players.groupby("Player Name")["MatchID"]
        .nunique()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "MatchID": "Convocações"})
        .sort_values("Convocações", ascending=False)
    )
    top_convocado = convocacoes.iloc[0]

    total_amarelos = df_players["yellow_cards"].sum()
    total_vermelhos = df_players["red_cards"].sum()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Artilheiro Histórico", top_artilheiro["Jogador"], f"{int(top_artilheiro['Gols'])} gols")
    col2.metric("Mais Convocado", top_convocado["Jogador"], f"{int(top_convocado['Convocações'])} partidas")
    col3.metric("Cartões Amarelos", f"{int(total_amarelos):,}".replace(",", "."))
    col4.metric("Cartões Vermelhos", f"{int(total_vermelhos):,}".replace(",", "."))

    st.divider()

    col_a, col_b = st.columns(2)

    # Gráfico 1: Top 15 artilheiros
    fig1 = px.bar(
        artilheiros.head(15),
        x="Gols",
        y="Jogador",
        orientation="h",
        title="Top 15 Artilheiros Históricos",
        labels={"Gols": "Gols Marcados", "Jogador": ""},
        color="Gols",
        color_continuous_scale="YlOrRd",
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"})
    col_a.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Top 10 mais convocados
    fig2 = px.bar(
        convocacoes.head(10),
        x="Convocações",
        y="Jogador",
        orientation="h",
        title="Top 10 Jogadores por Convocações",
        labels={"Convocações": "Partidas Disputadas", "Jogador": ""},
        color="Convocações",
        color_continuous_scale="Teal",
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    col_b.plotly_chart(fig2, use_container_width=True)
```

---

## Task 6: Função main() e sidebar de navegação

**Files:**
- Modify: `dashboard.py`

- [ ] **Step 1: Adicionar função main() e bloco de entrada no final do arquivo**

```python
def main():
    df_cups, df_matches, df_players = load_data()

    with st.sidebar:
        st.title("⚽ Copa do Mundo")
        st.caption("Dados históricos FIFA 1930–2014")
        st.divider()
        pagina = st.radio(
            "Navegação",
            options=["Visão Geral", "Seleções", "Partidas", "Jogadores"],
            index=0,
        )

    if pagina == "Visão Geral":
        page_visao_geral(df_cups)
    elif pagina == "Seleções":
        page_selecoes(df_cups, df_matches)
    elif pagina == "Partidas":
        page_partidas(df_matches)
    elif pagina == "Jogadores":
        page_jogadores(df_players)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar o dashboard**

```bash
streamlit run dashboard.py
```

Esperado: browser abre em `http://localhost:8501` com o dashboard funcionando.

- [ ] **Step 3: Verificar cada seção manualmente**
  - Clicar em "Visão Geral" → ver 4 KPIs e 3 gráficos
  - Clicar em "Seleções" → ver 3 KPIs, ranking de campeões, top gols
  - Clicar em "Partidas" → ver 3 KPIs, histograma, barras por fase
  - Clicar em "Jogadores" → ver 4 KPIs, artilheiros, convocações

- [ ] **Step 4: Commit**

```bash
git add dashboard.py
git commit -m "feat: add Copa do Mundo interactive dashboard

- Sidebar navigation with 4 sections (Visão Geral, Seleções, Partidas, Jogadores)
- KPIs and Plotly charts per section
- Data loaded from data/WorldCups.csv, WorldCupMatches.csv, WorldCupPlayers.csv"
```
