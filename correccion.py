import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Corrección de Volumen - DUSA", layout="centered")

# Estilos personalizados para mantener la imagen corporativa
st.markdown("""
    <style>
    .titulo-grande { font-size: 1.8rem; font-weight: bold; color: #2E4053; margin-bottom: 0px; }
    .subtitulo { font-size: 1rem; color: #808B96; margin-bottom: 25px; }
    .resultado-texto { font-size: 16px; font-weight: bold; color: #2E86C1; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<p class="titulo-grande">CORRECCIÓN DE VOLUMEN</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Base de Datos Alcoholimetría - DUSA / Edwin Freitez</p>', unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    # Cargamos el archivo completo usando punto y coma como separador
    df = pd.read_csv("Libro Alcoholimetria Python.csv", sep=";", decimal=",", skiprows=1)
    # Renombramos columnas para estandarizar (Temp, B a K como Grados Ap., Factor)
    cols = ["Temp"] + [str(c) for c in df.columns[1:-1]] + ["Factor"]
    df.columns = cols
    return df

try:
    df_tabla = cargar_datos()

    # Contenedor de entradas
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            temp_user = st.number_input("Temperatura observada (°C):", value=28.0, step=0.5, format="%.1f")
        with col2:
            grado_real_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    if st.button("BUSCAR DATOS EN TABLA", use_container_width=True):
        # 1. Filtramos TODAS las filas que coincidan con la temperatura
        dif_temp = (df_tabla['Temp'] - temp_user).abs()
        temp_mas_cercana = df_tabla.loc[dif_temp.idxmin(), 'Temp']
        filas_temp = df_tabla[df_tabla['Temp'] == temp_mas_cercana]

        # 2. Buscamos el grado real más cercano en toda la sub-tabla de esa temperatura
        matriz_grados = filas_temp.iloc[:, 1:-1].astype(float)
        distancia = (matriz_grados - grado_real_user).abs()
        
        # Encontramos la posición exacta del valor mínimo de diferencia
        valor_minimo = distancia.stack().min()
        posicion = distancia.stack()[distancia.stack() == valor_minimo].index[0]
        
        fila_id = posicion[0]    # Índice de la fila en el dataframe original
        grado_ap_col = posicion[1] # Nombre de la columna (Grado Aparente)

        # 3. Obtenemos los valores finales
        grado_aparente = grado_ap_col
        factor_v20 = df_tabla.loc[fila_id, 'Factor']

        # Mostrar Resultados con estilo
        st.markdown('<p class="resultado-texto">RESULTADOS:</p>', unsafe_allow_html=True)
        
        res1, res2 = st.columns(2)
        res1.metric("Grado Aparente", f"{grado_aparente} °GL")
        res2.metric("Factor (V20)", f"{factor_v20}")
        
        st.caption(f"Datos basados en la temperatura de {temp_mas_cercana} °C encontrada en tablas.")

except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.info("Asegúrate de que el archivo CSV se llame exactamente: Libro Alcoholimetria Python.csv")
