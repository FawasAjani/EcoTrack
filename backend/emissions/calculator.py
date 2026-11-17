
"""
EcoTrack transport emissions calculator.

Car calculations estimate direct CO2 from fuel combustion.
Walking and cycling are assigned zero operational emissions.
Bus and train calculations use historical Irish
service-specific passenger-kilometre emission factors.
"""

from emissions.factors import (
    FUEL_FACTORS,
    PASSENGER_KM_FACTORS,
    ZERO_OPERATIONAL_EMISSIONS,
    CAR_FUEL_CONSUMPTION,
)


def calculate_car_emissions(distance_km, fuel_type):
    """Estimate direct CO2 emissions from a car journey."""

    if fuel_type not in FUEL_FACTORS:
        raise ValueError("Unsupported fuel type.")

    if distance_km < 0:
        raise ValueError("Distance cannot be negative.")

    fuel_consumption = CAR_FUEL_CONSUMPTION[fuel_type]
    fuel_factor = FUEL_FACTORS[fuel_type]

    # Convert litres per 100 km into litres used for this journey.
    litres_used = distance_km * fuel_consumption / 100

    emissions = litres_used * fuel_factor["factor"]

    return {
        "emissions": round(emissions, 6),
        "metric": "CO2",
        "unit": "kg CO2",
        "emission_factor": fuel_factor["factor"],
        "emission_factor_unit": fuel_factor["unit"],
        "emission_factor_source": fuel_factor["source"],
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

    if distance_km < 0:
        raise ValueError("Distance cannot be negative.")

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

    emissions = distance_km * factor

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

    if distance_km < 0:
        raise ValueError("Distance cannot be negative.")

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
