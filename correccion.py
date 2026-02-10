import streamlit as st
import pandas as pd

st.set_page_config(page_title="Corrección de Volumen DUSA", layout="centered")

@st.cache_data
def cargar_datos_excel():
    # Cargamos el archivo completo
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", skiprows=1)
    df = df.iloc[:, :12]
    
    # Nombres temporales para procesar
    columnas_estandar = ["Temp"] + [f"C{i}" for i in range(1, 11)] + ["Factor"]
    
    # Guardamos los encabezados reales (Grados Aparentes: 5.0, 5.1, etc.)
    nombres_grados = [str(c) for c in df.columns[1:11]]
    
    df.columns = columnas_estandar
    # Limpieza numérica profunda
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df.dropna(subset=["Temp"]), nombres_grados

try:
    df, nombres_grados = cargar_datos_excel()

    st.title("Buscador de Alcoholimetría DUSA")

    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5)
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1)

    if st.button("CALCULAR"):
        # 1. Filtro de Temperatura
        temp_mas_cercana = df.iloc[(df['Temp'] - t_user).abs().argsort()[:1]]['Temp'].values[0]
        bloque_temp = df[df['Temp'] == temp_mas_cercana]

        # 2. LOGICA DE PRECISIÓN:
        # En lugar de buscar en todo el bloque, buscamos la fila 
        # donde la media de los grados coincida con el rango del grado real.
        # Esto evita que salte a la hoja 1 si buscas grado 90.
        matriz = bloque_temp.iloc[:, 1:11]
        
        # Buscamos la fila dentro del bloque de temperatura que contiene el valor más cercano
        # Usamos una búsqueda de valor absoluto en toda la matriz del bloque
        diferencias = (matriz - g_user).abs()
        min_error_bloque = diferencias.min(axis=1).min()
        
        # Encontramos la posición exacta
        posicion = diferencias.stack()[diferencias.stack() == min_error_bloque].index[0]
        fila_id = posicion[0]
        col_id = posicion[1]
        
        # 3. Mapeo de resultados
        idx_col = int(col_id.replace('C', '')) - 1
        grado_ap_final = nombres_grados[idx_col]
        factor_final = df.loc[fila_id, "Factor"]

        # Mostrar Resultados
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Grado Aparente", f"{grado_ap_final} °GL")
        c2.metric("Factor (V20)", f"{factor_final:.3f}")
        
        st.info(f"Validado para Temperatura: {temp_mas_cercana} °C")

except Exception as e:
    st.error(f"Error: {e}")


