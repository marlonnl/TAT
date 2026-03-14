import streamlit as st
import pandas as pd
import time


st.title("Página inicial")
# st.set_page_config(layout="centered")

uploaded_file = st.file_uploader(
    "Envie o arquivo .CSV", type=["csv"], max_upload_size=400
)

if uploaded_file is not None:
    # old configs
    # usecols=[1, 3, 4, 5, 6, 7, 13, 17, 18],
    # dtype={5: manchester_dtype, 6: protocolo_dtype},
    df = pd.read_csv(
        uploaded_file,
        header=2,
        usecols=[
            "Data",
            "Requisição",
            "Setor Hospitalar",
            "Manchester",
            "Protocolo",
            "Exame",
            " TA Coleta ",
            " TA Triagem ",
            " TAT LAB ",
            " TAT ",
        ],
        encoding="latin1",
        sep=";",
    )

    # renaming cols with extra space
    df = df.rename(
        columns={
            " TA Coleta ": "TA Coleta",
            " TA Triagem ": "TA Triagem",
            " TAT LAB ": "TAT LAB",
            " TAT ": "TAT",
        }
    )

    # time variables
    month = pd.to_datetime(df["Data"].iloc[1], dayfirst=True).month
    year = pd.to_datetime(df["Data"].iloc[1], dayfirst=True).year

    # storing dataframe into state
    st.session_state["dataset"] = {
        "df": df,
        "file_name": uploaded_file.name,
        "month": month,
        "year": year,
    }

    st.toast("Arquivo carregado com sucesso.", icon="✅")
    time.sleep(0.5)

if "dataset" in st.session_state and "df" in st.session_state["dataset"]:
    st.success(
        f":material/check: Arquivo '{st.session_state["dataset"]["file_name"]}' carregado com sucesso."
    )
    st.info(
        f":material/info: Para visualizar os dados navegue pelo menu na parte superior da página."
    )
