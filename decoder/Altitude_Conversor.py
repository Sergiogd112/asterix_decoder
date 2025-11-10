import pandas as pd
import numpy as np

# --- Constantes de Corrección ---
QNE_HPA = 1013.25
TRANSITION_ALTITUDE_FT = 6000
FEET_PER_HPA = 30

def qnh_to_qne(qnh_hpa, elevation_ft):
    #Convierte la altitud de QNH a QNE (FL)
    
    # Presión estándar internacional (ISA)
    qne_hpa = 1013.25

    # Diferencia de presión en hPa
    pressure_diff_hpa = qnh_hpa - qne_hpa

    # Ajuste de altitud en pies (aproximadamente 27 pies por hPa)
    altitude_correction_ft = pressure_diff_hpa * 27

    # Altitud de presión en pies
    pressure_altitude_ft = elevation_ft - altitude_correction_ft

    # Convertir a Nivel de Vuelo (FL)
    flight_level = pressure_altitude_ft / 100

    return flight_level

def qnh_to_qfe(qnh_hpa, airport_elevation_ft):

    # Calcula la caída de presión por la elevación del aeropuerto
    pressure_drop_hpa = airport_elevation_ft / 27

    # El QFE es el QNH menos la caída de presión
    qfe_hpa = qnh_hpa - pressure_drop_hpa

    return qfe_hpa

def apply_qnh_correction(df: pd.DataFrame, bp_column_name: str, alt_column_name: str = "Altitude (ft)") -> pd.DataFrame:

    # Altitud real = Altitud indicada + (QNH actual - QNH estándar) * 30 ft
    # Se aplica solo por debajo de la Altitud de Transición (6000 ft).
    
    if bp_column_name not in df.columns:
        # No se encontró BP, simplemente crea la columna duplicada
        df['Altitude_Corrected_ft'] = df.get(alt_column_name)
        return df

    if alt_column_name not in df.columns:
        # No se encontró altitud, no se puede hacer nada
        return df

    # Crear una copia para evitar SettingWithCopyWarning
    df_corrected = df.copy()

    # Convertir altitud y BP a numérico, forzando errores a NaN
    alt = pd.to_numeric(df_corrected[alt_column_name], errors='coerce')
    bps = pd.to_numeric(df_corrected[bp_column_name], errors='coerce')
    
    # Rellenar BP faltantes (NaN) con QNE para que la corrección sea 0
    bps = bps.fillna(QNE_HPA)

    # 1. Calcular la corrección en pies
    correction_ft = (bps - QNE_HPA) * FEET_PER_HPA
    
    # 2. Aplicar la corrección SOLO si la altitud está por debajo de la TA
    # Usamos np.where para la lógica condicional
    df_corrected['Altitude_Corrected_ft'] = np.where(
        (alt < TRANSITION_ALTITUDE_FT),
        alt + correction_ft,            # Si es verdadero
        alt                             # Si es falso (usar alt original)
    )
    
    # Redondear para legibilidad
    df_corrected['Altitude_Corrected_ft'] = df_corrected['Altitude_Corrected_ft'].round(2)
    
    return df_corrected