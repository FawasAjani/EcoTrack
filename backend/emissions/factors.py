
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

# Historical Irish passenger transport factors.
#
# Source: CIÉ presentation:
# "Challenge to Decarbonise Transport and Enable Modal Shift"
# Presented by Caoimhe Donnelly, Chief Sustainability Officer,
# September 2023.
#
# The presentation's underlying reporting year and detailed
# calculation methodology were not specified in the material reviewed.
# These are historical published comparison factors, not verified
# current emission rates.
#
# Values converted from grams to kilograms:
# 24 g = 0.024 kg
# 31 g = 0.031 kg
# 14 g = 0.014 kg
#
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

# Temporary assumption for distance-based car estimates.
# This is a configurable assumption, not a verified fleet average.
CAR_FUEL_CONSUMPTION = {
    "Petrol": 7.0,
    "Diesel": 6.0,
}
