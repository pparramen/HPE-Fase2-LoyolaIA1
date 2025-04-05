import streamlit as st


 # --- CSS personalizado para los botones ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #dfe9f3, #ffffff);
        font-family: 'Segoe UI', sans-serif;
    }
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #45a049;
        color: #f0f0f0;
    }
                
    div.stButton > button:focus {
        color: black !important;
        background-color: #4CAF50 !important;
        font-weight: bold !important;
        outline: none;
    }
                
        
    </style>
    """, unsafe_allow_html=True)

# Inicializar página actual
if "page" not in st.session_state:
    st.session_state.page = "home"

# Cambiar página
def change_page(page_name):
    st.session_state.page = page_name

# Enrutador
if st.session_state.page == "home":
    st.title("🏡 Bienvenido a GreenLake Village")
    if st.button("🌍 Recomendador de Rutas"):
        st.session_state.reset_rutas = True
        change_page("rutas")

    if st.button("🏨 Encuentra tu Hotel Ideal"):
        st.session_state.reset_hoteles = True
        change_page("hoteles")
    

    if st.button("📜 Book'n Green (Reseñas)"):
        st.session_state.reset_opiniones = True
        change_page("opiniones")

    if st.button("🌱 Informe de Sostenibilidad"):
        st.session_state.reset_sostenibilidad = True
        change_page("sostenibilidad")


elif st.session_state.page == "rutas":
    from Recomendador_rutas import app
    app(change_page)

elif st.session_state.page == "transporte":
    from Recomendador_transporte import app
    app(change_page)

elif st.session_state.page == "hoteles":
    from hoteles import app
    app(change_page)

elif st.session_state.page == "opiniones":
    from booking import app
    app(change_page)

elif st.session_state.page == "sostenibilidad":
    from sostenibilidad import app
    app(change_page)