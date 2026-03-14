import streamlit as st
import pandas as pd


MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def get_dataset(arg: str) -> str | None:
    "Retorna o valor de um dado no state de acordo com a chave(arg)"
    if "dataset" in st.session_state:
        return st.session_state["dataset"][arg]
    else:
        return None


def get_dataframe() -> pd.DataFrame | None:
    "Retorna o dataframe, caso ele  exista (tenha sido feito o upload e esteja no state)"
    if "dataset" in st.session_state and "df" in st.session_state["dataset"]:
        return st.session_state["dataset"]["df"]
    else:
        return None


def no_file() -> None:
    st.warning(
        f":material/warning: Nenhum arquivo carregado. Vá para a página inicial e faça o upload do .CSV."
    )


def show_date_badge() -> None:
    "Cria um elemento streamlit badge contendo o mês formatado e o ano. Exemplo: Fevereiro/2026"
    st.markdown(
        f":grey-badge[:material/calendar_month: **{MESES[get_dataset("month")]}/{get_dataset("year")}**]",
        width="stretch",
    )
