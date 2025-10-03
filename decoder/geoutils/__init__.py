"""
geoutils_pkg — geodesy utilities split into focused modules.

Public API:
- GeoUtils: main coordinate conversion utilities
- GeneralMatrix: lightweight matrix wrapper
- Maths: small math helpers
- Coordinates*: coordinate container classes
"""

from .maths import Maths
from .matrix import GeneralMatrix
from .coordinates import (
    Coordinates,
    CoordinatesPolar,
    CoordinatesXYZ,
    CoordinatesUVH,
    CoordinatesXYH,
    CoordinatesWGS84,
)
from .core import GeoUtils

__all__ = [
    "Maths",
    "GeneralMatrix",
    "Coordinates",
    "CoordinatesPolar",
    "CoordinatesXYZ",
    "CoordinatesUVH",
    "CoordinatesXYH",
    "CoordinatesWGS84",
    "GeoUtils",
]
