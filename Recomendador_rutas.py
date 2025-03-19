import streamlit as st
import pandas as pd
import unicodedata

# --- Funciones auxiliares ---

#Normaliza el texto según la base de datos
def normalizar_texto(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

#Convierte las horas en formato decimal a hh:mm
def horas_a_hhmm(decimal_horas):
    horas = int(decimal_horas)
    minutos = int((decimal_horas - horas) * 60)
    return f"{horas}:{minutos:02d}"

# Carga los datos de nuestra base de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv('baseDatos/rutas_turisticas.csv')
    df['tipo_ruta_normalizada'] = df['tipo_ruta'].apply(normalizar_texto)
    return df

df_rutas = cargar_datos()

# --- Título ---
st.title("Recomendador de Rutas Turísticas")
st.markdown("##### Responde a nuestras preguntas para descubrir tu ruta ideal!")

# Inicializar estado
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
st.subheader("1. Elige el tipo de experiencia que quieres vivir:")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Cultural"):
        st.session_state.tipo_ruta_input = "Cultural"
with col2:
    if st.button("Aventura"):
        st.session_state.tipo_ruta_input = "Aventura"
with col3:
    if st.button("Ecológica"):
        st.session_state.tipo_ruta_input = "Ecológica"
with col4:
    if st.button("Histórica"):
        st.session_state.tipo_ruta_input = "Histórica"
with col5:
    if st.button("Gastronómica"):
        st.session_state.tipo_ruta_input = "Gastronómica"

if st.session_state.tipo_ruta_input:
    st.markdown(f"**Opcion Seleccionada:** {st.session_state.tipo_ruta_input}")

# --- Pregunta 2: Popularidad ---
if st.session_state.tipo_ruta_input:
    st.subheader("2. ¿Qué tipo de rutas prefieres?")
    st.markdown("Las rutas populares suelen ser más atractivas y cuentan con mejores valoraciones, pero también "
                "están más concurridas. Por otro lado, las rutas poco populares no cuentan con tantas opiniones, pero son poco transitadas y pueden sorprenderte. "
                "**¡Descubre una nueva ruta de ensueño que nadie más conoce!**:")

    col6, col7 = st.columns(2)
    with col6:
        if st.button("Popular"):
            st.session_state.popularidad_input = 'popular'
    with col7:
        if st.button("Poco popular"):
            st.session_state.popularidad_input = 'poco popular'

    if st.session_state.popularidad_input:
        st.markdown(f"**Opcion Seleccionada:** {st.session_state.popularidad_input.title()}")

# --- Pregunta 3: Dificultad ---
if st.session_state.popularidad_input:
    st.subheader("3. Nivel de dificultad al que te quieres enfrentar:")
    st.markdown("Elige el nivel de dificultad que mejor se adapte a tus exigencias y condiciones:\n\n"
                "**Fácil**: Rutas sencillas y aptas para todos los públicos. Recorridos menores a 4 km.\n\n"
                "**Estándar**: Rutas con cierta dificultad, pero asequibles para la mayoría de personas. Recorridos comprendidos entre 4 y 6.5 km.\n\n"
                "**Extremo**: Rutas muy exigentes y solo aptas para los más aventureros. Recorridos superiores a 6.5 km.\n\n")
    col8, col9, col10 = st.columns(3)
    with col8:
        if st.button("Fácil"):
            st.session_state.dificultad_input = 'fácil'
    with col9:
        if st.button("Estándar"):
            st.session_state.dificultad_input = 'estandar'
    with col10:
        if st.button("Extremo"):
            st.session_state.dificultad_input = 'extremo'

    if st.session_state.dificultad_input:
        st.markdown(f"**Opcion Seleccionada:** {st.session_state.dificultad_input.title()}")

# --- Pregunta 4: Duración ---
if st.session_state.dificultad_input:
    st.subheader("4. Selecciona un rango estimado de duración para tu ruta (horas):")
    st.session_state.duracion = st.slider("Duración medida en horas:", 0.0, 15.0, st.session_state.duracion, 0.5)
    dur_min, dur_max = st.session_state.duracion
    st.markdown(f"Has seleccionado: **{horas_a_hhmm(dur_min)}** — **{horas_a_hhmm(dur_max)}** horas.")

# --- Pregunta 5: Prioridad de características de la ruta ---
if st.session_state.dificultad_input:
    st.subheader("5. ¿Qué priorizas más en tu ruta?")
    st.markdown("Buscaremos la ruta que mejor se adapte a tus preferencias escogidas en las preguntas anteriores."
            "Por favor, selecciona qué características **son más importantes para ti, de mayor a menor prioridad**, y las tendremos en cuenta para encontrar tu ruta ideal (1º: prioridad más importante):")
    
    opciones = ['Duración', 'Popularidad', 'Dificultad']
    col1, col2, col3 = st.columns(3)
    with col1:
        prioridad_1 = st.selectbox("1º Prioridad", opciones, key="pri1")
    with col2:
        restantes_1 = [o for o in opciones if o != prioridad_1]
        prioridad_2 = st.selectbox("2º Prioridad", restantes_1, key="pri2")
    with col3:
        restantes_2 = [o for o in restantes_1 if o != prioridad_2]
        prioridad_3 = restantes_2[0]
        st.selectbox("3º Prioridad", options=[prioridad_3], index=0, disabled=True)

    prioridades_final = [prioridad_1, prioridad_2, prioridad_3]
    st.session_state.prioridad = prioridades_final

# --- Recomendador ---

#Asigna los pesos a cada característica en función de la prioridad escogida en la última pregunta
#El filtro recomendará la ruta que más puntos adquiera en función de la prioridad escogida
#Asigna el peso 3 a la primera prioridad, 2 a la segunda y 1 a la tercera

if st.session_state.dificultad_input:
    if st.button("Recomiéndame mi Ruta"):
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

        st.success(f"Ruta recomendada: {mejor_ruta['ruta_nombre']}")
        st.markdown(f"**Tipo:** {mejor_ruta['tipo_ruta']}  ")
        st.markdown(f"**Valoración:** {mejor_ruta['popularidad']}  ")
        st.markdown(f"**Distancia:** {mejor_ruta['longitud_km']} km  ")
        st.markdown(f"**Duración:** {duracion_ruta} horas")
