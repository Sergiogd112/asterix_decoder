import bitstring

# --- Funciones de decodificación de stub ---
# Estas funciones se utilizan para OMITIR campos que están presentes
# pero que no nos interesa decodificar. Devuelven la cantidad
# de bits que deben ser saltados.


def skip_field(octets: int):
    """Genera una función simple para saltar un número fijo de octetos."""
    bits_to_skip = octets * 8

    def skipper(data: bitstring.BitArray):
        if len(data) < bits_to_skip:
            raise ValueError(f"Datos insuficientes para saltar {octets} octetos.")
        return None, bits_to_skip

    return skipper


def skip_variable_fx(data: bitstring.BitArray):
    """Salta un campo de longitud variable terminado por FX."""
    pos = 0
    while True:
        if pos + 8 > len(data):
            raise ValueError("Datos insuficientes para campo variable FX.")
        octet = data[pos : pos + 8]
        pos += 8
        if not octet[7]:  # Comprueba el bit FX (LSB)
            break
    return None, pos


def skip_compound_met_info(data: bitstring.BitArray):
    """Salta el campo compuesto de Met Info (FRN 31)."""
    if len(data) < 8:
        raise ValueError("Datos insuficientes para FSPEC de Met Info.")
    fspec = data[0:8]
    bits_processed = 8
    if fspec[0]:
        bits_processed += 16  # Wind Speed
    if fspec[1]:
        bits_processed += 16  # Wind Direction
    if fspec[2]:
        bits_processed += 16  # Temperature
    if fspec[3]:
        bits_processed += 8  # Turbulence

    if len(data) < bits_processed:
        raise ValueError("Datos insuficientes para campos de Met Info.")

    return None, bits_processed


def skip_compound_trajectory_intent(data: bitstring.BitArray):
    """Salta el campo compuesto de Trajectory Intent (FRN 34)."""
    if len(data) < 8:
        raise ValueError("Datos insuficientes para REP de Trajectory Intent.")
    rep = data[0:8].uint
    bits_processed = 8 + (rep * 15 * 8)  # 1 octeto REP + N * 15 octetos [cite: 1408]

    if len(data) < bits_processed:
        raise ValueError("Datos insuficientes para datos de Trajectory Intent.")

    return None, bits_processed


def skip_repetitive_mode_s_mb(data: bitstring.BitArray):
    """Salta el campo repetitivo Mode S MB Data (FRN 39)."""
    if len(data) < 8:
        raise ValueError("Datos insuficientes para REP de Mode S MB.")
    rep = data[0:8].uint
    bits_processed = 8 + (
        rep * 8 * 8
    )  # 1 octeto REP + N * 8 octetos [cite: 2051, 2052, 2054]

    if len(data) < bits_processed:
        raise ValueError("Datos insuficientes para datos de Mode S MB.")

    return None, bits_processed


# --- Funciones de decodificación ---


def decode_data_source_id(data: bitstring.BitArray):
    """Decodifica SAC/SIC del encabezado del mensaje."""
    if len(data) < 16:
        raise ValueError("Datos insuficientes para Data Source ID.")
    sac = data[0:8].uint
    sic = data[8:16].uint
    return {"SAC": sac, "SIC": sic}, 16


def decode_target_report_descriptor(data: bitstring.BitArray):
    """Obtiene ATP/ARC/RC/RAB y bits GBS de la descriptor FRN 2."""
    if len(data) < 8:
        raise ValueError("Datos insuficientes para Target Report Descriptor.")
    val = data[0:8].uint
    atp = (val >> 5) & 0b111
    arc = (val >> 3) & 0b11
    rc = (val >> 2) & 1
    rab = (val >> 1) & 1
    fx = data[7]

    atp_map = {
        0: "24-Bit ICAO address",
        1: "Duplicate address",
        2: "Surface vehicle address",
        3: "Anonymous address",
    }
    arc_map = {0: "25 ft", 1: "100 ft", 2: "Unknown", 3: "invalid"}

    decoded = {
        "ATP Description": atp_map.get(atp, "Reserved"),
        "ARC Description": arc_map.get(arc, "Reserved"),
        "RC Description": "Range Check Passed" if rc == 0 else "Range Check Failed",
        "RAB Description": (
            "Report from field monitor" if rab == 1 else "Report from ADS-B transceiver"
        ),
        "GBS": 0,
    }
    bits_processed = 8

    # Octetos de extensión
    if fx:
        decoded["GBS"] = data[bits_processed + 2]
        fx = data[bits_processed + 7]
        bits_processed += 8
        # Avanza el puntero por todas las extensiones FX
        while fx:
            if len(data) < (bits_processed + 8):
                raise ValueError(
                    "Datos insuficientes para extensión de Target Report Descriptor."
                )
            fx = data[bits_processed + 7]
            bits_processed += 8

    return decoded, bits_processed


def decode_wgs84_coords_high_res(data: bitstring.BitArray):
    """Convierte coordenadas WGS-84 de 32 bits en grados lat/lon."""
    if len(data) < 64:
        raise ValueError("Datos insuficientes para coordenadas de alta resolución.")
    lat_raw = data[0:32].int
    lon_raw = data[32:64].int
    lsb = 180 / (2**30)
    lat = lat_raw * lsb
    lon = lon_raw * lsb
    return {"Latitude (deg)": lat, "Longitude (deg)": lon}, 64


def decode_target_address(data: bitstring.BitArray):
    """Lee la dirección ICAO de 24 bits y la devuelve en hexadecimal."""
    if len(data) < 24:
        raise ValueError("Datos insuficientes para Target Address.")
    addr = data[0:24].uint
    return {"ICAO Address (hex)": f"{addr:06X}"}, 24


def decode_time_of_reception_position(data: bitstring.BitArray):
    """Convierte un sello temporal de 24 bits en segundos y string HH:MM:SS."""
    if len(data) < 24:
        raise ValueError("Datos insuficientes para Time of Reception Position.")
    time_val = data[0:24].uint / 128.0
    h = int(time_val // 3600) % 24
    m = int((time_val % 3600) // 60)
    s = time_val % 60
    return {
        "Time (s since midnight)": time_val,
        "UTC Time (HH:MM:SS)": f"{h:02d}:{m:02d}:{s:06.3f}",
    }, 24


def decode_mode3a_code(data: bitstring.BitArray):
    """Decodifica el código intermitente Mode 3/A en formato ABCD."""
    if len(data) < 16:
        raise ValueError("Datos insuficientes para Mode 3/A Code.")
    val = data[0:16].uint
    code = val & 0x0FFF
    a = (code >> 9) & 0b111
    b = (code >> 6) & 0b111
    c = (code >> 3) & 0b111
    d = code & 0b111
    return {"Mode-3/A Code": f"{a}{b}{c}{d}"}, 16


def decode_flight_level(data: bitstring.BitArray):
    """Calcula Flight Level y altitudes barométricas derivadas."""
    if len(data) < 16:
        raise ValueError("Datos insuficientes para Flight Level.")
    fl_raw = data[0:16].int
    flight_level = fl_raw / 4
    flight_level_corrected = (
        flight_level  # El pdf v2.1 (I021/145) dice que el LSB es 1/4 FL.
    )

    return {
        "Flight Level (FL)": flight_level_corrected,
        "Altitude (ft)": flight_level_corrected * 100,
        "Altitude (m)": flight_level_corrected * 30.48,
    }, 16


def decode_air_speed(data: bitstring.BitArray):
    """Interpreta IAS/Mach y devuelve la unidad adecuada."""
    if len(data) < 16:
        raise ValueError("Datos insuficientes para Air Speed.")

    # bits 0-1: IM (IAS/Mach)
    im = data[0:2].uint

    # bits 2-15: Air Speed
    air_speed_raw = data[2:16].uint

    decoded = {}
    if im == 0:  # IAS
        # LSB = 1 kt
        decoded["IAS (kt)"] = air_speed_raw * 1
    elif im == 1:  # Mach
        # LSB = 0.001 Mach
        decoded["Mach"] = air_speed_raw * 0.001
    # If im is 2 or 3, it's not valid according to CAT21, so we don't decode.

    return decoded, 16


def decode_magnetic_heading(data: bitstring.BitArray):
    """Convierte el heading magnético codificado en grados."""
    if len(data) < 16:
        raise ValueError("Datos insuficientes para Magnetic Heading.")

    # LSB = 360 / 2^16 deg
    heading_raw = data[0:16].uint
    heading = heading_raw * (360 / 2**16)

    return {"Magnetic Heading (deg)": heading}, 16


def decode_target_status(data: bitstring.BitArray):
    """Mapea los bits de estado (VFI/RAB/GBS/NRM) a cadenas legibles."""
    if len(data) < 8:
        raise ValueError("Datos insuficientes para Target Status.")

    val = data[0:8].uint

    # bits 0-1: VFI (Valid/Invalid)
    vfi = (val >> 6) & 0b11
    vfi_map = {0: "Valid", 1: "Invalid", 2: "Reserved", 3: "Reserved"}

    # bits 2-3: RAB (Reported by ADS-B or RBM)
    rab = (val >> 4) & 0b11
    rab_map = {
        0: "Reported by ADS-B",
        1: "Reported by RBM",
        2: "Reserved",
        3: "Reserved",
    }

    # bits 4-5: GBS (Ground Bit Status)
    gbs = (val >> 2) & 0b11
    gbs_map = {0: "No ground bit", 1: "Ground bit set", 2: "Reserved", 3: "Reserved"}

    # bits 6-7: NRM (Navigation Integrity)
    nrm = val & 0b11
    nrm_map = {0: "Normal", 1: "Degraded", 2: "Reserved", 3: "Reserved"}

    decoded = {
        "Target Status VFI": vfi_map.get(vfi, "Unknown"),
        "Target Status RAB": rab_map.get(rab, "Unknown"),
        "Target Status GBS": gbs_map.get(gbs, "Unknown"),
        "Target Status NRM": nrm_map.get(nrm, "Unknown"),
    }

    return decoded, 8


def decode_airborne_ground_vector(data: bitstring.BitArray):
    """Obtiene velocidad/rumbo en tierra desde FRN 26."""
    if len(data) < 32:
        raise ValueError("Datos insuficientes para Airborne Ground Vector.")

    # bits 0-15: Ground Speed
    ground_speed_raw = data[0:16].uint
    # LSB = 2^-14 NM/s = 1/256 kt (approx)
    # 1 NM/s = 3600 NM/h = 3600 kt
    # So, LSB = (2^-14) * 3600 kt = 0.2197 kt
    # A more common LSB for ground speed is 1/256 NM/s, which is 1/256 * 1852 m/s = 7.23 m/s
    # Let's assume LSB = 1/256 NM/s, and convert to knots
    ground_speed_kts = ground_speed_raw * (2**-14) * 3600  # Convert NM/s to knots

    # bits 16-31: Track Angle
    track_angle_raw = data[16:32].uint
    # LSB = 360 / 2^16 deg
    track_angle = track_angle_raw * (360 / 2**16)

    return {
        "Ground Speed (kts)": ground_speed_kts,
        "Track Angle (deg)": track_angle,
    }, 32


def decode_target_identification(data: bitstring.BitArray):
    """Convierte el identificador de objetivo codificado en caracteres."""
    if len(data) < 48:
        raise ValueError("Datos insuficientes para Target Identification.")
    chars = ""
    for i in range(0, 48, 6):
        char_code = data[i : i + 6].uint
        if 1 <= char_code <= 26:
            chars += chr(char_code + 64)
        elif char_code == 32:
            chars += " "
        elif 48 <= char_code <= 57:
            chars += chr(char_code)
    return {"Target Identification": chars.strip()}, 48


# --- MAPA UAP COMPLETO ---
# (Nombre, Especificación de Longitud, Función de Decodificación)
# Si la función es un 'skip', el valor decodificado será None.

UAP_MAP = {
    # FRN: (Nombre, Especificación de Longitud, Función)
    1: ("Data Source Identification", "2", decode_data_source_id),
    2: ("Target Report Descriptor", "1+", decode_target_report_descriptor),
    3: ("Track Number", "2", skip_field(2)),
    4: ("Service Identification", "1", skip_field(1)),
    5: ("Time of Applicability for Position", "3", skip_field(3)),
    6: ("Position in WGS-84 Co-ordinates", "6", skip_field(6)),
    7: (
        "Position in WGS-84 Co-ordinates High Resolution",
        "8",
        decode_wgs84_coords_high_res,
    ),
    # -- FX Bit --
    8: ("Time of Applicability for Velocity", "3", skip_field(3)),
    9: ("Air Speed", "2", decode_air_speed),
    10: ("True Air Speed", "2", skip_field(2)),
    11: ("Target Address", "3", decode_target_address),
    12: (
        "Time of Message Reception of Position",
        "3",
        decode_time_of_reception_position,
    ),
    13: ("Time of Message Reception of Position-High Precision", "4", skip_field(4)),
    14: ("Time of Message Reception for Velocity", "3", skip_field(3)),
    # -- FX Bit --
    15: ("Time of Message Reception of Velocity-High Precision", "4", skip_field(4)),
    16: ("Geometric Height", "2", skip_field(2)),
    17: ("Quality Indicators", "1+", skip_variable_fx),
    18: ("MOPS Version", "1", skip_field(1)),
    19: ("Mode 3/A Code", "2", decode_mode3a_code),
    20: ("Roll Angle", "2", skip_field(2)),
    21: ("Flight Level", "2", decode_flight_level),
    # -- FX Bit --
    22: ("Magnetic Heading", "2", decode_magnetic_heading),
    23: ("Target Status", "1", decode_target_status),
    24: ("Barometric Vertical Rate", "2", skip_field(2)),
    25: ("Geometric Vertical Rate", "2", skip_field(2)),
    26: ("Airborne Ground Vector", "4", decode_airborne_ground_vector),
    27: ("Track Angle Rate", "2", skip_field(2)),
    28: ("Time of Report Transmission", "3", skip_field(3)),
    # -- FX Bit --
    29: ("Target Identification", "6", decode_target_identification),
    30: ("Emitter Category", "1", skip_field(1)),
    31: ("Met Information", "1+", skip_compound_met_info),
    32: ("Selected Altitude", "2", skip_field(2)),
    33: ("Final State Selected Altitude", "2", skip_field(2)),
    34: ("Trajectory Intent", "1+", skip_compound_trajectory_intent),
    35: ("Service Management", "1", skip_field(1)),
    # -- FX Bit --
    36: ("Aircraft Operational Status", "1", skip_field(1)),
    37: ("Surface Capabilities and Characteristics", "1+", skip_variable_fx),
    38: ("Message Amplitude", "1", skip_field(1)),
    39: ("Mode S MB Data", "1+N*8", skip_repetitive_mode_s_mb),
    40: ("ACAS Resolution Advisory Report", "7", skip_field(7)),
    41: ("Receiver ID", "1", skip_field(1)),
    42: ("Data Ages", "1+", skip_variable_fx),
    # -- FX Bit --
    # 43-47 No Usados [cite: 2588]
    48: ("Reserved Expansion Field", "1+", skip_variable_fx),
    49: ("Special Purpose Field", "1+", skip_variable_fx),
    # 50-56 No Definidos en UAP v2.1
}


def decode_cat21(cat, length, data: bitstring.BitArray):
    """
    Decodifica un mensaje ASTERIX CAT21 basado en la especificación Eurocontrol v2.1.
    Esta versión está CORREGIDA para saltar correctamente los campos no decodificados.
    """
    if cat != 21:
        raise ValueError("La categoría debe ser 21")

    pos = 0
    decoded = {"Category": cat}

    # Decodifica el FSPEC (puede tener múltiples octetos)
    fspec_data = []
    more_fspec = True
    while more_fspec and pos < len(data):
        if pos + 8 > len(data):
            # Paquete truncado, no se puede leer el FSPEC
            return [], {}, pos

        fspec_bits = data[pos : pos + 8]
        fspec_data.extend(fspec_bits[:7])  # Añade 7 bits de FRN
        more_fspec = fspec_bits[7]  # Comprueba el bit FX
        pos += 8

    # Itera sobre los campos presentes en el mensaje y los decodifica o salta
    for frn, present in enumerate(fspec_data, start=1):
        if not present:
            continue  # El campo no está en este registro, saltar.

        if pos >= len(data):
            # FSPEC dijo que había más datos, pero el paquete está truncado.
            print(
                f"[Warning] Paquete truncado. FSPEC indicó FRN {frn} pero no quedan datos."
            )
            break

        if frn not in UAP_MAP:
            # Nuestro UAP_MAP está incompleto o el dato es de una versión desconocida.
            # No podemos continuar porque no sabemos cuántos bits saltar.
            print(
                f"[ERROR] FRN {frn} presente pero no definido en UAP_MAP. Decodificación detenida."
            )
            break

        # Obtener el nombre, la especificación de longitud y la función (ya sea decodificar o saltar)
        item_name, item_length_spec, decoder_func = UAP_MAP[frn]

        try:
            # Pasar los *datos restantes* a la función de decodificación/salto.
            # La función es responsable de consumir la cantidad correcta de bits.
            item_data = data[pos:]

            decoded_value, bits_processed = decoder_func(item_data)

            if decoded_value is not None:
                # Si no era una función de salto, guardar el valor
                decoded.update(decoded_value)

            pos += bits_processed

        except (ValueError, IndexError) as e:
            # Error al decodificar o saltar un campo (ej. datos insuficientes)
            print(
                f"[Warning] Fallo al procesar FRN {frn} ('{item_name}'). Error: {e}. Deteniendo este paquete."
            )
            # Una vez que un campo falla, estamos desincronizados. Es más seguro parar.
            break
        except Exception as e:
            print(
                f"[ERROR] Error inesperado en FRN {frn} ('{item_name}'): {e}. Deteniendo este paquete."
            )
            break

    return decoded
