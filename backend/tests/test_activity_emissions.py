
import pytest

from routes.activities import calculate_activity_emissions


def test_petrol_car_activity_emissions():
    result = calculate_activity_emissions({
        "category": "Car",
        "quantity": 100,
        "unit": "km",
        "fuel_type": "Petrol",
    })

    assert result["emissions_kg_co2"] == pytest.approx(16.177)
    assert result["emissions_kg_co2e"] is None
    assert result["emission_factor"] == 2.311


def test_diesel_car_activity_emissions():
    result = calculate_activity_emissions({
        "category": "Car",
        "quantity": 100,
        "unit": "km",
        "fuel_type": "Diesel",
    })

    assert result["emissions_kg_co2"] == pytest.approx(16.092)
    assert result["emissions_kg_co2e"] is None
    assert result["emission_factor"] == 2.682


@pytest.mark.parametrize("category", ["Walking", "Cycling"])
def test_active_transport_has_zero_operational_emissions(category):
    result = calculate_activity_emissions({
        "category": category,
        "quantity": 10,
        "unit": "km",
    })

    assert result["emissions_kg_co2"] is None
    assert result["emissions_kg_co2e"] == 0.0


@pytest.mark.parametrize("category", ["Bus", "Train"])
def test_bus_and_train_emissions_remain_unavailable(category):
    result = calculate_activity_emissions({
        "category": category,
        "quantity": 20,
        "unit": "km",
    })

    assert result["emissions_kg_co2"] is None
    assert result["emissions_kg_co2e"] is None
    assert result["emission_factor"] is None


def test_transport_distance_must_use_kilometres():
    with pytest.raises(ValueError):
        calculate_activity_emissions({
            "category": "Car",
            "quantity": 100,
            "unit": "miles",
            "fuel_type": "Petrol",
        })


def test_unsupported_transport_category_is_rejected():
    with pytest.raises(ValueError):
        calculate_activity_emissions({
            "category": "Airplane",
            "quantity": 100,
            "unit": "km",
        })
