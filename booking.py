import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

rutas = pd.read_csv('rutas_turisticas.csv')
transporte = pd.read_csv('uso_transporte.csv')
ocupacion = pd.read_csv('ocupacion_hotelera.csv')
opiniones = pd.read_csv('opiniones_turisticas.csv')
sostenibilidad = pd.read_csv('datos_sostenibilidad.csv')

st.title('Destination: Green Lake')
st.image('imagen_intro.png')

# Creamos un dataset con las opiniones agrupadas por servicio 
conteo_servicios = opiniones['nombre_servicio'].value_counts().to_dict()
servicios = opiniones.groupby(['nombre_servicio', 'tipo_servicio']).agg({'puntuacion': 'mean'}).reset_index()
servicios['num_opiniones'] = opiniones['nombre_servicio'].map(conteo_servicios)
servicios['descripcion_servicio'] = servicios.apply(
    lambda row: row['tipo_servicio'] if row['tipo_servicio'] in ['Hotel', 'Ruta'] else row['nombre_servicio'].split()[-1],
    axis=1
)
servicios['descripcion_servicio'] = servicios['descripcion_servicio'].replace('Guiado', 'Tour Guiado')
servicios['puntuacion'] = servicios['puntuacion'].round(1)
# Selección del servicio deseado
tipos_servicios = list(servicios['descripcion_servicio'].unique())
selected_service = st.selectbox('Seleccionar Servicio Deseado',options=tipos_servicios)
servicios_filtered = servicios[servicios['descripcion_servicio'] == selected_service]
# Seleccionar puntuación mínima
min_puntuacion = st.slider("Puntuación media mínima", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
servicios_filtered = servicios_filtered[servicios_filtered['puntuacion'] >= min_puntuacion]
# Ordenar por: 
orden = st.radio("Ordenar por", ["Puntuación (de mayor a menor)", "Puntuación (de menor a mayor)", "Número de opiniones"])

if orden == "Puntuación (de mayor a menor)":
    servicios_filtered = servicios_filtered.sort_values(by="puntuacion", ascending=False)
elif orden == "Puntuación (de menor a mayor)":
    servicios_filtered = servicios_filtered.sort_values(by="puntuacion", ascending=True)
elif orden == "Número de opiniones":
    servicios_filtered = servicios_filtered.sort_values(by="num_opiniones", ascending=False)
# Enseñar los servicios disponibles
for index, row in servicios_filtered.iterrows():
    nombre_servicio = row["nombre_servicio"]
    puntuacion = row["puntuacion"]
    num_opiniones = row["num_opiniones"]
    estrellas = "⭐" * int(puntuacion) + "✩" * (5 - int(puntuacion))  # Generar estrellas visuales
    st.markdown(f"**{nombre_servicio}** - {estrellas}  {puntuacion}/5 ({num_opiniones} opiniones)")

# Dar a seleccionar el Servicio 
aux = st.selectbox("Selecciona un servicio para ver sus opiniones:", servicios_filtered["nombre_servicio"])
opiniones_filtradas = opiniones[opiniones["nombre_servicio"] == aux]

opiniones_por_pagina = 3
total_opiniones = len(opiniones_filtradas)
total_paginas = (total_opiniones // opiniones_por_pagina) + (1 if total_opiniones % opiniones_por_pagina > 0 else 0)

# Inicializar sesión de Streamlit para la página actual
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = 1

# Botones de navegación
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Anterior") and st.session_state.pagina_actual > 1:
        st.session_state.pagina_actual -= 1
with col2:
    if st.button("Siguiente ➡️") and st.session_state.pagina_actual < total_paginas:
        st.session_state.pagina_actual += 1

# Calcular índices de inicio y fin para mostrar comentarios
indice_inicio = (st.session_state.pagina_actual - 1) * opiniones_por_pagina
indice_fin = indice_inicio + opiniones_por_pagina

# Mostrar opiniones paginadas
st.write(f"### Opiniones sobre {aux}: (Página {st.session_state.pagina_actual} de {total_paginas})")

for _, row in opiniones_filtradas.iloc[indice_inicio:indice_fin].iterrows():
    opinion = row["comentario"]
    puntuacion = row["puntuacion"]

    st.markdown(f"**{puntuacion}⭐** - 🗣️ {opinion}")

# Desactivar botón si ya estamos en la primera o última página
if total_opiniones == 0:
    st.warning("No hay opiniones disponibles para este servicio.")





