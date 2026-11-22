
"""
EcoTrack transport emissions calculator.

Car calculations estimate operational CO2 emissions.
Electric cars use electricity consumption and the Irish grid factor.
Conventional hybrids use an assumed petrol consumption rate.
Walking and cycling are assigned zero operational emissions.
Bus and train use historical Irish passenger-kilometre factors.
"""

import math

from emissions.factors import (
    FUEL_FACTORS,
    PASSENGER_KM_FACTORS,
    ZERO_OPERATIONAL_EMISSIONS,
    CAR_FUEL_CONSUMPTION,
    ELECTRIC_CAR_CONSUMPTION,
    ELECTRICITY_EMISSION_FACTOR,
)


def validate_distance(distance_km):
    """Validate a transport distance."""

    try:
        distance = float(distance_km)
    except (TypeError, ValueError):
        raise ValueError("Distance must be a valid number.")

    if not math.isfinite(distance) or distance < 0:
        raise ValueError("Distance cannot be negative.")

    return distance


def calculate_car_emissions(distance_km, fuel_type):
    """Estimate operational CO2 emissions from a car journey."""

    distance = validate_distance(distance_km)

    # Electric vehicle calculation
    if fuel_type == "Electric":
        consumption = ELECTRIC_CAR_CONSUMPTION
        electricity_factor = ELECTRICITY_EMISSION_FACTOR

        energy_used = (
            distance * consumption["consumption"] / 100
        )

        emissions = energy_used * electricity_factor["factor"]

        return {
            "emissions": round(emissions, 6),
            "metric": "CO2",
            "unit": "kg CO2",
            "emission_factor": electricity_factor["factor"],
            "emission_factor_unit": electricity_factor["unit"],
            "emission_factor_source": (
                f'{electricity_factor["source"]}; '
                f'assumed vehicle consumption: '
                f'{consumption["consumption"]} '
                f'{consumption["unit"]}; '
                f'{consumption["source"]}'
            ),
            "emission_factor_year": electricity_factor["year"],
            "energy_consumption_kwh_per_100km": (
                consumption["consumption"]
            ),
            "electricity_used_kwh": round(energy_used, 6),
        }

    # Petrol, Diesel and Hybrid calculation
    if fuel_type not in CAR_FUEL_CONSUMPTION:
        raise ValueError("Unsupported fuel type.")

    fuel_consumption = CAR_FUEL_CONSUMPTION[fuel_type]

    # A conventional hybrid uses the petrol combustion factor
    # with a separate assumed fuel-consumption rate.
    if fuel_type == "Hybrid":
        fuel_factor = FUEL_FACTORS["Petrol"]
    else:
        fuel_factor = FUEL_FACTORS[fuel_type]

    litres_used = distance * fuel_consumption / 100
    emissions = litres_used * fuel_factor["factor"]

    source = fuel_factor["source"]

    if fuel_type == "Hybrid":
        source = (
            f"{source}; conventional hybrid petrol consumption "
            f"assumption: {fuel_consumption} L/100km"
        )

    return {
        "emissions": round(emissions, 6),
        "metric": "CO2",
        "unit": "kg CO2",
        "emission_factor": fuel_factor["factor"],
        "emission_factor_unit": fuel_factor["unit"],
        "emission_factor_source": source,
        "emission_factor_year": fuel_factor["year"],
        "fuel_consumption_l_per_100km": fuel_consumption,
    }


def calculate_passenger_transport_emissions(
    distance_km,
    transport_type,
    transport_service
):
    """
    Calculate bus or train emissions using the selected service factor.

    Emissions are calculated in kg CO2e using passenger-kilometres.
    """

    distance = validate_distance(distance_km)

    if transport_type not in PASSENGER_KM_FACTORS:
        raise ValueError("Unsupported passenger transport type.")

    service_factors = PASSENGER_KM_FACTORS[transport_type]

    if not transport_service:
        raise ValueError(
            f"A service must be selected for {transport_type} journeys."
        )

    if transport_service not in service_factors:
        raise ValueError(
            f"Unsupported {transport_type} service: {transport_service}."
        )

    factor_data = service_factors[transport_service]
    factor = factor_data["factor"]

    emissions = distance * factor

    return {
        "emissions": round(emissions, 6),
        "metric": "CO2e",
        "unit": "kg CO2e",
        "emission_factor": factor,
        "emission_factor_unit": factor_data["unit"],
        "emission_factor_source": factor_data["source"],
        "emission_factor_year": factor_data["year"],
    }


def calculate_zero_operational_emissions(distance_km, activity_type):
    """Return zero operational emissions for walking or cycling."""

    distance = validate_distance(distance_km)

    if activity_type not in ZERO_OPERATIONAL_EMISSIONS:
        raise ValueError("Unsupported activity type.")

    factor_data = ZERO_OPERATIONAL_EMISSIONS[activity_type]

    return {
        "emissions": 0.0,
        "metric": "CO2e",
        "unit": "kg CO2e",
        "emission_factor": factor_data["factor"],
        "emission_factor_unit": factor_data["unit"],
        "emission_factor_source": factor_data["source"],
        "emission_factor_year": factor_data["year"],
    }
