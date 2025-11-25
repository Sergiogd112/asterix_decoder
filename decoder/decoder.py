import pandas as pd
import bitstring
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from rich import print
from .cat21 import decode_cat21

from .cat48 import decode_cat48


class Decoder:
    def __init__(self):
        pass

    def split_data(self, bit_data, max_messages=None):
        result = []
        current_pos = 0
        total_bits = len(bit_data)
        i = 0
        with tqdm(total=total_bits // 8, desc="Splitting") as pbar:
            while current_pos + 24 <= total_bits:  # Need at least 24 bits for header
                cat = bit_data[current_pos : current_pos + 8].uint
                length = bit_data[current_pos + 8 : current_pos + 24].uint
                # print(f"Found message with CAT={cat} and length={length}")
                data_end = current_pos + (length) * 8

                if data_end > total_bits:
                    break

                data = bit_data[current_pos + 24 : data_end]
                result.append((cat, length, data))

                current_pos = data_end
                pbar.update(length)
                i += 1
                if max_messages is not None and i > max_messages:
                    break

        return result

    def _decode_element(self, element, radar_coords=None):
        cat, length, data = element
        if cat == 48:
            return decode_cat48(cat, length, data, radar_coords=radar_coords)
        elif cat == 21:
            return decode_cat21(cat, length, data)
        return None

    def load(self, file_name, parallel=True, max_messages=None, radar_coords=None):
        with open(file_name, "rb") as f:
            data = f.read()
        bit_data = bitstring.BitArray(data)
        print(f"Loaded {len(data)} bytes from {file_name}")
        splitted_data = self.split_data(bit_data, max_messages)
        decoded_messages = []

        # Create a partial function with radar_coords
        from functools import partial

        decode_func = partial(self._decode_element, radar_coords=radar_coords)

        if parallel:
            with Pool(processes=min(cpu_count() - 1, 8)) as pool:
                results = list(
                    tqdm(
                        pool.imap(decode_func, splitted_data),
                        total=len(splitted_data),
                        desc="Decoding",
                        unit="Msg",
                    )
                )
        else:
            results = list(
                tqdm(
                    map(decode_func, splitted_data),
                    total=len(splitted_data),
                    desc="Decoding",
                    unit="Msg",
                )
            )
        decoded_messages.extend([msg for msg in results if msg is not None])
        if max_messages is not None:
            results = results[:max_messages]
        # print(results)
        return results

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
            # Include top-level fields
            for key, value in message.items():
                if not isinstance(value, dict):
                    flat_record[key] = value
                else:
                    # Include nested dictionary fields
                    flat_record.update(value)
            flattened_data.append(flat_record)

        df = pd.DataFrame(flattened_data)

        # Lista de columnas exacta que solicitaste
        cols_to_export = [
            "Category",
            "SIC",
            "ATP Description",
            "ARC Description",
            "RC Description",
            "RAB Description",
            "Latitude (deg)",
            "Longitude (deg)",
            "ICAO Address (hex)",
            "Time (s since midnight)",
            "UTC Time (HH:MM:SS)",
            "Mode-3/A Code",
            "Flight Level (FL)",
            "Altitude (ft)",
            "Target Identification",
            "Range (m)Theta",
            "TA",
            "Barometric Pressure Setting",
            "GS(kts)",
            "HDG(deg)IAS",
            "Mach",
            "STAT",
        ]

        # Reordenar y filtrar el DataFrame para que coincida con la lista
        final_cols = [col for col in cols_to_export if col in df.columns]
        filtered_df = df[final_cols]

        output_csv = "decoded_adsb_data.csv"
        filtered_df.to_csv(output_csv, index=False)
        print(f"[INFO] CSV exportado correctamente: {output_csv}")
