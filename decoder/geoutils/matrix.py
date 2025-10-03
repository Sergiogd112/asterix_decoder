"""GeneralMatrix: lightweight numpy-backed matrix wrapper used across geoutils."""

from __future__ import annotations
from typing import List, Optional, Tuple
import numpy as np
from scipy import linalg as la


class GeneralMatrix:
    """A small wrapper around numpy arrays to mirror the prior API.

    The wrapper provides convenience constructors and methods used by GeoUtils.
    """

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
            return float(self.A[i, j])
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
