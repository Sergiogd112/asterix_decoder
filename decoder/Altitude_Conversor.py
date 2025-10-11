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
