import streamlit as st
import pandas as pd

st.set_page_config(page_title="Corrección de Volumen DUSA", layout="centered")

@st.cache_data
def cargar_base_completa():
    # Cargamos el Excel
    df = pd.read_excel("Libro Alcoholimetria Python.xlsx", header=None)
    
    # Función interna para limpiar comas y convertir a número
    def limpiar_numero(valor):
        if pd.isna(valor): return None
        try:
            # Si es texto y tiene coma, la cambiamos por punto
            val_str = str(valor).replace(',', '.')
            return float(val_str)
        except:
            return None

    # Aplicamos la limpieza a todo el DataFrame
    df_limpio = df.applymap(limpiar_numero)
    return df_limpio, df # Retornamos el limpio para buscar y el original por si acaso

try:
    df_numeric, df_original = cargar_base_completa()
    
    st.title("Buscador de Alcoholimetría DUSA")
    
    col1, col2 = st.columns(2)
    with col1:
        # Forzamos que la entrada también sea tratada con precisión
        t_user = st.number_input("Temperatura (°C):", value=28.0, step=0.5, format="%.1f")
    with col2:
        g_user = st.number_input("Grado Real Leído:", value=96.5, step=0.1, format="%.1f")

    if st.button("CALCULAR CORRECCIÓN"):
        # 1. Buscamos en las columnas de datos (1 a 10)
        matriz_busqueda = df_numeric.iloc[:, 1:11]
        
        # Calculamos la diferencia absoluta
        distancias = (matriz_busqueda - g_user).abs()
        min_global = distancias.min().min()
        
        # Filtramos por ese error mínimo (margen de 0.01 por si acaso)
        if min_global < 0.2:
            # Buscamos las filas que tienen ese valor
            indices_posibles = distancias[distancias.min(axis=1) <= min_global + 0.01].index.tolist()
            
            encontrado = False
            for idx in indices_posibles:
                # Verificamos la temperatura en la columna 0
                temp_fila = df_numeric.iloc[idx, 0]
                
                if temp_fila is not None and abs(temp_fila - t_user) < 0.1:
                    # ¡Bingo! Ahora buscamos el encabezado de esa hoja
                    # Subimos desde idx hasta encontrar la fila de "encabezados" (donde la temp suele ser < 10 o hay salto)
                    cursor = idx
                    while cursor > 0:
                        # Buscamos la fila donde los valores de las columnas 1-10 
                        # son los "Grados Aparentes" (normalmente fila 2 de cada hoja)
                        # Una pista: la temperatura en esa fila suele ser NaN o texto en el original
                        if pd.isna(df_numeric.iloc[cursor-1, 0]):
                            fila_cabecera = cursor
                            break
                        cursor -= 1
                    
                    col_idx = distancias.loc[idx].idxmin()
                    
                    # El grado aparente está en la fila de cabecera, misma columna
                    grado_aparente = df_original.iloc[fila_cabecera, col_idx]
                    # El factor está en la columna 11 (L)
                    factor_correc = df_original.iloc[idx, 11]
                    
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    c1.metric("Grado Aparente", f"{grado_aparente} °GL")
                    c2.metric("Factor (V20)", f"{factor_correc}")
                    st.success(f"Coincidencia encontrada en tabla de {temp_fila} °C")
                    encontrado = True
                    break
            
            if not encontrado:
                st.warning(f"Se encontró el grado {g_user} en el archivo, pero no para la temperatura {t_user}°C.")
        else:
            st.error(f"El grado {g_user} no parece estar en ninguna tabla del archivo.")

except Exception as e:
    st.error(f"Error técnico: {e}")




