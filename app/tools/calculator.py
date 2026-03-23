"""
Tool 3 – Calculation Tool

Performs mathematical computations on retrieved data.
Supports aggregations, KPI calculations, and derived metrics.
"""

import math

# Safe builtins allowed in expressions
_SAFE_BUILTINS = {
    "sum": sum,
    "len": len,
    "min": min,
    "max": max,
    "round": round,
    "abs": abs,
    "float": float,
    "int": int,
    "pow": pow,
    "sorted": sorted,
}

# Safe math functions
_SAFE_MATH = {
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "ceil": math.ceil,
    "floor": math.floor,
}


def calculate(expression: str, data: dict | None = None) -> dict:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A Python math expression string.
                    Can reference variables from the data dict.
        data: Optional dict of variables available to the expression.
              e.g. {"values": [1, 2, 3], "total_co2": 1500.0}

    Returns:
        dict with keys:
            - success: bool
            - result: computed value
            - expression: the original expression
            - error: error message if failed
    """
    if data is None:
        data = {}

    # Build a restricted namespace
    namespace = {}
    namespace.update(_SAFE_BUILTINS)
    namespace.update(_SAFE_MATH)
    namespace.update(data)
    namespace["__builtins__"] = {}  # Block access to real builtins

    try:
        result = eval(expression, namespace)
        return {
            "success": True,
            "result": result,
            "expression": expression,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "expression": expression,
            "error": str(e),
        }


# ---------------------
# Convenience helpers
# ---------------------

def average(values: list) -> float:
    """Calculate the average of a list of numbers."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def percentage(part: float, whole: float) -> float:
    """Calculate percentage."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


def ratio(a: float, b: float) -> float:
    """Calculate ratio a:b as a float."""
    if b == 0:
        return 0.0
    return round(a / b, 4)


def fuel_efficiency(distance_nm: float, fuel_mt: float) -> float:
    """Calculate fuel efficiency in NM per MT."""
    if fuel_mt == 0:
        return 0.0
    return round(distance_nm / fuel_mt, 4)


def emission_per_distance(co2_mt: float, distance_nm: float) -> float:
    """Calculate CO2 emission per nautical mile."""
    if distance_nm == 0:
        return 0.0
    return round(co2_mt / distance_nm, 4)
