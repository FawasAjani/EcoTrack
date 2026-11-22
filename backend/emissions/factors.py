
"""
Transport emission factors and assumptions for EcoTrack.

Values are centralised so they can be reviewed and updated
without changing the calculation functions.
"""

# Fuel combustion factors.
# Source: SEAI 2025 provisional road-fuel factors.
# These represent direct CO2 emissions, not full lifecycle CO2e.
FUEL_FACTORS = {
    "Petrol": {
        "factor": 2.311,
        "unit": "kg CO2/litre",
        "source": "SEAI 2025 provisional road-fuel factors",
        "year": 2025,
    },
    "Diesel": {
        "factor": 2.682,
        "unit": "kg CO2/litre",
        "source": "SEAI 2025 provisional road-fuel factors",
        "year": 2025,
    },
}

# Historical Irish passenger transport factors.
# Source: CIÉ, Challenge to Decarbonise Transport and Enable
# Modal Shift, September 2023 presentation.
# Underlying reporting year and detailed methodology were not specified.
# Unit: kg CO2e per passenger-kilometre.

PASSENGER_KM_FACTORS = {
    "Bus": {
        "Dublin Bus": {
            "factor": 0.024,
            "unit": "kg CO2e/passenger-km",
            "source": (
                "CIÉ, Challenge to Decarbonise Transport and Enable "
                "Modal Shift, September 2023 presentation. "
                "Underlying reporting year and methodology not specified."
            ),
            "year": 2023,
        },
        "Bus Éireann": {
            "factor": 0.031,
            "unit": "kg CO2e/passenger-km",
            "source": (
                "CIÉ, Challenge to Decarbonise Transport and Enable "
                "Modal Shift, September 2023 presentation. "
                "Underlying reporting year and methodology not specified."
            ),
            "year": 2023,
        },
    },
    "Train": {
        "Irish Rail": {
            "factor": 0.024,
            "unit": "kg CO2e/passenger-km",
            "source": (
                "CIÉ, Challenge to Decarbonise Transport and Enable "
                "Modal Shift, September 2023 presentation. "
                "Underlying reporting year and methodology not specified."
            ),
            "year": 2023,
        },
        "DART": {
            "factor": 0.014,
            "unit": "kg CO2e/passenger-km",
            "source": (
                "CIÉ, Challenge to Decarbonise Transport and Enable "
                "Modal Shift, September 2023 presentation. "
                "Underlying reporting year and methodology not specified."
            ),
            "year": 2023,
        },
    },
}

# Initial model boundary: operational emissions only.
ZERO_OPERATIONAL_EMISSIONS = {
    "Cycling": {
        "factor": 0.0,
        "unit": "kg CO2e/km",
        "source": "EcoTrack initial operational-emissions boundary",
        "year": 2026,
    },
    "Walking": {
        "factor": 0.0,
        "unit": "kg CO2e/km",
        "source": "EcoTrack initial operational-emissions boundary",
        "year": 2026,
    },
}

# Distance-based car fuel consumption assumptions.
# These are representative model assumptions, not measurements
# for every vehicle.
CAR_FUEL_CONSUMPTION = {
    "Petrol": 7.0,
    "Diesel": 6.0,
    "Hybrid": 5.3,
}

# Electric vehicle energy consumption assumption.
ELECTRIC_CAR_CONSUMPTION = {
    "consumption": 16.06,
    "unit": "kWh/100km",
    "source": "SEAI fuel comparison methodology",
    "year": 2025,
}

# Irish electricity emissions factor.
ELECTRICITY_EMISSION_FACTOR = {
    "factor": 0.1978,
    "unit": "kg CO2/kWh",
    "source": "SEAI 2025 provisional electricity conversion factor",
    "year": 2025,
}
