import streamlit as st
import pandas as pd
import unicodedata

# --- Funciones auxiliares ---
def normalizar_texto(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv('baseDatos/rutas_turisticas.csv')
    df['tipo_ruta_normalizada'] = df['tipo_ruta'].apply(normalizar_texto)
    return df

df_rutas = cargar_datos()

# --- Título ---
st.title("🌍 Recomendador de Rutas Turísticas")
st.write("¡Responde a nuestras preguntas para desubrir tu ruta ideal!")

# --- Paso 1: Tipo de ruta ---
tipos_opciones = ['Cultural', 'Aventura', 'Ecológica', 'Histórica', 'Gastronómica']
tipo_ruta_input = st.radio("1. Elige el tipo de experiencia que quieres vivir:", tipos_opciones)

# Normalizamos input
tipo_ruta_norm = normalizar_texto(tipo_ruta_input)

# --- Paso 2: Popularidad ---
popularidad_input = st.radio("2. ¿Qué tipo de rutas prefieres? Las rutas populares suelen ser más atractivas y cuentan con mejores valoraciones, pero también "
"están más concurridas. Por otro lado, las rutas poco populares no cuentan con tantas opiniones, pero son poco transitadas y pueden sorprenderte. "
"¡Descubre una nueva ruta de ensueño que nadie más conoce! :", ['Popular', 'Poco popular']).lower()

# --- Paso 3: Dificultad ---
dificultad_input = st.radio("3. Nivel de dificultad de la ruta al que te quieres enfrentar:", ['Fácil', 'Estándar', 'Extremo']).lower()

# --- Paso 4: Slider de duración ---
st.write("4. Selecciona un rango estimado de duración para tu ruta (horas):")
duracion_min, duracion_max = st.slider("Duración (horas):", 0.0, 15.0, (2.0, 5.0), 0.5)

# --- Botón para recomendar ---
if st.button("🔍 Recomiendame mi Ruta"):
    # Filtrar por tipo_ruta
    rutas_filtradas = df_rutas[df_rutas['tipo_ruta_normalizada'] == tipo_ruta_norm]

    recomendaciones = []

    for _, ruta in rutas_filtradas.iterrows():
        puntuacion = 0

        if popularidad_input == 'popular' and ruta['popularidad'] >= 4.0:
            puntuacion += 3
        elif popularidad_input == 'poco popular' and ruta['popularidad'] < 4.0:
            puntuacion += 3

        distancia = ruta['longitud_km']
        if dificultad_input == 'fácil' and distancia < 4.0:
            puntuacion += 2
        elif dificultad_input == 'estandar' and 4.0 <= distancia <= 6.5:
            puntuacion += 2
        elif dificultad_input == 'extremo' and distancia > 6.5:
            puntuacion += 2

        duracion = ruta['duracion_hr']
        if duracion_min <= duracion <= duracion_max:
            puntuacion += 1

        recomendaciones.append((ruta, puntuacion))

    recomendaciones.sort(key=lambda x: x[1], reverse=True)
    mejor_ruta = recomendaciones[0][0]
    puntuacion_max = recomendaciones[0][1]

    st.success(f"Ruta recomendada: {mejor_ruta['ruta_nombre']}")
    st.markdown(f"**Tipo:** {mejor_ruta['tipo_ruta']}  ")
    st.markdown(f"**Valoración:** {mejor_ruta['popularidad']}  ")
    st.markdown(f"**Distancia:** {mejor_ruta['longitud_km']} km  ")
    st.markdown(f"**Duración:** {mejor_ruta['duracion_hr']} horas  ")
    #st.markdown(f"**Puntuación calculada:** {puntuacion_max} puntos")
