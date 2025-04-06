import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


opiniones = pd.read_csv('baseDatos/opiniones_turisticas.csv')
opiniones = opiniones[opiniones['tipo_servicio'] != 'Hotel']

def app(change_page_func):
    st.title("Descubre qué dicen los viajeros sobre GreenLake Village ⭐🏕️")
    st.image('img/imagen_intro.png')

    # Creamos un dataset con las opiniones agrupadas por servicio 
    conteo_servicios = opiniones['nombre_servicio'].value_counts().to_dict()
    servicios = opiniones.groupby(['nombre_servicio', 'tipo_servicio']).agg({'puntuacion': 'mean'}).reset_index()
    servicios['num_opiniones'] = servicios['nombre_servicio'].map(conteo_servicios)
    servicios['descripcion_servicio'] = servicios.apply(
        lambda row: row['tipo_servicio'] if row['tipo_servicio'] in ['Hotel', 'Ruta'] else row['nombre_servicio'].split()[-1],
        axis=1
    )
    servicios['descripcion_servicio'] = servicios['descripcion_servicio'].replace('Guiado', 'Tour Guiado')
    servicios['puntuacion'] = servicios['puntuacion'].round(1)
    # Selección del servicio deseado
    tipos_servicios = list(servicios['descripcion_servicio'].unique())
    selected_service = st.selectbox('_Selecciona el tipo de servicio que deseas consultar 📌_',options=tipos_servicios)
    servicios_filtered = servicios[servicios['descripcion_servicio'] == selected_service]
    # Seleccionar puntuación mínima
    min_puntuacion = st.slider("_Puntuación media mínima del servicio 💯_", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
    servicios_filtered = servicios_filtered[servicios_filtered['puntuacion'] >= min_puntuacion]
    # Ordenar por: 
    # Valor por defecto para orden si no existe
    if "orden_opiniones" not in st.session_state:
        st.session_state.orden_opiniones = "Puntuación (de mayor a menor)"

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True) #Espacio entre botones
    # Título de orden con un poco de espacio
    st.markdown("##### 🔽 Ordenar servicios por:")

    # Distribución en columnas
    col1, col2, col3, col4, col5 = st.columns([0.5, 2, 2, 2, 0.5])

    with col2:
        if st.button("🔝 Mayor puntuación"):
            st.session_state.orden_opiniones = "Puntuación (de mayor a menor)"
    with col3:
        if st.button("🔻 Menor puntuación"):
            st.session_state.orden_opiniones = "Puntuación (de menor a mayor)"
    with col4:
        if st.button("👥 Más opiniones"):
            st.session_state.orden_opiniones = "Número de opiniones"

    # Aplicar ordenamiento según botón seleccionado
    orden = st.session_state.orden_opiniones

    if orden == "Puntuación (de mayor a menor)":
        servicios_filtered = servicios_filtered.sort_values(by="puntuacion", ascending=False)
    elif orden == "Puntuación (de menor a mayor)":
        servicios_filtered = servicios_filtered.sort_values(by="puntuacion", ascending=True)
    elif orden == "Número de opiniones":
        servicios_filtered = servicios_filtered.sort_values(by="num_opiniones", ascending=False)

    # (Opcional: Mostrar cuál fue el último criterio aplicado)
    st.markdown(f"<p style='text-align:center; color:gray;'>Orden actual: <strong>{orden}</strong></p>", unsafe_allow_html=True)



    # Enseñar los servicios disponibles
    for index, row in servicios_filtered.iterrows():
        nombre_servicio = row["nombre_servicio"]
        puntuacion = row["puntuacion"]
        # Si no hay comentarios, se pone a 0
        num_opiniones = int(row["num_opiniones"]) if not pd.isna(row["num_opiniones"]) else 0
        estrellas = "⭐" * int(puntuacion) + "✩" * (5 - int(puntuacion))
        st.markdown(f"""
        <div style="background-color:#f5f5f5; padding:12px; border-radius:10px; border:1px solid #ccc; margin-bottom:10px;">
            <strong>{nombre_servicio}</strong><br>
            {estrellas} &nbsp; <strong>{puntuacion}/5</strong> -  {num_opiniones} comentarios 💬
        </div>
        """, unsafe_allow_html=True)


    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True) #Espacio entre botones
    # Dar a seleccionar el Servicio 
    st.markdown("#### Opiniones completas de nuestros viajeros 🗣️")
    aux = st.selectbox("_Selecciona cualquier servicio para ver todas sus opiniones:_", servicios_filtered["nombre_servicio"])
    opiniones_filtradas = opiniones[opiniones["nombre_servicio"] == aux]

    opiniones_por_pagina = 3
    total_opiniones = len(opiniones_filtradas)
    total_paginas = (total_opiniones // opiniones_por_pagina) + (1 if total_opiniones % opiniones_por_pagina > 0 else 0)

    # Inicializar sesión de Streamlit para la página actual 
    if "pagina_actual" not in st.session_state:
        st.session_state.pagina_actual = 1

    # Botones de navegación
    col1, col2, col3, col4 = st.columns([2.5, 2, 4.5, 0.5]) 
    with col2:
        if st.button("⬅️ Anterior") and st.session_state.pagina_actual > 1:
            st.session_state.pagina_actual -= 1
    with col3:
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

        st.markdown(f"""
        <div style="background-color:#e3f2fd; padding:15px; border-radius:10px; border:1px solid #90caf9; margin-bottom:10px;">
            <p style="margin:0;"><strong>{puntuacion}⭐</strong> <span style="margin-left:8px;">🗣️</span> {opinion}</p>
        </div>
        """, unsafe_allow_html=True)

    # Desactivar botón si ya estamos en la primera o última página
    if total_opiniones == 0:
        st.warning("No hay opiniones disponibles para este servicio.")

    #Botón para volver al inicio
    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
    if st.button("🏠 Volver al Inicio"):
        change_page_func("home")






