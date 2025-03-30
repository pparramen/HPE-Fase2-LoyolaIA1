import streamlit as st
import pandas as pd
import unicodedata
from datetime import date
import joblib

#Cargamos nuestros modelos de Clasificación y Regresión entrenados previamente con los datos de uso de transporte
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

#Realizamos la predicción del transporte más adecuado según la ruta, fecha y preferencia del usuario (Clasificación)
#Además, se estiman el tiempo de ese trayecto y el número de usuarios que utilizan ese transporte en esa fecha (Regresión)
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

    #Asignamos un score de sostenibilidad a cada medio de transporte
    sostenibilidad_map = {
        'Bicicleta': 5,
        'Tranvía': 4,
        'Metro': 4,
        'Autobús': 3,
        'Coche Compartido': 2,
        'Avion': 1
    }
    eco_nivel = sostenibilidad_map.get(transporte_pred, 3)

    #Devolvemos las predicciones y el nivel de sostenibilidad de nuestra opción
    return {
        'transporte_recomendado': transporte_pred,
        'tiempo_estimado_min': int(round(tiempo_estimado)),
        'usuarios_estimados': int(usuarios_estimados),
        'sostenibilidad_nivel': eco_nivel
    }

#Función principal de la página de recomendación de transporte
def app(change_page_func):
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

    st.title("🌍 Organizador de viajes en GreenLake Village 🌍")

    if "resultado_ruta" not in st.session_state or st.session_state.resultado_ruta is None:
        st.warning("Primero debes seleccionar una ruta en la página anterior.")
        return

    destino_completo = st.session_state.resultado_ruta['nombre']
    destino = destino_completo.split(' - ')[0]
    st.markdown(f"### 📍 Tu destino es: **{destino}**")

    st.markdown("##### ¿Listo para dar el siguiente paso? 🧳 \n\n"
                " Ya conocemos tu destino ideal, ahora es el momento de llegar a él. Te ayudaremos a encontrar el mejor trayecto que se adapte a tus necesidades, para que solo tengas que preocuparte por disfrutar del viaje. 😎🏞️")

    #Cargamos los datos de ciudades de origen posible
    @st.cache_data
    def cargar_ciudades():
        df = pd.read_csv("baseDatos/uso_transporte.csv")
        df[['origen', 'destino']] = df['ruta_popular'].str.split(' - ', expand=True)
        return sorted(df['origen'].unique())

    ciudades_origen = [c for c in cargar_ciudades() if c != destino]


    opciones_con_placeholder = ["Escoge una opción"] + ciudades_origen
    st.markdown("##### 📍 Selecciona tu ciudad de origen")
    origen = st.selectbox("_Escoge entre las opciones disponibles según las rutas registradas:_", opciones_con_placeholder)

    #Al escoger la ciudad de origen se desvelan el resto de opciones de configuración
    if origen != "Escoge una opción":
        st.session_state.origen = origen

        st.markdown("##### 📅 Selecciona la fecha estimada del viaje")   
        fecha = st.date_input("_Usaremos esta información para predecir el transporte más adecuado esa semana:_", value=date.today() if st.session_state.get("fecha") is None else st.session_state.fecha, min_value=date.today())
        st.session_state.fecha = fecha

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

        st.markdown("#### 💡 ¿Qué prefieres priorizar en tu viaje?")
        st.markdown("Selecciona tu preferencia para optimizar tu viaje:\n\n"
                    "**🌱 Sostenibilidad**: ¡En GreenLake Village apostamos por un turismo responsable! Priorizaremos el medio de transporte más sostenible disponible según tu ruta y fecha.\n\n"
                    "**⏱️ Eficiencia**: ¿Quieres llegar rápido? Te recomendaremos el transporte que requiera el menor tiempo en llegar a su destino entre las opciones viables.\n\n"
                    "**🔥 Popularidad**: Basándonos en datos históricos, seleccionaremos el transporte más utilizado por otros viajeros en fechas similares.\n\n")

        col1, col2, col3, col4, col5 = st.columns([1, 2, 1.7, 2, 1])
        if "preferencia_transporte" not in st.session_state:
            st.session_state.preferencia_transporte = None

        with col2:
            if st.button("🌱 Sostenibilidad"):
                st.session_state.preferencia_transporte = "eco"
        with col3:
            if st.button("⏱️ Eficiencia"):
                st.session_state.preferencia_transporte = "eficiencia"
        with col4:
            if st.button("🔥 Popularidad"):
                st.session_state.preferencia_transporte = "popularidad"

        preferencia = st.session_state.preferencia_transporte

        #Nos indica si el usuario ha seleccionado una opción de preferencia
        if preferencia:
            st.success(f"Has seleccionado la opción: **{preferencia.capitalize()}**")
            st.session_state.resultado_transporte = predecir_transporte(origen, destino, str(fecha), preferencia)

        resultado = st.session_state.get("resultado_transporte")
        if resultado:
            st.markdown("---")
            st.markdown(f"""
            <div style="background-color:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #ddd;">
            <h4>🚀 Transporte recomendado</h4>
            <ul>
                <li><strong>Transporte:</strong> {resultado['transporte_recomendado']}</li>
                <li><strong>Duración estimada:</strong> {resultado['tiempo_estimado_min']} minutos</li>
                <li><strong>Popularidad estimada:</strong> {resultado['usuarios_estimados']} usuarios</li>
                <li><strong>Sostenibilidad:</strong> {resultado['sostenibilidad_nivel']} / 5</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
            st.subheader("¡Felicidades, ya tienes planificada tu ruta en GreenLake Village! ⛰️💫")
            st.markdown("A continuación, vamos a proporcionarte un resumen de la recomendación de nuestro algoritmo \n\n")
            ruta_nombre = st.session_state.resultado_ruta['nombre']
            duracion_ruta = st.session_state.resultado_ruta['duracion']

            st.markdown("""
            <div style="background-color:#e8f5e9; padding:20px; border-radius:12px; border:1px solid #c8e6c9;">
            <h4>📝 Resumen de tu viaje</h4>
            <ul>
                <li><strong>🧭 Ruta escogida:</strong> {ruta}</li>
                <li><strong> 🗺️ Trayecto seleccionado:</strong> {trayecto}</li>
                <li><strong>🚍 Transporte escogido:</strong> {transporte}</li>
                <li><strong>🗓️ Fecha estimada:</strong> {fecha}</li>
                <li><strong>⏱️ Tiempo estimado de trayecto:</strong> {tiempo_trayecto} minutos</li>
                <li><strong>🕓 Duración estimada de la ruta:</strong> {tiempo_ruta} horas</li>
            </ul>
            </div>
            """.format(
                ruta = ruta_nombre,
                trayecto= origen + " - " + destino,
                transporte=resultado['transporte_recomendado'],
                fecha=fecha.strftime('%d/%m/%Y'),
                tiempo_trayecto=resultado['tiempo_estimado_min'],
                tiempo_ruta=duracion_ruta
            ), unsafe_allow_html=True)

            st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
            st.markdown("Gracias por confiar en nosotros para encontrar tu ruta ideal. Deseamos que disfrutes de tu viaje, te esperamos en GreenLake Village 😄🌍 ")

            #Botón para volver al inicio
            st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
            if st.button("🏠 Volver al Inicio"):
                change_page_func("home")
