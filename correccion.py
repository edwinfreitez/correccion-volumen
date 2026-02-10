import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="DUSA - Corrección de Volumen", layout="centered")

@st.cache_data
def cargar_y_unificar_decimales():
    # 1. Cargamos el Excel tal cual
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", header=None)
    
    # 2. Función guerrera para limpiar cualquier formato
    def limpiar_a_flotante(valor):
        if pd.isna(valor): return np.nan
        # Convertimos a string, cambiamos coma por punto y tratamos de hacerlo número
        try:
            val_limpio = str(valor).replace(',', '.').strip()
            return float(val_limpio)
        except:
            # Si es una palabra que no es número (ej. "Grado"), devolvemos NaN
            return np.nan

    # Aplicamos la limpieza a todo el documento (Celda por celda)
    # Usamos .map porque .applymap está quedando obsoleto
    df_numerico = df.map(limpiar_a_flotante)
    
    return df_numerico, df

try:
    df_num, df_orig = cargar_y_unificar_decimales()
    
    st.title("Corrección de Volumen DUSA")
    st.markdown("### Lógica de Precisión con Unificación de Decimales")

    col1, col2 = st.columns(2)
    with col1:
        # Aquí Streamlit usa punto por defecto, pero nuestra función ya sabe convertirlo
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5, format="%.1f")
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    if st.button("BUSCAR RESULTADOS", use_container_width=True):
        # 1. Buscamos la fila de temperatura en la COLUMNA 0 (Columna A)
        # Usamos un margen muy pequeño (0.01) para absorber errores de redondeo
        indices_filas = df_num[ (df_num[0] - t_user).abs() < 0.01 ].index.tolist()

        if indices_filas:
            mejor_error = 999
            encontrado = False

            for idx in indices_filas:
                # 2. Escaneamos de la columna 1 a la 10 (B a K) buscando el Grado Real
                fila_grados = df_num.iloc[idx, 1:11]
                distancias = (fila_grados - g_user).abs()
                
                # Si el error es menor a 0.2 (por ejemplo), es nuestra fila
                if distancias.min() < 0.2:
                    error_actual = distancias.min()
                    col_ganadora = distancias.idxmin()
                    
                    # 3. Buscamos el encabezado hacia arriba
                    cursor = idx
                    fila_cabecera = -1
                    while cursor >= 0:
                        # Buscamos la fila donde la columna de temperatura esté vacía 
                        # Eso indica que es la fila de encabezados del bloque
                        if pd.isna(df_num.iloc[cursor, 0]):
                            fila_cabecera = cursor
                            break
                        cursor -= 1
                    
                    # Si no encontró cabecera vacía, asumimos que está 2 filas arriba (ajuste manual)
                    if fila_cabecera == -1: fila_cabecera = idx - (int(t_user*2) % 60) 

                    grado_aparente = df_orig.iloc[fila_cabecera, col_ganadora]
                    factor_v20 = df_orig.iloc[idx, 11] # Columna L

                    st.markdown("---")
                    res1, res2 = st.columns(2)
                    res1.metric("Grado Aparente", f"{grado_aparente} °GL")
                    res2.metric("Factor (V20)", f"{factor_v20}")
                    st.success(f"Dato localizado exitosamente.")
                    encontrado = True
                    break
            
            if not encontrado:
                st.warning(f"Se encontró la temperatura {t_user}, pero el grado {g_user} no aparece en esas tablas.")
        else:
            # Si llegamos aquí es que ni convirtiendo comas encontramos el 28.0
            st.error(f"No se encontró el valor {t_user} en la columna A. Verifique que la temperatura esté en la primera columna del Excel.")

except Exception as e:
    st.error(f"Error en el proceso: {e}")




