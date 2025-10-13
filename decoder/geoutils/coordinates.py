"""Coordinate container classes used by GeoUtils."""

from typing import Tuple, Optional


class Coordinates:
    """Base class for coordinate containers."""

    pass


class CoordinatesPolar(Coordinates):
    """Spherical coordinates (rho, theta, elevation)."""

    def __init__(self, rho: float = 0.0, theta: float = 0.0, elevation: float = 0.0):
        self.rho = rho
        self.theta = theta
        self.elevation = elevation

    @staticmethod
    def to_string(c: "CoordinatesPolar") -> str:
        return f"R: {c.rho:.4f}m T: {c.theta:.4f}rad E: {c.elevation:.4f}rad"

    @staticmethod
    def to_string_standard(c: "CoordinatesPolar") -> str:
        # Lazy import to avoid circular dependency with core.GeoUtils
        from .core import GeoUtils

        return f"R: {c.rho * GeoUtils.METERS2NM:.4f}NM T: {c.theta * GeoUtils.RADS2DEGS:.4f}° E: {c.elevation * GeoUtils.RADS2DEGS:.4f}°"


class CoordinatesXYZ(Coordinates):
    """Cartesian coordinates in meters."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f"X: {self.x:.4f}m Y: {self.y:.4f}m Z: {self.z:.4f}m"

    @staticmethod
    def to_string(c: "CoordinatesXYZ") -> str:
        return f"X: {c.x:.4f}m Y: {c.y:.4f}m Z: {c.z:.4f}m"


class CoordinatesUVH(Coordinates):
    """Stereographic / projection coordinates (u, v, height)."""

    def __init__(self, u: float = 0.0, v: float = 0.0, height: float = 0.0):
        self.u = u
        self.v = v
        self.height = height


class CoordinatesXYH(Coordinates):
    """Planar coordinates with height."""

    def __init__(self, x: float = 0.0, y: float = 0.0, height: float = 0.0):
        self.x = x
        self.y = y
        self.height = height


class CoordinatesWGS84(Coordinates):
    """Latitude/Longitude/Height in radians/meters."""

    def __init__(self, lat: float = 0.0, lon: float = 0.0, height: float = 0.0):
        self.lat = lat
        self.lon = lon
        self.height = height

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CoordinatesWGS84):
            return (
                abs(self.lat - other.lat) < 1e-10
                and abs(self.lon - other.lon) < 1e-10
                and abs(self.height - other.height) < 1e-10
            )
        return False

    def __hash__(self) -> int:
        return hash((round(self.lat, 10), round(self.lon, 10), round(self.height, 10)))

    def __str__(self) -> str:
        # Lazy import to avoid circular import with core
        from .core import GeoUtils

        d1, d2, d3, n = GeoUtils.radians_2_lat_lon(self.lat)
        lat_str = f"{int(d1):02d}:{int(d2):02d}:{d3:.4f}{'N' if n == 0 else 'S'}"
        d1, d2, d3, n = GeoUtils.radians_2_lat_lon(self.lon)
        lon_str = f"{int(d1):03d}:{int(d2):02d}:{d3:.4f}{'E' if n == 0 else 'W'}"
        degs_lat = self.lat * GeoUtils.RADS2DEGS
        degs_lon = self.lon * GeoUtils.RADS2DEGS
        return f"{lat_str} {lon_str} {self.height:.4f}m\nlat:{degs_lat:.9f} lon:{degs_lon:.9f}"
    def __repr__(self)-> str:
        return self.__str__()
