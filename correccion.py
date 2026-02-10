import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Buscador Alcoholimetría DUSA", layout="centered")

# --- FUNCIONES LÓGICAS DE LA MACRO ---

def redondear05(num):
    """Clon de la función redondear05 de tu VBA"""
    parte_entera = int(num)
    parte_decimal = num - parte_entera
    if parte_decimal < 0.25:
        return float(parte_entera)
    elif parte_decimal < 0.75:
        return float(parte_entera + 0.5)
    else:
        return float(parte_entera + 1)

@st.cache_data
def cargar_datos_maestros():
    # Cargamos el Excel completo
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", header=None)
    
    # Limpieza de comas a puntos para que Python entienda los números
    def limpia(x):
        if pd.isna(x): return np.nan
        try:
            return float(str(x).replace(',', '.'))
        except:
            return np.nan

    df_num = df.map(limpia)
    return df_num, df

# --- INTERFAZ ---
st.title("Corrección de Volumen (Lógica Macro)")

try:
    df_num, df_orig = cargar_datos_maestros()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        t_raw = st.number_input("Temp. Usuario (°C):", value=28.0, step=0.1)
    with col2:
        gr_raw = st.number_input("Grado Real Usuario:", value=96.5, step=0.01)
    with col3:
        tolerancia = st.number_input("Tolerancia:", value=0.02, step=0.01, format="%.2f")

    if st.button("BUSCAR FACTOR (VBA STYLE)", use_container_width=True):
        # Aplicamos el redondeo de la macro
        temp_buscada = redondear05(t_raw)
        
        # 1. Filtrar filas por la temperatura redondeada (Columna A / Índice 0)
        filas_temp = df_num[df_num[0] == temp_buscada].index.tolist()
        
        encontrado = False
        for idx in filas_temp:
            # 2. Buscar el Grado Real en las columnas B a K (índices 1 a 10)
            fila_datos = df_num.iloc[idx, 1:11]
            
            # Aplicamos la lógica de tolerancia de la macro: Abs(celda - buscado) < tolerancia
            coincidencias = (fila_datos - gr_raw).abs() < tolerancia
            
            if coincidencias.any():
                col_idx = coincidencias.idxmax() # Obtiene la primera columna que cumple
                
                # 3. Obtener Grado Aparente (Buscando el encabezado del bloque)
                # Subimos desde la fila actual hasta encontrar la fila de "Grados Aparentes"
                cursor = idx
                while cursor > 0:
                    # En la macro la cabecera suele estar en la fila 5 del bloque
                    # Aquí buscamos la fila que tiene los títulos (5.0, 5.1...)
                    # Se reconoce porque la celda de temp (col 0) está vacía o dice "ºC"
                    if pd.isna(df_num.iloc[cursor, 0]) or str(df_orig.iloc[cursor, 0]).strip() == "ºC":
                        fila_cabecera = cursor
                        break
                    cursor -= 1
                
                grado_aparente = df_orig.iloc[fila_cabecera, col_idx]
                factor_v20 = df_orig.iloc[idx, 11] # Columna L (Índice 11)
                
                # Mostrar resultados igual que la macro
                st.markdown("---")
                st.subheader("Resultados:")
                c1, c2 = st.columns(2)
                c1.metric("Grado Aparente", f"{grado_aparente} °GL")
                c2.metric("Factor (V20)", f"{factor_v20}")
                
                st.info(f"Temp. ajustada a: {temp_buscada} °C | Tolerancia aplicada: {tolerancia}")
                encontrado = True
                break
        
        if not encontrado:
            st.warning(f"No se encontró el valor {gr_raw} para la temperatura {temp_buscada} °C con la tolerancia actual.")

except Exception as e:
    st.error(f"Error técnico: {e}")




