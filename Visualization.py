import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import plotly.express as px

# Load datasets
data_files = [
    "datos_sostenibilidad.csv",
    "ocupacion_hotelera.csv",
    "opiniones_turisticas.csv",
    "rutas_turisticas.csv",
    "uso_transporte.csv"
]

datasets = {}
for file in data_files:
    try:
        datasets[file] = pd.read_csv(file)
        print(f"Loaded {file} successfully!")
    except Exception as e:
        print(f"Error loading {file}: {e}")

df_sostenibilidad = datasets[data_files[0]] 
df_hotel = datasets[data_files[1]] 
df_opinion = datasets[data_files[2]] 
df_rutas = datasets[data_files[3]] 
df_usotrans = datasets[data_files[4]] 

# for name, df in datasets.items():
#     print(f"\nDataset: {name}")
#     print(df.info())
#     print(df.head())
#     print('-'*40)

#Funciones para Streamlit
def date_treatment(df,base_data, list_opt=None):
    df["fecha"] = pd.to_datetime(df["fecha"],format="%Y-%m-%d", errors="coerce")  # Convertir a datetime
    df = df.dropna(subset=["fecha"])
    df["mes"] = df["fecha"].dt.strftime("%B")  # Nombre del mes
    df["dia_semana"] = df["fecha"].dt.strftime("%A")  # Nombre del día
    df["anno"] = df["fecha"].dt.year
    orden_meses = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    modes = list(df.keys())
    modes.remove('fecha')
    modes.remove("anno")
    modes.remove("dia_semana")
    modes.remove("mes")
    modes.remove(base_data)
    print(modes)
    if list_opt!=None: #esto está para poder ver las puntuaciones de opiniones solas y que no salga para escoger idiomas o comentarios
        mode=st.selectbox('Información solicitada:',list_opt)
    else:
        mode=st.selectbox('Información solicitada:',modes)
    # Ordenar los días de la semana
    orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    selected_data = sorted(df[base_data].unique())
    selected_anno = sorted(df['anno'].unique())
    selected_data.append('Todos')
    selected_anno.append('Todos')

    i = st.selectbox(f"Selecciona {base_data}:", selected_data )
    j = st.selectbox("Selecciona el año:", selected_anno )
    if i == 'Todos':
        df_filtered = df
    else:
        df_filtered = df[ (df[base_data] ==i)]
    if j!='Todos':
        df_filtered = df_filtered[(df_filtered['anno'] ==j)]

    return df_filtered,mode,orden_dias,orden_meses,i


def mode_fecha(df_filtered,mode,i,base_data):
    # Graficar ocupación por fecha
    st.subheader(f"{mode} por fecha - {i}")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_filtered, x="fecha", y=mode, hue=base_data, palette="viridis", ax=ax)
    ax.set_title(f"{mode} por Fecha", fontsize=16)
    ax.set_xlabel("Fecha", fontsize=12)
    ax.set_ylabel(f"{mode}", fontsize=12)
    ax.legend(title=f"{base_data}", loc="upper right")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def mode_mes(filtered_mes,mode,i,base_data):
    # Graficar la ocupación por mes
    st.subheader(f"{mode} promedio por mes - {i}")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(x=filtered_mes.index, y=filtered_mes.values, color='b', ax=ax)
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"{base_data} promedio")
    ax.set_title(f"{base_data} por mes")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def mode_semana(filtered_dia,mode,i,base_data):
    
    # Graficar la ocupación por día de la semana
    st.subheader(f"{mode} promedio por día de la semana -{i}")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=filtered_dia.index, y=filtered_dia.values, color='r', ax=ax)
    ax.set_xlabel("Día de la semana")
    ax.set_ylabel(f"{base_data} promedio")
    ax.set_title(f"{base_data} promedio por día de la semana")
    st.pyplot(fig)



#visualizaciones streamlit
def visualizacion_sostenibilidad(df):
    st.title("Visualización de la Sostenibilidad de los Hoteles")
    texto = '''Con esta visualización podemos responder a preguntas como: ¿Qué porcentaje de residuos se reciclan?
        ¿Qué fechas tienen más dificultades para reciclar o ahorrar agua o electricidad?'''
    st.text(texto)
    base_data ='hotel_nombre'
    df_filtered,mode,orden_dias,orden_meses,i = date_treatment(df,base_data)
        
    mode_fecha(df_filtered,mode,i,base_data)

    filtered_mes = df_filtered.groupby("mes")[mode].mean().reindex(orden_meses)
    
    mode_mes(filtered_mes,mode,i,base_data)
   
    mes = st.selectbox('Mes que desea consultar', sorted(df_filtered['mes'].unique()))
    df_filtered1 = df_filtered[(df_filtered['mes'] ==mes)]
    filtered_dia = df_filtered1.groupby("dia_semana")[mode].mean().reindex(orden_dias)
    mode_semana(filtered_dia,mode,i,base_data)
    
def visualizacion_hoteles(df):
    st.title("Visualización de la Ocupación de Hoteles")
    texto = '''Con esta visualización podemos responder preguntas como:
        ¿Qué hoteles tienen mayor ocupación? 
        ¿Cuáles son los meses y días con más reservas?'''
    st.text(texto)
    base_data ='hotel_nombre'
    df_filtered,mode,orden_dias,orden_meses,i = date_treatment(df,base_data)
     
    mode_fecha(df_filtered, mode, i,base_data)

    filtered_mes = df_filtered.groupby("mes")[mode].mean().reindex(orden_meses)
    mode_mes(filtered_mes, mode, i,base_data)
   
    mes = st.selectbox('Mes que desea consultar', sorted(df_filtered['mes'].unique()))
    df_filtered1 = df_filtered[df_filtered['mes'] == mes]
    filtered_dia = df_filtered1.groupby("dia_semana")[mode].mean().reindex(orden_dias)
    mode_semana(filtered_dia, mode, i,base_data)

def visualizacion_opiniones(df):
    st.title("Análisis de Opiniones de los Clientes")
    texto = '''Esta visualización permite conocer la satisfacción de los clientes:
        ¿Qué hoteles tienen mejores calificaciones?
        ¿Cómo varían las opiniones a lo largo del tiempo?'''
    st.text(texto)
    base_data ='nombre_servicio'
    df_filtered,mode,orden_dias,orden_meses,i = date_treatment(df,base_data,list_opt='puntuacion')
     
    mode_fecha(df_filtered, mode, i,base_data)

    filtered_mes = df_filtered.groupby("mes")[mode].mean().reindex(orden_meses)
    mode_mes(filtered_mes, mode, i,base_data)

    mes = st.selectbox('Mes que desea consultar', sorted(df_filtered['mes'].unique()))
    df_filtered1 = df_filtered[df_filtered['mes'] == mes]
    filtered_dia = df_filtered1.groupby("dia_semana")[mode].mean().reindex(orden_dias)
    mode_semana(filtered_dia, mode, i,base_data)

#!!!
#este no usa fechas asi que no puedo usar las funciones creadas, por lo que queda pendiente
# def visualizacion_rutas(df):
#     st.title("Análisis de las Rutas de Viaje")
#     texto = '''Con esta visualización podemos responder preguntas como:
#         ¿Cuáles son las rutas más populares? 
#         ¿En qué épocas del año hay más movimiento?'''
#     st.text(texto)
#     base_data = 'tipo_ruta'
#     df_filtered, mode, orden_dias, orden_meses, i = date_treatment(df,base_data)

#     mode_fecha(df_filtered, mode, i,base_data)

#     filtered_mes = df_filtered.groupby("mes")[mode].mean().reindex(orden_meses)
#     mode_mes(filtered_mes, mode, i,base_data)

#     mes = st.selectbox('Mes que desea consultar', sorted(df_filtered['mes'].unique()))
#     df_filtered1 = df_filtered[df_filtered['mes'] == mes]
#     filtered_dia = df_filtered1.groupby("dia_semana")[mode].mean().reindex(orden_dias)
#     mode_semana(filtered_dia, mode, i,base_data)

def visualizacion_usotrans(df):
    st.title("Visualización del Uso de los Servicios")
    texto = '''Con esta visualización podemos analizar:
        ¿Qué servicios se usan más? 
        ¿Cuándo se registra mayor demanda?'''
    st.text(texto)
    base_data = 'tipo_transporte'
    df_filtered, mode, orden_dias, orden_meses, i = date_treatment(df,base_data)

    mode_fecha(df_filtered, mode, i,base_data)

    filtered_mes = df_filtered.groupby("mes")[mode].mean().reindex(orden_meses)
    mode_mes(filtered_mes, mode, i,base_data)

    mes = st.selectbox('Mes que desea consultar', sorted(df_filtered['mes'].unique()))
    df_filtered1 = df_filtered[df_filtered['mes'] == mes]
    filtered_dia = df_filtered1.groupby("dia_semana")[mode].mean().reindex(orden_dias)
    mode_semana(filtered_dia, mode, i,base_data)

    






#EJECUCIÓN

st.header("ANÁLISIS DATOS")
st.write("¿Qué información desea consultar primero?")

# Función para actualizar los checkboxes
def update_checkbox(selected):
    for key in ["sostenibilidad", "hoteles", "opiniones", "rutas", "uso"]:
        if key != selected:
            st.session_state[key] = False

# Crear los checkboxes con exclusividad
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    checkbox_sostenibilidad = st.checkbox("Sostenibilidad", value=False, 
                                          key="sostenibilidad",
                                          on_change=update_checkbox, 
                                          args=("sostenibilidad",))

with col2:
    checkbox_hotel = st.checkbox("Hoteles", value=False, 
                                 key="hoteles",
                                 on_change=update_checkbox, 
                                 args=("hoteles",))

with col3:
    checkbox_opiniones = st.checkbox("Opiniones", value=False, 
                                     key="opiniones",
                                     on_change=update_checkbox, 
                                     args=("opiniones",))

with col4:
    checkbox_rutas = st.checkbox("Rutas", value=False, 
                                 key="rutas",
                                 on_change=update_checkbox, 
                                 args=("rutas",))

with col5:
    checkbox_uso = st.checkbox("Uso transporte", value=False, 
                               key="uso",
                               on_change=update_checkbox, 
                               args=("uso",))


if checkbox_sostenibilidad:
    visualizacion_sostenibilidad(df_sostenibilidad)
    
if checkbox_hotel:
    visualizacion_hoteles(df_hotel)
    
if checkbox_opiniones:
    visualizacion_opiniones(df_opinion)
    
if checkbox_rutas:
    # visualizacion_rutas(df_rutas)
    st.text('Pendiente revisión tipo gráficas')
    
if checkbox_uso:
    visualizacion_usotrans(df_usotrans)
    