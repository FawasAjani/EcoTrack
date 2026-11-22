
import pytest

from emissions.electricity_calculator import (
    calculate_electricity_emissions,
    ELECTRICITY_EMISSION_FACTOR
)


def test_calculate_electricity_emissions():
    result = calculate_electricity_emissions(250)

    assert result["quantity_kwh"] == 250
    assert result["emissions_kg_co2"] == 49.45
    assert result["emission_factor"] == 0.1978
    assert result["emission_factor_unit"] == "kg CO2/kWh"
    assert result["emissions_unit"] == "kg CO2"


def test_calculate_small_electricity_consumption():
    result = calculate_electricity_emissions(10)

    assert result["emissions_kg_co2"] == 1.978


def test_calculate_decimal_electricity_consumption():
    result = calculate_electricity_emissions(125.5)

    assert result["emissions_kg_co2"] == round(
        125.5 * ELECTRICITY_EMISSION_FACTOR, 6
    )


def test_reject_zero_electricity_consumption():
    with pytest.raises(ValueError):
        calculate_electricity_emissions(0)


def test_reject_negative_electricity_consumption():
    with pytest.raises(ValueError):
        calculate_electricity_emissions(-100)


@pytest.mark.parametrize(
    "quantity",
    ["invalid", None, float("nan"), float("inf"), float("-inf")]
)
def test_reject_invalid_electricity_consumption(quantity):
    with pytest.raises(ValueError):
        calculate_electricity_emissions(quantity)
