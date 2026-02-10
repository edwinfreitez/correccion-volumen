import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Corrección de Volumen - DUSA", layout="centered")

# Estilos personalizados (manteniendo tu línea de diseño)
st.markdown("""
    <style>
    .titulo-grande { font-size: 1.5rem; font-weight: bold; color: #2E4053; margin-bottom: 0px; }
    .subtitulo { font-size: 1rem; color: #808B96; margin-bottom: 20px; }
    .resultado-label { font-size: 16px; font-weight: bold; color: #2E86C1; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<p class="titulo-grande">CORRECCIÓN DE VOLUMEN</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Base de Datos Alcoholimetría - DUSA</p>', unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    # Cargamos omitiendo la primera fila de títulos y usando la segunda como encabezado de Grado Aparente
    df = pd.read_csv("Libro Alcoholimetria Python.csv", sep=";", decimal=",", skiprows=1)
    # Renombramos la primera columna a 'Temp' y la última a 'Factor'
    cols = list(df.columns)
    cols[0] = "Temp"
    cols[-1] = "Factor"
    df.columns = cols
    return df

try:
    df_tabla = cargar_datos()

    # Entradas de usuario
    col1, col2 = st.columns(2)
    with col1:
        temp_user = st.number_input("Temperatura observada (°C):", value=20.0, step=0.5, format="%.1f")
    with col2:
        grado_real_user = st.number_input("Grado Real deseado:", value=5.50, step=0.01, format="%.2f")

    if st.button("BUSCAR DATOS EN TABLA", use_container_width=True):
        # 1. Encontrar la fila de temperatura más cercana
        dif_temp = (df_tabla['Temp'] - temp_user).abs()
        idx_fila = dif_temp.idxmin()
        fila = df_tabla.loc[idx_fila]

        # 2. Buscar el Grado Real más cercano en esa fila (columnas B a K)
        # Excluimos la primera (Temp) y la última (Factor)
        solo_grados = fila.iloc[1:-1].astype(float)
        dif_grado = (solo_grados - grado_real_user).abs()
        col_ganadora = dif_grado.idxmin() # Esto nos da el Grado Aparente (nombre de la columna)
        
        valor_encontrado = fila[col_ganadora]
        factor_encontrado = fila['Factor']

        # Mostrar Resultados
        st.markdown('<p class="resultado-label">Resultados encontrados:</p>', unsafe_allow_html=True)
        
        res1, res2 = st.columns(2)
        res1.metric("Grado Aparente", f"{col_ganadora} °GL")
        res2.metric("Factor (V20)", f"{factor_encontrado}")
        
        st.info(f"Dato obtenido para la temperatura más cercana: {fila['Temp']} °C")

except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'Libro Alcoholimetria Python.csv'. Asegúrate de que esté en la misma carpeta.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar los datos: {e}")