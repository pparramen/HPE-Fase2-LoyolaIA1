import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.ticker as ticker



def app(change_page_func):


    #----- Cargar datos ------

    opiniones = pd.read_csv('baseDatos/opiniones_turisticas.csv')
    opiniones = opiniones[opiniones['tipo_servicio'] == 'Hotel']
    df = pd.read_csv("baseDatos/ocupacion_hotelera.csv", parse_dates=["fecha"])

    # Excluir el año 2020 por ser atípico en los datos de ocupación
    df = df[df["fecha"].dt.year != 2020]    

    # Crear datos adicionales
    num_opiniones = opiniones['nombre_servicio'].value_counts().to_dict()
    opiniones_hoteles = opiniones.groupby(['nombre_servicio']).agg({'puntuacion': 'mean'}).reset_index()
    opiniones_hoteles['num_opiniones'] = opiniones_hoteles['nombre_servicio'].map(num_opiniones)
    opiniones_hoteles['puntuacion'] = opiniones_hoteles['puntuacion'].round(2)

    # ----- Título y descripción -----
    st.title("Explora y valora los hoteles de GreenLake Village 🌍🛎️")
    st.image('img/hoteles.png')
    st.write(
        """
        ###### En esta sección podrá encontrar información sobre los hoteles disponibles en la ciudad, incluyendo su puntuación media y las opiniones de otros usuarios. Además, podrá consultar el precio medio histórico por noche y la tasa de ocupación esperada para sus fechas de visita.
        """
    )
    # ----- Mostrar hoteles disponibles y puntuaciones -----

    st.write("### Hoteles de Green Lake")
    # Ordenar por: 
    # Inicializamos valor por defecto si no existe aún
    if "orden_hoteles" not in st.session_state:
        st.session_state.orden_hoteles = "Puntuación (de mayor a menor)"

    st.markdown("##### 🔽 Ordenar hoteles por:")

    # Distribución centrada con columnas
    col1, col2, col3, col4, col5 = st.columns([0.5, 2, 2, 2, 0.5])

    with col2:
        if st.button("🔝 Mayor puntuación"):
            st.session_state.orden_hoteles = "Puntuación (de mayor a menor)"
    with col3:
        if st.button("🔻 Menor puntuación"):
            st.session_state.orden_hoteles = "Puntuación (de menor a mayor)"
    with col4:
        if st.button("👥 Más opiniones"):
            st.session_state.orden_hoteles = "Número de opiniones"

    # Aplicar orden seleccionado
    orden = st.session_state.orden_hoteles

    if orden == "Puntuación (de mayor a menor)":
        opiniones_hoteles = opiniones_hoteles.sort_values(by="puntuacion", ascending=False)
    elif orden == "Puntuación (de menor a mayor)":
        opiniones_hoteles = opiniones_hoteles.sort_values(by="puntuacion", ascending=True)
    elif orden == "Número de opiniones":
        opiniones_hoteles = opiniones_hoteles.sort_values(by="num_opiniones", ascending=False)

    # Mostrar orden actual (opcional)
    st.markdown(f"<p style='text-align:center; color:gray;'>Orden actual: <strong>{orden}</strong></p>", unsafe_allow_html=True)

    # Mostrar hoteles
    for index, row in opiniones_hoteles.iterrows():
        nombre_servicio = row["nombre_servicio"]
        puntuacion = row["puntuacion"]
        num_opiniones = int(row["num_opiniones"]) if not pd.isna(row["num_opiniones"]) else 0
        estrellas = "⭐" * int(puntuacion) + "✩" * (5 - int(puntuacion))

        st.markdown(f"""
        <div style="background-color:#f5f5f5; padding:12px; border-radius:10px; border:1px solid #ccc; margin-bottom:10px;">
            <strong>{nombre_servicio}</strong><br>
            {estrellas} &nbsp; <strong>{puntuacion}/5</strong> ({num_opiniones} opiniones)
        </div>
        """, unsafe_allow_html=True)


    # ----- Selección de hotel -----
    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True) #Espacio entre botones
    hoteles = sorted(df["hotel_nombre"].unique())
    st.markdown("#### Opiniones de los húespedes 🗣️")
    selected_hotel = st.selectbox("_Seleccione un hotel_:", hoteles)

    # ----- Mostrar opiniones del hotel seleccionado -----
    opiniones_filtradas = opiniones[opiniones["nombre_servicio"] == selected_hotel]

    opiniones_por_pagina = 3
    total_opiniones = len(opiniones_filtradas)
    total_paginas = (total_opiniones // opiniones_por_pagina) + (1 if total_opiniones % opiniones_por_pagina > 0 else 0)

    # Inicializar sesión de Streamlit para la página actual
    if "pagina_actual" not in st.session_state:
        st.session_state.pagina_actual = 1


    
    st.write(f"### Opiniones sobre {selected_hotel}: (Página {st.session_state.pagina_actual} de {total_paginas})")
    
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


    # ----- Selección del rango de fechas para 2025 -----
    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True) #Espacio entre botones
    st.write(f"### Estimación de su reserva en {selected_hotel} 📅")
    st.write(
        """
        ###### Seleccione un rango de fechas en el que tenga pensado alojarse durante este año 2025. Nuestro algoritmo estimará el precio por noche según el histórico de precios, y también le mostrará la ocupación esperada para esos días. Así podrá planificar su viaje con mayor precisión y comodidad.🧳 
        """
    )
    # Se define un rango por defecto (por ejemplo, del 1 al 7 de enero de 2025)
    default_start = pd.Timestamp.today().normalize()
    default_end = default_start + pd.Timedelta(days=7)
    start_date, end_date = st.date_input("_Rango de fechas:_", value=(default_start, default_end))

    # Verificar que las fechas pertenezcan al año 2025
    if start_date.year != 2025 or end_date.year != 2025:
        st.error("Por favor, seleccione fechas pertenecientes a 2025.")
    else:
        # Opción para elegir si se calcula para el último año o los últimos 5 años
        # Inicializar si no está en sesión
        if "precio_modo" not in st.session_state:
            st.session_state.precio_modo = "Último año"

        st.markdown("#### Calcular precio medio basado en:")

        # Distribución centrada
        col1, col2, col3, col4 = st.columns([1, 1.5, 1.8, 0.5])

        with col2:
            if st.button("🗓️ Último año"):
                st.session_state.precio_modo = "Último año"
        with col3:
            if st.button("📊 Últimos 5 años"):
                st.session_state.precio_modo = "Últimos 5 años"

        opcion = st.session_state.precio_modo

        st.markdown(f"<p style='text-align:center; color:gray;'>Modo seleccionado: <strong>{opcion}</strong></p>", unsafe_allow_html=True)


        # Filtrar datos para el hotel seleccionado
        df_hotel = df[df["hotel_nombre"] == selected_hotel].copy()

        # Crear una columna con (mes, día) para comparar con el rango elegido
        df_hotel["mes_dia"] = df_hotel["fecha"].apply(lambda x: (x.month, x.day))
        
    # Generar la lista de días del rango seleccionado
        dias = pd.date_range(start_date, end_date)
        
        daily_means = {}
        total_sum = 0.0
        
        for day in dias:
            md = (day.month, day.day)
            df_day = df_hotel[df_hotel["mes_dia"] == md]
            
            if df_day.empty:
                mean_day = None
            else:
                if opcion == "Último año":
                    # Seleccionar el año más reciente para ese día
                    max_year = df_day["fecha"].dt.year.max()
                    df_day = df_day[df_day["fecha"].dt.year == max_year]
                else:  # Últimos 5 años
                    available_years = sorted(df_day["fecha"].dt.year.unique(), reverse=True)
                    selected_years = available_years[:5]
                    df_day = df_day[df_day["fecha"].dt.year.isin(selected_years)]
                mean_day = df_day["precio_promedio_noche"].mean()
            
            if mean_day is not None:
                daily_means[day.strftime("%Y-%m-%d")] = mean_day
                total_sum += mean_day
            else:
                daily_means[day.strftime("%Y-%m-%d")] = "No hay datos"
        
        st.markdown("### Precio promedio por noche")

        #Tabla de fechas y precios
        tabla_html = """
        <style>
            .custom-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 16px;
            }
            .custom-table th, .custom-table td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }
            .custom-table th {
                background-color: #c8e6c9;
                color: #2e7d32;
            }
            .custom-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>

        <table class="custom-table">
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Precio promedio</th>
                </tr>
            </thead>
            <tbody>
        """

        for fecha_str, promedio in daily_means.items():
            if isinstance(promedio, str):
                tabla_html += f"<tr><td>{fecha_str}</td><td style='color:#c62828; font-weight:bold;'>{promedio}</td></tr>"
            else:
                tabla_html += f"<tr><td>{fecha_str}</td><td><strong>{promedio:.2f}€</strong></td></tr>"

        tabla_html += "</tbody></table>"

        st.markdown(tabla_html, unsafe_allow_html=True)

        
        st.markdown(f"""
        <div style="background-color:#e8f5e9; border:1px solid #81c784; border-radius:10px; padding:10px; margin-top:5px;">
            <h5 style="margin:0;">Precio total estimado:</h5>
            <p style="font-size:20px; font-weight:bold; color:#2e7d32; margin:0;">{total_sum:.2f}€</p>
        </div>
        """, unsafe_allow_html=True)

        
        pred_df = pd.read_csv("baseDatos/predicciones_hoteles_2025.csv", index_col=0, parse_dates=True)
        pred_df.index = pd.to_datetime(pred_df.index)

        # Filtrar las predicciones para el rango de fechas seleccionado
        pred_range = pred_df.loc[start_date:end_date, selected_hotel]
        
        if pred_range.empty:
            st.warning("No se encontraron datos de predicción para el rango de fechas seleccionado.")
        else:
            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True) #Espacio entre botones
            st.write("### Tasa de ocupación esperada para tus fechas")
            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(10, 5))

            
            sns.lineplot(
                x=pred_range.index,
                y=pred_range.values,
                marker="o",
                linewidth=2,
                markersize=7,
                color="#388e3c",
                ax=ax
            )
            
            ax.set_xlabel("Fecha", fontsize=13)
            ax.set_ylabel("Tasa de Ocupación (%)", fontsize=13)
            ax.set_xticks(pred_range.index)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            fig.autofmt_xdate(rotation=45)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
            sns.despine(top=True, right=True)
            plt.tight_layout()
            st.pyplot(fig)


    #Botón para volver al inicio
    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
    if st.button("🏠 Volver al Inicio"):
        change_page_func("home")
