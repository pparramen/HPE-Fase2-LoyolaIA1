import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

#----- Cargar datos ------

opiniones = pd.read_csv('datos/opiniones_turisticas.csv')
opiniones = opiniones[opiniones['tipo_servicio'] == 'Hotel']
df = pd.read_csv("datos/ocupacion_hotelera.csv", parse_dates=["fecha"])

# Excluir el año 2020 por ser atípico en los datos de ocupación
df = df[df["fecha"].dt.year != 2020]

# Crear datos adicionales
num_opiniones = opiniones['nombre_servicio'].value_counts().to_dict()
opiniones_hoteles = opiniones.groupby(['nombre_servicio']).agg({'puntuacion': 'mean'}).reset_index()
opiniones_hoteles['num_opiniones'] = opiniones_hoteles['nombre_servicio'].map(num_opiniones)
opiniones_hoteles['puntuacion'] = opiniones_hoteles['puntuacion'].round(2)

# ----- Título y descripción -----
st.image('img/hoteles.png')
st.write(
    """
    En esta sección podrá encontrar información sobre los hoteles disponibles en la ciudad, incluyendo su puntuación media y las opiniones de otros usuarios.
    Además, podrá consultar el precio medio histórico por noche y la tasa de ocupación esperada para sus fechas de visita.
    """
)
# ----- Mostrar hoteles disponibles y puntuaciones -----

st.write("### Hoteles de Green Lake")
# Ordenar por: 
orden = st.radio("Ordenar por", ["Puntuación (de mayor a menor)", "Puntuación (de menor a mayor)", "Número de opiniones"])

if orden == "Puntuación (de mayor a menor)":
    opiniones_hoteles = opiniones_hoteles.sort_values(by="puntuacion", ascending=False)
elif orden == "Puntuación (de menor a mayor)":
    opiniones_hoteles = opiniones_hoteles.sort_values(by="puntuacion", ascending=True)
elif orden == "Número de opiniones":
    opiniones_hoteles = opiniones_hoteles.sort_values(by="num_opiniones", ascending=False)
# Enseñar los servicios disponibles
for index, row in opiniones_hoteles.iterrows():
    nombre_servicio = row["nombre_servicio"]
    puntuacion = row["puntuacion"]
    num_opiniones = row["num_opiniones"]
    estrellas = "⭐" * int(puntuacion) + "✩" * (5 - int(puntuacion))  # Generar estrellas visuales
    st.markdown(f"**{nombre_servicio}** - {estrellas}  {puntuacion}/5 ({num_opiniones} opiniones)")


# ----- Selección de hotel -----

hoteles = sorted(df["hotel_nombre"].unique())
st.write("### Seleccione un hotel")
selected_hotel = st.selectbox(" ", hoteles)

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

for _, row in opiniones_filtradas.iloc[indice_inicio:indice_fin].iterrows():
    opinion = row["comentario"]
    puntuacion = row["puntuacion"]

    st.markdown(f"**{puntuacion}⭐** - 🗣️ {opinion}")

# Desactivar botón si ya estamos en la primera o última página
if total_opiniones == 0:
    st.warning("No hay opiniones disponibles para este servicio.")


# ----- Selección del rango de fechas para 2025 -----
st.write("### Fechas de su visita durante 2025")
# Se define un rango por defecto (por ejemplo, del 1 al 7 de enero de 2025)
default_start = pd.to_datetime("2025-01-01")
default_end = pd.to_datetime("2025-01-07")
start_date, end_date = st.date_input("Rango de fechas", value=(default_start, default_end))

# Verificar que las fechas pertenezcan al año 2025
if start_date.year != 2025 or end_date.year != 2025:
    st.error("Por favor, seleccione fechas pertenecientes a 2025.")
else:
    # Opción para elegir si se calcula para el último año o los últimos 5 años
    opcion = st.radio("Calcular precio medio basado en", options=["Último año", "Últimos 5 años"])

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
    
    st.write("### Precio promedio por noche")
    for fecha_str, promedio in daily_means.items():
        if isinstance(promedio, str):
            st.write(f"{fecha_str}: **{promedio}$**")
        else:
            st.write(f"{fecha_str}: **{promedio:.2f}$**")
    
    st.write("### Precio total estimado")
    st.write(f"**{total_sum:.2f}$**")

    pred_df = pd.read_csv("datos/predicciones_hoteles_2025.csv", index_col=0, parse_dates=True)
    pred_df.index = pd.to_datetime(pred_df.index)

    # Filtrar las predicciones para el rango de fechas seleccionado
    pred_range = pred_df.loc[start_date:end_date, selected_hotel]
    
    if pred_range.empty:
        st.warning("No se encontraron datos de predicción para el rango de fechas seleccionado.")
    else:
        st.write("### Tasa de ocupación esparada para tus fechas")
        sns.set_theme(style="white")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x=pred_range.index, y=pred_range.values, marker="o", ax=ax)
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Tasa de Ocupación (%)")
        ax.set_xticks(pred_range.index)
        date_format = mdates.DateFormatter('%d %b')  # Ejemplo: 29 Mar
        plt.gca().xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        sns.despine(top=True, right=True)
        plt.tight_layout()

        
        st.pyplot(fig)