import streamlit as st
import pandas as pd
import unicodedata

def app(change_page_func):
    st.title("🌍 Organizador de viajes en GreenLake Village 🌍")


    # Botón para volver a home
    if st.button("🏠 Volver al Inicio"):
        change_page_func("home")