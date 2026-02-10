import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Corrección de Volumen DUSA", layout="centered")

@st.cache_data
def cargar_base_completa():
    # Cargamos TODO el Excel sin saltar filas para no perder los encabezados de cada bloque
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", header=None)
    return df

try:
    df_raw = cargar_base_completa()
    
    st.title("Buscador de Alcoholimetría DUSA")
    
    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5)
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1)

    if st.button("CALCULAR CORRECCIÓN"):
        # LÓGICA DE HOJAS: El Excel tiene bloques. Cada bloque tiene su propia Fila 2 (Grados Aparentes)
        # Vamos a buscar en qué parte del Excel está el Grado Real que se acerca al usuario
        
        # 1. Convertimos a números para buscar
        matriz_busqueda = df_raw.iloc[:, 1:11].apply(pd.to_numeric, errors='coerce')
        
        # Buscamos la diferencia mínima en TODO el documento
        distancias = (matriz_busqueda - g_user).abs()
        min_global = distancias.min().min()
        
        # 2. Identificamos TODAS las filas donde aparece ese valor o uno muy cercano
        # Pero necesitamos filtrar por la temperatura que pidió el usuario
        filas_posibles = distancias[distancias.min(axis=1) == min_global].index.tolist()
        
        resultado_final = None
        
        for idx in filas_posibles:
            # Verificamos si la temperatura en esa fila (Columna 0) coincide con t_user
            temp_en_fila = pd.to_numeric(df_raw.iloc[idx, 0], errors='coerce')
            
            if abs(temp_en_fila - t_user) < 0.1: # Si la temperatura coincide
                # ¡ENCONTRAMOS LA CELDA! 
                # Ahora subimos para encontrar el encabezado de ese bloque (Fila 2 del bloque)
                # El encabezado suele estar unas filas arriba de donde empieza la temperatura 10.0
                
                # Buscamos hacia arriba la fila que tiene los grados aparentes (ej. 99.0, 99.1...)
                # En tu estructura, es la fila 2 de cada hoja.
                # Como es un solo archivo, buscaremos la fila con "Grado Aparente" más cercana arriba.
                cursor = idx
                while cursor > 0:
                    if "Grado Aparente" in str(df_raw.iloc[cursor, 0]) or "ºC" in str(df_raw.iloc[cursor, 0]):
                        fila_encabezado = cursor + 1 # La fila de los valores (5.0, 5.1...)
                        break
                    cursor -= 1
                
                col_idx = distancias.loc[idx].idxmin()
                
                grado_aparente = df_raw.iloc[fila_encabezado, col_idx]
                factor_correc = df_raw.iloc[idx, 11] # Columna L
                
                resultado_final = (grado_aparente, factor_correc, temp_en_fila)
                break

        if resultado_final:
            st.markdown("---")
            c1, c2 = st.columns(2)
            c1.metric("Grado Aparente", f"{resultado_final[0]} °GL")
            c2.metric("Factor (V20)", f"{resultado_final[1]}")
            st.success(f"Dato localizado en la tabla de {resultado_final[2]} °C")
        else:
            st.warning("No se encontró una coincidencia exacta para esa Temperatura y Grado en las tablas.")

except Exception as e:
    st.error(f"Error de lectura: {e}")



