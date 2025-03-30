import streamlit as st
import pandas as pd
import unicodedata

def app(change_page_func):

    # --- Reinicio del estado si venimos desde Home ---
    if st.session_state.get("reset_rutas", False):
        for key in [
            "tipo_ruta_input", "popularidad_input", "dificultad_input",
            "duracion", "prioridad", "resultado_ruta",
            "duracion_anterior", "clear_resultado"
        ]:
            st.session_state.pop(key, None)
        st.session_state.reset_rutas = False


     # --- Inicializaciones ---
    if "resultado_ruta" not in st.session_state:
        st.session_state.resultado_ruta = None

    if "clear_resultado" not in st.session_state:
        st.session_state.clear_resultado = False

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

    # --- Funciones auxiliares ---

    #Normalizamos el texto según la base de datos
    def normalizar_texto(texto):
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        ).lower()

    #Convertimos las horas en formato decimal a hh:mm
    def horas_a_hhmm(decimal_horas):
        horas = int(decimal_horas)
        minutos = int((decimal_horas - horas) * 60)
        return f"{horas}:{minutos:02d}"

    # Cargamos los datos de nuestra base de datos
    @st.cache_data
    def cargar_datos():
        df = pd.read_csv('baseDatos/rutas_turisticas.csv')
        df['tipo_ruta_normalizada'] = df['tipo_ruta'].apply(normalizar_texto)
        return df

    df_rutas = cargar_datos()


    # --- Título ---
    st.title("🌍 Recomendador de Rutas Turísticas en GreenLake Village 🌍")
    st.markdown("##### Responde a nuestras preguntas para descubrir tu ruta ideal! 🧭")

    # Inicializamos el estado
    if 'tipo_ruta_input' not in st.session_state:
        st.session_state.tipo_ruta_input = ''
    if 'popularidad_input' not in st.session_state:
        st.session_state.popularidad_input = ''
    if 'dificultad_input' not in st.session_state:
        st.session_state.dificultad_input = ''
    if 'duracion' not in st.session_state:
        st.session_state.duracion = (2.0, 5.0)
    if 'prioridad' not in st.session_state:
        st.session_state.prioridad = ['Duración', 'Popularidad', 'Dificultad']

    # --- Pregunta 1: Tipo de ruta ---
    st.subheader("1️⃣ Elige el tipo de experiencia que quieres vivir:")
    #Primera fila de botones
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    with col2:
        if st.button("🏛️ Cultural"):
            st.session_state.tipo_ruta_input = "Cultural"
            st.session_state.clear_resultado = True
    with col3:
        if st.button("🥾 Aventura"):
            st.session_state.tipo_ruta_input = "Aventura"
            st.session_state.clear_resultado = True
    with col4:
        if st.button("🌱 Ecológica"):
            st.session_state.tipo_ruta_input = "Ecológica"
            st.session_state.clear_resultado = True

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True) #Espacio entre botones

    #Segunda fila de botones
    col6, col7, col8, col9, col10 = st.columns([1.5, 2, 1.7, 1, 0.5 ])
    with col7:
        if st.button("🏰 Histórica"):
            st.session_state.tipo_ruta_input = "Histórica"
            st.session_state.clear_resultado = True
    with col8:
        if st.button("🍽️ Gastronómica"):
            st.session_state.tipo_ruta_input = "Gastronómica"
            st.session_state.clear_resultado = True

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
    if st.session_state.tipo_ruta_input:
        st.markdown(f"**Opción Seleccionada:** {st.session_state.tipo_ruta_input}")

    # --- Pregunta 2: Popularidad ---
    if st.session_state.tipo_ruta_input:
        st.subheader("2️⃣ ¿Qué tipo de rutas prefieres?")
        st.markdown("Las rutas populares suelen ser más atractivas y cuentan con mejores valoraciones, pero también "
                    "están más concurridas. Por otro lado, las rutas poco populares no cuentan con tantas opiniones, pero son poco transitadas y pueden sorprenderte. "
                    "**¡Descubre una nueva ruta de ensueño que nadie más conoce!**:")

        col1, col2, col3, col4 = st.columns([1, 2, 2, 1]) 

        with col2:
            if st.button("🔥 Popular"):
                st.session_state.popularidad_input = 'popular'
                st.session_state.clear_resultado = True
        with col3:
            if st.button("❓ Poco popular"):
                st.session_state.popularidad_input = 'poco popular'
                st.session_state.clear_resultado = True

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True) #Espacio entre botones
        if st.session_state.popularidad_input:
            st.markdown(f"**Opción Seleccionada:** {st.session_state.popularidad_input.title()}")

    # --- Pregunta 3: Dificultad ---
    if st.session_state.popularidad_input:
        st.subheader("3️⃣ Nivel de dificultad al que te quieres enfrentar:")
        st.markdown("Elige el nivel de dificultad que mejor se adapte a tus exigencias y condiciones:\n\n"
                    "**Fácil**: Rutas sencillas y aptas para todos los públicos. Recorridos menores a 4 km.\n\n"
                    "**Estándar**: Rutas con cierta dificultad, pero asequibles para la mayoría de personas. Recorridos comprendidos entre 4 y 6.5 km.\n\n"
                    "**Extremo**: Rutas muy exigentes y solo aptas para los más aventureros. Recorridos superiores a 6.5 km.\n\n")
        
        col7, col8, col9, col10, col11 = st.columns([1, 1.8, 2, 2, 1])
        with col8:
            if st.button("✅ Fácil"):
                st.session_state.dificultad_input = 'fácil'
                st.session_state.clear_resultado = True
        with col9:
            if st.button("⚖️ Estándar"):
                st.session_state.dificultad_input = 'estandar'
                st.session_state.clear_resultado = True
        with col10:
            if st.button("😈 Extremo"):
                st.session_state.dificultad_input = 'extremo'
                st.session_state.clear_resultado = True

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True) #Espacio entre botones
        if st.session_state.dificultad_input:
            st.markdown(f"**Opción Seleccionada:** {st.session_state.dificultad_input.title()}")
       

    # --- Pregunta 4: Duración ---
    # Inicializamos duración anterior si no existe
    if "duracion_anterior" not in st.session_state:
        st.session_state.duracion_anterior = st.session_state.duracion 

    if st.session_state.dificultad_input:
        st.subheader("4️⃣ Selecciona un rango estimado de duración para tu ruta (horas):")
        st.session_state.duracion = st.slider("⏳ Duración medida en horas:", 0.0, 15.0, st.session_state.duracion, 0.5)
        dur_min, dur_max = st.session_state.duracion
        st.markdown(f"Has seleccionado: **{horas_a_hhmm(dur_min)}** — **{horas_a_hhmm(dur_max)}** horas.")

        # Si cambia la duración respecto a la anterior, limpiamos resultado
        if st.session_state.duracion != st.session_state.duracion_anterior:
            st.session_state.clear_resultado = True
            st.session_state.duracion_anterior = st.session_state.duracion

    # --- Pregunta 5: Prioridad de características de la ruta ---
    if st.session_state.dificultad_input:
        st.subheader("5️⃣ ¿Qué priorizas más en tu ruta?")
        st.markdown("Buscaremos la ruta que mejor se adapte a tus preferencias escogidas en las preguntas anteriores.\n"
                    "Selecciona qué características **son más importantes para ti, de mayor a menor prioridad**:\n")

        opciones = ['Duración', 'Popularidad', 'Dificultad']
        col1, col2, col3 = st.columns(3)
        with col1:
            prioridad_1 = st.selectbox("🥇 **1º Prioridad**", opciones, key="pri1")
        with col2:
            restantes_1 = [o for o in opciones if o != prioridad_1]
            prioridad_2 = st.selectbox("🥈 **2º Prioridad**", restantes_1, key="pri2")
        with col3:
            restantes_2 = [o for o in restantes_1 if o != prioridad_2]
            prioridad_3 = restantes_2[0]
            st.selectbox("🥉 **3º Prioridad**", options=[prioridad_3], index=0, disabled=True)

        prioridades_final = [prioridad_1, prioridad_2, prioridad_3]

        # Si cambian las prioridades, limpiamos el resultado
        if st.session_state.prioridad != prioridades_final:
            st.session_state.clear_resultado = True
        st.session_state.prioridad = prioridades_final



    if st.session_state.get("clear_resultado", False):
        st.session_state.resultado_ruta = None
        st.session_state.clear_resultado = False
    

    # --- Recomendador ---
    if st.session_state.dificultad_input:
        if st.button("🔍 Recomiéndame mi Ruta"):
            pesos = {
                st.session_state.prioridad[0]: 3, 
                st.session_state.prioridad[1]: 2,
                st.session_state.prioridad[2]: 1
            }

            tipo_ruta_norm = normalizar_texto(st.session_state.tipo_ruta_input)
            rutas_filtradas = df_rutas[df_rutas['tipo_ruta_normalizada'] == tipo_ruta_norm]

            recomendaciones = []
            dur_min, dur_max = st.session_state.duracion

            for _, ruta in rutas_filtradas.iterrows():
                puntuacion = 0

                if st.session_state.popularidad_input == 'popular' and ruta['popularidad'] >= 4.0:
                    puntuacion += pesos['Popularidad']
                elif st.session_state.popularidad_input == 'poco popular' and ruta['popularidad'] < 4.0:
                    puntuacion += pesos['Popularidad']

                distancia = ruta['longitud_km']
                if st.session_state.dificultad_input == 'fácil' and distancia < 4.0:
                    puntuacion += pesos['Dificultad']
                elif st.session_state.dificultad_input == 'estandar' and 4.0 <= distancia <= 6.5:
                    puntuacion += pesos['Dificultad']
                elif st.session_state.dificultad_input == 'extremo' and distancia > 6.5:
                    puntuacion += pesos['Dificultad']

                duracion = ruta['duracion_hr']
                if dur_min <= duracion <= dur_max:
                    puntuacion += pesos['Duración']

                recomendaciones.append((ruta, puntuacion))

            recomendaciones.sort(key=lambda x: x[1], reverse=True)
            mejor_ruta = recomendaciones[0][0]
            duracion_ruta = horas_a_hhmm(mejor_ruta['duracion_hr'])

            # Guardamos ruta recomendada en session_state para después usarla
            st.session_state.resultado_ruta = {
                "nombre": mejor_ruta['ruta_nombre'],
                "tipo": mejor_ruta['tipo_ruta'],
                "valoracion": mejor_ruta['popularidad'],
                "distancia": mejor_ruta['longitud_km'],
                "duracion": duracion_ruta
            }


    # --- MOSTRAR RUTA RECOMENDADA ---
    if st.session_state.resultado_ruta:
        ruta = st.session_state.resultado_ruta

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background-color:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #ddd;">
        <h4>🌟 Ruta recomendada: {ruta['nombre']}</h4>
        <ul>
            <li><strong>Tipo:</strong> {ruta['tipo']}</li>
            <li><strong>Valoración:</strong> {ruta['valoracion']}</li>
            <li><strong>Distancia:</strong> {ruta['distancia']} km</li>
            <li><strong>Duración:</strong> {ruta['duracion']} horas</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
        st.subheader("Perfecto, ya has encontrado tu ruta ideal 🎉")
        st.markdown("¿Te gustaría organizar tu viaje con nosotros y descubrir la mejor forma de llegar a tu destino? 😎")

        # Botón para ir a transporte
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        if st.button("🚌 Organiza mi viaje"):
            st.session_state.resultado_transporte = None
            st.session_state.preferencia_transporte = None
            st.session_state.origen = None
            st.session_state.fecha = None
            change_page_func("transporte")
        st.markdown("</div>", unsafe_allow_html=True)
