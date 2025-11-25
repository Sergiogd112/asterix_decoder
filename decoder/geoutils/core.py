"""GeoUtils: main geodesy and coordinate transformation utilities."""

from typing import List, Optional, Tuple
import numpy as np

# Import the matrix and coordinate classes from the same package
from .matrix import GeneralMatrix
from .coordinates import (
    CoordinatesWGS84,
    CoordinatesXYZ,
    CoordinatesUVH,
    CoordinatesXYH,
    CoordinatesPolar,
)


class GeoUtils:
    """Utilities to convert between geodetic/geocentric/cartesian/stereographic coords.

    This class encapsulates ellipsoid constants and a set of coordinate conversion
    routines used across the decoder.
    """

    METERS2FEET = 3.28084
    FEET2METERS = 0.3048
    NM2METERS = 1852.0
    METERS2NM = 1.0 / NM2METERS
    DEGS2RADS = np.pi / 180.0
    RADS2DEGS = 180.0 / np.pi
    ALMOST_ZERO = 1e-10
    REQUIERED_PRECISION = 1e-8

    A = 6378137.0
    B = 6356752.3142
    E2 = 0.00669437999013

    def __init__(
        self,
        E: Optional[float] = None,
        A: Optional[float] = None,
        center_projection: Optional[CoordinatesWGS84] = None,
    ):
        """Allow overriding ellipsoid parameters and optionally set a projection center."""
        if E is not None and A is not None:
            self.E2 = E * E
            self.A = A
        self.center_projection: Optional[CoordinatesWGS84] = None
        self.T1: Optional[GeneralMatrix] = None
        self.R1: Optional[GeneralMatrix] = None
        self.R_S = 0.0
        self.rotation_matrix_ht: dict = {}
        self.translation_matrix_ht: dict = {}
        self.position_radar_matrix_ht: dict = {}
        self.rotation_radar_matrix_ht: dict = {}
        if center_projection is not None:
            self.set_center_projection(center_projection)

    @staticmethod
    def lat_lon_string_both_2_radians(
        line: str, height: Optional[float] = None
    ) -> CoordinatesWGS84:
        """Parse a combined lat/lon DMS string into radians, applying optional height."""
        # Delegate to full parser; keep interface stable
        res = GeoUtils.lat_lon_string_both_2_radians_full(line)
        if height is not None:
            res.height = height
        return res

    @staticmethod
    def lat_lon_string_both_2_radians_full(line: str) -> CoordinatesWGS84:
        """Robustly parse strings like '41:23:45N 002:10:03E 30' into WGS84 coords."""
        import re

        pattern = r"([-+]?)([0-9]+):([0-9]+):([0-9][0-9]*\.?[0-9]+)([NS]?)\s+([-+]?)([0-9]+):([0-9]+):([0-9][0-9]*\.?[0-9]+?)([EW]?)\s*([0-9][0-9]*\.?[0-9]+?)?"
        match = re.match(pattern, line)
        if not match:
            raise ValueError(f"Invalid coordinate format: {line}")
        groups = match.groups()
        try:
            lat_sign = -1 if groups[0] == "-" else 1
            lat_d = float(groups[1])
            lat_m = float(groups[2])
            lat_s = float(groups[3])
            lat_dir = -1 if groups[4] in ("S", "s") else 1
            lon_sign = -1 if groups[5] == "-" else 1
            lon_d = float(groups[6])
            lon_m = float(groups[7])
            lon_s = float(groups[8])
            lon_dir = -1 if groups[9] in ("W", "w") else 1
            h_str = groups[10] if len(groups) > 10 else "0"
            height = float(h_str) if h_str else 0.0

            lat_ns = 1 if lat_sign * lat_dir < 0 else 0
            lon_ns = 1 if lon_sign * lon_dir < 0 else 0

            res = CoordinatesWGS84()
            res.lat = GeoUtils.lat_lon_2_radians(lat_d, lat_m, lat_s, lat_ns)
            res.lon = GeoUtils.lat_lon_2_radians(lon_d, lon_m, lon_s, lon_ns)
            res.height = height
            return res
        except ValueError as e:
            raise ValueError(f"Parsing error for line '{line}': {e}")

    @staticmethod
    def lat_lon_2_degrees(d1: float, d2: float, d3: float, ns: int) -> float:
        """Convert DMS components into signed decimal degrees."""
        d = d1 + d2 / 60.0 + d3 / 3600.0
        if ns == 1:
            d *= -1.0
        return d

    @staticmethod
    def lat_lon_2_radians(d1: float, d2: float, d3: float, ns: int) -> float:
        """Convert DMS components into signed radians."""
        d = GeoUtils.lat_lon_2_degrees(d1, d2, d3, ns)
        return d * GeoUtils.DEGS2RADS

    @staticmethod
    def lat_lon_string_2_degrees(s1: str, s2: str, s3: str, ns: int) -> float:
        """Helper that accepts string digits and forwards to lat_lon_2_degrees."""
        d1, d2, d3 = float(s1), float(s2), float(s3)
        return GeoUtils.lat_lon_2_degrees(d1, d2, d3, ns)

    @staticmethod
    def degrees_2_lat_lon(d: float) -> Tuple[float, float, float, int]:
        """Split decimal degrees into degrees/minutes/seconds plus hemisphere."""
        ns = 1 if d < 0 else 0
        if ns == 1:
            d = -d
        d1 = np.floor(d)
        d2 = np.floor((d - d1) * 60.0)
        d3 = ((d - d1) * 60.0 - d2) * 60.0
        return float(d1), float(d2), d3, ns

    @staticmethod
    def radians_2_lat_lon(d: float) -> Tuple[float, float, float, int]:
        """Convert radians back to DMS components."""
        d_deg = d * GeoUtils.RADS2DEGS
        return GeoUtils.degrees_2_lat_lon(d_deg)

    @staticmethod
    def center_coordinates(l: List[CoordinatesWGS84]) -> Optional[CoordinatesWGS84]:
        """Return the midpoint of a list of WGS84 coordinates."""
        if not l:
            return None
        lats = [c.lat for c in l]
        lons = [c.lon for c in l]
        heights = [c.height for c in l]
        res = CoordinatesWGS84()
        res.lat = (min(lats) + max(lats)) / 2.0
        res.lon = (min(lons) + max(lons)) / 2.0
        res.height = max(heights)
        return res

    def change_geodesic_2_geocentric(
        self, c: CoordinatesWGS84
    ) -> Optional[CoordinatesXYZ]:
        """Convert geodetic WGS84 coordinates to earth-centered Cartesian."""
        if c is None:
            return None
        res = CoordinatesXYZ()
        sin_lat = np.sin(c.lat)
        nu = self.A / np.sqrt(1 - self.E2 * sin_lat**2)
        cos_lat = np.cos(c.lat)
        cos_lon = np.cos(c.lon)
        sin_lon = np.sin(c.lon)
        res.x = (nu + c.height) * cos_lat * cos_lon
        res.y = (nu + c.height) * cos_lat * sin_lon
        res.z = (nu * (1 - self.E2) + c.height) * sin_lat
        return res

    def change_geocentric_2_geodesic(
        self, c: CoordinatesXYZ
    ) -> Optional[CoordinatesWGS84]:
        """Convert earth-centered Cartesian coordinates back to WGS84."""
        if c is None:
            return None
        res = CoordinatesWGS84()
        b = self.B
        if abs(c.x) < GeoUtils.ALMOST_ZERO and abs(c.y) < GeoUtils.ALMOST_ZERO:
            if abs(c.z) < GeoUtils.ALMOST_ZERO:
                res.lat = np.pi / 2.0
            else:
                sign_z = 1 if c.z > 0 else -1
                res.lat = (np.pi / 2.0) * (sign_z + 0.5)
            res.lon = 0.0
            res.height = abs(c.z) - b
            return res
        d_xy = np.sqrt(c.x**2 + c.y**2)
        p = np.arctan(
            (c.z / d_xy) / (1 - (self.A * self.E2) / np.sqrt(d_xy**2 + c.z**2))
        )
        res.lat = p
        sin_p = np.sin(p)
        nu = self.A / np.sqrt(1 - self.E2 * sin_p**2)
        cos_p = np.cos(p)
        res.height = (d_xy / cos_p) - nu
        lat_over = p
        loop_count = 0
        while (
            abs(res.lat - lat_over) > GeoUtils.REQUIERED_PRECISION and loop_count < 50
        ):
            loop_count += 1
            lat_over = res.lat
            sin_lat = np.sin(res.lat)
            nu = self.A / np.sqrt(1 - self.E2 * sin_lat**2)
            res.lat = np.arctan(
                (c.z + res.height) / nu / (d_xy * (1 - self.E2 + res.height / nu))
            )
            cos_lat = np.cos(res.lat)
            res.height = d_xy / cos_lat - nu
        res.lon = np.arctan2(c.y, c.x)
        return res

    def set_center_projection(self, c: CoordinatesWGS84) -> Optional[CoordinatesWGS84]:
        """Pre-compute translation/rotation matrices for a new stereographic center."""
        if c is None:
            return None
        c2 = CoordinatesWGS84(c.lat, c.lon, 0.0)
        self.center_projection = c2
        sin_lat = np.sin(c2.lat)
        self.R_S = (self.A * (1.0 - self.E2)) / (1 - self.E2 * sin_lat**2) ** 1.5
        self.T1 = GeoUtils.calculate_translation_matrix(c2, self.A, self.E2)
        self.R1 = GeoUtils.calculate_rotation_matrix(c2.lat, c2.lon)
        return self.center_projection

    def get_center_projection(self) -> Optional[CoordinatesWGS84]:
        """Return the coordinate currently used as stereographic center."""
        return self.center_projection

    def change_geocentric_2_system_cartesian(
        self, geo: CoordinatesXYZ
    ) -> Optional[CoordinatesXYZ]:
        """Convert global Cartesian coordinates into the projection's local frame."""
        if (
            self.center_projection is None
            or self.R1 is None
            or self.T1 is None
            or geo is None
        ):
            return None
        input_arr = np.array([[geo.x], [geo.y], [geo.z]])
        input_matrix = GeneralMatrix(input_arr)
        temp = input_matrix - self.T1
        r2 = self.R1 @ temp
        return CoordinatesXYZ(
            r2.get_element(0, 0), r2.get_element(1, 0), r2.get_element(2, 0)
        )

    def change_system_cartesian_2_geocentric(
        self, car: CoordinatesXYZ
    ) -> Optional[CoordinatesXYZ]:
        """Convert local system Cartesian coordinates back to earth-centered."""
        if car is None:
            return None
        input_arr = np.array([[car.x], [car.y], [car.z]])
        input_matrix = GeneralMatrix(input_arr)
        r2 = self.R1.transpose() @ input_matrix
        r3 = r2 + self.T1
        return CoordinatesXYZ(
            r3.get_element(0, 0), r3.get_element(1, 0), r3.get_element(2, 0)
        )

    def change_system_xyh_2_system_z(self, c: CoordinatesXYH) -> float:
        """Recover Z from XYH stereographic coordinates."""
        if c is None:
            return 0.0
        xh = c.x / (self.R_S + c.height)
        yh = c.y / (self.R_S + c.height)
        temp = xh**2 + yh**2
        if temp > 1:
            return -(self.R_S + self.center_projection.height)
        else:
            return (self.R_S + c.height) * np.sqrt(1.0 - temp) - (
                self.R_S + self.center_projection.height
            )

    def change_system_cartesian_2_stereographic(
        self, c: CoordinatesXYZ
    ) -> Optional[CoordinatesUVH]:
        """Project local Cartesian coordinates to stereographic UVH."""
        if c is None:
            return None
        res = CoordinatesUVH()
        d_xy2 = c.x**2 + c.y**2
        denom = c.z + self.center_projection.height + self.R_S
        res.height = np.sqrt(d_xy2 + denom**2) - self.R_S
        k = (2 * self.R_S) / (
            2 * self.R_S + self.center_projection.height + c.z + res.height
        )
        res.u = k * c.x
        res.v = k * c.y
        return res

    def change_stereographic_2_system_cartesian(
        self, c: CoordinatesUVH
    ) -> Optional[CoordinatesXYZ]:
        """Convert stereographic UVH coordinates back to local Cartesian."""
        if c is None:
            return None
        res = CoordinatesXYZ()
        d_uv2 = c.u**2 + c.v**2
        num = 4 * self.R_S**2 - d_uv2
        den = 4 * self.R_S**2 + d_uv2
        res.z = (c.height + self.R_S) * (num / den) - (
            self.R_S + self.center_projection.height
        )
        k = (2 * self.R_S) / (
            2 * self.R_S + self.center_projection.height + res.z + c.height
        )
        res.x = c.u / k
        res.y = c.v / k
        return res

    @staticmethod
    def calculate_elevation(
        center_coordinates: CoordinatesWGS84, R: float, rho: float, h: float
    ) -> float:
        """Solve for elevation angle from spherical geometry inputs."""
        if rho < GeoUtils.ALMOST_ZERO or R == -1.0 or center_coordinates is None:
            return 0.0
        temp = (
            2 * R * (h - center_coordinates.height)
            + h**2
            - center_coordinates.height**2
            - rho**2
        ) / (2 * rho * (R + center_coordinates.height))
        if -1.0 <= temp <= 1.0:
            return np.arcsin(temp)
        return np.pi / 2.0

    @staticmethod
    def calculate_azimuth(x: float, y: float) -> float:
        """Return an azimuth angle in radians for the provided X/Y."""
        if abs(y) < GeoUtils.ALMOST_ZERO:
            theta = (x / abs(x)) * np.pi / 2.0 if x != 0 else 0.0
        else:
            theta = np.arctan2(x, y)
        if theta < 0.0:
            theta += 2 * np.pi
        return theta

    def calculate_earth_radius(self, geo: CoordinatesWGS84) -> float:
        """Compute the radius of curvature at a given latitude."""
        if geo is None:
            return np.nan
        sin_lat = np.sin(geo.lat)
        return (self.A * (1.0 - self.E2)) / (1 - self.E2 * sin_lat**2) ** 1.5

    @staticmethod
    def calculate_rotation_matrix(lat: float, lon: float) -> GeneralMatrix:
        """Build the rotation matrix that aligns ENU axes with ECEF."""
        sin_lon, cos_lon = np.sin(lon), np.cos(lon)
        sin_lat, cos_lat = np.sin(lat), np.cos(lat)
        coef_r1 = np.array(
            [
                [-sin_lon, cos_lon, 0.0],
                [-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
                [cos_lat * cos_lon, cos_lat * sin_lon, sin_lat],
            ]
        )
        return GeneralMatrix(coef_r1)

    @staticmethod
    def calculate_translation_matrix(
        c: CoordinatesWGS84, A: float, E2: float
    ) -> GeneralMatrix:
        """Build the translation vector (as matrix) for the given origin."""
        sin_lat = np.sin(c.lat)
        nu = A / np.sqrt(1 - E2 * sin_lat**2)
        cos_lat, sin_lat = np.cos(c.lat), np.sin(c.lat)
        cos_lon, sin_lon = np.cos(c.lon), np.sin(c.lon)
        coef_t1 = np.array(
            [
                [(nu + c.height) * cos_lat * cos_lon],
                [(nu + c.height) * cos_lat * sin_lon],
                [(nu * (1 - E2) + c.height) * sin_lat],
            ]
        )
        return GeneralMatrix(coef_t1)

    @staticmethod
    def calculate_position_radar_matrix(
        T1: GeneralMatrix, t: GeneralMatrix, r: GeneralMatrix
    ) -> GeneralMatrix:
        """Precompute translation for radar Cartesian systems."""
        r1 = T1 - t
        return r @ r1

    @staticmethod
    def calculate_rotation_radar_matrix(
        R1: GeneralMatrix, r: GeneralMatrix
    ) -> GeneralMatrix:
        """Precompute rotation for radar Cartesian systems."""
        r2 = R1.transpose()
        return r @ r2

    @staticmethod
    def change_radar_spherical_2_radar_cartesian(
        polar_coordinates: CoordinatesPolar,
    ) -> Optional[CoordinatesXYZ]:
        """Convert radar spherical (rho/theta/elev) into radar Cartesian XYZ."""
        if polar_coordinates is None:
            return None
        res = CoordinatesXYZ()
        cos_el = np.cos(polar_coordinates.elevation)
        sin_theta = np.sin(polar_coordinates.theta)
        cos_theta = np.cos(polar_coordinates.theta)
        res.x = polar_coordinates.rho * cos_el * sin_theta
        res.y = polar_coordinates.rho * cos_el * cos_theta
        res.z = polar_coordinates.rho * np.sin(polar_coordinates.elevation)
        return res

    @staticmethod
    def change_radar_cartesian_2_radar_spherical(
        cartesian_coordinates: CoordinatesXYZ,
    ) -> Optional[CoordinatesPolar]:
        """Convert radar Cartesian coordinates back into rho/theta/elevation."""
        if cartesian_coordinates is None:
            return None
        res = CoordinatesPolar()
        res.rho = np.sqrt(
            cartesian_coordinates.x**2
            + cartesian_coordinates.y**2
            + cartesian_coordinates.z**2
        )
        res.theta = GeoUtils.calculate_azimuth(
            cartesian_coordinates.x, cartesian_coordinates.y
        )
        if res.rho == 0:
            res.elevation = 0.0
        else:
            res.elevation = np.arcsin(cartesian_coordinates.z / res.rho)
        return res

    def change_radar_cartesian_2_geocentric(
        self, radar_coordinates: CoordinatesWGS84, cartesian_coordinates: CoordinatesXYZ
    ) -> CoordinatesXYZ:
        """Convert radar Cartesian coordinates into ECEF using cached transforms."""
        translation_matrix = self.obtain_translation_matrix(radar_coordinates)
        rotation_matrix = self.obtain_rotation_matrix(radar_coordinates)
        input_arr = np.array(
            [
                [cartesian_coordinates.x],
                [cartesian_coordinates.y],
                [cartesian_coordinates.z],
            ]
        )
        input_matrix = GeneralMatrix(input_arr)
        r1 = rotation_matrix.transpose() @ input_matrix
        r2 = r1 + translation_matrix
        return CoordinatesXYZ(
            r2.get_element(0, 0), r2.get_element(1, 0), r2.get_element(2, 0)
        )

    def change_geocentric_2_radar_cartesian(
        self,
        radar_coordinates: CoordinatesWGS84,
        geocentric_coordinates: CoordinatesXYZ,
    ) -> CoordinatesXYZ:
        """Convert ECEF coordinates into radar-aligned Cartesian."""
        translation_matrix = self.obtain_translation_matrix(radar_coordinates)
        rotation_matrix = self.obtain_rotation_matrix(radar_coordinates)
        input_arr = np.array(
            [
                [geocentric_coordinates.x],
                [geocentric_coordinates.y],
                [geocentric_coordinates.z],
            ]
        )
        input_matrix = GeneralMatrix(input_arr)
        temp = input_matrix - translation_matrix
        r1 = rotation_matrix @ temp
        return CoordinatesXYZ(
            r1.get_element(0, 0), r1.get_element(1, 0), r1.get_element(2, 0)
        )

    def change_radar_cartesian_2_system_cartesian(
        self, radar_coordinates: CoordinatesWGS84, cartesian_coordinates: CoordinatesXYZ
    ) -> CoordinatesXYZ:
        """Convert radar-centric Cartesian coordinates into the stereographic system."""
        position_radar_matrix = self.obtain_position_radar_matrix(radar_coordinates)
        rotation_radar_matrix = self.obtain_rotation_radar_matrix(radar_coordinates)
        input_arr = np.array(
            [
                [cartesian_coordinates.x],
                [cartesian_coordinates.y],
                [cartesian_coordinates.z],
            ]
        )
        input_matrix = GeneralMatrix(input_arr)
        temp = input_matrix - position_radar_matrix
        r1 = rotation_radar_matrix @ temp
        return CoordinatesXYZ(
            r1.get_element(0, 0), r1.get_element(1, 0), r1.get_element(2, 0)
        )

    def change_system_cartesian_2_radar_cartesian(
        self, radar_coordinates: CoordinatesWGS84, cartesian_coordinates: CoordinatesXYZ
    ) -> CoordinatesXYZ:
        """Convert stereographic system coordinates back to radar Cartesian."""
        position_radar_matrix = self.obtain_position_radar_matrix(radar_coordinates)
        rotation_radar_matrix = self.obtain_rotation_radar_matrix(radar_coordinates)
        input_arr = np.array(
            [
                [cartesian_coordinates.x],
                [cartesian_coordinates.y],
                [cartesian_coordinates.z],
            ]
        )
        input_matrix = GeneralMatrix(input_arr)
        r1 = rotation_radar_matrix @ input_matrix
        r1 = r1 + position_radar_matrix
        return CoordinatesXYZ(
            r1.get_element(0, 0), r1.get_element(1, 0), r1.get_element(2, 0)
        )

    def obtain_rotation_matrix(
        self, radar_coordinates: CoordinatesWGS84
    ) -> GeneralMatrix:
        """Return (and cache) the ENU-to-ECEF rotation for a radar site."""
        if radar_coordinates not in self.rotation_matrix_ht:
            self.rotation_matrix_ht[radar_coordinates] = (
                GeoUtils.calculate_rotation_matrix(
                    radar_coordinates.lat, radar_coordinates.lon
                )
            )
        return self.rotation_matrix_ht[radar_coordinates]

    def obtain_translation_matrix(
        self, radar_coordinates: CoordinatesWGS84
    ) -> GeneralMatrix:
        """Return (and cache) the translation vector for a radar site."""
        if radar_coordinates not in self.translation_matrix_ht:
            self.translation_matrix_ht[radar_coordinates] = (
                GeoUtils.calculate_translation_matrix(
                    radar_coordinates, self.A, self.E2
                )
            )
        return self.translation_matrix_ht[radar_coordinates]

    def obtain_position_radar_matrix(
        self, radar_coordinates: CoordinatesWGS84
    ) -> GeneralMatrix:
        """Return cached translation from stereographic origin to radar."""
        if radar_coordinates not in self.position_radar_matrix_ht:
            t = self.obtain_translation_matrix(radar_coordinates)
            r = self.obtain_rotation_matrix(radar_coordinates)
            self.position_radar_matrix_ht[radar_coordinates] = (
                GeoUtils.calculate_position_radar_matrix(self.T1, t, r)
            )
        return self.position_radar_matrix_ht[radar_coordinates]

    def obtain_rotation_radar_matrix(
        self, radar_coordinates: CoordinatesWGS84
    ) -> GeneralMatrix:
        """Return cached rotation from stereographic axes to radar axes."""
        if radar_coordinates not in self.rotation_radar_matrix_ht:
            r = self.obtain_rotation_matrix(radar_coordinates)
            self.rotation_radar_matrix_ht[radar_coordinates] = (
                GeoUtils.calculate_rotation_radar_matrix(self.R1, r)
            )
        return self.rotation_radar_matrix_ht[radar_coordinates]
