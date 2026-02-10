import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Buscador Alcoholimetría DUSA", layout="centered")

@st.cache_data
def cargar_excel_flexible():
    # Cargamos el archivo completo sin procesar
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", header=None)
    
    # Función para limpiar cualquier valor y convertirlo en número (manejando comas)
    def a_numero(x):
        try:
            if pd.isna(x): return np.nan
            return float(str(x).replace(',', '.'))
        except:
            return np.nan

    # Limpiamos todo el DataFrame celda por celda
    df_num = df.map(a_numero)
    return df_num, df

try:
    df_num, df_orig = cargar_excel_flexible()
    
    st.title("Corrección de Volumen DUSA")

    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5, format="%.1f")
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    if st.button("CALCULAR AHORA", use_container_width=True):
        # 1. Buscamos todas las filas donde la COLUMNA 0 sea igual a la temperatura
        # Usamos un margen de error (0.01) para evitar problemas de precisión decimal
        indices_temp = df_num[ (df_num[0] - t_user).abs() < 0.01 ].index.tolist()

        if indices_temp:
            mejor_error = 999
            resultado = None

            # 2. De esas filas encontradas, buscamos el Grado Real en las columnas 1 a 10
            for idx in indices_temp:
                fila_datos = df_num.iloc[idx, 1:11]
                distancias = (fila_datos - g_user).abs()
                
                if distancias.min() < mejor_error:
                    mejor_error = distancias.min()
                    col_idx = distancias.idxmin()
                    fila_idx = idx
                    
                    # 3. Localizar el encabezado (Grado Aparente)
                    # Subimos desde la fila encontrada hasta hallar la fila de títulos de ese bloque
                    cursor = fila_idx
                    while cursor > 0:
                        # Buscamos la fila que tiene los grados (5.0, 5.1...) 
                        # Se reconoce porque la celda de temperatura (col 0) está vacía o tiene texto como "ºC"
                        val_temp_col = str(df_orig.iloc[cursor, 0]).strip().lower()
                        if pd.isna(df_num.iloc[cursor, 0]) or "º" in val_temp_col or "temp" in val_temp_col:
                            fila_cabecera = cursor
                            break
                        cursor -= 1
                    
                    # En tu base limpia, si no hay "ºC", el encabezado es la fila inmediatamente superior al bloque
                    # Por seguridad, si el bucle no detecta nada, tomamos la fila 1 (donde suelen estar los grados)
                    if 'fila_cabecera' not in locals(): fila_cabecera = 1

                    grado_aparente = df_orig.iloc[fila_cabecera, col_idx]
                    factor_v20 = df_orig.iloc[fila_idx, 11] # Columna L

                    resultado = (grado_aparente, factor_v20)

            if resultado and mejor_error < 0.2:
                st.markdown("---")
                c1, c2 = st.columns(2)
                c1.metric("Grado Aparente", f"{resultado[0]} °GL")
                c2.metric("Factor (V20)", f"{resultado[1]}")
                st.success(f"Encontrado con éxito en la base de datos.")
            else:
                st.warning(f"No se encontró el grado {g_user} para {t_user}°C.")
        else:
            st.error(f"No se encontró ninguna fila con la temperatura {t_user}°C. Revisa el formato de la columna A.")

except Exception as e:
    st.error(f"Ocurrió un error: {e}")




