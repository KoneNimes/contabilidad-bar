
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestión Contable Bar", layout="centered")

st.title("📊 Contabilidad del Bar")

# Inicializar datos en sesión si no existen
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=["Fecha", "Tipo", "Concepto", "Monto (€)"])

# Formulario de registro
st.subheader("Registrar Movimiento")
with st.form("formulario_contable", clear_on_submit=True):
    fecha = st.date_input("Fecha", datetime.today())
    tipo = st.selectbox("Tipo de Movimiento", ["Ingreso", "Gasto"])
    concepto = st.text_input("Concepto (ej. Caja del día, Proveedores, Bebidas)")
    monto = st.number_input("Monto (€)", min_value=0.0, step=0.5, format="%.2f")
    
    guardar = st.form_submit_button("Guardar Registro")

if guardar:
    if concepto.strip() != "" and monto > 0:
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Tipo": tipo,
            "Concepto": concepto,
            "Monto (€)": monto
        }])
        st.session_state.datos = pd.concat([st.session_state.datos, nuevo_registro], ignore_index=True)
        st.success("✅ Registro guardado correctamente.")
    else:
        st.warning("⚠️ Ingresa un concepto y un monto mayor a cero.")

# Resumen financiero
st.divider()
st.subheader("📈 Resumen")

df = st.session_state.datos
if not df.empty:
    total_ingresos = df[df["Tipo"] == "Ingreso"]["Monto (€)"].sum()
    total_gastos = df[df["Tipo"] == "Gasto"]["Monto (€)"].sum()
    beneficio = total_ingresos - total_gastos

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos", f"{total_ingresos:.2f} €")
    col2.metric("Gastos", f"{total_gastos:.2f} €")
    col3.metric("Beneficio", f"{beneficio:.2f} €")

    st.subheader("📋 Historial de Registros")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aún no hay movimientos registrados hoy.")
