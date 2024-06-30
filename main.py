import streamlit as st
import pandas as pd
import plotly.express as px
import locale

# Configurar la localización para formateo de números
locale.setlocale(locale.LC_ALL, '')  # Utiliza la configuración regional del sistema

# Título de la aplicación
st.title('Procesador de Transacciones de Tarjeta de Crédito')

# Agregar campo para ingresar el Sueldo Líquido o Monto Disponible
monto_disponible = st.number_input('Ingrese el Sueldo Líquido o Monto Disponible:', min_value=0.0, step=1.0)

# Cargar archivo de Excel
archivo_excel = st.file_uploader("Cargar archivo Excel", type=["xlsx", "xls"])

if archivo_excel is not None:
    try:
        # Leer el archivo Excel y renombrar columnas si es necesario
        df = pd.read_excel(archivo_excel, skiprows=17, usecols="B:K")
        df = df.rename(columns={df.columns[9]: 'Monto'})

        # Seleccionar solo las columnas necesarias y renombrar según corresponda
        df = df[['Fecha', 'Tipo de Tarjeta ', 'Descripción', 'Ciudad', 'Cuotas', 'Monto']]

        # Mostrar las primeras filas para verificar la estructura del archivo
        st.write("Estructura del archivo:")
        st.write(df.head())

        # Continuar con el procesamiento si no hay errores hasta aquí
        if 'Monto' in df.columns:
            # Convertir la columna 'Cuotas' a numérica
            def convertir_cuotas(cuotas):
                if isinstance(cuotas, str) and '/' in cuotas:
                    partes = cuotas.split('/')
                    try:
                        return int(partes[1])
                    except ValueError:
                        return 1  # Si no se puede convertir, asumimos 1 cuota
                elif pd.isna(cuotas):
                    return 1  # Si es NaN, asumimos 1 cuota
                else:
                    return cuotas

            df['Cuotas'] = df['Cuotas'].apply(convertir_cuotas)

            # Dividir los montos en cuotas antes de sumarlos
            def sumar_montos_cuotas(row):
                monto = row['Monto']
                cuotas = row['Cuotas']
                if pd.isna(monto):  # Manejar casos donde el monto es NaN
                    return 0
                if cuotas == 0:  # Evitar división por cero
                    return 0
                monto_primera_cuota = monto / cuotas
                return monto_primera_cuota

            df['Monto'] = df.apply(sumar_montos_cuotas, axis=1)

            # Filtrar y sumar los montos positivos (abonos) y los negativos (gastos)
            abonos = df[df['Monto'] > 0]['Monto'].sum()
            gastos = df[df['Monto'] < 0]['Monto'].sum()

            # Calcular el monto restante disponible
            monto_restante = monto_disponible - abonos

            # Formatear los resultados para mostrarlos en formato de miles y millones
            abonos_formato = locale.format_string('%.2f', abonos, grouping=True)
            gastos_formato = locale.format_string('%.2f', gastos, grouping=True)
            monto_restante_formato = locale.format_string('%.2f', monto_restante, grouping=True)

            # Mostrar resultados formateados
            st.subheader('Resultados')
            st.write(f'Suma de Gastos (Compras) (positivos): ${abonos_formato}')
            st.write(f'Suma de Abonos o Reversos (negativos): ${gastos_formato}')
            st.write(f'Monto restante disponible: ${monto_restante_formato}')

            # Obtener los gastos más frecuentes y sumarizados
            gastos_frecuentes = df[df['Monto'] < 0].groupby('Descripción')['Monto'].count().reset_index()
            gastos_frecuentes = gastos_frecuentes.rename(columns={'Monto': 'Cantidad'})

            # Ordenar por la cantidad de gastos de mayor a menor
            gastos_frecuentes = gastos_frecuentes.sort_values(by='Cantidad', ascending=False)

            # Generar gráfico de barras horizontales de los gastos más frecuentes
            fig_gastos_frecuentes = px.bar(gastos_frecuentes, x='Cantidad', y='Descripción', orientation='h',
                                           title='Gastos Más Frecuentes', labels={'Descripción': 'Descripción'})
            st.plotly_chart(fig_gastos_frecuentes)

            # Generar gráfico de pastel con los gastos más frecuentes
            fig_pie_gastos_frecuentes = px.pie(gastos_frecuentes, values='Cantidad', names='Descripción',
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
