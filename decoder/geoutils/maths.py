"""Small math helpers used by geoutils."""

import numpy as np


class Maths:
    """Small math utility functions."""

    @staticmethod
    def hypot(a: float, b: float) -> float:
        """Stable hypot implementation (avoid overflow/underflow)."""
        if abs(a) > abs(b):
            r = b / a
            return abs(a) * np.sqrt(1 + r * r)
        elif b != 0:
            r = a / b
            return abs(b) * np.sqrt(1 + r * r)
        else:
            return 0.0
