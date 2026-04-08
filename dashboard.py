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

    # Attendance por partida
    df_matches["Attendance"] = (
        pd.to_numeric(
            df_matches["Attendance"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", "", regex=False),
            errors="coerce",
        )
    )

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
            "accent": "#0ea5e9",
            "green": "#10b981",
            "amber": "#f59e0b",
            "orange": "#f97316",
            "violet": "#8b5cf6",
            "rose": "#f43f5e",
            "table_row_alt": "#1a2332",
        }
    return {
        "bg": "#f8fafc",
        "card": "#ffffff",
        "border": "#e2e8f0",
        "text": "#0f172a",
        "muted": "#64748b",
        "shadow": "0 2px 8px rgba(0,0,0,0.08)",
        "template": "plotly_white",
        "accent": "#0ea5e9",
        "green": "#10b981",
        "amber": "#f59e0b",
        "orange": "#f97316",
        "violet": "#8b5cf6",
        "rose": "#f43f5e",
        "table_row_alt": "#f1f5f9",
    }


ACCENT = "#0ea5e9"


def inject_css(c: dict):
    bg = c["bg"]
    card = c["card"]
    border = c["border"]
    shadow = c["shadow"]
    muted = c["muted"]
    text = c["text"]
    alt_row = c["table_row_alt"]
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;0,9..40,800;1,9..40,400&family=JetBrains+Mono:wght@500;700&display=swap');

        [data-testid="stAppViewContainer"] > .main {{
            background-color: {bg};
            font-family: 'DM Sans', sans-serif;
        }}
        [data-testid="stHeader"] {{
            background-color: {bg};
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

        /* ---- Hero KPI row ---- */
        .hero-wrap {{
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin: 24px 0 8px 0;
        }}
        .hero-card {{
            flex: 1 1 140px;
            background: {card};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 22px 16px 16px 16px;
            box-shadow: {shadow};
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .hero-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(14,165,233,0.13);
        }}
        .hero-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #0ea5e9, #8b5cf6);
        }}
        .hero-label {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {muted};
            margin: 0 0 8px 0;
        }}
        .hero-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.65rem;
            font-weight: 700;
            color: {text};
            line-height: 1.1;
            margin: 0;
        }}
        .hero-sub {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.7rem;
            color: {muted};
            margin: 6px 0 0 0;
        }}

        /* ---- Section KPIs ---- */
        .kpi-wrap {{
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin: 14px 0 26px 0;
        }}
        .kpi-card {{
            flex: 1 1 160px;
            background: {card};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: {shadow};
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(14,165,233,0.1);
        }}
        .kpi-card::after {{
            content: '';
            position: absolute;
            bottom: 0; left: 16px; right: 16px;
            height: 2px;
            background: linear-gradient(90deg, transparent, {ACCENT}44, transparent);
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        .kpi-card:hover::after {{
            opacity: 1;
        }}
        .kpi-label {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.67rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {muted};
            margin: 0 0 6px 0;
        }}
        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.55rem;
            font-weight: 700;
            color: {text};
            line-height: 1.1;
            margin: 0;
        }}
        .kpi-sub {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            color: {muted};
            margin: 5px 0 0 0;
        }}

        /* ---- Section titles ---- */
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 0 0 4px 0;
        }}
        .section-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .block-title {{
            font-family: 'DM Sans', sans-serif;
            font-size: 1.2rem;
            font-weight: 800;
            color: {text};
            letter-spacing: -0.02em;
            margin: 0;
        }}
        .block-subtitle {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.82rem;
            color: {muted};
            margin: 0 0 20px 0;
            padding-left: 20px;
        }}
        .section-divider {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, {border}, transparent);
            margin: 44px 0 28px 0;
        }}

        /* ---- Mini table ---- */
        .mini-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.78rem;
            color: {text};
        }}
        .mini-table th {{
            text-align: left;
            padding: 10px 12px;
            font-weight: 700;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {muted};
            border-bottom: 2px solid {border};
        }}
        .mini-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid {border};
            transition: background 0.15s ease;
        }}
        .mini-table tr:nth-child(even) {{
            background: {alt_row};
        }}
        .mini-table tr:hover td {{
            background: {ACCENT}08;
        }}

        /* ---- Chart card wrapper ---- */
        .chart-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 20px 16px 12px 16px;
            box-shadow: {shadow};
            margin-bottom: 8px;
        }}

        /* ---- Responsive ---- */
        @media (max-width: 768px) {{
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }}
            .hero-value, .kpi-value {{ font-size: 1.25rem; }}
            .hero-card {{ flex: 1 1 45%; }}
            .block-title {{ font-size: 1.05rem; }}
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
            f"<h1 style='margin:0;font-family:DM Sans,sans-serif;font-size:1.8rem;"
            f"font-weight:800;color:{text_color};letter-spacing:-0.03em;'>"
            f"Copa do Mundo FIFA"
            f"<span style='font-size:0.85rem;font-weight:500;color:#0ea5e9;"
            f"margin-left:14px;font-family:JetBrains Mono,monospace;'>"
            f"1930\u20132014</span></h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='margin:4px 0 0 0;font-size:0.82rem;color:{muted_color};"
            f"font-family:DM Sans,sans-serif;'>"
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


def fmt(n: int) -> str:
    """Formata número com pontos como separador de milhar (pt-BR)."""
    return f"{n:,}".replace(",", ".")


def render_hero(df_cups, df_matches, df_players, c: dict):
    total_goals = int(df_cups["GoalsScored"].sum())
    total_matches = int(df_cups["MatchesPlayed"].sum())
    total_attendance = int(df_cups["Attendance"].sum())
    total_teams = len(
        pd.concat(
            [df_matches["Home Team Name"], df_matches["Away Team Name"]]
        ).unique()
    )
    total_champions = df_cups["Winner"].nunique()
    total_players = df_players["Player Name"].nunique()

    items = [
        ("Edi\u00e7\u00f5es", str(len(df_cups)), "1930 a 2014"),
        ("Total de Gols", fmt(total_goals), f"em {fmt(total_matches)} partidas"),
        ("P\u00fablico Total", f"{total_attendance / 1e6:.1f}M", "em todas as edi\u00e7\u00f5es"),
        ("Sele\u00e7\u00f5es", str(total_teams), "pa\u00edses participaram"),
        ("Campe\u00f5es", str(total_champions), "sele\u00e7\u00f5es diferentes"),
        ("Jogadores", fmt(total_players), "atletas registrados"),
    ]
    cards = "".join(
        f'<div class="hero-card">'
        f'<p class="hero-label">{lbl}</p>'
        f'<p class="hero-value">{val}</p>'
        f'<p class="hero-sub">{sub}</p>'
        f'</div>'
        for lbl, val, sub in items
    )
    st.markdown(f'<div class="hero-wrap">{cards}</div>', unsafe_allow_html=True)


def _chart_layout(c: dict, height: int = 260, **kwargs):
    """Retorna dict base de layout para todos os charts."""
    base = dict(
        template=c["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=0, r=20, t=40, b=0),
        showlegend=False,
    )
    base.update(kwargs)
    return base


def render_bloco1(df_cups, c: dict):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">'
        '<div class="section-dot" style="background:#0ea5e9;"></div>'
        '<p class="block-title">A Evolu\u00e7\u00e3o do Futebol</p>'
        '</div>'
        '<p class="block-subtitle">'
        'Como o esporte cresceu de 13 sele\u00e7\u00f5es em 1930 para 32 em 2014'
        '</p>',
        unsafe_allow_html=True,
    )

    idx_max_att = df_cups["Attendance"].idxmax()
    best_att = df_cups.loc[idx_max_att]
    df_cups_calc = df_cups.copy()
    df_cups_calc["GoalsPerMatch"] = df_cups_calc["GoalsScored"] / df_cups_calc["MatchesPlayed"]
    avg_gpm = df_cups_calc["GoalsPerMatch"].mean()

    kpis = [
        (
            "Maior P\u00fablico",
            fmt(int(best_att["Attendance"])),
            f"Copa {int(best_att['Year'])} \u00b7 {best_att['Country']}",
        ),
        (
            "M\u00e9dia de Gols",
            f"{df_cups['GoalsScored'].mean():.1f}",
            "gols por edi\u00e7\u00e3o",
        ),
        (
            "Gols / Partida",
            f"{avg_gpm:.2f}",
            "m\u00e9dia hist\u00f3rica",
        ),
        (
            "Crescimento",
            f"13 \u2192 32",
            "times classificados",
        ),
    ]
    cards = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{lbl}</p>'
        f'<p class="kpi-value">{val}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for lbl, val, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards}</div>', unsafe_allow_html=True)

    # Row 1: Gols por edição + Público por edição
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_cups["Year"],
            y=df_cups["GoalsScored"],
            fill="tozeroy",
            fillcolor="rgba(14,165,233,0.12)",
            line=dict(color="#0ea5e9", width=2.5),
            mode="lines+markers",
            marker=dict(size=6, color="#0ea5e9"),
            name="Gols",
            hovertemplate="<b>%{x}</b> \u2014 %{y} gols<extra></extra>",
        ))
        fig.update_layout(**_chart_layout(c, 250, title="Gols por Edi\u00e7\u00e3o"))
        fig.update_xaxes(title="", gridcolor=c["border"])
        fig.update_yaxes(title="Gols", gridcolor=c["border"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        fig = px.bar(
            df_cups, x="Year", y="Attendance",
            color_discrete_sequence=["#0ea5e9"],
            labels={"Year": "", "Attendance": "P\u00fablico"},
            title="P\u00fablico Total por Edi\u00e7\u00e3o",
        )
        fig.update_layout(**_chart_layout(c, 250))
        fig.update_xaxes(gridcolor=c["border"])
        fig.update_yaxes(title="P\u00fablico", gridcolor=c["border"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Row 2: Gols por partida (tendência) + Times classificados
    col3, col4 = st.columns(2)

    with col3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_cups_calc["Year"],
            y=df_cups_calc["GoalsPerMatch"],
            mode="lines+markers",
            line=dict(color="#10b981", width=2.5),
            marker=dict(size=6, color="#10b981"),
            hovertemplate="<b>%{x}</b> \u2014 %{y:.2f} gols/partida<extra></extra>",
        ))
        fig.add_hline(
            y=avg_gpm,
            line_dash="dash",
            line_color="#64748b",
            annotation_text=f"M\u00e9dia: {avg_gpm:.2f}",
            annotation_position="top right",
        )
        fig.update_layout(**_chart_layout(c, 250, title="Gols por Partida (Tend\u00eancia)"))
        fig.update_xaxes(title="", gridcolor=c["border"])
        fig.update_yaxes(title="Gols / Partida", gridcolor=c["border"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col4:
        fig = px.bar(
            df_cups, x="Year", y="QualifiedTeams",
            color_discrete_sequence=["#8b5cf6"],
            labels={"Year": "", "QualifiedTeams": "Times"},
            title="Sele\u00e7\u00f5es Classificadas por Edi\u00e7\u00e3o",
            text="QualifiedTeams",
        )
        fig.update_layout(**_chart_layout(c, 250))
        fig.update_traces(textposition="outside")
        fig.update_xaxes(gridcolor=c["border"])
        fig.update_yaxes(title="Times", gridcolor=c["border"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_bloco2(df_cups, df_matches, c: dict):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">'
        '<div class="section-dot" style="background:#10b981;"></div>'
        '<p class="block-title">Quem Dominou a Copa</p>'
        '</div>'
        '<p class="block-subtitle">'
        'Poucos pa\u00edses concentram a maioria dos t\u00edtulos mundiais'
        '</p>',
        unsafe_allow_html=True,
    )

    champions = df_cups["Winner"].value_counts().reset_index()
    champions.columns = ["Selecao", "Titulos"]

    runners_up = df_cups["Runners-Up"].value_counts().reset_index()
    runners_up.columns = ["Selecao", "Vices"]

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

    # Host country wins
    host_wins = df_cups[df_cups["Winner"] == df_cups["Country"]]

    kpis = [
        (
            "Maior Campe\u00e3o",
            champions.iloc[0]["Selecao"],
            f"{int(champions.iloc[0]['Titulos'])} t\u00edtulos",
        ),
        (
            "Maior Vice",
            runners_up.iloc[0]["Selecao"],
            f"{int(runners_up.iloc[0]['Vices'])} finais perdidas",
        ),
        (
            "Sele\u00e7\u00f5es",
            str(total_selecoes),
            "pa\u00edses participaram",
        ),
        (
            "Campe\u00e3o em Casa",
            f"{len(host_wins)}x",
            f"de {len(df_cups)} edi\u00e7\u00f5es",
        ),
    ]
    cards = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{lbl}</p>'
        f'<p class="kpi-value">{val}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for lbl, val, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(
            champions.sort_values("Titulos"),
            x="Titulos", y="Selecao", orientation="h",
            title="Ranking de Campe\u00f5es",
            color_discrete_sequence=["#10b981"],
            text="Titulos",
            labels={"Titulos": "T\u00edtulos", "Selecao": ""},
        )
        fig.update_layout(**_chart_layout(c, 280))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        fig = px.bar(
            gols_top10.sort_values("Gols"),
            x="Gols", y="Selecao", orientation="h",
            title="Top 10 \u2014 Gols por Sele\u00e7\u00e3o",
            color_discrete_sequence=["#f59e0b"],
            text="Gols",
            labels={"Gols": "Gols", "Selecao": ""},
        )
        fig.update_layout(**_chart_layout(c, 280))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Tabela de Finais
    st.markdown(
        '<p class="block-title" style="font-size:0.95rem;margin-top:12px;">'
        'Todas as Finais</p>',
        unsafe_allow_html=True,
    )
    border = c["border"]
    text_color = c["text"]
    rows = ""
    for _, row in df_cups.iterrows():
        yr = int(row["Year"])
        country = row["Country"]
        winner = row["Winner"]
        runner = row["Runners-Up"]
        third = row["Third"]
        rows += (
            f"<tr>"
            f"<td><strong>{yr}</strong></td>"
            f"<td>{country}</td>"
            f"<td style='color:#10b981;font-weight:600;'>{winner}</td>"
            f"<td>{runner}</td>"
            f"<td>{third}</td>"
            f"</tr>"
        )
    st.markdown(
        f'<div style="max-height:380px;overflow-y:auto;border:1px solid {border};'
        f'border-radius:10px;margin-bottom:8px;">'
        f'<table class="mini-table">'
        f"<thead><tr>"
        f"<th>Ano</th><th>Sede</th><th>Campe\u00e3o</th><th>Vice</th><th>Terceiro</th>"
        f"</tr></thead>"
        f"<tbody>{rows}</tbody>"
        f"</table></div>",
        unsafe_allow_html=True,
    )


def render_bloco3(df_cups, df_matches, c: dict):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">'
        '<div class="section-dot" style="background:#f59e0b;"></div>'
        '<p class="block-title">Dentro de Campo</p>'
        '</div>'
        '<p class="block-subtitle">'
        'Padr\u00f5es t\u00e1ticos e os placares mais marcantes da hist\u00f3ria'
        '</p>',
        unsafe_allow_html=True,
    )

    df_m = df_matches.copy()
    df_m["Diff"] = (df_m["Home Team Goals"] - df_m["Away Team Goals"]).abs()

    # Resultados
    home_wins = (df_m["Home Team Goals"] > df_m["Away Team Goals"]).sum()
    draws = (df_m["Home Team Goals"] == df_m["Away Team Goals"]).sum()
    away_wins = (df_m["Home Team Goals"] < df_m["Away Team Goals"]).sum()
    total = len(df_m)
    pct_home = round(home_wins / total * 100, 1)
    pct_draw = round(draws / total * 100, 1)
    pct_away = round(away_wins / total * 100, 1)

    # Placar mais frequente
    df_m["Placar"] = (
        df_m["Home Team Goals"].astype(str)
        + " x "
        + df_m["Away Team Goals"].astype(str)
    )
    placar_freq = df_m["Placar"].value_counts().index[0]
    placar_freq_n = int(df_m["Placar"].value_counts().iloc[0])

    # Maior goleada
    idx_goleada = df_m["Diff"].idxmax()
    goleada = df_m.loc[idx_goleada]
    g_home = goleada["Home Team Name"]
    g_away = goleada["Away Team Name"]
    g_score = f"{int(goleada['Home Team Goals'])} x {int(goleada['Away Team Goals'])}"
    g_year = int(goleada["Year"])

    # Media de gols por partida ao longo das edições
    gpm_by_year = df_m.groupby("Year")["Total Goals"].mean().reset_index()
    gpm_by_year.columns = ["Year", "MediaGols"]

    kpis = [
        ("Placar Mais Comum", placar_freq, f"ocorreu {placar_freq_n}x"),
        ("Vit\u00f3rias Mandante", f"{pct_home}%", f"{home_wins} de {total} jogos"),
        ("Empates", f"{pct_draw}%", f"{draws} partidas"),
        ("Maior Goleada", g_score, f"{g_home} vs {g_away} ({g_year})"),
    ]
    cards = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{lbl}</p>'
        f'<p class="kpi-value">{val}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for lbl, val, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Distribuição de resultados (donut)
        fig = go.Figure(data=[go.Pie(
            labels=["Mandante", "Empate", "Visitante"],
            values=[home_wins, draws, away_wins],
            hole=0.55,
            marker=dict(colors=["#0ea5e9", "#94a3b8", "#f59e0b"]),
            textinfo="label+percent",
            textfont=dict(size=12),
            hovertemplate="%{label}: %{value} jogos (%{percent})<extra></extra>",
        )])
        fig.update_layout(**_chart_layout(
            c, 280,
            title="Distribui\u00e7\u00e3o de Resultados",
        ))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # Média de gols por fase
        gols_fase = (
            df_m.groupby("Stage")["Total Goals"]
            .mean()
            .reset_index()
            .rename(columns={"Stage": "Fase", "Total Goals": "Media"})
            .sort_values("Media", ascending=False)
            .head(8)
        )
        gols_fase["MediaFmt"] = gols_fase["Media"].round(2).astype(str)
        fig = px.bar(
            gols_fase.sort_values("Media"),
            x="Media", y="Fase", orientation="h",
            title="M\u00e9dia de Gols por Fase",
            color_discrete_sequence=["#0ea5e9"],
            text="MediaFmt",
            labels={"Media": "M\u00e9dia", "Fase": ""},
        )
        fig.update_layout(**_chart_layout(c, 280))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Top 8 goleadas (tabela)
    st.markdown(
        '<p class="block-title" style="font-size:0.95rem;margin-top:12px;">'
        'Maiores Goleadas</p>',
        unsafe_allow_html=True,
    )
    top_goleadas = df_m.nlargest(8, "Diff")[
        ["Year", "Stage", "Home Team Name", "Home Team Goals", "Away Team Goals", "Away Team Name"]
    ]
    border = c["border"]
    rows = ""
    for _, r in top_goleadas.iterrows():
        hg = int(r["Home Team Goals"])
        ag = int(r["Away Team Goals"])
        rows += (
            f"<tr>"
            f"<td>{int(r['Year'])}</td>"
            f"<td>{r['Stage']}</td>"
            f"<td style='text-align:right;font-weight:600;'>{r['Home Team Name']}</td>"
            f"<td style='text-align:center;font-weight:700;color:#0ea5e9;'>"
            f"{hg} x {ag}</td>"
            f"<td style='font-weight:600;'>{r['Away Team Name']}</td>"
            f"</tr>"
        )
    st.markdown(
        f'<div style="border:1px solid {border};border-radius:10px;overflow:hidden;'
        f'margin-bottom:8px;">'
        f'<table class="mini-table">'
        f"<thead><tr>"
        f"<th>Ano</th><th>Fase</th>"
        f"<th style='text-align:right;'>Mandante</th>"
        f"<th style='text-align:center;'>Placar</th>"
        f"<th>Visitante</th>"
        f"</tr></thead>"
        f"<tbody>{rows}</tbody>"
        f"</table></div>",
        unsafe_allow_html=True,
    )


def render_bloco4(df_matches, df_players, c: dict):
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header">'
        '<div class="section-dot" style="background:#f97316;"></div>'
        '<p class="block-title">Os Craques</p>'
        '</div>'
        '<p class="block-subtitle">'
        'Artilheiros, recordistas e os n\u00fameros individuais que marcaram a hist\u00f3ria'
        '</p>',
        unsafe_allow_html=True,
    )

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
    most_capped = convocacoes.iloc[0]

    total_yellows = int(df_players["yellow_cards"].sum())
    total_reds = int(df_players["red_cards"].sum())

    # Top yellow card players
    yellow_rank = (
        df_players.groupby("Player Name")["yellow_cards"]
        .sum()
        .reset_index()
        .rename(columns={"Player Name": "Jogador", "yellow_cards": "Amarelos"})
        .sort_values("Amarelos", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    kpis = [
        (
            "Artilheiro Hist\u00f3rico",
            top_scorer["Jogador"].split()[-1],
            f"{int(top_scorer['Gols'])} gols",
        ),
        (
            "Mais Partidas",
            most_capped["Jogador"].split()[-1],
            f"{int(most_capped['Partidas'])} jogos",
        ),
        (
            "Cart\u00f5es Amarelos",
            fmt(total_yellows),
            "em toda a hist\u00f3ria",
        ),
        (
            "Cart\u00f5es Vermelhos",
            str(total_reds),
            "expuls\u00f5es",
        ),
    ]
    cards = "".join(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">{lbl}</p>'
        f'<p class="kpi-value">{val}</p>'
        f'<p class="kpi-sub">{sub}</p>'
        f'</div>'
        for lbl, val, sub in kpis
    )
    st.markdown(f'<div class="kpi-wrap">{cards}</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        fig = px.bar(
            artilheiros.head(12).sort_values("Gols"),
            x="Gols", y="Jogador", orientation="h",
            title="Top 12 Artilheiros",
            color_discrete_sequence=["#f97316"],
            text="Gols",
            labels={"Gols": "Gols", "Jogador": ""},
        )
        fig.update_layout(**_chart_layout(c, 360))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        fig = px.bar(
            convocacoes.head(10).sort_values("Partidas"),
            x="Partidas", y="Jogador", orientation="h",
            title="Top 10 \u2014 Mais Jogos",
            color_discrete_sequence=["#8b5cf6"],
            text="Partidas",
            labels={"Partidas": "Partidas", "Jogador": ""},
        )
        fig.update_layout(**_chart_layout(c, 360))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_c:
        fig = px.bar(
            yellow_rank.sort_values("Amarelos"),
            x="Amarelos", y="Jogador", orientation="h",
            title="Top 10 \u2014 Cart\u00f5es Amarelos",
            color_discrete_sequence=["#f59e0b"],
            text="Amarelos",
            labels={"Amarelos": "Cart\u00f5es", "Jogador": ""},
        )
        fig.update_layout(**_chart_layout(c, 360))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_footer(c: dict):
    muted_color = c["muted"]
    text_color = c["text"]
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:center; padding: 12px 0 28px 0;">
            <p style="font-family:DM Sans,sans-serif;font-size:0.78rem;
               color:{muted_color}; margin:0;">
                <strong style="color:{text_color};">Sobre o Projeto</strong>
                &nbsp;&middot;&nbsp;
                Dados: <a href="https://www.kaggle.com/datasets/abecklas/fifa-world-cup"
                    target="_blank" style="color:#0ea5e9;text-decoration:none;">
                    Kaggle &mdash; FIFA World Cup Dataset</a>
                &nbsp;&middot;&nbsp; Per\u00edodo: 1930&ndash;2014
            </p>
            <p style="font-family:JetBrains Mono,monospace;font-size:0.72rem;
               color:{muted_color}; margin:8px 0 0 0;letter-spacing:0.02em;">
                Python 3 &middot; Streamlit &middot; pandas &middot; Plotly
                &nbsp;&middot;&nbsp;
                <a href="https://github.com/iambriansander/dashboard-copa-do-mundo"
                    target="_blank" style="color:#0ea5e9;text-decoration:none;">
                    github.com/iambriansander</a>
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
    render_hero(df_cups, df_matches, df_players, c)
    render_bloco1(df_cups, c)
    render_bloco2(df_cups, df_matches, c)
    render_bloco3(df_cups, df_matches, c)
    render_bloco4(df_matches, df_players, c)
    render_footer(c)


if __name__ == "__main__":
    main()
