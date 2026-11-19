
import math


def calculate_food_emissions(quantity_grams, emission_factor):
    """
    Calculate food-related emissions using the SAFAD emission factor.

    Args:
        quantity_grams: Food quantity in grams.
        emission_factor: kg CO2e per kg of food.

    Returns:
        Dictionary containing calculated emissions and factor details.
    """

    try:
        quantity = float(quantity_grams)
        factor = float(emission_factor)
    except (TypeError, ValueError):
        raise ValueError(
            "Quantity and emission factor must be valid numbers."
        )

    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError(
            "Food quantity must be greater than zero."
        )

    if not math.isfinite(factor) or factor < 0:
        raise ValueError(
            "Emission factor must be a non-negative number."
        )

    # Convert grams to kilograms.
    quantity_kg = quantity / 1000

    # Calculate total food emissions.
    emissions = quantity_kg * factor

    return {
        "emissions_kg_co2e": round(emissions, 6),
        "quantity_grams": quantity,
        "emission_factor": factor,
        "emission_factor_unit": "kg CO2e/kg",
        "emissions_unit": "kg CO2e",
    }
