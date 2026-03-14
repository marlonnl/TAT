import streamlit as st

# Controla o menu superior de navegação contendo as páginas visíveis

# list of pages
pages = [
    st.Page("home.py", title="Página inicial", icon=":material/home:"),
    st.Page(
        "pages/tat.py",
        title="Análise TAT",
        icon=":material/health_metrics:",
    ),
    st.Page("pages/demanda.py", title="Demanda", icon=":material/outpatient:"),
]

pg = st.navigation(
    pages,
    position="hidden",
)


# show pages manually (stays inside container) instead of using streamlit default
num_cols = len(pages)
columns = st.columns(num_cols)

for col, page in zip(columns[0:], pages):
    col.page_link(page, icon=page.icon)

pg.run()
