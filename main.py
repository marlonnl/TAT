import pandas as pd
from pandas.api.types import CategoricalDtype

import streamlit as st

manchester_dtype = CategoricalDtype(
  categories=[
    "EMERGÊNCIA",
    "MUITO URGENTE",
    "URGENTE",
    "POUCO URGENTE"
  ]
)

protocolo_dtype = CategoricalDtype(
  categories=[
    "SEPSE",
    "Janela AVC",
    "Dor Torácica"
  ]
)

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

METAS = {
  'sepse': [35],
  'dor torácica': [60],
  'janela avc': [45],
  'emergência': [20, 45, 80],
  'muito urgente': [30, 60, 100],
  'urgente': [50, 70, 120],
  'pouco urgente': [60, 100, 130],
  'não urgente': [80, 120, 150]
}

def mostrar_protocolo_tab(tab, df, session_key, protocolo, exame, meta):
    """
    Exibe uma aba de protocolo com métricas de tempo.
    """

    with tab:
        st.markdown(f'##### Protocolo de *{protocolo}*: `{exame}`')

        if session_key not in st.session_state:
            st.session_state[session_key] = df.copy()

        metric_container = st.container()

        edited_df = st.data_editor(
            df[['Requisição', 'Exame', 'TA Coleta', 'TAT LAB', 'TAT']],
            width='stretch',
            num_rows="dynamic",
            column_config={
                "Requisição": st.column_config.NumberColumn("Requisição"),
                "Exame": st.column_config.TextColumn("Exame"),
                "TA Coleta": st.column_config.TextColumn("TA Coleta"),
                "TAT LAB": st.column_config.TextColumn("TAT LAB"),
                "TAT": st.column_config.TextColumn("TAT"),
            },
            key=f"editor_{session_key}"
        )

        st.session_state[session_key].update(edited_df)

        for col in ['TA Coleta', 'TAT LAB', 'TAT']:
          edited_df[col] = pd.to_timedelta(edited_df[col], errors="coerce")

        # Calcula métricas
        df_meta = edited_df[pd.to_timedelta(edited_df['TAT LAB']) < meta]
        # print(f'{protocolo}: dentro da meta {len(df_meta)} e total {len(edited_df)}')
        rel_pct = round(len(df_meta) * 100 / len(edited_df), 2)

        def calc_metric(col):
            t = pd.to_timedelta(edited_df[col]).mean()
            t_f = str(t.round('1s')).split()[-1]
            t_dif = str(abs(t - meta).round('1s')).split()[-1]
            t_arrow = ["up", "red"] if (t - meta) > pd.Timedelta(0) else ["down", "green"]
            return t_f, t_dif, t_arrow

        tmc_f, tmc_dif, tmc_arrow = calc_metric('TA Coleta')
        tml_f, tml_dif, tml_arrow = calc_metric('TAT LAB')
        tat_f, tat_dif, tat_arrow = calc_metric('TAT')

        with metric_container:
            st.markdown(f":blue-badge[:material/alarm: Meta: {str(meta.round('1s')).split()[-1]}]")
            
            a, b = st.columns(2)
            c, d, e = st.columns(3)

            a.metric(label='Registros', value=len(edited_df), delta='100%', delta_arrow='off', delta_color='blue', border=True)
            b.metric(label='Dentro da meta', value=len(df_meta), delta=f'{rel_pct}%', delta_arrow='off', delta_color='gray', border=True)

            c.metric(label='Tempo médio de coleta', value=tmc_f, delta=tmc_dif, delta_arrow=tmc_arrow[0], delta_color=tmc_arrow[1], border=True)
            d.metric(label='Tempo médio de liberação', value=tml_f, delta=tml_dif, delta_arrow=tml_arrow[0], delta_color=tml_arrow[1], border=True)
            e.metric(label='TAT', value=tat_f, delta=tat_dif, delta_arrow=tat_arrow[0], delta_color=tat_arrow[1], border=True)
    


st.title("Análise TAT")

# st.text("Faça o upload dos dados")
uploaded_file = st.file_uploader("Escolha o arquivo .CSV", type=["csv"], max_upload_size=400)

if uploaded_file is not None:
  data = pd.read_csv(uploaded_file, header=2, usecols=[1,3, 4, 5, 6, 7, 13, 17, 18], dtype={5: manchester_dtype, 6: protocolo_dtype})

  # DataFrames
  sepse_df = data[(data['Protocolo'].str.lower() == 'sepse') & (data['Exame'] == 'LACTATO')]
  trp_df = data[(data['Protocolo'].str.lower() == 'dor torácica') & (data['Exame'] == 'TRP')]
  avc_df = data[(data['Protocolo'].str.lower() == 'janela avc') & (data['Exame'] == 'TAP')]
  # emergencia_df = data[(data['Manchester'].str.lower() == 'emergência') & (data['Exame'] in 'TAP')]

  # Definição do mês
  calendario = data['Data'].iloc[0]
  mes = pd.to_datetime(calendario, dayfirst=True).month

  st.markdown(f':grey-badge[:material/calendar_month: **{MESES[mes]}**]', width="stretch")

  # Tabs
  sepse_tab, card_tab, avc_tab, emergencia_tab, murgente_tab, urgente_tab, purgente_tab =st.tabs(['SEPSE', 'DOR TORÁCICA', 'AVC', 'EMERGÊNCIA', 'MUITO URGENTE', 'URGENTE', 'POUCO URGENTE'])

  mostrar_protocolo_tab(sepse_tab, sepse_df, 'sepse_df', 'Sepse', 'LACTATO', pd.Timedelta(minutes=35))
  mostrar_protocolo_tab(card_tab, trp_df, 'trp_df', 'Dor torácica', 'TRP', pd.Timedelta(minutes=60))
  mostrar_protocolo_tab(avc_tab, avc_df, 'avc_df', 'Janela AVC', 'TAP', pd.Timedelta(minutes=45))