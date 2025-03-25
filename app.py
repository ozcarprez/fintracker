import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FinTracker", layout="centered")
st.title("📊 FinTracker - Asistente de Operaciones")

st.markdown("""
Sube un archivo de Excel con los datos de tus operaciones para poder hacerle preguntas como:
- ¿Qué porcentaje se adelantó en la referencia 00056?
- ¿Qué día se hizo el adelanto?
- ¿Cuál fue el balance enviado?
""")

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Mostrar preview de la tabla
    st.subheader("Vista previa de la tabla")
    st.dataframe(df.head())

    pregunta = st.text_input("🤖 Escribe tu pregunta sobre una referencia específica")

    if pregunta:
        ref_col = "REFERENCE_NUMBER"
        if ref_col not in df.columns:
            st.error("No se encontró la columna de referencia en el archivo.")
        else:
            # Extraer la referencia mencionada en la pregunta
            import re
            match = re.search(r"\\b(\\d{3,5})\\b", pregunta)
            if match:
                ref = match.group(1)
                fila = df[df[ref_col] == ref]

                if fila.empty:
                    st.warning(f"No encontré la referencia {ref} en el archivo.")
                else:
                    fila = fila.iloc[0]
                    respuesta = ""

                    if "porcentaje" in pregunta or "adelantó" in pregunta:
                        porcentaje = fila.get("ADVANCED_PERCENTAGE", "Dato no disponible")
                        cantidad = fila.get("TOTAL_ADVANCE_AMOUNT", "Dato no disponible")
                        fecha = fila.get("DATE_SHIPMENT_ADVANCED", "Dato no disponible")
                        respuesta = f"Se adelantó el {porcentaje*100:.2f}% de la factura, equivalente a ${cantidad}, el día {fecha}."

                    elif "balance" in pregunta:
                        balance = fila.get("LIQUIDATION_BALANCE_RETURNED", "Dato no disponible")
                        respuesta = f"El balance enviado fue de ${balance}."

                    elif "vencimiento" in pregunta or "vence" in pregunta:
                        fecha_venc = fila.get("COLLECTION_DUE_ON", None)
                        if fecha_venc:
                            fecha_venc = pd.to_datetime(fecha_venc, dayfirst=True)
                            hoy = datetime.today()
                            dias = (hoy - fecha_venc).days
                            if dias > 0:
                                respuesta = f"El pago venció el {fecha_venc.strftime('%d/%m/%Y')} y tiene {dias} días de atraso."
                            else:
                                respuesta = f"El pago vence el {fecha_venc.strftime('%d/%m/%Y')} y aún no ha vencido."
                        else:
                            respuesta = "No se encontró la fecha de vencimiento."

                    else:
                        respuesta = "Pregunta válida, pero aún no tengo una respuesta preparada para ese tipo de consulta."

                    st.success(respuesta)
            else:
                st.warning("Por favor incluye un número de referencia en tu pregunta.")
