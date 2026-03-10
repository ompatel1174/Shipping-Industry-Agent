"""
Tool 3 – Calculation Tool

Performs mathematical computations on retrieved SQL data.
Supports:
- Aggregations (sum, average, min, max)
- KPI calculations
- Derived metrics (fuel efficiency, emission per distance)
- Percentage and ratio calculations

Designed for Shipping Industry Agent.
"""

from typing import List, Dict, Any


class CalculationTool:
    """
    Enterprise-grade Calculation Tool
    Designed to work with structured SQL results (list of dictionaries)
    """

    # ===============================
    # 🔹 Basic Aggregations
    # ===============================

    def sum_column(self, data: List[Dict], column: str) -> float:
        return sum(row.get(column, 0) for row in data)

    def average_column(self, data: List[Dict], column: str) -> float:
        values = [row.get(column, 0) for row in data]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 4)

    def min_column(self, data: List[Dict], column: str) -> float:
        values = [row.get(column, 0) for row in data]
        return min(values) if values else 0.0

    def max_column(self, data: List[Dict], column: str) -> float:
        values = [row.get(column, 0) for row in data]
        return max(values) if values else 0.0

    # ===============================
    # 🔹 KPI / Derived Metrics
    # ===============================

    def fuel_efficiency(self, distance_nm: float, fuel_mt: float) -> float:
        """
        Nautical Miles per Metric Ton
        """
        if fuel_mt == 0:
            return 0.0
        return round(distance_nm / fuel_mt, 4)

    def emission_per_distance(self, co2_mt: float, distance_nm: float) -> float:
        """
        CO2 per Nautical Mile
        """
        if distance_nm == 0:
            return 0.0
        return round(co2_mt / distance_nm, 4)

    def percentage(self, part: float, whole: float) -> float:
        if whole == 0:
            return 0.0
        return round((part / whole) * 100, 2)

    def ratio(self, a: float, b: float) -> float:
        if b == 0:
            return 0.0
        return round(a / b, 4)

    def percentage_change(self, current: float, previous: float) -> float:
        if previous == 0:
            return 0.0
        return round(((current - previous) / previous) * 100, 2)

    # ===============================
    # 🔹 Row-wise Calculations
    # ===============================

    def fuel_efficiency_per_row(
        self,
        data: List[Dict],
        distance_column: str,
        fuel_column: str,
    ) -> List[Dict]:

        results = []

        for row in data:
            distance = row.get(distance_column, 0)
            fuel = row.get(fuel_column, 0)

            efficiency = self.fuel_efficiency(distance, fuel)

            new_row = row.copy()
            new_row["fuel_efficiency"] = efficiency
            results.append(new_row)

        return results

    def emission_per_row(
        self,
        data: List[Dict],
        co2_column: str,
        distance_column: str,
    ) -> List[Dict]:

        results = []

        for row in data:
            co2 = row.get(co2_column, 0)
            distance = row.get(distance_column, 0)

            emission = self.emission_per_distance(co2, distance)

            new_row = row.copy()
            new_row["emission_per_nm"] = emission
            results.append(new_row)

        return results

    # ===============================
    # 🔹 Unified Agent Interface
    # ===============================

    def execute(
        self,
        calculation_type: str,
        data: List[Dict] | None = None,
        **kwargs
    ) -> Any:
        """
        Unified entry point for Agent to call calculations.
        """

        if calculation_type == "sum":
            return self.sum_column(data, kwargs["column"])

        elif calculation_type == "average":
            return self.average_column(data, kwargs["column"])

        elif calculation_type == "min":
            return self.min_column(data, kwargs["column"])

        elif calculation_type == "max":
            return self.max_column(data, kwargs["column"])

        elif calculation_type == "fuel_efficiency":
            return self.fuel_efficiency(
                kwargs["distance"],
                kwargs["fuel"]
            )

        elif calculation_type == "fuel_efficiency_per_row":
            return self.fuel_efficiency_per_row(
                data,
                kwargs["distance_column"],
                kwargs["fuel_column"]
            )

        elif calculation_type == "emission_per_row":
            return self.emission_per_row(
                data,
                kwargs["co2_column"],
                kwargs["distance_column"]
            )

        elif calculation_type == "percentage":
            return self.percentage(
                kwargs["part"],
                kwargs["whole"]
            )

        elif calculation_type == "ratio":
            return self.ratio(
                kwargs["a"],
                kwargs["b"]
            )

        elif calculation_type == "percentage_change":
            return self.percentage_change(
                kwargs["current"],
                kwargs["previous"]
            )

        else:
            raise ValueError(f"Unsupported calculation type: {calculation_type}")