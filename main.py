import streamlit as st
import pandas as pd
import plotly.express as px

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

        # Filtrar y sumar los montos positivos (abonos) y los negativos (gastos)
        abonos = montos[montos > 0]
        gastos = montos[montos < 0]

        # Calcular el monto restante disponible
        suma_abonos = abonos.sum()
        suma_gastos = gastos.sum()
        monto_restante = monto_disponible - suma_abonos

        # Mostrar resultados formateados
        st.subheader('Resultados')
        st.write(f'Suma de abonos (positivos): ${suma_abonos:.2f}')
        st.write(f'Suma de gastos (negativos): ${suma_gastos:.2f}')
        st.write(f'Monto restante disponible: ${monto_restante:.2f}')

        # Asignar colores a los abonos (azul) y gastos (rojo)
        colors = ['blue' if x > 0 else 'red' for x in df['Monto']]

        # Añadir hover text personalizado con la columna 4 y la columna 10
        hover_text = [f'Info Columna 4: {row.iloc[3]}<br>Gasto: ${row.iloc[10]:.2f}' for index, row in df.iterrows()]

        # Generar gráfico de barras con colores asignados
        fig = px.bar(df, x=df.index, y='Monto', title='Gastos por Transacción', color=colors, text=hover_text)
        fig.update_traces(hovertemplate='%{text}')

        st.plotly_chart(fig)

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')
else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
