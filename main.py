import streamlit as st
import pandas as pd

# Título de la aplicación
st.title('Procesador de Transacciones de Tarjeta de Crédito')

# Agregar campo para ingresar el Sueldo Líquido o Monto Disponible
monto_disponible = st.number_input('Ingrese el Sueldo Líquido o Monto Disponible:', min_value=0.0, step=1.0)

# Cargar archivo de Excel
archivo_excel = st.file_uploader("Cargar archivo Excel", type=["xlsx", "xls"])

if archivo_excel is not None:
    try:
        # Leer el archivo Excel con el motor predeterminado (xlrd)
        df = pd.read_excel(archivo_excel)

        # Mostrar las primeras filas para verificar la estructura del archivo
        st.write("Estructura del archivo:")
        st.write(df.head())

        # Obtener la columna de montos (Columna K, a partir de la fila 19)
        montos = df.iloc[18:, 10]  # Columna K, filas 19 en adelante (indexado desde 0)

        # Filtrar y sumar los montos positivos y registrar los negativos como abonos o reversos
        suma_positivos = montos[montos > 0].sum()
        suma_negativos = montos[montos < 0].sum()

        # Calcular el monto restante disponible
        monto_restante = monto_disponible - suma_positivos

        # Mostrar resultados
        st.subheader('Resultados')
        st.write(f'Suma de montos positivos: {suma_positivos:.2f}')

        if suma_negativos != 0:
            st.write(f'Suma de montos negativos (abonos o reversos): {suma_negativos:.2f}')
        else:
            st.write('No se encontraron montos negativos para registrar como abonos o reversos.')

        # Mostrar el monto restante disponible
        st.subheader('Monto Restante Disponible')
        st.write(f'Monto restante disponible: {monto_restante:.2f}')

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')
else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
