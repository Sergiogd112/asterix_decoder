import pandas as pd
import bitstring
from tqdm import tqdm
from .cat21 import decode_cat21
import multiprocessing
import os

# FUNCIÓN HELPER PARA MULTIPROCESSING
def decode_packet_worker(element):
    """Decodifica un único paquete de datos. Devuelve los datos si es CAT21, si no None."""
    try:
        cat, length, data = element
        if cat == 21:
            _, decoded_data, _ = decode_cat21(cat, length, data)
            return decoded_data
    except Exception:
        # Ignora errores en paquetes individuales para no detener todo el proceso
        pass
    return None

class Decoder:
    def __init__(self):
        pass

    def split_data(self, bit_data):
        """Divide los datos binarios en paquetes ASTERIX individuales."""
        result = []
        current_pos = 0
        total_bits = len(bit_data)
        
        while current_pos + 24 <= total_bits:
            cat = bit_data[current_pos : current_pos + 8].uint
            length = bit_data[current_pos + 8 : current_pos + 24].uint
            data_end = current_pos + (length * 8)

            if data_end > total_bits:
                break

            data = bit_data[current_pos + 24 : data_end]
            result.append((cat, length, data))
            current_pos = data_end
        
        return result

    def load(self, file_name):
        """Carga y procesa el archivo ASTERIX usando todos los núcleos de la CPU."""
        with open(file_name, "rb") as f:
            self.data = f.read()
        self.bit_data = bitstring.BitArray(self.data)
        print(f"Loaded {len(self.data)} bytes from {file_name}")

        print("Dividiendo el archivo en paquetes ASTERIX...")
        self.splited_data = self.split_data(self.bit_data)
        print(f"Se encontraron {len(self.splited_data)} paquetes en total.")

        num_cores = os.cpu_count()
        print(f"Iniciando decodificación en paralelo usando {num_cores} núcleos de CPU...")

        decoded_messages = []
        with multiprocessing.Pool(processes=num_cores) as pool:
            results_iterator = pool.imap_unordered(decode_packet_worker, self.splited_data)
            
            for result in tqdm(results_iterator, total=len(self.splited_data), desc="Procesando paquetes"):
                if result:
                    decoded_messages.append(result)
        
        print(f"Decodificación completada. Se encontraron {len(decoded_messages)} mensajes de CAT21.")
        
        self.export_to_csv(decoded_messages)

    def export_to_csv(self, decoded_messages):
        """
        Exporta los mensajes decodificados a un archivo CSV, aplanando la estructura de datos.
        """
        if not decoded_messages:
            print("[WARNING] No hay mensajes CAT21 decodificados para exportar.")
            return

        print("Aplanando datos y generando CSV...")
        
        # Lógica de aplanamiento robusta
        flattened_data = []
        for message in decoded_messages:
            flat_record = {}
            for field_value in message.values():
                if isinstance(field_value, dict):
                    flat_record.update(field_value)
            flattened_data.append(flat_record)
        
        df = pd.DataFrame(flattened_data)

        # Lista de columnas exacta que solicitaste
        cols_to_export = [
            "SAC", "SIC", "ATP Description", "ARC Description", "RC Description",
            "RAB Description", "Latitude (deg)", "Longitude (deg)",
            "ICAO Address (hex)", "Time (s since midnight)", "UTC Time (HH:MM:SS)",
            "Mode-3/A Code", "Flight Level (FL)", "Altitude (ft)",
            "Target Identification"
        ]

        # Reordenar y filtrar el DataFrame para que coincida con la lista
        final_cols = [col for col in cols_to_export if col in df.columns]
        filtered_df = df[final_cols]

        output_csv = "decoded_adsb_data.csv"
        filtered_df.to_csv(output_csv, index=False)
        print(f"[INFO] CSV exportado correctamente: {output_csv}")