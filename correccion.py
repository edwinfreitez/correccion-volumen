import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Corrección de Volumen DUSA", layout="centered")

@st.cache_data
def cargar_base_completa():
    # 1. Cargamos el Excel sin encabezados para tener control total
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", header=None)
    
    # 2. Función para convertir comas en puntos y texto en números
    def limpiar_valor(x):
        if pd.isna(x): return np.nan
        try:
            # Si es texto "96,5", lo pasa a "96.5" y luego a float
            return float(str(x).replace(',', '.'))
        except:
            return np.nan

    # Usamos .map() en lugar de .applymap() para evitar el error técnico
    df_num = df.map(limpiar_valor)
    return df_num, df

try:
    df_num, df_orig = cargar_base_completa()
    
    st.title("Buscador de Alcoholimetría DUSA")
    
    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5, format="%.1f")
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    if st.button("CALCULAR CORRECCIÓN", use_container_width=True):
        # 1. Buscamos en qué filas la temperatura coincide exactamente
        # Columna 0 es la temperatura
        filas_temp = df_num[df_num[0] == t_user].index.tolist()
        
        mejor_error = 9999
        resultado = None

        # 2. De esas filas, buscamos cuál tiene el grado real más cercano en las cols 1 a 10
        for idx in filas_temp:
            fila_datos = df_num.iloc[idx, 1:11]
            distancias = (fila_datos - g_user).abs()
            min_err_fila = distancias.min()
            
            if min_err_fila < mejor_error:
                mejor_error = min_err_fila
                col_ganadora = distancias.idxmin()
                fila_ganadora = idx
                
                # 3. Para este bloque, buscamos el encabezado (Grado Aparente)
                # Subimos desde la fila encontrada hasta encontrar la fila de títulos de esa hoja
                cursor = fila_ganadora
                while cursor > 0:
                    # En tu Excel, la fila de grados (5.0, 5.1... 99.0) está arriba de la temp 10.0
                    # Detectamos esa fila porque suele tener valores pero la celda de Temp está vacía o tiene "ºC"
                    if pd.isna(df_num.iloc[cursor, 0]) or str(df_orig.iloc[cursor, 0]).strip() == "ºC":
                        fila_cabecera = cursor
                        break
                    cursor -= 1
                
                # Si no encontramos ºC, el encabezado suele estar 2 filas arriba de la temp 10.0 (ajustable)
                # En la mayoría de tus bloques es la fila justo antes de que empiecen los datos
                
                grado_aparente = df_orig.iloc[fila_cabecera, col_ganadora]
                factor_v20 = df_orig.iloc[fila_ganadora, 11] # Columna L
                
                resultado = (grado_aparente, factor_v20)

        # 4. Mostrar Resultados
        if resultado and mejor_error < 0.5: # Si el error es razonable
            st.markdown("---")
            res1, res2 = st.columns(2)
            # Limpiamos el resultado por si viene con comas
            g_ap_limpio = str(resultado[0]).replace(',', '.')
            res1.metric("Grado Aparente", f"{g_ap_limpio} °GL")
            res2.metric("Factor (V20)", f"{resultado[1]}")
            st.success(f"Dato encontrado con éxito.")
        else:
            st.error("No se encontró el Grado Real para esa temperatura en ninguna tabla.")

except Exception as e:
    st.error(f"Error técnico: {e}")




