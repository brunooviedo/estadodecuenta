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

        # Función para obtener el cupo total desde las celdas combinadas H15:L15
        def obtener_cupo_total(df):
            try:
                # Unir el contenido de las celdas combinadas
                cupo_total = ' '.join(str(df.iloc[14, col]) for col in range(7, 12))
                return cupo_total
            except Exception as e:
                st.error(f'Error al obtener el cupo total: {e}')
                return None

        # Obtener el cupo total, cupo utilizado y cupo disponible
        cupo_total = obtener_cupo_total(df)  # Llamada a la función para obtener el cupo total
        cupo_utilizado = df.iloc[14, 4]  # Columna E15
        cupo_disponible = df.iloc[14, 1]  # Columna B15

        # Mostrar información del cupo de la tarjeta de crédito
        st.subheader('Cupo de la Tarjeta de Crédito')
        st.write(f'Cupo Total: {cupo_total}')
        st.write(f'Cupo Utilizado: {cupo_utilizado}')
        st.write(f'Cupo Disponible: {cupo_disponible}')

        # Filtrar y sumar los montos correspondientes a pagos de 1 cuota (columna H contiene "01/01")
        if 'Fecha' in df.columns:
            df_filt = df[df['Fecha'].astype(str).str.contains('01/01', na=False)]
        else:
            st.warning('No se encontró la columna "Fecha" en el archivo.')

        # Dividir los montos en cuotas antes de sumarlos
        def sumar_montos_cuotas(row):
            monto = row.iloc[10]  # Columna K
            cuotas = int(row.iloc[7].split('/')[1])  # Columna H
            return monto / cuotas

        df_filt['Monto'] = df_filt.apply(sumar_montos_cuotas, axis=1)

        # Obtener la columna de montos filtrada
        montos = df_filt['Monto']

        # Filtrar y sumar los montos positivos y registrar los negativos como abonos o reversos
        suma_positivos = montos[montos > 0].sum()
        suma_negativos = montos[montos < 0].sum()

        # Calcular el monto restante disponible
        monto_restante = monto_disponible - suma_positivos

        # Mostrar resultados
        st.subheader('Resultados')
        st.write(f'Suma de montos positivos (pagos de 1 cuota): {suma_positivos:.2f}')

        if suma_negativos != 0:
            st.write(f'Suma de montos negativos (abonos o reversos): {suma_negativos:.2f}')
        else:
            st.write('No se encontraron montos negativos para registrar como abonos o reversos.')

        # Mostrar el monto restante disponible
        st.subheader('Monto Restante Disponible')
        st.write(f'Monto restante disponible: {monto_restante:.2f}')

        # Generar gráfico de gastos por categoría con Plotly
        if 'Categoria' in df_filt.columns:
            fig = px.bar(df_filt, x='Categoria', y='Monto', title='Gastos por Categoría')
            st.plotly_chart(fig)
        else:
            st.warning('No se encontró la columna de Categoría en el archivo.')

    except Exception as e:
        st.error(f'Ocurrió un error al procesar el archivo: {e}')
        st.write('Asegúrate de que el archivo de Excel esté en el formato correcto y no esté bloqueado o abierto en otra aplicación.')
else:
    st.warning('No se ha cargado ningún archivo de Excel. Por favor, selecciona un archivo válido.')
