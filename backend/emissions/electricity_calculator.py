
import math


# SEAI 2025 provisional Irish electricity consumption factor.
# Source: https://www.seai.ie/data-and-insights/seai-statistics/conversion-factors
# Original unit: g CO2/kWh
# Converted unit: kg CO2/kWh

ELECTRICITY_EMISSION_FACTOR = 0.1978
ELECTRICITY_FACTOR_YEAR = 2025
ELECTRICITY_DATASET_NAME = "SEAI"
ELECTRICITY_DATASET_VERSION = "2025 provisional"
ELECTRICITY_FACTOR_UNIT = "kg CO2/kWh"


def calculate_electricity_emissions(quantity_kwh):
    """
    Calculate electricity-related CO2 emissions using the
    SEAI 2025 provisional Irish electricity consumption factor.

    Args:
        quantity_kwh: Electricity consumed in kilowatt-hours.

    Returns:
        Dictionary containing emissions and factor details.
    """

    try:
        quantity = float(quantity_kwh)
    except (TypeError, ValueError):
        raise ValueError(
            "Electricity consumption must be a valid number."
        )

    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError(
            "Electricity consumption must be greater than zero."
        )

    emissions = quantity * ELECTRICITY_EMISSION_FACTOR

    return {
        "emissions_kg_co2": round(emissions, 6),
        "quantity_kwh": quantity,
        "emission_factor": ELECTRICITY_EMISSION_FACTOR,
        "emission_factor_unit": ELECTRICITY_FACTOR_UNIT,
        "emissions_unit": "kg CO2",
        "dataset_name": ELECTRICITY_DATASET_NAME,
        "dataset_version": ELECTRICITY_DATASET_VERSION,
        "factor_year": ELECTRICITY_FACTOR_YEAR,
        "country_model": "Ireland"
    }
