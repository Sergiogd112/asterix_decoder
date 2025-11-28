from typing import Any, Optional

def load(
    file_path: str,
    radar_lat: float,
    radar_lon: float,
    radar_alt: float,
    max_messages: Optional[int] = None,
    debug_save_path: Optional[str] = None,
) -> list[dict[str, Any]]: ...
