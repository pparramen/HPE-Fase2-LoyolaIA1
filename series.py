import pandas as pd
from prophet import Prophet

# 1. Cargar el dataset y convertir la columna 'fecha' a datetime
df = pd.read_csv('ocupacion_hotelera.csv', parse_dates=['fecha'])

# 2. Eliminar datos de los años 2019 y 2020 (por considerarse atípicos)
df = df[~df['fecha'].dt.year.isin([2019, 2020])]

# 3. Obtener la lista de hoteles únicos
hoteles = df['hotel_nombre'].unique()

# 4. Crear un DataFrame futuro con las fechas de 2025 (predicción diaria)
fechas_futuras = pd.date_range(start='2025-01-01', end='2025-12-31', freq='D')
df_futuro = pd.DataFrame({'ds': fechas_futuras})

# 5. Inicializar un DataFrame para almacenar los resultados con índice de fechas de 2025
df_resultados = pd.DataFrame(index=fechas_futuras)

# 6. Iterar sobre cada hotel y ajustar el modelo Prophet
for hotel in hoteles:
    # Filtrar datos para el hotel actual
    df_hotel = df[df['hotel_nombre'] == hotel].copy()
    # Preparar datos para Prophet (columnas "ds" y "y")
    df_prophet = df_hotel[['fecha', 'tasa_ocupacion']].rename(columns={'fecha': 'ds', 'tasa_ocupacion': 'y'})
    
    # Crear y ajustar el modelo Prophet con estacionalidades semanal y anual, y agregar estacionalidad mensual
    modelo = Prophet(weekly_seasonality=True, yearly_seasonality=True)
    modelo.add_seasonality(name='mensual', period=30.5, fourier_order=5)
    modelo.fit(df_prophet)
    
    # Realizar el pronóstico para el año 2025
    pronostico = modelo.predict(df_futuro)
    
    # Guardar en el DataFrame la ocupación prevista para el hotel actual
    df_resultados[hotel] = pronostico['yhat'].values


print(df_resultados)
df_resultados.to_csv("../Basedatos/predicciones_hoteles_2025.csv", index=True)