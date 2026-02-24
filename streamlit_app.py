import pandas as pd
from pandas.api.types import CategoricalDtype

EXAMES_1 = ["GASO", "GASOV", "HT", "HB", "PLA", "NA", "K", "CAIO"]
EXAMES_2 = ["H", "TAP", "KPTT", "TRP", "PCRQ", "LACTATO", "AMI"]
EXAMES_3 = ["AUR", "ALB", "BIL", "CA", "CPK", "CKMB", "CL", "FERRO", "FAL", "LDH", "FOSFORO", "G", "LIPASE", "MAG", "PT", "GGT", "TGO", "TGP", "U", "FIB", "BHCG", "EAS"]

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
    "Janela AVC"
    "Dor torácica"
  ]
)

import streamlit as st

st.title("Análise TAT")

# st.text("Faça o upload dos dados")
uploaded_file = st.file_uploader("Escolha o arquivo .CSV", type=["csv", "xlsx"])

if uploaded_file is not None:
  data = pd.read_csv(uploaded_file, header=2, usecols=[5, 6, 7, 13, 17], dtype={5: manchester_dtype, 6: protocolo_dtype})

  # st.write("Dados")
  # st.dataframe(data)

  # data = pd.read_csv('data.csv', header=2, usecols=[5, 6, 7, 13, 17], dtype={5: manchester_dtype, 6: protocolo_dtype})
  # data = pd.read_csv('data.csv', header=2, usecols=[5, 6, 7, 13, 17], nrows=100, dtype={6: manchester_dtype})
  # Seleciona apenas as colunas necessárias
  # data = data.iloc[:, [5, 6, 7, 13, 17]]

  # Converte tempos em segundos
  # data['TA Coleta'] = pd.to_timedelta(data.iloc[:, 3]).dt.total_seconds()
  data['TA Coleta segundos'] = pd.to_timedelta(data['TA Coleta']).dt.total_seconds()
  data['TAT LAB segundos'] = pd.to_timedelta(data['TAT LAB']).dt.total_seconds()

  # print(data)

  # Filtra todas linhas com Manchester == URGENTE
  urgencias_df = data[data['Manchester'] == 'URGENTE']

  # print(len(uregencias))

  urgencias_20 = data[data['TAT LAB segundos'] <= 1200.0]
  # print(urgencias_20)

  sepse_df = data[(data['Protocolo'] == 'SEPSE') & (data['Exame'] == 'LACTATO')]



  sepse_tab, card_tab, avc_tab, emergencia_tab, murgente_tab, urgente_tab, purgente_tab =st.tabs(['SEPSE', 'DOR TORÁCICA', 'AVC', 'EMERGÊNCIA', 'MUITO URGENTE', 'URGENTE', 'POUCO URGENTE'])

  with sepse_tab:
    sepse_prazo = sepse_df[sepse_df['TAT LAB segundos'] < 2100] # 2100s = 35min

    st.markdown(f'''
                Tempos de entrega de **lactato** em **protocolo de sepse**.  
                Total de registros: **{len(sepse_df)}**.  
                Entregas dentro do prazo (35 min): **{len(sepse_prazo)}**
                ''')
    st.data_editor(sepse_df.iloc[:, :5])

  with emergencia_tab:
    st.data_editor(urgencias_20)