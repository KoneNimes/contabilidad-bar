
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Gestión Contable Bar", layout="centered")

st.title("📊 Contabilidad del Bar")

# Inicializar datos en sesión si no existen
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=["Fecha", "Tipo", "Categoría", "Método", "Concepto", "Monto (€)"])

CATEGORIAS_INGRESO = ["Caja del día", "Ventas Eventos", "Otros Ingresos"]
CATEGORIAS_GASTO = ["Proveedores (Bebidas/Comida)", "Suministros (Luz, Agua, Gas)", "Alquiler", "Personal / Salarios", "Mantenimiento / Impuestos", "Otros Gastos"]
METODOS_PAGO = ["Efectivo", "Banco / Tarjeta"]

# --- FORMULARIO DE REGISTRO ---
st.subheader("Registrar Movimiento")
with st.form(key="form_unico_contable", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha = st.date_input("Fecha", datetime.today(), key="f_fecha")
        tipo = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"], key="f_tipo")
    with col_f2:
        metodo = st.selectbox("Método / Cuenta", METODOS_PAGO, key="f_metodo")
        if tipo == "Ingreso":
            categoria = st.selectbox("Categoría", CATEGORIAS_INGRESO, key="f_cat_ingr")
        else:
            categoria = st.selectbox("Categoría", CATEGORIAS_GASTO, key="f_cat_gast")

    concepto = st.text_input("Concepto (ej. Factura Mahou, Panadería, Caja Noche)", key="f_concepto")
    monto = st.number_input("Monto (€)", min_value=0.0, step=0.5, format="%.2f", key="f_monto")
    
    guardar = st.form_submit_button("Guardar Registro")

if guardar:
    if concepto.strip() != "" and monto > 0:
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Tipo": tipo,
            "Categoría": categoria,
            "Método": metodo,
            "Concepto": concepto,
            "Monto (€)": monto
        }])
        st.session_state.datos = pd.concat([st.session_state.datos, nuevo_registro], ignore_index=True)
        st.success("✅ Registro guardado correctamente.")
    else:
        st.warning("⚠️ Ingresa un concepto y un monto mayor a cero.")

# --- FILTROS DE FECHA Y RESUMEN ---
st.divider()
st.subheader("📈 Resumen Financiero")

df = st.session_state.datos

if not df.empty:
    df['Fecha_dt'] = pd.to_datetime(df['Fecha']).dt.date
    hoy = date.today()

    filtro_tiempo = st.radio(
        "Ver datos de:",
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
        total_ingresos = df_filtrado[df_filtrado["Tipo"] == "Ingreso"]["Monto (€)"].sum()
        total_gastos = df_filtrado[df_filtrado["Tipo"] == "Gasto"]["Monto (€)"].sum()
        beneficio = total_ingresos - total_gastos

        efectivo_ingr = df_filtrado[(df_filtrado["Tipo"] == "Ingreso") & (df_filtrado["Método"] == "Efectivo")]["Monto (€)"].sum()
        efectivo_gast = df_filtrado[(df_filtrado["Tipo"] == "Gasto") & (df_filtrado["Método"] == "Efectivo")]["Monto (€)"].sum()
        saldo_efectivo = efectivo_ingr - efectivo_gast

        banco_ingr = df_filtrado[(df_filtrado["Tipo"] == "Ingreso") & (df_filtrado["Método"] == "Banco / Tarjeta")]["Monto (€)"].sum()
        banco_gast = df_filtrado[(df_filtrado["Tipo"] == "Gasto") & (df_filtrado["Método"] == "Banco / Tarjeta")]["Monto (€)"].sum()
        saldo_banco = banco_ingr - banco_gast

        c1, c2, c3 = st.columns(3)
        c1.metric("Ingresos Totales", f"{total_ingresos:.2f} €")
        c2.metric("Gastos Totales", f"{total_gastos:.2f} €")
        c3.metric("Beneficio Neto", f"{beneficio:.2f} €")

        st.markdown("#### 💵 Desglose por Caja / Banco")
        cb1, cb2 = st.columns(2)
        cb1.metric("Saldo en Efectivo (Caja)", f"{saldo_efectivo:.2f} €")
        cb2.metric("Saldo en Banco / Tarjeta", f"{saldo_banco:.2f} €")

        st.subheader("📋 Historial de Registros")
        columnas_mostrar = ["Fecha", "Tipo", "Categoría", "Método", "Concepto", "Monto (€)"]
        st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True)
    else:
        st.info("No hay registros para el período seleccionado.")
else:
    st.info("Aún no hay movimientos registrados.")
