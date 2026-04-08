import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Copa do Mundo FIFA",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_data():
    df_cups = pd.read_csv("data/WorldCups.csv")
    df_matches = pd.read_csv("data/WorldCupMatches.csv")
    df_players = pd.read_csv("data/WorldCupPlayers.csv")

    df_cups["Year"] = df_cups["Year"].astype(int)
    df_cups["Attendance"] = (
        df_cups["Attendance"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    df_matches = df_matches.dropna(subset=["Home Team Name", "Away Team Name", "Year"])
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

    df_players = df_players.dropna(subset=["Player Name"])
    df_players["goals"] = df_players["Event"].str.count(r"(?<![A-Z])G\d+")
    df_players["yellow_cards"] = df_players["Event"].str.count(r"Y\d+")
    df_players["red_cards"] = df_players["Event"].str.count(r"R\d+")

    return df_cups, df_matches, df_players


def get_colors(dark: bool) -> dict:
    if dark:
        return {
            "bg": "#0e1117",
            "card": "#1a1f2e",
            "card_border": "#2d3748",
            "text": "#e2e8f0",
            "text_muted": "#94a3b8",
            "shadow": "0 2px 12px rgba(0,0,0,0.4)",
            "plotly_template": "plotly_dark",
            "plot_bg": "#1a1f2e",
            "paper_bg": "#1a1f2e",
        }
    return {
        "bg": "#f8fafc",
        "card": "#ffffff",
        "card_border": "#e2e8f0",
        "text": "#1e293b",
        "text_muted": "#64748b",
        "shadow": "0 2px 8px rgba(0,0,0,0.08)",
        "plotly_template": "plotly_white",
        "plot_bg": "#ffffff",
        "paper_bg": "#ffffff",
    }


def inject_css(c: dict):
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: {c['bg']};
    }}
    [data-testid="stHeader"] {{
        background-color: {c['bg']};
        border-bottom: 1px solid {c['card_border']};
    }}
    [data-testid="stSidebar"] {{
        display: none;
    }}
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }}
    .kpi-card {{
        background: {c['card']};
        border: 1px solid {c['card_border']};
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: {c['shadow']};
        text-align: center;
    }}
    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {c['text_muted']};
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 800;
        color: {c['text']};
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: 0.78rem;
        color: {c['text_muted']};
        margin-top: 4px;
    }}
    .section-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {c['text']};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #00d4aa;
        display: inline-block;
    }}
    .chart-card {{
        background: {c['card']};
        border: 1px solid {c['card_border']};
        border-radius: 16px;
        padding: 8px;
        box-shadow: {c['shadow']};
        margin-bottom: 16px;
    }}
    .js-plotly-plot, .plotly {{
        border-radius: 12px;
    }}
    @media (max-width: 768px) {{
        [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }}
        .kpi-value {{
            font-size: 1.5rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_header(dark: bool) -> bool:
    """Renderiza o header e retorna o novo estado do dark mode."""
    icon = "🌙" if not dark else "☀️"
    label = "Modo Escuro" if not dark else "Modo Claro"

    col_title, col_spacer, col_btn = st.columns([6, 2, 2])
    with col_title:
        st.markdown(
            f"""<h1 style="margin:0; font-size:1.6rem; font-weight:800; color:{'#1e293b' if not dark else '#e2e8f0'};">
            ⚽ Copa do Mundo FIFA <span style="font-size:0.9rem; font-weight:400; color:#00d4aa;">1930 – 2014</span>
            </h1>""",
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button(f"{icon} {label}", use_container_width=True):
            return not dark
    return dark


def render_kpis(df_cups, df_matches, df_players, c: dict):
    st.markdown('<p class="section-title">Números da Competição</p>', unsafe_allow_html=True)

    total_copas = len(df_cups)
    total_gols = int(df_cups["GoalsScored"].sum())
    total_partidas = int(df_cups["MatchesPlayed"].sum())
    idx_max = df_cups["Attendance"].idxmax()
    melhor = df_cups.loc[idx_max]
    maior_publico = int(melhor["Attendance"])
    maior_publico_ano = int(melhor["Year"])

    total_selecoes = len(
        pd.concat([df_matches["Home Team Name"], df_matches["Away Team Name"]]).unique()
    )

    champions = df_cups["Winner"].value_counts()
    maior_campeao = champions.index[0]
    maior_campeao_titulos = int(champions.iloc[0])

    artilheiros = (
        df_players.groupby("Player Name")["goals"]
        .sum()
        .reset_index()
        .sort_values("goals", ascending=False)
    )
    top_scorer = artilheiros.iloc[0]

    kpis = [
        ("Edições", str(total_copas), "1930 a 2014"),
        ("Gols Marcados", f"{total_gols:,}".replace(",", "."), f"{total_partidas:,} partidas".replace(",", ".")),
        ("Maior Público", f"{maior_publico:,}".replace(",", "."), f"Copa {maior_publico_ano}"),
        ("Seleções", str(total_selecoes), "países diferentes"),
        ("Maior Campeão", maior_campeao, f"{maior_campeao_titulos} títulos"),
        ("Artilheiro", top_scorer["Player Name"].split()[-1], f"{int(top_scorer['goals'])} gols"),
    ]

    cols = st.columns(6)
    for col, (label, value, sub) in zip(cols, kpis):
        with col:
            st.markdown(
                f"""<div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)


def render_gols_chart(df_cups, c: dict):
    st.markdown('<p class="section-title">Evolução Histórica</p>', unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_cups["Year"],
        y=df_cups["GoalsScored"],
        mode="lines+markers",
        name="Gols",
        line=dict(color="#00d4aa", width=3),
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.15)",
        marker=dict(size=8, color="#00d4aa"),
        hovertemplate="<b>%{x}</b><br>Gols: %{y}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_cups["Year"],
        y=df_cups["Attendance"],
        mode="lines+markers",
        name="Público",
        yaxis="y2",
        line=dict(color="#7c6af7", width=2, dash="dot"),
        marker=dict(size=6, color="#7c6af7"),
        hovertemplate="<b>%{x}</b><br>Público: %{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        template=c["plotly_template"],
        paper_bgcolor=c["paper_bg"],
        plot_bgcolor=c["plot_bg"],
        height=280,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Gols", gridcolor=c["card_border"]),
        yaxis2=dict(title="Público", overlaying="y", side="right", gridcolor="transparent"),
        xaxis=dict(gridcolor=c["card_border"]),
        hovermode="x unified",
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


def render_teams(df_cups, df_matches, c: dict):
    st.markdown('<p class="section-title">Seleções</p>', unsafe_allow_html=True)

    champions = df_cups["Winner"].value_counts().reset_index()
    champions.columns = ["Seleção", "Títulos"]

    gols_casa = df_matches.groupby("Home Team Name")["Home Team Goals"].sum().rename("Gols")
    gols_fora = df_matches.groupby("Away Team Name")["Away Team Goals"].sum().rename("Gols")
    gols_total = gols_casa.add(gols_fora, fill_value=0).reset_index()
    gols_total.columns = ["Seleção", "Gols"]
    gols_top10 = gols_total.sort_values("Gols", ascending=False).head(10)

    col_a, col_b = st.columns(2)

    with col_a:
        fig1 = px.bar(
            champions,
            x="Títulos",
            y="Seleção",
            orientation="h",
            title="🏆 Campeões Mundiais",
            color="Títulos",
            color_continuous_scale=[[0, "#00a884"], [1, "#00d4aa"]],
            text="Títulos",
        )
        fig1.update_layout(
            template=c["plotly_template"],
            paper_bgcolor=c["paper_bg"],
            plot_bgcolor=c["plot_bg"],
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
            showlegend=False,
        )
        fig1.update_traces(textposition="outside")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        fig2 = px.bar(
            gols_top10,
            x="Gols",
            y="Seleção",
            orientation="h",
            title="⚽ Top 10 — Gols Marcados",
            color="Gols",
            color_continuous_scale=[[0, "#c0392b"], [1, "#ff6b35"]],
            text="Gols",
        )
        fig2.update_layout(
            template=c["plotly_template"],
            paper_bgcolor=c["paper_bg"],
            plot_bgcolor=c["plot_bg"],
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
            showlegend=False,
        )
        fig2.update_traces(textposition="outside")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)


def render_players(df_matches, df_players, c: dict):
    st.markdown('<p class="section-title">Partidas & Jogadores</p>', unsafe_allow_html=True)

    df_matches = df_matches.copy()
    gols_fase = (
        df_matches.groupby("Stage")["Total Goals"]
        .mean()
        .reset_index()
        .rename(columns={"Stage": "Fase", "Total Goals": "Média"})
        .sort_values("Média", ascending=False)
        .head(10)
    )

    artilheiros = (
        df_players.groupby("Player Name")["goals"]
        .sum()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "goals": "Gols"})
        .sort_values("Gols", ascending=False)
    )
    convocacoes = (
        df_players.groupby("Player Name")["MatchID"]
        .nunique()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "MatchID": "Partidas"})
        .sort_values("Partidas", ascending=False)
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        fig1 = px.bar(
            gols_fase,
            x="Média",
            y="Fase",
            orientation="h",
            title="📊 Média de Gols por Fase",
            color="Média",
            color_continuous_scale=[[0, "#4c51bf"], [1, "#7c6af7"]],
            text=gols_fase["Média"].round(1),
        )
        fig1.update_layout(
            template=c["plotly_template"],
            paper_bgcolor=c["paper_bg"],
            plot_bgcolor=c["plot_bg"],
            height=320,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
        )
        fig1.update_traces(textposition="outside")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        fig2 = px.bar(
            artilheiros.head(12),
            x="Gols",
            y="Jogador",
            orientation="h",
            title="🥇 Top 12 Artilheiros",
            color="Gols",
            color_continuous_scale=[[0, "#b7791f"], [1, "#ff6b35"]],
            text="Gols",
        )
        fig2.update_layout(
            template=c["plotly_template"],
            paper_bgcolor=c["paper_bg"],
            plot_bgcolor=c["plot_bg"],
            height=320,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
        )
        fig2.update_traces(textposition="outside")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_c:
        fig3 = px.bar(
            convocacoes.head(10),
            x="Partidas",
            y="Jogador",
            orientation="h",
            title="🌍 Top 10 Mais Convocados",
            color="Partidas",
            color_continuous_scale=[[0, "#065f46"], [1, "#00d4aa"]],
            text="Partidas",
        )
        fig3.update_layout(
            template=c["plotly_template"],
            paper_bgcolor=c["paper_bg"],
            plot_bgcolor=c["plot_bg"],
            height=320,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False,
        )
        fig3.update_traces(textposition="outside")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    df_cups, df_matches, df_players = load_data()

    c = get_colors(st.session_state.dark_mode)
    inject_css(c)

    novo_dark = render_header(st.session_state.dark_mode)
    if novo_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = novo_dark
        st.rerun()

    st.markdown("<hr style='margin: 8px 0 20px 0; opacity:0.15'>", unsafe_allow_html=True)

    render_kpis(df_cups, df_matches, df_players, c)
    render_gols_chart(df_cups, c)
    render_teams(df_cups, df_matches, c)
    render_players(df_matches, df_players, c)


if __name__ == "__main__":
    main()
