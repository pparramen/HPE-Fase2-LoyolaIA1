import streamlit as st

# Inicializar página actual
if "page" not in st.session_state:
    st.session_state.page = "home"

# Cambiar página
def change_page(page_name):
    st.session_state.page = page_name

# Enrutador
if st.session_state.page == "home":
    st.title("🏡 Bienvenido a GreenLake Village")
    if st.button("🌍 Ir a Recomendador de Rutas"):
        st.session_state.reset_rutas = True
        change_page("rutas")

elif st.session_state.page == "rutas":
    from Recomendador_rutas import app
    app(change_page)

elif st.session_state.page == "transporte":
    from Recomendador_transporte import app
    app(change_page)
