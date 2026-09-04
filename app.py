import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Gestión Contable Bar Nimes", layout="centered")

st.title("📊 Contabilidad Bar Nimes")

# Listas de conceptos específicos facilitadas por el usuario
CONCEPTOS_GASTO = [
    "Alquiler local bar Nimes",
    "Cafe Durbán",
    "Cervezas Discema",
    "Luz electrica energy",
    "Seguridad verisure SECURITAS",
    "Fibra Internet Digi",
    "Bolsas",
    "Bazar chino",
    "Mercadona",
    "Consum",
    "Makro",
    "Seguros Allianz",
    "Fumigación",
    "Gastos varios",
    "Sueldo de Yuli",
    "Sueldo de Tino",
    "Pago de autónomo",
    "Pago de impuestos",
    "Servicios de agua emivasa",
    "Extintores",
    "Carnes Miguel",
    "Ferretería",
    "Otro (especificar)"
]

CONCEPTOS_INGRESO = [
    "Pago en efectivo",
    "Pago en tarjeta",
    "Cuadre de caja efectivo",
    "Cuadre de caja tarjetas",
    "Máquinas de juegos",
    "Ingresos varios",
    "Devolución de impuestos",
    "Otro (especificar)"
]

METODOS_PAGO = ["Efectivo", "Banco / Tarjeta"]

# Configuración de Saldo Inicial en Session State
if 'saldo_inicial' not in st.session_state:
    st.session_state.saldo_inicial = 37448.83

# Inicializar datos en sesión si no existen
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=["Fecha", "Tipo", "Concepto", "Método", "Monto (€)"])

# --- AJUSTE DE SALDO ANTERIOR / INICIAL ---
with st.expander("⚙️ Configuración de Saldo Anterior / Inicial"):
    nuevo_saldo_init = st.number_input(
        "Saldo Anterior Arrastrado (€)",
        value=float(st.session_state.saldo_inicial),
        step=100.0,
        format="%.2f",
        key="f_saldo_init"
    )
    if st.button("Actualizar Saldo Inicial"):
        st.session_state.saldo_inicial = nuevo_saldo_init
        st.success(f"Saldo inicial actualizado a {nuevo_saldo_init:.2f} €")

st.divider()

# --- FORMULARIO DE REGISTRO ---
st.subheader("Registrar Movimiento")
with st.form(key="form_bar_nimes", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha = st.date_input("Fecha", datetime.today(), key="f_fecha")
        tipo = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"], key="f_tipo")
    with col_f2:
        metodo = st.selectbox("Método / Cuenta", METODOS_PAGO, key="f_metodo")
        if tipo == "Ingreso":
            concepto_sel = st.selectbox("Concepto / Proveedor", CONCEPTOS_INGRESO, key="f_con_ing")
        else:
            concepto_sel = st.selectbox("Concepto / Proveedor", CONCEPTOS_GASTO, key="f_con_gas")

    # Si elige 'Otro (especificar)', permite escribir libremente
    concepto_extra = ""
    if concepto_sel == "Otro (especificar)":
        concepto_extra = st.text_input("Especifica el concepto libremente", key="f_extra")

    monto = st.number_input("Monto (€)", min_value=0.0, step=0.5, format="%.2f", key="f_monto")
    
    guardar = st.form_submit_button("Guardar Registro")

if guardar:
    concepto_final = concepto_extra.strip() if concepto_sel == "Otro (especificar)" else concepto_sel
    
    if concepto_final != "" and monto > 0:
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Tipo": tipo,
            "Concepto": concepto_final,
            "Método": metodo,
            "Monto (€)": monto
        }])
        st.session_state.datos = pd.concat([st.session_state.datos, nuevo_registro], ignore_index=True)
        st.success("✅ Registro guardado correctamente.")
    else:
        st.warning("⚠️ Ingresa un concepto válido y un monto mayor a cero.")

# --- FILTROS DE FECHA Y RESUMEN ---
st.divider()
st.subheader("📈 Resumen Financiero")

df = st.session_state.datos

# Cálculo General Incluyendo Saldo Anterior
total_ingresos_historico = df[df["Tipo"] == "Ingreso"]["Monto (€)"].sum() if not df.empty else 0.0
total_gastos_historico = df[df["Tipo"] == "Gasto"]["Monto (€)"].sum() if not df.empty else 0.0
saldo_actual_total = st.session_state.saldo_inicial + total_ingresos_historico - total_gastos_historico

# Métricas Principales globales
m1, m2, m3, m4 = st.columns(4)
m1.metric("Saldo Anterior", f"{st.session_state.saldo_inicial:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
m2.metric("Ingresos Totales", f"{total_ingresos_historico:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
m3.metric("Gastos Totales", f"{total_gastos_historico:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
m4.metric("Saldo Actual Total", f"{saldo_actual_total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

if not df.empty:
    df['Fecha_dt'] = pd.to_datetime(df['Fecha']).dt.date
    hoy = date.today()

    filtro_tiempo = st.radio(
        "Ver desglose del historial por:",
        ["Hoy", "Esta Semana", "Este Mes", "Todo"],
        horizontal=True,
        key="f_radio_periodo"
    )

    if filtro_tiempo == "Hoy":
        df_filtrado = df[df['Fecha_dt'] == hoy]
    elif filtro_tiempo == "Esta Semana":
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        df_filtrado = df[df['Fecha_dt'] >= inicio_semana]
    elif filtro_tiempo == "Este Mes":
        df_filtrado = df[df['Fecha_dt'].apply(lambda x: x.month == hoy.month and x.year == hoy.year)]
    else:
        df_filtrado = df.copy()

    if not df_filtrado.empty:
        ingresos_periodo = df_filtrado[df_filtrado["Tipo"] == "Ingreso"]["Monto (€)"].sum()
        gastos_periodo = df_filtrado[df_filtrado["Tipo"] == "Gasto"]["Monto (€)"].sum()
        beneficio_periodo = ingresos_periodo - gastos_periodo

        st.markdown(f"#### 📅 Desglose del Período ({filtro_tiempo})")
        p1, p2, p3 = st.columns(3)
        p1.metric("Ingresos Período", f"{ingresos_periodo:.2f} €")
        p2.metric("Gastos Período", f"{gastos_periodo:.2f} €")
        p3.metric("Resultado Período", f"{beneficio_periodo:.2f} €")

        st.subheader("📋 Historial de Registros")
        columnas_mostrar = ["Fecha", "Tipo", "Concepto", "Método", "Monto (€)"]
        st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True)
    else:
        st.info("No hay registros guardados para el período seleccionado.")
else:
    st.info("Aún no has registrado ningún movimiento.")
