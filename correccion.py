import streamlit as st
import pandas as pd

st.set_page_config(page_title="Corrección de Volumen - DUSA", layout="centered")

# Estilos visuales
st.markdown("""
    <style>
    .titulo { font-size: 1.8rem; font-weight: bold; color: #2E4053; }
    .azul-dusa { color: #2E86C1; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="titulo">CORRECCIÓN DE VOLUMEN</p>', unsafe_allow_html=True)
st.write("Base de Datos Oficial - Destilerías Unidas S.A.")

@st.cache_data
def cargar_y_limpiar():
    # Cargamos el archivo
    df = pd.read_csv("Libro Alcoholimetria Python.csv", sep=";", decimal=",", skiprows=1)
    
    # Forzar nombres de columnas
    # La primera es Temp, de la 1 a la 10 son Grados Ap., la última es Factor
    nuevos_nombres = ["Temp"] + [str(df.columns[i]) for i in range(1, len(df.columns)-1)] + ["Factor"]
    df.columns = nuevos_nombres
    
    # Convertir todo a numérico por si acaso hay espacios o textos ocultos
    for col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    
    return df

try:
    df = cargar_y_limpiar()

    col1, col2 = st.columns(2)
    with col1:
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5)
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1)

    if st.button("CALCULAR AHORA", use_container_width=True):
        # 1. Filtro estricto por temperatura
        # Buscamos la fila que coincida exactamente o la más cercana
        temp_val = df.iloc[(df['Temp'] - t_user).abs().argsort()[:1]]['Temp'].values[0]
        bloque_temp = df[df['Temp'] == temp_val]

        # 2. Buscar el valor más cercano en el cuerpo de la tabla (Columnas de Grado Aparente)
        # Seleccionamos solo las columnas intermedias
        matriz = bloque_temp.iloc[:, 1:-1]
        
        # Encontramos la diferencia mínima absoluta
        diff = (matriz - g_user).abs()
        min_diff = diff.min().min()
        
        # Localizamos la columna y la fila del valor ganador
        # Buscamos en qué columna está ese valor mínimo
        columna_ganadora = diff.min(axis=0).idxmin()
        # Buscamos en qué fila de ese bloque está el valor
        fila_indice_ganador = diff[columna_ganadora].idxmin()
        
        # 3. Extraer resultados
        grado_aparente = columna_ganadora
        factor_v20 = df.loc[fila_indice_ganador, "Factor"]

        # Mostrar resultados
        st.markdown('<p class="azul-dusa">RESULTADOS ENCONTRADOS:</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Grado Aparente", f"{grado_aparente} °GL")
        c2.metric("Factor (V20)", f"{factor_v20:.3f}")
        
        st.caption(f"Validado con Temperatura: {temp_val} °C")

except Exception as e:
    st.error(f"Error técnico: {e}")

