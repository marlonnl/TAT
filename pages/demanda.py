import streamlit as st
import pandas as pd

from utils import (
    show_date_badge,
    get_dataframe,
    no_file,
    DIA_SEMANA,
    EXAMES_COLETA_TERCEIRIZADA,
)


st.title("Análise tempo de coleta")

df = get_dataframe()
# df["data"] = pd.to_datetime(df["data"], dayfirst=True).dt.normalize()


def _make_df_protocol(protocolo: str, exame: str, name: str) -> pd.DataFrame:
    df_filtered = df[
        (df["protocolo"].str.lower() == protocolo.lower())
        & (df["exame"].str.contains(exame, case=False, na=False))
    ]
    df_daily = (
        df_filtered.groupby("data")["requisição"]
        .nunique()
        .reindex(df["data"].unique(), fill_value=0)
        .reset_index(name=name)
    )

    return df_daily


if df is not None:
    show_date_badge()

    # print(df)

    # sepse_total = len(df[(df["protocolo"] == "SEPSE") & (df["exame"] == "LACTATO")])
    df_sepse = _make_df_protocol("Sepse", "lactato", "Sepse")
    df_avc = _make_df_protocol("janela avc", "tap", "AVC")
    df_dt = _make_df_protocol("dor torácica", "trp", "DT")

    # Filtragens
    setores = ["E GERAL SU", "E GERAL CO"]
    df_setores = df[df["setor hospitalar"].isin(setores)]

    # st.dataframe(df_setores)

    # remove EXAMES_COLETA_TERCEIRIZADA from dataframe
    df_setores = df_setores[~df_setores["exame"].isin(EXAMES_COLETA_TERCEIRIZADA)]

    # Tipa as datas e remove o horário (para posterior agrupamento)
    # df_setores["data"] = pd.to_datetime(
    #     df_setores["data"], dayfirst=True
    # ).dt.normalize()

    # Remove requisições duplicadas mantendo apenas o primeiro exame de cada
    df_setores.drop_duplicates(subset=["requisição"], keep="first", inplace=True)
    # print(unique_values)

    # daily = (
    #     df_setores.groupby(["Data", "Setor Hospitalar"])["Requisição"]
    #     .nunique()
    #     .reset_index()
    # )

    df_setores["ta coleta"] = pd.to_timedelta(df_setores["ta coleta"])

    # Fazendo a média
    df_media = (
        df_setores.groupby("data")["ta coleta"]
        .mean()
        .reset_index()
        .rename(columns={"ta coleta": "Média"})
    )
    df_media["Média"] = df_media["Média"].apply(
        lambda x: str(x.round("1s")).split()[-1] if pd.notna(x) else None
    )

    # Agrupa SUS e CO
    # df_setores = df_setores.groupby("Setor Hospitalar")["Requisição"].nunique()
    df_setores = (
        df_setores.groupby(["data", "setor hospitalar"])["requisição"]
        .nunique()
        .unstack(fill_value=0)
        .reset_index()
    )

    df_setores["Dia da semana"] = pd.to_datetime(
        df_setores["data"], dayfirst=True
    ).dt.weekday.map(DIA_SEMANA)

    # print(df_setores["data"].head())
    # print(pd.to_datetime(df_setores["data"], dayfirst=True, errors="coerce").head())
    # print(pd.to_datetime(df_setores["data"], dayfirst=True).dt.weekday.head())

    # df_setores = df_setores.pivot(
    #     index="Data", columns="Setor Hospitalar", values="Requisição"
    # )

    # print(df_setores.columns)

    # Soma dos setores
    df_setores["Total"] = df_setores["E GERAL SU"] + df_setores["E GERAL CO"]

    df_setores = df_setores.rename(
        columns={
            "E GERAL SU": "SUS",
            "E GERAL CO": "Convênio",
        }
    )

    # Junta a média ao dataframe
    df_setores = df_setores.merge(df_media, on="data", how="left")

    # Criando colunas PCP e Data formatada
    df_setores["PCP"] = None
    df_setores["Data"] = (
        pd.to_datetime(df_setores["data"]).dt.strftime("%d/%m")
        + " "
        + df_setores["Dia da semana"]
    )
    # df_setores["Sepse"] = sepse_total
    df_setores = df_setores.merge(df_sepse, on="data", how="left")
    df_setores = df_setores.merge(df_avc, on="data", how="left")
    df_setores = df_setores.merge(df_dt, on="data", how="left")

    st.data_editor(
        df_setores[
            ["Data", "SUS", "Convênio", "Total", "Média", "PCP", "Sepse", "AVC", "DT"]
        ],
        column_config={
            "PCP": st.column_config.NumberColumn(
                "PCP",
                min_value=0,
                max_value=3,
                step=1,
            )
        },
        hide_index=True,
        # df_setores
    )

    # st.bar_chart(df_setores, x="data", y=["SUS", "Convênio"])

else:
    no_file()


# add: contagem de sepse, avc e dt
