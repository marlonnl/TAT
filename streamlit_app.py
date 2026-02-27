import pandas as pd
from pandas.api.types import CategoricalDtype

EXAMES_1 = ["GASO", "GASOV", "HT", "HB", "PLA", "NA", "K", "CAIO"]
EXAMES_2 = ["H", "TAP", "KPTT", "TRP", "PCRQ", "LACTATO", "AMI"]
EXAMES_3 = ["AUR", "ALB", "BIL", "CA", "CPK", "CKMB", "CL", "FERRO", "FAL", "LDH", "FOSFORO", "G", "LIPASE", "MAG", "PT", "GGT", "TGO", "TGP", "U", "FIB", "BHCG", "EAS"]

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",
    4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro",
    10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

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

import streamlit as st


def metric_data(df, tempo_max):
    tempo_medio = pd.to_timedelta(sepse_df['TA Coleta']).mean()

    meta = pd.Timedelta(minutes=tempo_max)

    diferenca = tempo_medio - meta

    return tempo_medio, diferenca


st.title("Análise TAT")

# st.text("Faça o upload dos dados")
uploaded_file = st.file_uploader("Escolha o arquivo .CSV", type=["csv", "xlsx"], max_upload_size=400)

if uploaded_file is not None:
  data = pd.read_csv(uploaded_file, header=2, usecols=[1,3, 4, 5, 6, 7, 13, 17, 18], dtype={5: manchester_dtype, 6: protocolo_dtype})

  # Converte tempos em segundos
  # data['TA Coleta'] = pd.to_timedelta(data.iloc[:, 3]).dt.total_seconds()
  # data['TA Coleta segundos'] = pd.to_timedelta(data['TA Coleta']).dt.total_seconds()
  # data['TAT LAB segundos'] = pd.to_timedelta(data['TAT LAB']).dt.total_seconds()

  # print(data)

  # Filtra todas linhas com Manchester == URGENTE
  # urgencias_df = data[data['Manchester'] == 'URGENTE']

  # print(len(uregencias))

  # urgencias_20 = data[data['TAT LAB segundos'] <= 1200.0]
  # print(urgencias_20)

  sepse_df = data[(data['Protocolo'] == 'SEPSE') & (data['Exame'] == 'LACTATO')]
  trp_df = data[(data['Protocolo'] == 'Dor Torácica') & (data['Exame'] == 'TRP')]
  avc_df = data[(data['Protocolo'] == 'Janela AVC') & (data['Exame'] == 'TAP')]
  # print(trp_df)

  calendario = data['Data'].iloc[0]
  mes = pd.to_datetime(calendario, dayfirst=True).month

  # st.markdown(f'Mês: **{MESES[mes]}**')
  st.markdown(f':grey-badge[:material/calendar_month: **{MESES[mes]}**]', width="stretch")

  sepse_tab, card_tab, avc_tab, emergencia_tab, murgente_tab, urgente_tab, purgente_tab =st.tabs(['SEPSE', 'DOR TORÁCICA', 'AVC', 'EMERGÊNCIA', 'MUITO URGENTE', 'URGENTE', 'POUCO URGENTE'])

  with sepse_tab:
    st.markdown('##### Procolo de *sepse*: `LACTATO`')

    # states
    if "sepse_df" not in st.session_state:
      st.session_state.sepse_df = sepse_df.copy()

    metric_container = st.container()

    edited_sepse_df = st.data_editor(
              sepse_df[['Requisição', 'Exame', 'TA Coleta', 'TAT LAB', 'TAT']],
              use_container_width=True,
              num_rows="dynamic",  # permite adicionar/remover linhas
              column_config={
                  "Requisição": st.column_config.NumberColumn("Requisição"),
                  "Exame": st.column_config.TextColumn("Exame"),
                  "TA Coleta": st.column_config.TextColumn("TA Coleta"),
                  "TAT LAB": st.column_config.TextColumn("TAT LAB"),
                  "TAT": st.column_config.TextColumn("TAT"),
              },
              key="editor_sepse")

    st.session_state.sepse_df.update(edited_sepse_df)

    # Converte tempos
    for col in ['TA Coleta', 'TAT LAB', 'TAT']:
        edited_sepse_df[col] = pd.to_timedelta(edited_sepse_df[col], errors="coerce")

    # Variaveis
    meta = pd.Timedelta(minutes=35)
    sepse_prazo = edited_sepse_df[pd.to_timedelta(edited_sepse_df['TAT LAB']) < meta]
    sepse_rel = round(((len(sepse_prazo) * 100) / len(edited_sepse_df)), 2)

    tmc = pd.to_timedelta(edited_sepse_df['TA Coleta']).mean()
    tmc_f = str(tmc.round('1s')).split()[-1]
    tmc_dif = str(abs(tmc - meta).round('1s')).split()[-1]
    tmc_arrow = ["up", "red"] if (tmc - meta) > pd.Timedelta(0) else ["down", "green"]

    tml = pd.to_timedelta(edited_sepse_df['TAT LAB']).mean()
    tml_f = str(tml.round('1s')).split()[-1]
    tml_dif = str(abs(tml - meta).round('1s')).split()[-1]
    tml_arrow = ["up", "red"] if (tml - meta) > pd.Timedelta(0) else ["down", "green"]

    tat = pd.to_timedelta(edited_sepse_df['TAT']).mean()
    tat_f = str(tat.round('1s')).split()[-1]
    tat_dif = str(abs(tat - meta).round('1s')).split()[-1]
    tat_arrow = ["up", "red"] if (tat - meta) > pd.Timedelta(0) else ["down", "green"]


    with metric_container:
      st.markdown(f":blue-badge[:material/alarm: Meta: {str(meta.round('1s')).split()[-1]}]")
       
      a, b = st.columns(2)
      c, d, e = st.columns(3)
      
      a.metric(label='Registros', value=len(edited_sepse_df), delta='100%', delta_arrow='off', delta_color='blue', border=True)
      b.metric(label='Dentro da meta', value=len(sepse_prazo), delta=f'{sepse_rel}%', delta_arrow='off', delta_color='gray', border=True)

      c.metric(label='Tempo médio de coleta', value=tmc_f, delta=tmc_dif, delta_arrow=tmc_arrow[0], delta_color=tmc_arrow[1], border=True)
      d.metric(label='Tempo médio de liberação', value=tml_f, delta=tml_dif, delta_arrow=tml_arrow[0], delta_color=tml_arrow[1], border=True)
      e.metric(label='TAT', value=tat_f, delta=tat_dif, delta_arrow=tat_arrow[0], delta_color=tat_arrow[1], border=True)

  with card_tab:
    # Variaveis
    meta = pd.Timedelta(minutes=60)
    trp_prazo = trp_df[pd.to_timedelta(trp_df['TAT LAB']) < meta]
    trp_rel = round(((len(trp_prazo) * 100) / len(trp_df)), 2)

    st.markdown(f":blue-badge[:material/alarm: Meta: {str(meta.round('1s')).split()[-1]}]")

    tmc = pd.to_timedelta(trp_df['TA Coleta']).mean()
    tmc_f = str(tmc.round('1s')).split()[-1]
    tmc_dif = str(abs(tmc - meta).round('1s')).split()[-1]
    tmc_arrow = ["up", "red"] if (tmc - meta) > pd.Timedelta(0) else ["down", "green"]

    tml = pd.to_timedelta(trp_df['TAT LAB']).mean()
    tml_f = str(tml.round('1s')).split()[-1]
    tml_dif = str(abs(tml - meta).round('1s')).split()[-1]
    tml_arrow = ["up", "red"] if (tml - meta) > pd.Timedelta(0) else ["down", "green"]

    tat = pd.to_timedelta(trp_df['TAT']).mean()
    tat_f = str(tat.round('1s')).split()[-1]
    tat_dif = str(abs(tat - meta).round('1s')).split()[-1]
    tat_arrow = ["up", "red"] if (tat - meta) > pd.Timedelta(0) else ["down", "green"]

    a, b = st.columns(2)
    c, d, e = st.columns(3)
    
    a.metric(label='Registros', value=len(trp_df), delta='100%', delta_arrow='off', delta_color='blue', border=True)
    b.metric(label='Dentro da meta', value=len(trp_prazo), delta=f'{trp_rel}%', delta_arrow='off', delta_color='gray', border=True)

    c.metric(label='Tempo médio de coleta', value=tmc_f, delta=tmc_dif, delta_arrow=tmc_arrow[0], delta_color=tmc_arrow[1], border=True)
    d.metric(label='Tempo médio de liberação', value=tml_f, delta=tml_dif, delta_arrow=tml_arrow[0], delta_color=tml_arrow[1], border=True)
    e.metric(label='TAT', value=tat_f, delta=tat_dif, delta_arrow=tat_arrow[0], delta_color=tat_arrow[1], border=True)

    st.data_editor(trp_df[['Requisição', 'Exame', 'TA Coleta', 'TAT LAB', 'TAT']])

  with avc_tab:
    # Variaveis
    meta = pd.Timedelta(minutes=45)
    avc_prazo = avc_df[pd.to_timedelta(avc_df['TAT LAB']) < meta]
    avc_rel = round(((len(avc_prazo) * 100) / len(avc_df)), 2)

    st.markdown(f":blue-badge[:material/alarm: Meta: {str(meta.round('1s')).split()[-1]}]")

    tmc = pd.to_timedelta(avc_df['TA Coleta']).mean()
    tmc_f = str(tmc.round('1s')).split()[-1]
    tmc_dif = str(abs(tmc - meta).round('1s')).split()[-1]
    tmc_arrow = ["up", "red"] if (tmc - meta) > pd.Timedelta(0) else ["down", "green"]

    tml = pd.to_timedelta(avc_df['TAT LAB']).mean()
    tml_f = str(tml.round('1s')).split()[-1]
    tml_dif = str(abs(tml - meta).round('1s')).split()[-1]
    tml_arrow = ["up", "red"] if (tml - meta) > pd.Timedelta(0) else ["down", "green"]

    tat = pd.to_timedelta(avc_df['TAT']).mean()
    tat_f = str(tat.round('1s')).split()[-1]
    tat_dif = str(abs(tat - meta).round('1s')).split()[-1]
    tat_arrow = ["up", "red"] if (tat - meta) > pd.Timedelta(0) else ["down", "green"]

    a, b = st.columns(2)
    c, d, e = st.columns(3)
    
    a.metric(label='Registros', value=len(avc_df), delta='100%', delta_arrow='off', delta_color='blue', border=True)
    b.metric(label='Dentro da meta', value=len(avc_prazo), delta=f'{avc_rel}%', delta_arrow='off', delta_color='gray', border=True)

    c.metric(label='Tempo médio de coleta', value=tmc_f, delta=tmc_dif, delta_arrow=tmc_arrow[0], delta_color=tmc_arrow[1], border=True)
    d.metric(label='Tempo médio de liberação', value=tml_f, delta=tml_dif, delta_arrow=tml_arrow[0], delta_color=tml_arrow[1], border=True)
    e.metric(label='TAT', value=tat_f, delta=tat_dif, delta_arrow=tat_arrow[0], delta_color=tat_arrow[1], border=True)

    st.data_editor(avc_df[['Requisição', 'Exame', 'TA Coleta', 'TAT LAB', 'TAT']])
