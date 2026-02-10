import streamlit as st
import pandas as pd

st.set_page_config(page_title="Corrección de Volumen DUSA", layout="centered")

# Estilos para que se vea bien
st.markdown("""
    <style>
    .titulo { font-size: 1.8rem; font-weight: bold; color: #2E4053; }
    .resultado { font-size: 20px; color: #2E86C1; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos_excel():
    # Cargamos el Excel. skiprows=1 para saltar la primera fila de título
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", skiprows=1)
    
    # Nos aseguramos de tomar solo las primeras 12 columnas (A hasta L)
    df = df.iloc[:, :12]
    
    # Renombramos para no tener errores con los nombres de las columnas
    # Temp | 10 columnas de Grados Aparentes | Factor
    nuevas_cols = ["Temp"] + [str(df.columns[i]) for i in range(1, 11)] + ["Factor"]
    df.columns = nuevas_cols
    
    # Limpieza: Convertir a número y quitar filas vacías que pueda traer Excel
    df = df.dropna(subset=["Temp"]) 
    return df

try:
    df_tabla = cargar_datos_excel()

    st.markdown('<p class="titulo">BUSCADOR DE ALCOHOLIMETRÍA (EXCEL)</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5, format="%.1f")
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    if st.button("CALCULAR VALORES", use_container_width=True):
        # 1. Filtrar por la temperatura más cercana
        temp_val = df_tabla.iloc[(df_tabla['Temp'] - t_user).abs().argsort()[:1]]['Temp'].values[0]
        bloque_filas = df_tabla[df_tabla['Temp'] == temp_val]

        # 2. Buscar en la matriz de grados (columnas de la 1 a la 10)
        matriz_grados = bloque_filas.iloc[:, 1:11]
        
        # Encontrar la diferencia mínima con el grado real ingresado
        distancias = (matriz_grados - g_user).abs()
        min_error = distancias.min().min()
        
        # Localizar la columna (Grado Aparente) y la fila (para el Factor)
        col_ganadora = distancias.min(axis=0).idxmin()
        fila_idx = distancias[col_ganadora].idxmin()
        
        # 3. Obtener resultados finales
        grado_aparente = col_ganadora
        factor_final = df_tabla.loc[fila_idx, "Factor"]

        # Mostrar resultados
        st.markdown("---")
        st.markdown('<p class="resultado">RESULTADOS:</p>', unsafe_allow_html=True)
        
        res1, res2 = st.columns(2)
        res1.metric("Grado Aparente", f"{grado_aparente} °GL")
        res2.metric("Factor (V20)", f"{factor_final:.3f}")
        
        st.caption(f"Búsqueda exitosa en tabla de {temp_val} °C")

except Exception as e:
    st.error(f"Error al leer el archivo Excel: {e}")
    st.info("Revisa que el archivo se llame: Libro Alcoholimetria Python.xlsx")

