
import pytest

from emissions.food_calculator import calculate_food_emissions


def test_beef_emissions_calculation():
    result = calculate_food_emissions(200, 32.1932)

    assert result["emissions_kg_co2e"] == pytest.approx(6.43864)
    assert result["quantity_grams"] == 200
    assert result["emission_factor"] == 32.1932


def test_chicken_emissions_calculation():
    result = calculate_food_emissions(150, 2.4261)

    assert result["emissions_kg_co2e"] == pytest.approx(0.363915)


def test_small_food_quantity():
    result = calculate_food_emissions(50, 0.5191)

    assert result["emissions_kg_co2e"] == pytest.approx(0.025955)


def test_zero_emission_factor():
    result = calculate_food_emissions(100, 0)

    assert result["emissions_kg_co2e"] == 0


def test_zero_quantity_is_rejected():
    with pytest.raises(ValueError):
        calculate_food_emissions(0, 32.1932)


def test_negative_quantity_is_rejected():
    with pytest.raises(ValueError):
        calculate_food_emissions(-100, 32.1932)


def test_negative_emission_factor_is_rejected():
    with pytest.raises(ValueError):
        calculate_food_emissions(100, -2.5)


@pytest.mark.parametrize(
    "quantity,factor",
    [
        ("invalid", 2.5),
        (100, "invalid"),
        (None, 2.5),
        (100, None),
    ],
)
def test_invalid_inputs_are_rejected(quantity, factor):
    with pytest.raises(ValueError):
        calculate_food_emissions(quantity, factor)


@pytest.mark.parametrize(
    "quantity,factor",
    [
        (float("nan"), 2.5),
        (100, float("inf")),
        (float("inf"), 2.5),
        (100, float("-inf")),
    ],
)
def test_non_finite_inputs_are_rejected(quantity, factor):
    with pytest.raises(ValueError):
        calculate_food_emissions(quantity, factor)
