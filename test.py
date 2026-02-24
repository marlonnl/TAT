import pandas as pd
from pandas.api.types import CategoricalDtype

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

data = pd.read_csv('data.csv', header=2, usecols=[5, 6, 7, 13, 17], nrows=100, dtype={5: manchester_dtype, 6: protocolo_dtype})

data['TA Coleta'] = pd.to_timedelta(data.iloc[:, 3]).dt.total_seconds()
data['TAT LAB'] = pd.to_timedelta(data.iloc[:, 4]).dt.total_seconds()

sepse_df = data[data['Protocolo'] == 'SEPSE']

print(sepse_df)