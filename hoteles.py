import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Cargar el dataset (asegúrese de que "ocupacion_hotelera.csv" esté en la misma carpeta)
df = pd.read_csv("datos/ocupacion_hotelera.csv", parse_dates=["fecha"])

# Excluir el año 2020 por ser atípico
df = df[df["fecha"].dt.year != 2020]

# Convertir a string o mantener el nombre del hotel según el dataset (se asume columna "hotel")
hoteles = sorted(df["hotel_nombre"].unique())
selected_hotel = st.selectbox("Seleccione un hotel", hoteles)

# Selección del rango de fechas para 2025
st.write("Seleccione el rango de fechas en 2025 para su visita")
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
    
    st.write("Precio promedio por noche")
    for fecha_str, promedio in daily_means.items():
        if isinstance(promedio, str):
            st.write(f"{fecha_str}: **{promedio}$**")
        else:
            st.write(f"{fecha_str}: **{promedio:.2f}$**")
    
    st.write("Precio total estimado")
    st.write(f"**{total_sum:.2f}$**")

    pred_df = pd.read_csv("datos/predicciones_hoteles_2025.csv", index_col=0, parse_dates=True)
    pred_df.index = pd.to_datetime(pred_df.index)

    # Filtrar las predicciones para el rango de fechas seleccionado
    pred_range = pred_df.loc[start_date:end_date, selected_hotel]
    
    if pred_range.empty:
        st.warning("No se encontraron datos de predicción para el rango de fechas seleccionado.")
    else:
        st.write("Tasa de ocupación esparada para tus fechas")
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