import streamlit as st
import pandas as pd
import unicodedata
from datetime import date
import joblib

# --------------------
# Cargar y usar modelos IA
# --------------------
def cargar_modelos(preferencia):
    sufijo = preferencia.lower()
    base_path = f"modelos/predictor_rutas_transportes/"
    clf = joblib.load(f'{base_path}modelo_transporte_{sufijo}.pkl')
    reg_time = joblib.load(f'{base_path}modelo_tiempo_{sufijo}.pkl')
    reg_users = joblib.load(f'{base_path}modelo_usuarios_{sufijo}.pkl')

    le_origen = joblib.load(f'{base_path}encoder_origen_{sufijo}.pkl')
    le_destino = joblib.load(f'{base_path}encoder_destino_{sufijo}.pkl')
    le_transporte = joblib.load(f'{base_path}encoder_transporte_{sufijo}.pkl')

    return clf, reg_time, reg_users, le_origen, le_destino, le_transporte


def predecir_transporte(origen, destino, fecha_str, preferencia):
    fecha = pd.to_datetime(fecha_str)
    mes = fecha.month
    dia_semana = fecha.dayofweek

    clf, reg_time, reg_users, le_origen, le_destino, le_transporte = cargar_modelos(preferencia)

    origen_enc = le_origen.transform([origen])[0] if origen in le_origen.classes_ else 0
    destino_enc = le_destino.transform([destino])[0] if destino in le_destino.classes_ else 0
    X_input = [[origen_enc, destino_enc, mes, dia_semana]]

    transporte_pred_enc = clf.predict(X_input)[0]
    transporte_pred = le_transporte.inverse_transform([transporte_pred_enc])[0]

    tiempo_estimado = reg_time.predict(X_input)[0]
    usuarios_estimados = reg_users.predict(X_input)[0]

    sostenibilidad_map = {
        'Bicicleta': 5,
        'Tranvía': 4,
        'Metro': 4,
        'Autobús': 3,
        'Coche Compartido': 2,
        'Avion': 1
    }
    eco_nivel = sostenibilidad_map.get(transporte_pred, 3)

    return {
        'transporte_recomendado': transporte_pred,
        'tiempo_estimado_min': int(round(tiempo_estimado)),
        'usuarios_estimados': int(usuarios_estimados),
        'sostenibilidad_nivel': eco_nivel
    }

# --------------------
# Streamlit App
# --------------------
def app(change_page_func):
    st.title("🌍 Organizador de viajes en GreenLake Village 🌍")

    if st.button("🏠 Volver al Inicio"):
        change_page_func("home")

    if "resultado_ruta" not in st.session_state or st.session_state.resultado_ruta is None:
        st.warning("Primero debes seleccionar una ruta en la página anterior.")
        return

    destino_completo = st.session_state.resultado_ruta['nombre']
    destino = destino_completo.split(' - ')[0]
    st.markdown(f"### 📍 Tu destino es: **{destino}**")

    @st.cache_data
    def cargar_ciudades():
        df = pd.read_csv("baseDatos/uso_transporte.csv")
        df[['origen', 'destino']] = df['ruta_popular'].str.split(' - ', expand=True)
        ciudades = sorted(df['origen'].unique())
        return [c for c in ciudades if c != destino]

    ciudades_origen = cargar_ciudades()
    origen = st.selectbox("📍 Selecciona tu ciudad de origen:", ciudades_origen)
    fecha = st.date_input("📅 Selecciona una fecha estimada:", min_value=date.today())

    st.markdown("### 💡 ¿Qué prefieres priorizar en tu viaje?")
    col1, col2, col3 = st.columns(3)
    preferencia = None
    with col1:
        if st.button("🌱 Sostenibilidad"):
            preferencia = "eco"
    with col2:
        if st.button("⏱️ Eficiencia"):
            preferencia = "eficiencia"
    with col3:
        if st.button("🔥 Popularidad"):
            preferencia = "popularidad"

    if origen and destino and fecha and preferencia:
        resultado = predecir_transporte(origen, destino, str(fecha), preferencia)
        st.markdown("---")
        st.subheader("🚀 Transporte recomendado")
        st.markdown(f"**Transporte:** {resultado['transporte_recomendado']}")
        st.markdown(f"**Duración estimada:** {resultado['tiempo_estimado_min']} minutos")
        st.markdown(f"**Popularidad estimada:** {resultado['usuarios_estimados']} usuarios")
        st.markdown(f"**Sostenibilidad:** {resultado['sostenibilidad_nivel']} / 5")
