import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import plotly.express as px

# Load datasets
def charge(data_files):
    
    datasets = {}
    for file in data_files:
        try:
            datasets[file] = pd.read_csv(r'.\baseDatos\\'+file)
            print(f"Loaded {file} successfully!")
        except Exception as e:
            print(f"Error loading {file}: {e}")

    df_sostenibilidad = datasets[data_files[0]] 
    df_hotel = datasets[data_files[1]] 
    df_opinion = datasets[data_files[2]] 
    df_rutas = datasets[data_files[3]] 
    df_usotrans = datasets[data_files[4]] 
    return df_sostenibilidad,df_hotel,df_opinion,df_rutas,df_usotrans


#Funciones para Streamlit
def date_treatment(df,base_data,select_mode=True):
    df["fecha"] = pd.to_datetime(df["fecha"],format="%Y-%m-%d", errors="coerce")  # Convertir a datetime
    df = df.dropna(subset=["fecha"])
    df["mes"] = df["fecha"].dt.strftime("%B")  # Nombre del mes
    df["dia_semana"] = df["fecha"].dt.strftime("%A")  # Nombre del día
    df["anno"] = df["fecha"].dt.year
    orden_meses = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    if select_mode:
        modes = list(df.keys())
        modes.remove('fecha')
        modes.remove("anno")
        modes.remove("dia_semana")
        modes.remove("mes")
        modes.remove(base_data)
        
        mode=st.selectbox('Información solicitada:',modes)
    else:
        mode = None
    # Ordenar los días de la semana
    orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return df,mode,orden_dias,orden_meses

def seleccionar(df,base_data):
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

    return df_filtered,i,j


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



def mode_mes(filtered_mes, mode, i, base_data):
    # Graficar la ocupación por mes
    st.subheader(f"{mode} promedio por mes - {i}")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(x=filtered_mes.index, y=filtered_mes.values, color='b', ax=ax)
    
    # Calcular y agregar línea de media mensual
    mean_value = filtered_mes.values.mean()
    ax.axhline(mean_value, color='r', linestyle='--', label=f'Media: {mean_value:.2f}')
    ax.legend()
    
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"{base_data} promedio")
    ax.set_title(f"{base_data} por mes")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def mode_mes_comparativo(df,filtered_mes, mode, i, base_data,orden_meses):
    
    texto = '''¿Con qué otro hotel y período desea comparar'''
    st.text(texto)
    selected_data = sorted(df[base_data].unique())
    selected_anno = sorted(df['anno'].unique())
    selected_data.append('Todos')
    selected_anno.append('Todos')

    I = st.selectbox(f" {base_data}:", selected_data )
    J = st.selectbox("Año:", selected_anno )
    if I == 'Todos':
        df_filtered2 = df
    else:
        df_filtered2 = df[ (df[base_data] ==I)]
    if J!='Todos':
        df_filtered2 = df_filtered2[(df_filtered2['anno'] ==J)]
    # df_filtered,i = seleccionar( df,base_data)
    filtered_mes2 = df_filtered2.groupby("mes")[mode].mean().reindex(orden_meses)
    # Graficar la ocupación por mes
    st.subheader(f"{mode} promedio por mes - {i}")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(x=filtered_mes.index, y=filtered_mes.values, color='b', ax=ax, width=0.5, align = 'center')
    sns.barplot(x=filtered_mes2.index, y=filtered_mes2.values, color='r', ax=ax, width=0.5, align= 'edge')
    # Calcular y agregar línea de media mensual
    mean_value = filtered_mes.values.mean()
    ax.axhline(mean_value, color='r', linestyle='--', label=f'Media original: {mean_value:.2f}')
    mean_value = filtered_mes2.values.mean()
    ax.axhline(mean_value, color='b', linestyle=':', label=f'Media comparativa: {mean_value:.2f}')
    ax.legend()
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"{base_data} promedio")
    ax.set_title(f"{base_data} por mes")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    return I
    


def mode_mes_boxplot(df_filtered, mode):
    # texto = '''En esta gráfica se muestra la media de cada mes y los valores más extremos así como los que están dentro de la desviación típica'''
    # st.text(texto)
    st.subheader(f"Distribución de {mode} por mes")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(x="mes", y=mode, data=df_filtered, order=[
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ], ax=ax)
    ax.set_xlabel("Mes")
    ax.set_ylabel(f"Distribución de {mode}")
    ax.set_title(f"Boxplot de {mode} por mes")
    plt.xticks(rotation=45)
    st.pyplot(fig)


def mode_semana(filtered_dia,mode,i,base_data):
    # Graficar la ocupación por día de la semana
    st.subheader(f"{mode} promedio por día de la semana -{i}")
    fig, ax = plt.subplots(figsize=(10, 5))
    # Calcular y agregar línea de media mensual
    mean_value = filtered_dia.values.mean()
    ax.axhline(mean_value, color='r', linestyle='--', label=f'Media: {mean_value:.2f}')
    ax.legend()
    sns.lineplot(x=filtered_dia.index, y=filtered_dia.values, color='b', ax=ax)
    ax.set_xlabel("Día de la semana")
    ax.set_ylabel(f"{base_data} promedio")
    ax.set_title(f"{base_data} promedio por día de la semana")
    st.pyplot(fig)


#visualizaciones streamlit
def visualizacion_sostenibilidad(change_page_func):
    data_files = [
        "datos_sostenibilidad.csv",
        "ocupacion_hotelera.csv",
        "opiniones_turisticas.csv",
        "rutas_turisticas.csv",
        "uso_transporte.csv"
    ]
    df,df_hotel,_,_,_=charge(data_files)
    st.title("Visualización de la Sostenibilidad de los Hoteles")
    texto = '''Aquí se muestra un gráfico sencillo de barras, seleccionando la variable de sostenibilidad y el año
    Se puede ver mes a mes el gasto realizado por cada hotel.'''
    st.text(texto)
    base_data ='hotel_nombre'
    df,mode,orden_dias,orden_meses, = date_treatment(df,base_data)
    df_filtered,i,j=seleccionar(df,base_data)
    filtered_mes = df_filtered.groupby("mes")[mode].mean().reindex(orden_meses)
    mode_mes( filtered_mes, mode, i,base_data)
    # mode_fecha(df_filtered,mode,i,base_data)
    texto= '''Para poder conocer mejor la situación del hotel se ofrecen otras posibilidades de información'''
    info_extra = st.checkbox("¿Desea información comparativa?", value=False)
    #revisar que se está llamando aquí
    if info_extra:
        st.title("Comparación de Hoteles")
        media_mode_A = df[[mode]].mean()
        df_A = df[df['anno']==j]#.mean()
        media_mode_AA = df_A[[mode]].mean()
        df_i= df[df["hotel_nombre"] == i]
        media_mode_i = df_i[[mode]].mean()
        df_iA = df_i[df_i['anno']==j]#.mean()
        media_mode_ia = df_iA[[mode]].mean()
        
        data_medias = {
                f"Métrica {mode}": ['Media', "Media anual"],
                'Total': [media_mode_A.values[0], media_mode_AA.values[0]],
                i: [media_mode_i.values[0], media_mode_ia.values[0]],
            }
        df_medias = pd.DataFrame(data_medias)
        st.write("Media y moda del hotel y variable pedida respecto al total")
        st.table(df_medias)
        I=mode_mes_comparativo(df,filtered_mes, mode, i, base_data,orden_meses)
        

        if i != I:
            st.text('''Hacer una comparativa de las reservas y tasa de ocupación en ese mismo período de los diferentes hoteles''')
            df_hotel_e,_,_,_ = date_treatment(df_hotel,base_data,select_mode=False)
            df_hotel_1 = df_hotel_e[df_hotel_e["hotel_nombre"] == i]
            df_hotel_2 = df_hotel_e[df_hotel_e["hotel_nombre"] == I]

            # Calcular las medias
            media_TO_1 = df_hotel_1[["tasa_ocupacion"]].mean()
            media_TO_2 = df_hotel_2[["tasa_ocupacion"]].mean()
            media_RC_1 = df_hotel_1[["reservas_confirmadas"]].mean()
            media_RC_2 = df_hotel_2[["reservas_confirmadas"]].mean()
            # Crear DataFrame para la tabla
            data_medias_com = {
                "Métrica": ["Tasa de Ocupación", "Reservas Confirmadas"],
                i: [media_TO_1.values[0], media_RC_1.values[0]],
                I: [media_TO_2.values[0], media_RC_2.values[0]],
            }
            df_medias_com = pd.DataFrame(data_medias_com)

            # Crear la aplicación Streamlit
            
            st.write('''Media de la Tasa de Ocupación y Reservas Confirmadas:
                     conviene revisarlo para saber si las escalas de los hoteles son comparables''')
            st.table(df_medias_com)
            st.write('')




        # I #el hotel nuevo
        # J #el año que se está mirando
    info_box = st.checkbox("¿Desea información en cajas?", value=False)
    if info_box:
        
        st.text('''En esta gráfica se presenta la media y los valores de la moda en la caja y en los extremos los valores más alejados''')
        filtered_mes = df_filtered[['mes', mode]].dropna()#.reindex(orden_meses)  
        mode_mes_boxplot(filtered_mes,mode)
    info_semana = st.checkbox("¿Desea información diaria de algún mes?", value=False)
    if  info_semana:
        st.title("Consulta semanal")
        mes = st.selectbox('Mes que desea consultar', orden_meses)
        df_filtered1 = df_filtered[(df_filtered['mes'] == mes)]
        filtered_dia = df_filtered1.groupby("dia_semana")[mode].mean().reindex(orden_dias)
        mode_semana(filtered_dia,mode,i,base_data)
    #Botón para volver al inicio
    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
    if st.button("🏠 Volver al Inicio"):
        change_page_func("home")
    
    



#EJECUCIÓN
def app (change_page_func):
    st.header("ANÁLISIS DATOS")
# st.write("¿Qué información desea consultar primero?")

    visualizacion_sostenibilidad(change_page_func)

    

