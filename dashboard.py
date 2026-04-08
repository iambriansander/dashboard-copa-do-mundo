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

    # WorldCups: Attendance usa ponto como separador de milhar (ex: "1.045.246")
    df_cups["Year"] = df_cups["Year"].astype(int)
    df_cups["Attendance"] = (
        df_cups["Attendance"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    # WorldCupMatches: dropna em Year antes do cast para evitar ValueError
    df_matches = df_matches.dropna(
        subset=["Home Team Name", "Away Team Name", "Year"]
    )
    df_matches["Year"] = df_matches["Year"].astype(int)
    df_matches["Home Team Goals"] = (
        pd.to_numeric(df_matches["Home Team Goals"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df_matches["Away Team Goals"] = (
        pd.to_numeric(df_matches["Away Team Goals"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df_matches["Total Goals"] = (
        df_matches["Home Team Goals"] + df_matches["Away Team Goals"]
    )
    df_matches["Home Team Name"] = df_matches["Home Team Name"].str.strip()
    df_matches["Away Team Name"] = df_matches["Away Team Name"].str.strip()

    # WorldCupPlayers: regex exclui gols contra (OG) com lookbehind negativo
    df_players = df_players.dropna(subset=["Player Name"])
    df_players["goals"] = df_players["Event"].str.count(r"(?<![A-Z])G\d+")
    df_players["yellow_cards"] = df_players["Event"].str.count(r"Y\d+")
    df_players["red_cards"] = df_players["Event"].str.count(r"R\d+")

    return df_cups, df_matches, df_players


def get_colors(dark: bool) -> dict:
    if dark:
        return {
            "bg": "#0f172a",
            "card": "#1e293b",
            "border": "#334155",
            "text": "#f1f5f9",
            "muted": "#94a3b8",
            "shadow": "0 2px 8px rgba(0,0,0,0.4)",
            "template": "plotly_dark",
        }
    return {
        "bg": "#f8fafc",
        "card": "#ffffff",
        "border": "#e2e8f0",
        "text": "#0f172a",
        "muted": "#64748b",
        "shadow": "0 2px 8px rgba(0,0,0,0.08)",
        "template": "plotly_white",
    }


def inject_css(c: dict):
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {c['bg']};
        }}
        [data-testid="stHeader"] {{
            background-color: {c['bg']};
        }}
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1200px;
        }}
        .kpi-wrap {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin: 16px 0 28px 0;
        }}
        .kpi-card {{
            flex: 1 1 160px;
            background: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: {c['shadow']};
        }}
        .kpi-label {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {c['muted']};
            margin: 0 0 6px 0;
        }}
        .kpi-value {{
            font-size: 1.75rem;
            font-weight: 800;
            color: {c['text']};
            line-height: 1.1;
            margin: 0;
        }}
        .kpi-sub {{
            font-size: 0.75rem;
            color: {c['muted']};
            margin: 4px 0 0 0;
        }}
        .block-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {c['text']};
            letter-spacing: -0.01em;
            margin: 0 0 4px 0;
        }}
        .block-subtitle {{
            font-size: 0.85rem;
            color: {c['muted']};
            margin: 0 0 20px 0;
        }}
        .section-divider {{
            border: none;
            border-top: 1px solid {c['border']};
            margin: 36px 0;
        }}
        @media (max-width: 768px) {{
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }}
            .kpi-value {{ font-size: 1.4rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(dark: bool, c: dict):
    text_color = c["text"]
    muted_color = c["muted"]
    col_title, _, col_btn = st.columns([7, 1, 2])
    with col_title:
        st.markdown(
            f"<h1 style='margin:0;font-size:1.7rem;font-weight:800;color:{text_color};'>"
            f"Copa do Mundo FIFA"
            f"<span style='font-size:0.9rem;font-weight:400;color:#0ea5e9;margin-left:12px;'>"
            f"1930 \u2013 2014</span></h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='margin:2px 0 0 0;font-size:0.85rem;color:{muted_color};'>"
            f"An\u00e1lise hist\u00f3rica de 20 edi\u00e7\u00f5es da Copa do Mundo FIFA</p>",
            unsafe_allow_html=True,
        )
    with col_btn:
        st.markdown("<div style='padding-top:8px'>", unsafe_allow_html=True)
        label = "\u2600 Claro" if dark else "\u263e Escuro"
        if st.button(label, use_container_width=True, key="theme_btn"):
            st.session_state.dark_mode = not dark
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_bloco1(df_cups, c: dict):
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(
        '<p class="block-title">A Evolu\u00e7\u00e3o do Futebol</p>'
        '<p class="block-subtitle">O esporte cresceu muito em 90 anos de Copa do Mundo</p>',
        unsafe_allow_html=True,
    )

    idx_max = df_cups["Attendance"].idxmax()
    melhor = df_cups.loc[idx_max]

    kpis = [
        ("Edi\u00e7\u00f5es", str(len(df_cups)), "1930 a 2014"),
        (
            "Gols Marcados",
            f"{int(df_cups['GoalsScored'].sum()):,}".replace(",", "."),
            f"em {int(df_cups['MatchesPlayed'].sum()):,} partidas".replace(",", "."),
        ),
        (
            "Maior P\u00fablico",
            f"{int(melhor['Attendance']):,}".replace(",", "."),
            f"Copa {int(melhor['Year'])} \u00b7 {melhor['Country']}",
        ),
        (
            "M\u00e9dia de Gols",
            f"{df_cups['GoalsScored'].mean():.1f}",
            "gols por edi\u00e7\u00e3o",
        ),
    ]

    cards_html = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{label}</p>'
        f'<p class="kpi-value">{value}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for label, value, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards_html}</div>', unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_cups["Year"],
        y=df_cups["GoalsScored"],
        fill="tozeroy",
        fillcolor="rgba(14,165,233,0.12)",
        line=dict(color="#0ea5e9", width=2.5),
        mode="lines+markers",
        marker=dict(size=7, color="#0ea5e9"),
        name="Gols",
        hovertemplate="<b>%{x}</b> \u2014 %{y} gols<extra></extra>",
    ))
    fig1.update_layout(
        template=c["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=240,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
        xaxis=dict(title="", gridcolor=c["border"]),
        yaxis=dict(title="Gols", gridcolor=c["border"]),
        hovermode="x unified",
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    fig2 = px.bar(
        df_cups,
        x="Year",
        y="Attendance",
        color_discrete_sequence=["#0ea5e9"],
        labels={"Year": "", "Attendance": "P\u00fablico"},
    )
    fig2.update_layout(
        template=c["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
        xaxis=dict(gridcolor=c["border"]),
        yaxis=dict(title="P\u00fablico", gridcolor=c["border"]),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


def render_bloco2(df_cups, df_matches, c: dict):
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(
        '<p class="block-title">Quem Dominou a Copa</p>'
        '<p class="block-subtitle">Poucos pa\u00edses concentram a maioria dos t\u00edtulos mundiais</p>',
        unsafe_allow_html=True,
    )

    champions = df_cups["Winner"].value_counts().reset_index()
    champions.columns = ["Selecao", "Titulos"]

    gols_casa = (
        df_matches.groupby("Home Team Name")["Home Team Goals"].sum().rename("Gols")
    )
    gols_fora = (
        df_matches.groupby("Away Team Name")["Away Team Goals"].sum().rename("Gols")
    )
    gols_total = gols_casa.add(gols_fora, fill_value=0).reset_index()
    gols_total.columns = ["Selecao", "Gols"]
    gols_top10 = gols_total.sort_values("Gols", ascending=False).head(10)

    total_selecoes = len(
        pd.concat(
            [df_matches["Home Team Name"], df_matches["Away Team Name"]]
        ).unique()
    )

    kpis = [
        (
            "Maior Campe\u00e3o",
            champions.iloc[0]["Selecao"],
            f"{int(champions.iloc[0]['Titulos'])} t\u00edtulos",
        ),
        ("Sele\u00e7\u00f5es Participantes", str(total_selecoes), "pa\u00edses diferentes"),
    ]
    cards_html = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{label}</p>'
        f'<p class="kpi-value">{value}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for label, value, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards_html}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        fig1 = px.bar(
            champions.sort_values("Titulos"),
            x="Titulos",
            y="Selecao",
            orientation="h",
            title="Ranking de Campe\u00f5es",
            color_discrete_sequence=["#10b981"],
            text="Titulos",
            labels={"Titulos": "T\u00edtulos", "Selecao": ""},
        )
        fig1.update_layout(
            template=c["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=0, r=20, t=40, b=0),
            showlegend=False,
        )
        fig1.update_traces(textposition="outside")
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        fig2 = px.bar(
            gols_top10.sort_values("Gols"),
            x="Gols",
            y="Selecao",
            orientation="h",
            title="Top 10 \u2014 Gols Marcados",
            color_discrete_sequence=["#f59e0b"],
            text="Gols",
            labels={"Gols": "Gols", "Selecao": ""},
        )
        fig2.update_layout(
            template=c["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=0, r=20, t=40, b=0),
            showlegend=False,
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


def render_bloco3(df_matches, df_players, c: dict):
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(
        '<p class="block-title">N\u00fameros que Surpreendem</p>'
        '<p class="block-subtitle">Estat\u00edsticas curiosas e os maiores jogadores da hist\u00f3ria</p>',
        unsafe_allow_html=True,
    )

    df_matches = df_matches.copy()
    df_matches["Placar"] = (
        df_matches["Home Team Goals"].astype(str)
        + "x"
        + df_matches["Away Team Goals"].astype(str)
    )
    placar_freq = df_matches["Placar"].value_counts().index[0]

    vitorias_mandante = (
        df_matches["Home Team Goals"] > df_matches["Away Team Goals"]
    ).sum()
    pct_mandante = round(vitorias_mandante / len(df_matches) * 100, 1)

    artilheiros = (
        df_players.groupby("Player Name")["goals"]
        .sum()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "goals": "Gols"})
        .sort_values("Gols", ascending=False)
        .reset_index(drop=True)
    )
    top_scorer = artilheiros.iloc[0]

    convocacoes = (
        df_players.groupby("Player Name")["MatchID"]
        .nunique()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "MatchID": "Partidas"})
        .sort_values("Partidas", ascending=False)
        .reset_index(drop=True)
    )

    gols_fase = (
        df_matches.groupby("Stage")["Total Goals"]
        .mean()
        .reset_index()
        .rename(columns={"Stage": "Fase", "Total Goals": "Media"})
        .sort_values("Media", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    gols_fase["MediaFmt"] = gols_fase["Media"].round(2).astype(str)

    kpis = [
        ("Placar Mais Frequente", placar_freq, "de todos os tempos"),
        ("Vit\u00f3rias do Mandante", f"{pct_mandante}%", "das partidas"),
        (
            "Artilheiro Hist\u00f3rico",
            top_scorer["Jogador"].split()[-1],
            f"{int(top_scorer['Gols'])} gols",
        ),
    ]
    cards_html = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{label}</p>'
        f'<p class="kpi-value">{value}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for label, value, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards_html}</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        fig1 = px.bar(
            gols_fase,
            x="Media",
            y="Fase",
            orientation="h",
            title="M\u00e9dia de Gols por Fase",
            color_discrete_sequence=["#0ea5e9"],
            text="MediaFmt",
            labels={"Media": "M\u00e9dia", "Fase": ""},
        )
        fig1.update_layout(
            template=c["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=0, r=20, t=40, b=0),
            showlegend=False,
        )
        fig1.update_traces(textposition="outside")
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        fig2 = px.bar(
            artilheiros.head(12).sort_values("Gols"),
            x="Gols",
            y="Jogador",
            orientation="h",
            title="Top 12 Artilheiros",
            color_discrete_sequence=["#f97316"],
            text="Gols",
            labels={"Gols": "Gols", "Jogador": ""},
        )
        fig2.update_layout(
            template=c["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=0, r=20, t=40, b=0),
            showlegend=False,
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with col_c:
        fig3 = px.bar(
            convocacoes.head(10).sort_values("Partidas"),
            x="Partidas",
            y="Jogador",
            orientation="h",
            title="Top 10 Mais Convocados",
            color_discrete_sequence=["#8b5cf6"],
            text="Partidas",
            labels={"Partidas": "Partidas", "Jogador": ""},
        )
        fig3.update_layout(
            template=c["template"],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=0, r=20, t=40, b=0),
            showlegend=False,
        )
        fig3.update_traces(textposition="outside")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


def render_footer(c: dict):
    muted_color = c["muted"]
    text_color = c["text"]
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:center; padding: 8px 0 24px 0;">
            <p style="font-size:0.8rem; color:{muted_color}; margin:0;">
                <strong style="color:{text_color};">Sobre o Projeto</strong>
                &nbsp;&middot;&nbsp;
                Dados: <a href="https://www.kaggle.com/datasets/abecklas/fifa-world-cup"
                    target="_blank" style="color:#0ea5e9;">Kaggle &mdash; FIFA World Cup Dataset</a>
                &nbsp;&middot;&nbsp; Per\u00edodo: 1930&ndash;2014
            </p>
            <p style="font-size:0.8rem; color:{muted_color}; margin:6px 0 0 0;">
                Python 3 &middot; Streamlit &middot; pandas &middot; Plotly
                &nbsp;&middot;&nbsp;
                <a href="https://github.com/iambriansander/dashboard-copa-do-mundo"
                    target="_blank" style="color:#0ea5e9;">github.com/iambriansander</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    dark = st.session_state.dark_mode
    c = get_colors(dark)
    inject_css(c)

    df_cups, df_matches, df_players = load_data()

    render_header(dark, c)
    render_bloco1(df_cups, c)
    render_bloco2(df_cups, df_matches, c)
    render_bloco3(df_matches, df_players, c)
    render_footer(c)


if __name__ == "__main__":
    main()
