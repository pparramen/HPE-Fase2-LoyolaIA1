import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ----------- CARGA Y PREPROCESADO ----------- #
@st.cache_data
def cargar_datos():
    df = pd.read_csv("baseDatos/sostenibilidad_ocupacion.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Preprocesado
    df["ocupacion_real"] = df["reservas_confirmadas"] - df["cancelaciones"]
    df["ocupacion_real"] = df["ocupacion_real"].replace(0, 1)

    df["energia_por_persona"] = df["consumo_energia_kwh"] / df["ocupacion_real"]
    df["residuos_por_persona"] = df["residuos_generados_kg"] / df["ocupacion_real"]
    df["agua_por_persona"] = df["uso_agua_m3"] / df["ocupacion_real"]
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
        "reservas": int((datos["reservas_confirmadas"] - datos["cancelaciones"]).sum())
    }

# ----------- INTERFAZ PRINCIPAL ----------- #
def app(change_page_func):
    st.title("🌱 Informe de Sostenibilidad Hotelera")
    st.image("img/sostenibilidad_header.png")

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
            st.write(f"⚡ Energía por huésped: **{resumen['energia']} kWh**")
            st.write(f"🗑️ Residuos por huésped: **{resumen['residuos']} kg**")
            st.write(f"💧 Agua por huésped: **{resumen['agua']} m³**")
    else:
        st.warning("No hay datos para ese hotel y mes.")

    st.markdown("---")
    if st.button("🏠 Volver al inicio"):
        change_page_func("home")
