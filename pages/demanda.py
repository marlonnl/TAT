import streamlit as st
import pandas as pd

from utils import show_date_badge, get_dataframe, no_file


st.title("Análise tempo de coleta")

df = get_dataframe()

if df is not None:
    show_date_badge()
    st.write("...")
else:
    no_file()
