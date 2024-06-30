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

        # Crear un DataFrame para el gráfico de barras con los índices adecuados
        df['Descripcion'] = df.iloc[:, 4]  # Columna E (índice 4)
        df['Color'] = ['blue' if x > 0 else 'red' for x in df['Monto']]

        # Añadir hover text personalizado con la columna 4 y la columna 10
        df['Hover'] = df.apply(lambda row: f'Info Columna 4: {row.iloc[4]}<br>Gasto: ${row.iloc[10]:.2f}', axis=1)

        # Generar gráfico de barras con colores asignados
        fig = px.bar(df, x='Descripcion', y='Monto', title='Gastos por Transacción', color='Color', text='Hover')
        fig.update_traces(hovertemplate='%{text}')
        st.plotly_chart(fig)

        # Filtrar los gastos del DataFrame
        df_gastos = df[df['Monto'] < 0].copy()
        df_gastos['Porcentaje'] = (df_gastos['Monto'] / suma_gastos.abs()) * 100

        # Generar gráfico de pastel
        fig_pie = px.pie(df_gastos, values='Monto', names='Descripcion', title='Distribución de Gastos',
                         hover_data=['Porcentaje'], labels={'Monto': 'Monto (CLP)'})
        fig_pie.update_traces(textinfo='percent+label', hovertemplate='Gasto: %{value:.2f}<br>Porcentaje: %{percent:.2%}')
        st.plotly_chart(fig_pie)

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')
else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
