import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# ----------- CARGA Y PREPROCESADO ----------- #
@st.cache_data
def cargar_datos():
    df = pd.read_csv("baseDatos/sostenibilidad_ocupacion.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Preprocesado
    df["reservas_confirmadas"] = df["reservas_confirmadas"].replace(0, 1)

    df["energia_por_persona"] = df["consumo_energia_kwh"] / df["reservas_confirmadas"]
    df["residuos_por_persona"] = df["residuos_generados_kg"] / df["reservas_confirmadas"]
    df["agua_por_persona"] = df["uso_agua_m3"] / df["reservas_confirmadas"]
    df["reciclaje_invertido"] = 100 - df["porcentaje_reciclaje"]

    # Score de sostenibilidad
    vars_score = ["energia_por_persona", "residuos_por_persona", "agua_por_persona", "reciclaje_invertido"]
    scaler = MinMaxScaler()
    df[vars_score] = scaler.fit_transform(df[vars_score])
    df["sostenibilidad_score"] = 1 - df[vars_score].mean(axis=1)

    return df

# ----------- FUNCIONES ----------- #
def obtener_resumen_mensual(df, hotel, mes, año):
    mes_str = str(mes).zfill(2)
    periodo = f"{año}-{mes_str}"
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    datos = df[(df["hotel_nombre"] == hotel) & (df["mes"] == periodo)]

    if datos.empty:
        return None

    return {
        "periodo": periodo,
        "score": round(datos["sostenibilidad_score"].mean(), 2),
        "energia": round(datos["consumo_energia_kwh"].sum(), 2),
        "residuos": round(datos["residuos_generados_kg"].sum(), 2),
        "agua": round(datos["uso_agua_m3"].sum(), 2),
        "reciclaje": round(datos["porcentaje_reciclaje"].mean(), 2),
        "reservas": datos["reservas_confirmadas"].sum()
    }

def ocupacion_semanal(df, hotel, mes):

    df_filtrado = df[(df["hotel_nombre"] == hotel) & 
                     (df["fecha"].dt.month == mes)].copy()

    if df_filtrado.empty:
        st.info("No hay datos históricos para ese hotel y mes.")
        return

    df_filtrado["año"] = df_filtrado["fecha"].dt.year
    df_filtrado["dia"] = df_filtrado["fecha"].dt.day

    # Crear columna de tramo: 1-10, 11-20, 21-31
    def clasificar_tramo(dia):
        if dia <= 10:
            return "Días 1-10"
        elif dia <= 20:
            return "Días 11-20"
        else:
            return "Días 21-31"

    df_filtrado["tramo"] = df_filtrado["dia"].apply(clasificar_tramo)
    # Sumar por tramo
    agrupado = df_filtrado.groupby("tramo")[["reservas_confirmadas", "cancelaciones"]].sum().reset_index()

    # Hacer la media
    n_años = df_filtrado["año"].nunique()
    agrupado["Reservas Confirmadas"] = (agrupado["reservas_confirmadas"] / n_años).astype(int)
    agrupado["Cancelaciones"] = (agrupado["cancelaciones"] / n_años).astype(int)


    resumen = agrupado[["tramo", "Reservas Confirmadas", "Cancelaciones"]]
    resumen = pd.melt(resumen, id_vars="tramo", var_name="Tipo", value_name="Promedio")

    # Ordenar los tramos de forma lógica
    orden_tramos = ["Días 1-10", "Días 11-20", "Días 21-31"]
    resumen["tramo"] = pd.Categorical(resumen["tramo"], categories=orden_tramos, ordered=True)

    # Gráfico
    custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    sns.set_theme(style="white", rc=custom_params)
    colores = {
    "Reservas Confirmadas": "#FFD6A5",  
    "Cancelaciones": "#A8E6A1"    
    }
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(data=resumen, x="tramo", y="Promedio", hue="Tipo", palette=colores ,dodge=True, width=0.6)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", label_type="edge", padding=2)
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.tight_layout()
    st.pyplot(plt.gcf())


# ----------- INTERFAZ PRINCIPAL ----------- #
def app(change_page_func):
    st.image("img/sostenibilidad_header.png")
    st.markdown('''
    Conoce el impacto ambiental de tu hotel a través de un informe mensual. Podrán seleccionar el mes
    y año, y conocer datos como el consumo de energía, los residuos generados, uso de agua y porcentaje
    de reciclaje durante esas fechas.

    Además, se les proporcionará un **score de sostenibilidad** en base a sus datos y los de otros hoteles,
    penalizando un excesivo uso de recursos por huésped y un bajo porcentaje de reciclaje.
         
    Para el mes seleccionado se presenta un gráfico que muestra las reservas y cancelaciones
    que se preveen para ese mes de forma pueda planificar y optimizar su consumo de recursos.
    ''')

    df = cargar_datos()

    # Selección de hotel, mes y año
    hoteles = sorted(df["hotel_nombre"].unique())
    hotel_sel = st.selectbox("🏨 Selecciona un hotel", hoteles)

    años = sorted(df["fecha"].dt.year.unique())
    año_sel = st.selectbox("📅 Año", años)
    mes_sel = st.selectbox("📆 Mes", list(range(1, 13)), format_func=lambda m: f"{m:02d}")

    resumen = obtener_resumen_mensual(df, hotel_sel, mes_sel, año_sel)

    if resumen:
        st.markdown(f"### 📊 Informe para **{hotel_sel}** en **{resumen['periodo']}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌿 Sostenibilidad Score", resumen["score"])
            st.write(f"📆 Reservas del mes: **{resumen['reservas']}**")
            st.write(f"♻️ Reciclaje: **{resumen['reciclaje']}%**")

        with col2:
            st.write(f"⚡ Energía Total Consumida: **{resumen['energia']} kWh**")
            st.write(f"🗑️ Residuos Generados: **{resumen['residuos']} kg**")
            st.write(f"💧 Uso de Agua: **{resumen['agua']} m³**")

        meses_dict = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo",
                    6: "Junio", 7: "Julio",8: "Agosto",9: "Septiembre",10: "Octubre",11: "Noviembre",12: "Diciembre"}

        st.markdown(f"### Previsión de Reservas para **{hotel_sel}** en **{meses_dict[mes_sel]}**")
        ocupacion_semanal(df, hotel_sel, mes_sel)
        
    else:
        st.warning("No hay datos para ese hotel y mes.")


    st.markdown("---")
    if st.button("🏠 Volver al inicio"):
        change_page_func("home")
