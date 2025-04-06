import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Leemos el CSV
ruta_csv = "uso_transporte.csv"
df = pd.read_csv(ruta_csv)

# Procesamos los datos para obtener las características necesarias
df[['origen', 'destino']] = df['ruta_popular'].str.split(' - ', expand=True) #Dividimos la ruta en origen y destino
df['fecha'] = pd.to_datetime(df['fecha']) #Convertimos la fecha a datetime
df['mes'] = df['fecha'].dt.month #Extraemos el mes de la fecha (factor que utilizaremos para un cálculo aproximado)
df['dia_semana'] = df['fecha'].dt.dayofweek #Extraemos el día de la semana (factor que utilizaremos para un cálculo aproximado)

# Clasificación de sostenibilidad según el transporte
sostenibilidad_map = {
    'Bicicleta': 5,
    'Tranvía': 4,
    'Metro': 4,
    'Autobús': 3,
    'Coche Compartido': 2,
    'Avion': 1
}
df['sostenibilidad'] = df['tipo_transporte'].map(sostenibilidad_map).fillna(3)

# 4. Normalizamos los valores para el cálculo del score
df['usuarios_norm'] = df['num_usuarios'] / df['num_usuarios'].max()
df['tiempo_norm'] = df['tiempo_viaje_promedio_min'] / df['tiempo_viaje_promedio_min'].max()
df['sostenibilidad_norm'] = df['sostenibilidad'] / 5

# Función para entrenar modelos de Clasificación y Regresión 
def entrenar_modelos(alpha, beta, gamma, sufijo_modelo):
    # Calculamos el score según la preferencia de pesos del usuario 
    df['score'] = (alpha * df['usuarios_norm'] +
                   beta * (1 - df['tiempo_norm']) +
                   gamma * df['sostenibilidad_norm'])

    # Lista con los transportes y su correspondiente score 
    df_top = df.loc[df.groupby(['fecha', 'origen', 'destino'])['score'].idxmax()]
    

    # Realizamos un encoding de las variables categóricas
    le_origen = LabelEncoder() 
    le_destino = LabelEncoder()  
    le_transporte = LabelEncoder()

    df_top['origen_enc'] = le_origen.fit_transform(df_top['origen'])
    df_top['destino_enc'] = le_destino.fit_transform(df_top['destino'])
    df_top['transporte_enc'] = le_transporte.fit_transform(df_top['tipo_transporte'])

    # Definimos el conjunto de entrenamiento del Clasificador
    X = df_top[['origen_enc', 'destino_enc', 'mes', 'dia_semana']] #Cracterísticas de entrada del modelo
    y = df_top['transporte_enc'] #Variable objetivo a predecir (tipo de transporte)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #Utilizamos un clasificador RandomForest para clasificar el mejor medio de transporte
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    # Guardamos modelo y encoders para la clasificación del transporte según las preferencias del usuario
    joblib.dump(clf, f'modelo_transporte_{sufijo_modelo}.pkl')
    joblib.dump(le_origen, f'encoder_origen_{sufijo_modelo}.pkl')
    joblib.dump(le_destino, f'encoder_destino_{sufijo_modelo}.pkl')
    joblib.dump(le_transporte, f'encoder_transporte_{sufijo_modelo}.pkl')

    # Usamos un regresor RandomForest para predecir tiempo y usuarios que tendra una ruta en un transporte y fecha específicos
    reg_time = RandomForestRegressor()
    reg_users = RandomForestRegressor()

    reg_time.fit(X_train, df_top.loc[X_train.index, 'tiempo_viaje_promedio_min'])
    reg_users.fit(X_train, df_top.loc[X_train.index, 'num_usuarios'])

    #Guardamos el modelo que nos estimará el tiempo y el número de usuarios
    joblib.dump(reg_time, f'modelo_tiempo_{sufijo_modelo}.pkl')
    joblib.dump(reg_users, f'modelo_usuarios_{sufijo_modelo}.pkl')

# Entrenamos 3 modelos según preferencias del usuario

# Modelo Eco -> (Más peso a que sea sostenible)
entrenar_modelos(alpha=0.2, beta=0.2, gamma=0.6, sufijo_modelo="eco")

# Modelo Eficiencia -> (Más peso a que la ruta tarde lo menos posible)
entrenar_modelos(alpha=0.2, beta=0.6, gamma=0.2, sufijo_modelo="eficiencia")

# Modelo Popularidad -> (Más peso a que ese transporte sea el más usado en esa fecha/ruta)
entrenar_modelos(alpha=0.6, beta=0.2, gamma=0.2, sufijo_modelo="popularidad")
