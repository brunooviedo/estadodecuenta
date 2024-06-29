import streamlit as st
import pandas as pd
import plotly.express as px
import locale

# Establecer configuración regional para formato de números
locale.setlocale(locale.LC_ALL, '')

# Título de la aplicación
st.title('Procesador de Transacciones de Tarjeta de Crédito')

# Agregar campo para ingresar el Sueldo Líquido o Monto Disponible
monto_disponible = st.number_input('Ingrese el Sueldo Líquido o Monto Disponible:', min_value=0.0, step=1.0)

# Cargar archivo de Excel
archivo_excel = st.file_uploader("Cargar archivo Excel", type=["xlsx", "xls"])

if archivo_excel is not None:
    try:
        # Leer el archivo Excel con el motor predeterminado (xlrd)
        df = pd.read_excel(archivo_excel, skiprows=18)  # Saltar las primeras 18 filas

        # Mostrar las primeras filas para verificar la estructura del archivo
        st.write("Estructura del archivo:")
        st.write(df.head())

        # Dividir los montos en cuotas antes de sumarlos
        def sumar_montos_cuotas(row):
            monto = row.iloc[10]  # Columna K
            cuotas = int(row.iloc[7].split('/')[1])  # Columna H
            return monto / cuotas

        df['Monto'] = df.apply(sumar_montos_cuotas, axis=1)

        # Obtener la columna de montos
        montos = df['Monto']

        # Filtrar y sumar los montos positivos y registrar los negativos como abonos o reversos
        suma_positivos = montos[montos > 0].sum()
        suma_negativos = montos[montos < 0].sum()

        # Calcular el monto restante disponible
        monto_restante = monto_disponible - suma_positivos

        # Mostrar resultados formateados en miles y millones
        st.subheader('Resultados')
        st.write(f'Suma de montos positivos (pagos de 1 cuota): {locale.format_string("%.2f", suma_positivos, grouping=True)}')
        if suma_negativos != 0:
            st.write(f'Suma de montos negativos (abonos o reversos): {locale.format_string("%.2f", suma_negativos, grouping=True)}')
        else:
            st.write('No se encontraron montos negativos para registrar como abonos o reversos.')

        # Mostrar el monto restante disponible
        st.subheader('Monto Restante Disponible')
        st.write(f'Monto restante disponible: {locale.format_string("%.2f", monto_restante, grouping=True)}')

        # Generar gráfico de gastos por categoría con Plotly
        if 'Categoria' in df.columns:
            fig = px.bar(df, x='Categoria', y='Monto', title='Gastos por Categoría')
            st.plotly_chart(fig)
        else:
            st.warning('No se encontró la columna de Categoría en el archivo.')

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')
else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
