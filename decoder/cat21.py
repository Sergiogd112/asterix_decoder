import bitstring

def decode_cat21(cat, length, data: bitstring.BitArray):
    """
    Decodifica un mensaje ASTERIX CAT21 basado en la especificación Eurocontrol v2.1.
    """
    if cat != 21:
        raise ValueError("La categoría debe ser 21")

    pos = 0
    decoded = {}
    
    # Decodifica el FSPEC (puede tener múltiples octetos)
    fspec_data = []
    more_fspec = True
    while more_fspec and pos < len(data):
        fspec_bits = data[pos:pos+8]
        fspec_data.extend(fspec_bits[:7])
        more_fspec = fspec_bits[7]
        pos += 8

    # Los FRN (Field Reference Number)
    fspec_map = {
        1: ('Data Source Identification', 2, decode_data_source_id),
        2: ('Target Report Descriptor', 'variable', decode_target_report_descriptor),
        7: ('Position in WGS-84 Co-ordinates High Resolution', 8, decode_wgs84_coords_high_res),
        11: ('Target Address', 3, decode_target_address),
        19: ('Mode 3/A Code', 2, decode_mode3a_code), 
        21: ('Flight Level', 2, decode_flight_level),
        12: ('Time of Message Reception of Position', 3, decode_time_of_reception_position),
        29: ('Target Identification', 6, decode_target_identification),
    }

    # Itera sobre los campos presentes en el mensaje y los decodifica
    for frn, present in enumerate(fspec_data, start=1):
        if present and frn in fspec_map:
            item_name, item_length, decoder_func = fspec_map[frn]
            
            try:
                # Asegura que hay suficientes datos para leer el campo
                if isinstance(item_length, int) and pos + item_length * 8 > len(data):
                    continue # Salta este campo si los datos del paquete están corruptos/incompletos

                if isinstance(item_length, int):
                    item_data = data[pos : pos + item_length * 8]
                    decoded_value, bits_processed = decoder_func(item_data)
                    decoded[item_name] = decoded_value
                    pos += bits_processed
                else: # Campo de longitud variable
                    item_data = data[pos:]
                    decoded_value, bits_processed = decoder_func(item_data)
                    decoded[item_name] = decoded_value
                    pos += bits_processed
            except (ValueError, IndexError):
                # Si un campo falla, es más seguro saltarlo
                if isinstance(item_length, int):
                    pos += item_length * 8
                else: # Si es variable, no podemos continuar con seguridad
                    break
    
    return [], decoded, pos

# --- FUNCIONES DE DECODIFICACIÓN CORREGIDAS ---

def decode_data_source_id(data: bitstring.BitArray):
    sac = data[0:8].uint
    sic = data[8:16].uint
    return {"SAC": sac, "SIC": sic}, 16

def decode_target_report_descriptor(data: bitstring.BitArray):
    val = data[0:8].uint
    atp = (val >> 5) & 0b111
    arc = (val >> 3) & 0b11
    rc = (val >> 2) & 1
    rab = (val >> 1) & 1
    
    atp_map = {0: "24-Bit ICAO address", 1: "Duplicate address", 2: "Surface vehicle address", 3: "Anonymous address"}
    arc_map = {0: "25 ft", 1: "100 ft", 2: "Unknown"}

    decoded = {
        "ATP Description": atp_map.get(atp, "Reserved"),
        "ARC Description": arc_map.get(arc, "Reserved"),
        "RC Description": "Range Check Passed" if rc == 0 else "Range Check Failed",
        "RAB Description": "Report from field monitor" if rab == 1 else "Report from ADS-B transceiver"
    }
    bits_processed = 8
    
    # Manejar octetos de extensión
    if data[7]: bits_processed += 8
    # Se podrían añadir más extensiones si el FX del segundo octeto estuviera activo
    
    return decoded, bits_processed

def decode_wgs84_coords_high_res(data: bitstring.BitArray):
    if len(data) < 64: raise ValueError("Datos insuficientes para coordenadas de alta resolución.")
    lat_raw = data[0:32].int
    lon_raw = data[32:64].int
    
    # Fórmula de escalado estándar de Eurocontrol: LSB = 180 / 2^31
    lat = lat_raw * (180 / 2**31)
    lon = lon_raw * (180 / 2**31)
    
    return {"Latitude (deg)": lat, "Longitude (deg)": lon}, 64

def decode_target_address(data: bitstring.BitArray):
    addr = data.uint
    return {"ICAO Address (hex)": f"{addr:06X}"}, 24

def decode_time_of_reception_position(data: bitstring.BitArray):
    time_val = data.uint / 128.0
    h = int(time_val // 3600) % 24
    m = int((time_val % 3600) // 60)
    s = time_val % 60
    return {
        "Time (s since midnight)": time_val,
        "UTC Time (HH:MM:SS)": f"{h:02d}:{m:02d}:{s:06.3f}"
    }, 24

def decode_mode3a_code(data: bitstring.BitArray):
    val = data.uint
    # Extraer los 12 bits del código squawk y formatearlos en octal
    code = (val & 0x0FFF)
    a = (code >> 9) & 0b111
    b = (code >> 6) & 0b111
    c = (code >> 3) & 0b111
    d = code & 0b111
    return {"Mode-3/A Code": f"{a}{b}{c}{d}"}, 16

def decode_flight_level(data: bitstring.BitArray):
    fl_raw = data.int
    flight_level = fl_raw / 4.0
    flight_level_corrected = flight_level / 10.0

    if -100 < flight_level_corrected < 900: # Rango de FL -1000ft a 90,000ft
        return {
            "Flight Level (FL)": flight_level_corrected,
            "Altitude (ft)": flight_level_corrected * 100
        }, 16
    else:
        return {}, 16 # Devuelve un diccionario vacío si el valor sigue siendo irreal


def decode_target_identification(data: bitstring.BitArray):
    chars = ""
    for i in range(0, 48, 6):
        char_code = data[i:i+6].uint
        # Tabla de caracteres ICAO
        if 1 <= char_code <= 26: chars += chr(char_code + 64)  # A-Z
        elif char_code == 32: chars += " "
        elif 48 <= char_code <= 57: chars += chr(char_code)  # 0-9
    
    return {"Target Identification": chars.strip()}, 48