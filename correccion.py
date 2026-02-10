import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Buscador Alcoholimetría DUSA", layout="centered")

@st.cache_data
def cargar_datos_limpios():
    # Cargamos tu Excel. Si es el CSV, cambia pd.read_excel por pd.read_csv
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx")
    
    # Nos aseguramos de que Python trate todo como número (punto decimal)
    def a_numero(x):
        try:
            return float(str(x).replace(',', '.'))
        except:
            return np.nan

    df_num = df.map(a_numero)
    return df_num

try:
    df = cargar_datos_limpios()
    
    st.title("Corrección de Volumen DUSA")
    st.info("Buscando en base de datos limpia (A: Temperatura, B-K: Grados, L: Factor)")

    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5, format="%.1f")
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    # La tolerancia la dejamos interna para que no falle (0.05 es ideal)
    tolerancia = 0.05

    if st.button("CALCULAR AHORA", use_container_width=True):
        # 1. Buscamos todas las filas donde la temperatura sea la que pusiste
        # Usamos un pequeño margen para la temperatura por si hay decimales invisibles
        bloque_temp = df[ (df.iloc[:, 0] - t_user).abs() < 0.1 ]

        if not bloque_temp.empty:
            # 2. En ese bloque, buscamos el Grado Real más cercano en las columnas B a K (1 a 10)
            matriz_grados = bloque_temp.iloc[:, 1:11]
            
            # Calculamos la distancia al valor buscado
            distancias = (matriz_grados - g_user).abs()
            min_error = distancias.min().min()

            if min_error <= tolerancia:
                # 3. Localizamos la celda exacta
                # Obtenemos la columna y la fila del valor más cercano
                col_nombre = distancias.min(axis=0).idxmin()
                fila_idx = distancias[col_nombre].idxmin()

                # 4. Resultados finales
                # Grado aparente: Es el nombre de la columna donde se encontró
                # Factor: Es el valor de la columna 11 (L) en esa misma fila
                grado_aparente = col_nombre
                factor_v20 = df.iloc[fila_idx, 11]

                st.markdown("---")
                c1, c2 = st.columns(2)
                c1.metric("Grado Aparente", f"{grado_aparente} °GL")
                c2.metric("Factor (V20)", f"{factor_v20}")
                st.success(f"Coincidencia encontrada a {t_user} °C")
            else:
                st.warning(f"No se encontró el grado {g_user} en la tabla de {t_user}°C (Error: {min_error:.3f})")
        else:
            st.error(f"La temperatura {t_user}°C no existe en la base de datos.")

except Exception as e:
    st.error(f"Error en la base de datos: {e}")




