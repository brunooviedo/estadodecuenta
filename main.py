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
        # Leer el archivo Excel
        df = pd.read_excel(archivo_excel, skiprows=18)  # Saltar las primeras 18 filas

        # Mostrar las primeras filas para verificar la estructura del archivo
        st.write("Estructura del archivo:")
        st.write(df.head())

        # Comprobar si hay suficientes filas en el DataFrame
        if df.shape[0] < 19:
            raise ValueError('El archivo no tiene suficientes filas de datos después de la fila 18.')

        # Dividir los montos en cuotas antes de sumarlos
        def sumar_montos_cuotas(row):
            monto = row.iloc[10]  # Columna K
            cuotas = int(row.iloc[7].split('/')[1])  # Columna H
            return monto / cuotas

        df['Monto'] = df.apply(sumar_montos_cuotas, axis=1)

        # Filtrar y sumar los montos positivos (abonos) y los negativos (gastos)
        abonos = df[df['Monto'] > 0]['Monto']
        gastos = df[df['Monto'] < 0]['Monto']

        # Calcular el monto restante disponible
        suma_abonos = abonos.sum()
        suma_gastos = gastos.sum()
        monto_restante = monto_disponible - suma_abonos

        # Mostrar resultados formateados
        st.subheader('Resultados')
        st.write(f'Suma de abonos (positivos): ${suma_abonos:.2f}')
        st.write(f'Suma de gastos (negativos): ${suma_gastos:.2f}')
        st.write(f'Monto restante disponible: ${monto_restante:.2f}')

        # Obtener los gastos más frecuentes y sumarizados
        gastos_frecuentes = df.iloc[19:, [4, 10]].copy()  # Seleccionar columna E (descripción) y K (monto)
        gastos_frecuentes.columns = ['Descripcion', 'Monto']
        gastos_frecuentes['Monto'] = gastos_frecuentes.apply(lambda row: sumar_montos_cuotas(row), axis=1)

        # Filtrar y contar los gastos más frecuentes
        gastos_frecuentes = gastos_frecuentes[gastos_frecuentes['Monto'] < 0]  # Solo gastos (monto negativo)
        gastos_frecuentes['Cantidad'] = gastos_frecuentes.groupby('Descripcion')['Monto'].transform('count')
        gastos_frecuentes = gastos_frecuentes[['Descripcion', 'Cantidad']].drop_duplicates().sort_values(by='Cantidad', ascending=False)

        # Generar gráfico de barras horizontales de los gastos más frecuentes
        fig_gastos_frecuentes = px.bar(gastos_frecuentes, x='Cantidad', y='Descripcion', orientation='h',
                                       title='Gastos Más Frecuentes', labels={'Descripcion': 'Descripción'})
        st.plotly_chart(fig_gastos_frecuentes)

        # Generar gráfico de pastel con los gastos más frecuentes
        fig_pie_gastos_frecuentes = px.pie(gastos_frecuentes, values='Cantidad', names='Descripcion',
                                           title='Distribución de Gastos Más Frecuentes')
        fig_pie_gastos_frecuentes.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie_gastos_frecuentes)

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')
else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
