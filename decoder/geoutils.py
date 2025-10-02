import numpy as np
import re
from typing import List, Tuple, Optional
from scipy import linalg as la


class Maths:
    @staticmethod
    def hypot(a: float, b: float) -> float:
        if abs(a) > abs(b):
            r = b / a
            return abs(a) * np.sqrt(1 + r * r)
        elif b != 0:
            r = a / b
            return abs(b) * np.sqrt(1 + r * r)
        else:
            return 0.0


class GeneralMatrix:
    def __init__(self, *args):
        if len(args) == 0:
            self.A = np.empty((0, 0))
            self.m = 0
            self.n = 0
            return

        arg = args[0]
        if isinstance(arg, int) and len(args) >= 2:
            # GeneralMatrix(int m, int n) or GeneralMatrix(int m, int n, double s)
            m = arg
            if len(args) == 2:
                n = args[1]
                self.A = np.zeros((m, n))
            elif len(args) == 3:
                n, s = args[1], args[2]
                self.A = np.full((m, n), s)
            else:
                raise ValueError("Invalid arguments for m, n constructor")
            self.m, self.n = m, n
            return

        if isinstance(arg, (list, np.ndarray)):
            if isinstance(arg, list) and len(args) == 1:
                # GeneralMatrix(double[][] A)
                A_list = args[0]
                if not A_list:
                    self.A = np.empty((0, 0))
                    self.m = 0
                    self.n = 0
                    return
                self.m = len(A_list)
                self.n = len(A_list[0])
                for row in A_list:
                    if len(row) != self.n:
                        raise ValueError("All rows must have the same length.")
                self.A = np.array(A_list, dtype=float)
            elif isinstance(arg, np.ndarray):
                # Accept numpy array
                self.A = arg.copy()
                self.m, self.n = self.A.shape
            elif (
                len(args) == 3 and isinstance(args[1], int) and isinstance(args[2], int)
            ):
                # GeneralMatrix(double[][] A, int m, int n)
                A_list, m, n = args[0], args[1], args[2]
                self.A = np.array(A_list, dtype=float)
                if self.A.shape != (m, n):
                    raise ValueError("Shape mismatch")
                self.m, self.n = m, n
            elif (
                isinstance(args[0], (list, np.ndarray))
                and len(args) == 2
                and isinstance(args[1], int)
            ):
                # GeneralMatrix(double[] vals, int m)
                vals = np.array(args[0], dtype=float)
                m = args[1]
                total_len = len(vals)
                n = total_len // m if m != 0 else 0
                if m * n != total_len:
                    raise ValueError("Array length must be a multiple of m.")
                self.A = vals.reshape(
                    (m, n), order="F"
                )  # Column-packed (Fortran order)
                self.m, self.n = m, n
            else:
                raise ValueError("Invalid constructor arguments")
        else:
            raise ValueError("Unsupported constructor")

    @property
    def array(self) -> np.ndarray:
        return self.A

    @property
    def array_copy(self) -> np.ndarray:
        return self.A.copy()

    @property
    def column_packed_copy(self) -> np.ndarray:
        return self.A.ravel(order="F")

    @property
    def row_packed_copy(self) -> np.ndarray:
        return self.A.ravel(order="C")

    @property
    def row_dimension(self) -> int:
        return self.m

    @property
    def column_dimension(self) -> int:
        return self.n

    @staticmethod
    def create(A_list: List[List[float]]) -> "GeneralMatrix":
        m = len(A_list)
        if m == 0:
            n = 0
        else:
            n = len(A_list[0])
            for row in A_list:
                if len(row) != n:
                    raise ValueError("All rows must have the same length.")
        X = GeneralMatrix(m, n)
        X.A = np.array(A_list, dtype=float)
        return X

    def copy(self) -> "GeneralMatrix":
        return GeneralMatrix(self.A.copy())

    def get_element(self, i: int, j: int) -> float:
        if 0 <= i < self.m and 0 <= j < self.n:
            return self.A[i, j]
        raise IndexError("Index out of range")

    def get_matrix_range(self, i0: int, i1: int, j0: int, j1: int) -> "GeneralMatrix":
        sub = self.A[i0 : i1 + 1, j0 : j1 + 1].copy()
        return GeneralMatrix(sub)

    def get_matrix_rows_cols(self, r: List[int], c: List[int]) -> "GeneralMatrix":
        sub = self.A[np.ix_(r, c)].copy()
        return GeneralMatrix(sub)

    def get_matrix_rows_range(self, r: List[int], j0: int, j1: int) -> "GeneralMatrix":
        sub = self.A[np.ix_(r, range(j0, j1 + 1))].copy()
        return GeneralMatrix(sub)

    def get_matrix_range_cols(self, i0: int, i1: int, c: List[int]) -> "GeneralMatrix":
        sub = self.A[range(i0, i1 + 1), c].copy()
        return GeneralMatrix(sub)

    def set_element(self, i: int, j: int, s: float):
        if 0 <= i < self.m and 0 <= j < self.n:
            self.A[i, j] = s
        else:
            raise IndexError("Index out of range")

    def set_matrix_range(self, i0: int, i1: int, j0: int, j1: int, X: "GeneralMatrix"):
        self.A[i0 : i1 + 1, j0 : j1 + 1] = X.A

    def set_matrix_rows_cols(self, r: List[int], c: List[int], X: "GeneralMatrix"):
        self.A[np.ix_(r, c)] = X.A

    # Similar for other set_matrix overloads...

    def transpose(self) -> "GeneralMatrix":
        return GeneralMatrix(self.A.T)

    def norm1(self) -> float:
        return np.sum(np.abs(self.A), axis=0).max()

    def norm2(self) -> float:
        s = la.svdvals(self.A)
        return s.max() if len(s) > 0 else 0.0

    def norm_inf(self) -> float:
        return np.sum(np.abs(self.A), axis=1).max()

    def norm_f(self) -> float:
        return la.norm(self.A, "fro")

    def unary_minus(self) -> "GeneralMatrix":
        return GeneralMatrix(-self.A)

    def add(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        return GeneralMatrix(self.A + B.A)

    def add_equals(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        self.A += B.A
        return self

    def subtract(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        return GeneralMatrix(self.A - B.A)

    def subtract_equals(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        self.A -= B.A
        return self

    def array_multiply(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        return GeneralMatrix(self.A * B.A)

    def array_multiply_equals(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        self.A *= B.A
        return self

    def array_right_divide(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        return GeneralMatrix(self.A / B.A)

    def array_right_divide_equals(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        self.A /= B.A
        return self

    def array_left_divide(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        return GeneralMatrix(B.A / self.A)

    def array_left_divide_equals(self, B: "GeneralMatrix") -> "GeneralMatrix":
        self._check_dimensions(B)
        self.A = B.A / self.A
        return self

    def multiply_scalar(self, s: float) -> "GeneralMatrix":
        return GeneralMatrix(s * self.A)

    def multiply_scalar_equals(self, s: float) -> "GeneralMatrix":
        self.A *= s
        return self

    def multiply(self, B: "GeneralMatrix") -> "GeneralMatrix":
        if self.n != B.m:
            raise ValueError("Inner dimensions must agree.")
        return GeneralMatrix(self.A @ B.A)

    def __add__(self, other: "GeneralMatrix") -> "GeneralMatrix":
        return self.add(other)

    def __sub__(self, other: "GeneralMatrix") -> "GeneralMatrix":
        return self.subtract(other)

    def __matmul__(self, other: "GeneralMatrix") -> "GeneralMatrix":
        return self.multiply(other)

    def __rmatmul__(self, other: "GeneralMatrix") -> "GeneralMatrix":
        return other.multiply(self)

    def solve(self, B: "GeneralMatrix") -> "GeneralMatrix":
        if self.m == self.n:
            # Square: use LU solve
            x = la.solve(self.A, B.A)
        else:
            # Rectangular: least squares using QR
            x, _, _, _ = la.lstsq(self.A, B.A, rcond=None)
        return GeneralMatrix(x)

    def solve_transpose(self, B: "GeneralMatrix") -> "GeneralMatrix":
        return self.transpose().solve(B.transpose())

    def inverse(self) -> "GeneralMatrix":
        if self.m != self.n:
            raise ValueError("Matrix must be square for inverse.")
        return GeneralMatrix(la.inv(self.A))

    def lud(self):
        # For compatibility, but not used directly
        pass

    def qrd(self):
        # For compatibility
        pass

    def chol(self):
        # For compatibility
        pass

    def svd(self):
        # For compatibility
        pass

    def eigen(self):
        # For compatibility
        pass

    def determinant(self) -> float:
        if self.m != self.n:
            raise ValueError("Matrix must be square for determinant.")
        return float(la.det(self.A))

    def rank(self) -> int:
        s = la.svdvals(self.A)
        tol = s.max() * max(self.A.shape) * np.finfo(s.dtype).eps if len(s) > 0 else 0
        return int(np.sum(s > tol))

    def condition(self) -> float:
        s = la.svdvals(self.A)
        if len(s) == 0 or s[-1] == 0:
            return np.inf
        return s[0] / s[-1]

    def trace(self) -> float:
        return float(np.trace(self.A))

    @staticmethod
    def random(m: int, n: int) -> "GeneralMatrix":
        return GeneralMatrix(np.random.rand(m, n))

    @staticmethod
    def identity(m: int, n: int) -> "GeneralMatrix":  # eye
        return GeneralMatrix(np.eye(m, n))

    @staticmethod
    def eye(m: int, n: int) -> "GeneralMatrix":
        return GeneralMatrix(np.eye(m, n))

    def _check_dimensions(self, B: "GeneralMatrix"):
        if self.m != B.m or self.n != B.n:
            raise ValueError("Matrix dimensions must agree.")

    def __str__(self):
        return str(self.A)

    def __repr__(self):
        return f"GeneralMatrix({self.A})"


class Coordinates:
    pass


class CoordinatesPolar(Coordinates):
    def __init__(self, rho: float = 0.0, theta: float = 0.0, elevation: float = 0.0):
        self.rho = rho
        self.theta = theta
        self.elevation = elevation

    @staticmethod
    def to_string(c: "CoordinatesPolar") -> str:
        return f"R: {c.rho:.4f}m T: {c.theta:.4f}rad E: {c.elevation:.4f}rad"

    @staticmethod
    def to_string_standard(c: "CoordinatesPolar") -> str:
        return f"R: {c.rho * GeoUtils.METERS2NM:.4f}NM T: {c.theta * GeoUtils.RADS2DEGS:.4f}° E: {c.elevation * GeoUtils.RADS2DEGS:.4f}°"


class CoordinatesXYZ(Coordinates):
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
    def __init__(self, u: float = 0.0, v: float = 0.0, height: float = 0.0):
        self.u = u
        self.v = v
        self.height = height


class CoordinatesXYH(Coordinates):
    def __init__(self, x: float = 0.0, y: float = 0.0, height: float = 0.0):
        self.x = x
        self.y = y
        self.height = height


class CoordinatesWGS84(Coordinates):
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
        d1, d2, d3, n = GeoUtils.radians_2_lat_lon(self.lat)
        lat_str = f"{int(d1):02d}:{int(d2):02d}:{d3:.4f}{'N' if n == 0 else 'S'}"
        d1, d2, d3, n = GeoUtils.radians_2_lat_lon(self.lon)
        lon_str = f"{int(d1):03d}:{int(d2):02d}:{d3:.4f}{'E' if n == 0 else 'W'}"
        degs_lat = self.lat * GeoUtils.RADS2DEGS
        degs_lon = self.lon * GeoUtils.RADS2DEGS
        return f"{lat_str} {lon_str} {self.height:.4f}m\nlat:{degs_lat:.9f} lon:{degs_lon:.9f}"


class GeoUtils:
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
        res = GeoUtils.lat_lon_string_both_2_radians(line)
        if height is not None:
            res.height = height
        return res

    @staticmethod
    def lat_lon_string_both_2_radians_full(line: str) -> CoordinatesWGS84:
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
        d = d1 + d2 / 60.0 + d3 / 3600.0
        if ns == 1:
            d *= -1.0
        return d

    @staticmethod
    def lat_lon_2_radians(d1: float, d2: float, d3: float, ns: int) -> float:
        d = GeoUtils.lat_lon_2_degrees(d1, d2, d3, ns)
        return d * GeoUtils.DEGS2RADS

    @staticmethod
    def lat_lon_string_2_degrees(s1: str, s2: str, s3: str, ns: int) -> float:
        d1, d2, d3 = float(s1), float(s2), float(s3)
        return GeoUtils.lat_lon_2_degrees(d1, d2, d3, ns)

    @staticmethod
    def degrees_2_lat_lon(d: float) -> Tuple[float, float, float, int]:
        ns = 1 if d < 0 else 0
        if ns == 1:
            d = -d
        d1 = np.floor(d)
        d2 = np.floor((d - d1) * 60.0)
        d3 = ((d - d1) * 60.0 - d2) * 60.0
        return float(d1), float(d2), d3, ns

    @staticmethod
    def radians_2_lat_lon(d: float) -> Tuple[float, float, float, int]:
        d_deg = d * GeoUtils.RADS2DEGS
        return GeoUtils.degrees_2_lat_lon(d_deg)

    @staticmethod
    def center_coordinates(l: List[CoordinatesWGS84]) -> Optional[CoordinatesWGS84]:
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
        return self.center_projection

    def change_geocentric_2_system_cartesian(
        self, geo: CoordinatesXYZ
    ) -> Optional[CoordinatesXYZ]:
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
        if abs(y) < GeoUtils.ALMOST_ZERO:
            theta = (x / abs(x)) * np.pi / 2.0 if x != 0 else 0.0
        else:
            theta = np.arctan2(x, y)
        if theta < 0.0:
            theta += 2 * np.pi
        return theta

    def calculate_earth_radius(self, geo: CoordinatesWGS84) -> float:
        if geo is None:
            return np.nan
        sin_lat = np.sin(geo.lat)
        return (self.A * (1.0 - self.E2)) / (1 - self.E2 * sin_lat**2) ** 1.5

    @staticmethod
    def calculate_rotation_matrix(lat: float, lon: float) -> GeneralMatrix:
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
        r1 = T1 - t
        return r @ r1

    @staticmethod
    def calculate_rotation_radar_matrix(
        R1: GeneralMatrix, r: GeneralMatrix
    ) -> GeneralMatrix:
        r2 = R1.transpose()
        return r @ r2

    @staticmethod
    def change_radar_spherical_2_radar_cartesian(
        polar_coordinates: CoordinatesPolar,
    ) -> Optional[CoordinatesXYZ]:
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
        if radar_coordinates not in self.rotation_radar_matrix_ht:
            r = self.obtain_rotation_matrix(radar_coordinates)
            self.rotation_radar_matrix_ht[radar_coordinates] = (
                GeoUtils.calculate_rotation_radar_matrix(self.R1, r)
            )
        return self.rotation_radar_matrix_ht[radar_coordinates]
