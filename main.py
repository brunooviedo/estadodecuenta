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
        # Leer el archivo Excel y renombrar columnas
        df = pd.read_excel(archivo_excel, skiprows=17, usecols="B:L", names=['Fecha', 'Columna2', 'Descripcion', 'Ciudad', 'Cuotas', 'Monto ($)'])

        # Renombrar las columnas según las especificaciones y seleccionar solo las necesarias
        df = df.rename(columns={'Columna2': 'Fecha'})
        df = df[['Fecha', 'Descripcion', 'Ciudad', 'Cuotas']]

        # Mostrar los nombres de las columnas para verificar la estructura del archivo
        st.write("Nombres de las columnas:")
        st.write(df.columns)

        # Mostrar las primeras filas para verificar la estructura del archivo
        st.write("Estructura del archivo:")
        st.write(df.head())

        # Verificar la presencia de NaN en el DataFrame
        st.write("Valores NaN en el DataFrame:")
        st.write(df.isnull().sum())

        # Continuar con el procesamiento si no hay errores hasta aquí
        if 'Monto' in df.columns:
            # Dividir los montos en cuotas antes de sumarlos
            def sumar_montos_cuotas(row):
                monto = row['Monto']
                if pd.isna(monto):  # Manejar casos donde el monto es NaN
                    return 0
                cuotas = row['Cuotas']
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
            gastos_frecuentes = df[df['Monto'] < 0].groupby('Descripcion')['Monto'].count().reset_index()
            gastos_frecuentes = gastos_frecuentes.rename(columns={'Monto': 'Cantidad'})

            # Ordenar por la cantidad de gastos de mayor a menor
            gastos_frecuentes = gastos_frecuentes.sort_values(by='Cantidad', ascending=False)

            # Generar gráfico de barras horizontales de los gastos más frecuentes
            fig_gastos_frecuentes = px.bar(gastos_frecuentes, x='Cantidad', y='Descripcion', orientation='h',
                                           title='Gastos Más Frecuentes', labels={'Descripcion': 'Descripción'})
            st.plotly_chart(fig_gastos_frecuentes)

            # Generar gráfico de pastel con los gastos más frecuentes
            fig_pie_gastos_frecuentes = px.pie(gastos_frecuentes, values='Cantidad', names='Descripcion',
                                               title='Distribución de Gastos Más Frecuentes')
            fig_pie_gastos_frecuentes.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie_gastos_frecuentes)

        else:
            st.warning("La columna 'Monto' no está presente en el DataFrame.")

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')

else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
