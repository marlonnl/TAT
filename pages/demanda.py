import streamlit as st
import pandas as pd

from utils import show_date_badge, get_dataframe, no_file, DIA_SEMANA


st.title("Análise tempo de coleta")

df = get_dataframe()

if df is not None:
    show_date_badge()

    # Filtragens
    setores = [" E GERAL SU", " E GERAL CO"]
    df_setores = df[df["Setor Hospitalar"].isin(setores)]

    # st.dataframe(df_setores)

    # Tipa as datas e remove o horário (para posterior agrupamento)
    df_setores["Data"] = pd.to_datetime(df_setores["Data"], dayfirst=True).dt.day

    # Remove requisições duplicadas mantendo apenas o primeiro exame de cada
    df_setores.drop_duplicates(subset=["Requisição"], keep="first", inplace=True)
    # print(unique_values)

    # daily = (
    #     df_setores.groupby(["Data", "Setor Hospitalar"])["Requisição"]
    #     .nunique()
    #     .reset_index()
    # )

    df_setores["TA Coleta"] = pd.to_timedelta(df_setores["TA Coleta"])

    # Fazendo a média
    df_media = (
        df_setores.groupby("Data")["TA Coleta"]
        .mean()
        .reset_index()
        .rename(columns={"TA Coleta": "Média"})
    )
    df_media["Média"] = df_media["Média"].apply(
        lambda x: str(x.round("1s")).split()[-1] if pd.notna(x) else None
    )

    # Agrupa SUS e CO
    # df_setores = df_setores.groupby("Setor Hospitalar")["Requisição"].nunique()
    df_setores = (
        df_setores.groupby(["Data", "Setor Hospitalar"])["Requisição"]
        .nunique()
        .unstack(fill_value=0)
        .reset_index()
    )

    df_setores["Dia da semana"] = pd.to_datetime(
        df_setores["Data"], dayfirst=True
    ).dt.weekday.map(DIA_SEMANA)

    # df_setores = df_setores.pivot(
    #     index="Data", columns="Setor Hospitalar", values="Requisição"
    # )

    # Soma dos setores
    df_setores["Total"] = df_setores[" E GERAL SU"] + df_setores[" E GERAL CO"]

    df_setores = df_setores.rename(
        columns={
            " E GERAL SU": "SUS",
            " E GERAL CO": "Convênio",
        }
    )

    # Junta a média ao dataframe
    df_setores = df_setores.merge(df_media, on="Data", how="left")

    # Criando coluna PCP
    df_setores["PCP"] = None

    st.data_editor(
        df_setores[
            ["Data", "Dia da semana", "SUS", "Convênio", "Total", "Média", "PCP"]
        ],
        column_config={
            "PCP": st.column_config.NumberColumn(
                "PCP",
                min_value=1,
                max_value=4,
                step=1,
            )
        },
        hide_index=True,
        # df_setores
    )

    st.bar_chart(df_setores, x="Data", y=["SUS", "Convênio"])

else:
    no_file()


# add: contagem de sepse, avc e dt
