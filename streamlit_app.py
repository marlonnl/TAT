import pandas as pd
from pandas.api.types import CategoricalDtype

import streamlit as st

manchester_dtype = CategoricalDtype(
    categories=["EMERGÊNCIA", "MUITO URGENTE", "URGENTE", "POUCO URGENTE"]
)

protocolo_dtype = CategoricalDtype(
    categories=["SEPSE", "Janela AVC", "Dor Torácica"]
)

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

EXAMES = [
    ['GASO', 'GASOV', 'HB', 'HT', 'PLA', 'NA', 'K', 'CAIO'],
    ['H', 'TAP', 'KPTT', 'TRP', 'PCRQ', 'LACTATO', 'AMI'],
    ['AUR', 'ALB', 'BIL', 'CA', 'CPK', 'CKMB', 'CL', 'FERRI', 'FAL',
     'LDH', 'FOS', 'G', 'LIPASE', 'MAG', 'PTF', 'YGT', 'TGO', 'TGP',
     'U', 'FIB', 'BHCG', 'EAS']
]

METAS = {
    'sepse':         [35],
    'dor torácica':  [60],
    'janela avc':    [45],
    'emergência':    [20, 45, 80],
    'muito urgente': [30, 60, 100],
    'urgente':       [50, 70, 120],
    'pouco urgente': [60, 100, 130],
    'não urgente':   [80, 120, 150],
}

COR = {
    'sepse':         'orange',
    'dor torácica':  'blue',
    'janela avc':    'yellow',
    'emergência':    'red',
    'muito urgente': 'orange',
    'urgente':       'yellow',
    'pouco urgente': 'blue',
}

def _grupos_protocolo(protocolo: str, exame: str) -> list[dict]:
    """Monta a lista de grupos para os protocolos (Sepse, AVC, DT)."""
    meta = pd.Timedelta(minutes=METAS[protocolo.lower()][0])
    return [{"exames": [exame], "meta": meta, "label": None}]


def _grupos_manchester(protocolo: str) -> list[dict]:
    """Monta a lista de grupos para as classificações Manchester."""
    return [
        {
            "exames": EXAMES[i],
            "meta": pd.Timedelta(minutes=METAS[protocolo.lower()][i]),
            "label": f"Grupo {i + 1}: {', '.join(EXAMES[i])}",
        }
        for i in range(len(EXAMES))
    ]


def _criar_tabela_referencia(protocolo: str) -> None:
    """Renderiza a tabela de exames vs metas para classificações Manchester."""
    protocolo_ = protocolo.lower()
    st.markdown(f'##### :{COR[protocolo_]}[:material/radio_button_checked:] *{protocolo}*')

    metas_fmt = [
        str(pd.Timedelta(minutes=m)).split()[-1]
        for m in METAS[protocolo_]
    ]
    classificacao = pd.DataFrame({
        "Meta de entrega": metas_fmt,
        "Exames": [', '.join(g) for g in EXAMES],
    })
    st.table(classificacao, border="horizontal")


def _bloco_metricas(edited_df: pd.DataFrame, meta: pd.Timedelta) -> None:
    """Renderiza os cards de métricas para um grupo de exames."""

    for col in ['TA Coleta', 'TAT LAB', 'TAT']:
        edited_df[col] = pd.to_timedelta(edited_df[col], errors="coerce")

    df_meta = edited_df[edited_df['TAT LAB'] < meta]
    rel_pct = round(len(df_meta) * 100 / len(edited_df), 2) if len(edited_df) > 0 else 0

    def calc_metric(col):
        if len(edited_df) == 0:
            return "00:00:00", "00:00:00", ["down", "green"]
        t = edited_df[col].mean()
        if pd.isna(t):
            return "00:00:00", "00:00:00", ["down", "green"]
        
        t_f   = str(t.round('1s')).split()[-1]
        t_dif = str(abs(t - meta).round('1s')).split()[-1]
        t_arrow = ["up", "red"] if (t - meta) > pd.Timedelta(0) else ["down", "green"]
        
        return t_f, t_dif, t_arrow

    tmc_f, tmc_dif, tmc_arrow = calc_metric('TA Coleta')
    tml_f, tml_dif, tml_arrow = calc_metric('TAT LAB')
    tat_f, tat_dif, tat_arrow = calc_metric('TAT')

    st.markdown(f":blue-badge[:material/alarm: Meta: {str(meta.round('1s')).split()[-1]}]")

    a, b = st.columns(2)
    c, d, e = st.columns(3)

    a.metric(label='Registros',      value=len(edited_df), delta='100%',       delta_arrow='off', delta_color='blue', border=True)
    b.metric(label='Dentro da meta', value=len(df_meta),   delta=f'{rel_pct}%', delta_arrow='off', delta_color='gray', border=True)

    c.metric(label='Tempo médio de coleta',     value=tmc_f, delta=tmc_dif, delta_arrow=tmc_arrow[0], delta_color=tmc_arrow[1], border=True)
    d.metric(label='Tempo médio de liberação',  value=tml_f, delta=tml_dif, delta_arrow=tml_arrow[0], delta_color=tml_arrow[1], border=True)
    e.metric(label='TAT',                       value=tat_f, delta=tat_dif, delta_arrow=tat_arrow[0], delta_color=tat_arrow[1], border=True)


def mostrar_protocolo_tab(
    tab,
    df: pd.DataFrame,
    session_key: str,
    protocolo: str,
    grupos: list[dict],        # [{"exames": [...], "meta": Timedelta, "label": str | None}]
    titulo_header: str | None = None,
) -> None:
    """
    Exibe uma aba de protocolo com métricas de tempo.

    Funciona para dois modelos:
    - Protocolos simples (Sepse, AVC, Dor Torácica): grupos com 1 item.
    - Manchester (Emergência, Muito Urgente…): grupos com 3 itens.

    Parâmetros
    ----------
    tab           : st.tab retornado por st.tabs()
    df            : DataFrame já filtrado para o protocolo/manchester
    session_key   : chave única para st.session_state
    protocolo     : nome do protocolo (para cor e legenda)
    grupos        : lista de dicts com chaves 'exames', 'meta' e 'label'
    titulo_header : título opcional exibido no topo da aba
                    (se None, usa o padrão "Protocolo de <protocolo>")
    """

    with tab:
        # --- Cabeçalho ---
        protocolo_ = protocolo.lower()
        if titulo_header:
            st.markdown(f'##### :{COR[protocolo_]}[:material/radio_button_checked:] {titulo_header}')
        else:
            # Protocolo simples: exibe o nome do exame que está em grupos[0]
            exame = grupos[0]["exames"][0]
            st.markdown(f'##### :{COR[protocolo_]}[:material/radio_button_checked:] Protocolo de *{protocolo}*: `{exame}`')

        # --- Session state ---
        if session_key not in st.session_state:
            st.session_state[session_key] = df.copy()

        is_manchester = len(grupos) > 1

        if is_manchester:
            # --- Manchester: segmented_control para navegar entre os grupos ---
            opcoes = [
                str(g["meta"].round("1s")).split()[-1]   # ex: "0:20:00"
                for g in grupos
            ]
            selecionado = st.segmented_control(
                label="Meta de entrega",
                options=opcoes,
                default=opcoes[0],
                key=f"seg_{session_key}",
            )
            # Garante que sempre haja uma seleção (segmented_control pode retornar None)
            idx = opcoes.index(selecionado) if selecionado in opcoes else 0
            grupo = grupos[idx]

            exames = grupo["exames"]
            meta   = grupo["meta"]
            label  = grupo["label"]

            if label:
                st.caption(label)

            df_grupo = df[df['Exame'].isin(exames)].copy()

            metric_container = st.container()

            edited_df = st.data_editor(
                df_grupo[['Requisição', 'Exame', 'TA Coleta', 'TAT LAB', 'TAT']],
                width='stretch',
                num_rows="dynamic",
                column_config={
                    "Requisição": st.column_config.NumberColumn("Requisição"),
                    "Exame":      st.column_config.TextColumn("Exame"),
                    "TA Coleta":  st.column_config.TextColumn("TA Coleta"),
                    "TAT LAB":    st.column_config.TextColumn("TAT LAB"),
                    "TAT":        st.column_config.TextColumn("TAT"),
                },
                key=f"editor_{session_key}_{idx}",
            )

            st.session_state[session_key].update(edited_df)

            with metric_container:
                _bloco_metricas(edited_df.copy(), meta)

            st.divider()
            _criar_tabela_referencia(protocolo)

        else:
            # --- Protocolo simples: comportamento original ---
            grupo  = grupos[0]
            exames = grupo["exames"]
            meta   = grupo["meta"]

            df_grupo = df[df['Exame'].isin(exames)].copy()

            metric_container = st.container()

            edited_df = st.data_editor(
                df_grupo[['Requisição', 'Exame', 'TA Coleta', 'TAT LAB', 'TAT']],
                width='stretch',
                num_rows="dynamic",
                column_config={
                    "Requisição": st.column_config.NumberColumn("Requisição"),
                    "Exame":      st.column_config.TextColumn("Exame"),
                    "TA Coleta":  st.column_config.TextColumn("TA Coleta"),
                    "TAT LAB":    st.column_config.TextColumn("TAT LAB"),
                    "TAT":        st.column_config.TextColumn("TAT"),
                },
                key=f"editor_{session_key}_{exames[0]}",
            )

            st.session_state[session_key].update(edited_df)

            with metric_container:
                _bloco_metricas(edited_df.copy(), meta)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

st.title("Análise TAT")

#st.write(' oi')
uploaded_file = st.file_uploader("Escolha o arquivo .CSV", type=["csv"], max_upload_size=400)

if uploaded_file is not None:
    data = pd.read_csv(
        uploaded_file, header=2,
        #usecols=[1, 3, 4, 5, 6, 7, 13, 17, 18],
        #dtype={5: manchester_dtype, 6: protocolo_dtype},
        encoding='latin1',
        sep=';'
    )
    print(data)
    
    # Filtragens
    ## Protocolos
    sepse_df      = data[(data['Protocolo'].str.lower() == 'sepse')        & (data['Exame'] == 'LACTATO')]
    trp_df        = data[(data['Protocolo'].str.lower() == 'dor torácica') & (data['Exame'] == 'TRP')]
    avc_df        = data[(data['Protocolo'].str.lower() == 'janela avc')   & (data['Exame'] == 'TAP')]
    ## Manchester
    emergencia_df = data[data['Manchester'].str.lower() == 'emergência']
    murgente_df   = data[data['Manchester'].str.lower() == 'muito urgente']
    urgente_df    = data[data['Manchester'].str.lower() == 'urgente']
    purgente_df   = data[data['Manchester'].str.lower() == 'pouco urgente']

    # Data
    mes = pd.to_datetime(data['Data'].iloc[0], dayfirst=True).month
    ano = pd.to_datetime(data['Data'].iloc[0], dayfirst=True).year
    st.markdown(f':grey-badge[:material/calendar_month: **{MESES[mes]}/{ano}**]', width="stretch")

    # Tabs
    sepse_tab, card_tab, avc_tab, emergencia_tab, murgente_tab, urgente_tab, purgente_tab = st.tabs(
        ['SEPSE', 'DOR TORÁCICA', 'AVC', 'EMERGÊNCIA', 'MUITO URGENTE', 'URGENTE', 'POUCO URGENTE']
    )

    # Montagem dos dashboards
    ## Protocolos
    mostrar_protocolo_tab(sepse_tab, sepse_df, 'sepse_df',  'Sepse',       _grupos_protocolo('sepse',        'LACTATO'))
    mostrar_protocolo_tab(card_tab,  trp_df,   'trp_df',    'Dor torácica', _grupos_protocolo('dor torácica', 'TRP'))
    mostrar_protocolo_tab(avc_tab,   avc_df,   'avc_df',    'Janela AVC',   _grupos_protocolo('janela avc',   'TAP'))

    ## Manchester
    mostrar_protocolo_tab(emergencia_tab, emergencia_df, 'emergencia',  'Emergência',    _grupos_manchester('emergência'),    'Emergência')
    mostrar_protocolo_tab(murgente_tab,   murgente_df,   'murgente',    'Muito Urgente', _grupos_manchester('muito urgente'), 'Muito Urgente')
    mostrar_protocolo_tab(urgente_tab,    urgente_df,    'urgente',     'Urgente',       _grupos_manchester('urgente'),       'Urgente')
    mostrar_protocolo_tab(purgente_tab,   purgente_df,   'purgente',    'Pouco Urgente', _grupos_manchester('pouco urgente'), 'Pouco urgente')
