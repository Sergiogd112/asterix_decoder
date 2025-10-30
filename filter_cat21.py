import pandas as pd
import sys

# 1. Filtro Geográfico
LAT_MIN = 40.9
LAT_MAX = 41.7
LON_MIN = 1.5
LON_MAX = 2.6

# 2. Archivos
INPUT_FILE = 'cat21.csv'
OUTPUT_FILE = 'cat21_filtered.csv'

def filter_csv():
    """
    Carga el CSV, aplica los filtros de GBS y geográfico y guarda el resultado.
    """
    print(f"Cargando {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{INPUT_FILE}'.")
        print("Asegúrate de ejecutar primero el script 'decoder' para generar este archivo.")
        return
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return

    print(f"Filas originales: {len(df)}")

    # --- Filtro 1: Descartar vehículos en tierra ---
    
    if 'GBS' not in df.columns:
        print("\n[ERROR FATAL]")
        print("La columna 'GBS' no se encuentra en el CSV.")
        print("Asegúrate de haber modificado 'cat21.py' y 'decoder.py' y regenerado el CSV.")
        sys.exit(1) # Salir con código de error
        
    # Aplicar el filtro GBS
    # Mantenemos solo las filas donde GBS es 0 (Ground Bit not set )
    df_filtered = df[df['GBS'] == 0].copy()
    print(f"Filas después del filtro GBS (solo aéreos): {len(df_filtered)}")

    # --- Filtro 2: Filtro Geográfico ---
    # 40.9º N < Latitud < 41.7º N
    # 1.5º E < Longitud < 2.6º E
    
    # Asegurarse de que las columnas de lat/lon sean numéricas
    df_filtered['Latitude (deg)'] = pd.to_numeric(df_filtered['Latitude (deg)'], errors='coerce')
    df_filtered['Longitude (deg)'] = pd.to_numeric(df_filtered['Longitude (deg)'], errors='coerce')
    
    # Eliminar filas donde la conversión a número falló (si las hubiera)
    df_filtered = df_filtered.dropna(subset=['Latitude (deg)', 'Longitude (deg)'])

    # Aplicar el filtro geográfico
    df_filtered = df_filtered[
        (df_filtered['Latitude (deg)'] > LAT_MIN) &
        (df_filtered['Latitude (deg)'] < LAT_MAX) &
        (df_filtered['Longitude (deg)'] > LON_MIN) &
        (df_filtered['Longitude (deg)'] < LON_MAX)
    ]
    print(f"Filas después del filtro geográfico: {len(df_filtered)}")

    # --- Guardar el resultado ---
    df_filtered.to_csv(OUTPUT_FILE, index=False)
    print(f"\n¡Éxito! CSV filtrado guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_csv()