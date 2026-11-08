
"""
Transport emission factors and assumptions for EcoTrack.

Values are kept centralised so that they can be reviewed and updated
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

# Passenger transport factors.
# PLACEHOLDERS: replace these with verified Irish IPTEM factors
# before using them for production emissions reporting.
PASSENGER_KM_FACTORS = {
    "Bus": {
        "factor": None,
        "unit": "kg CO2e/passenger-km",
        "source": "Irish IPTEM dataset - verification required",
        "year": None,
    },
    "Train": {
        "factor": None,
        "unit": "kg CO2e/passenger-km",
        "source": "Irish IPTEM dataset - verification required",
        "year": None,
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

# Temporary assumption for distance-based car estimates.
# This is a configurable assumption, not a verified fleet average.
CAR_FUEL_CONSUMPTION = {
    "Petrol": 7.0,
    "Diesel": 6.0,
}
