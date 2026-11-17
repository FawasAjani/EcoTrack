
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


@pytest.mark.parametrize(
    "category,service,expected_factor,expected_emissions",
    [
        ("Bus", "Dublin Bus", 0.024, 0.48),
        ("Bus", "Bus Éireann", 0.031, 0.62),
        ("Train", "Irish Rail", 0.024, 0.48),
        ("Train", "DART", 0.014, 0.28),
    ],
)
def test_passenger_transport_emissions(
    category,
    service,
    expected_factor,
    expected_emissions,
):
    result = calculate_activity_emissions({
        "category": category,
        "quantity": 20,
        "unit": "km",
        "transport_service": service,
    })

    assert result["emissions_kg_co2"] is None
    assert result["emissions_kg_co2e"] == pytest.approx(
        expected_emissions
    )
    assert result["emission_factor"] == expected_factor
    assert result["emission_factor_unit"] == (
        "kg CO2e/passenger-km"
    )
    assert result["emission_factor_source"]
    assert result["emission_factor_year"] == 2023


@pytest.mark.parametrize("category", ["Bus", "Train"])
def test_passenger_transport_requires_service(category):
    with pytest.raises(ValueError):
        calculate_activity_emissions({
            "category": category,
            "quantity": 20,
            "unit": "km",
        })


@pytest.mark.parametrize(
    "category,invalid_service",
    [
        ("Bus", "Irish Rail"),
        ("Train", "Dublin Bus"),
        ("Bus", "Unknown Bus"),
        ("Train", "Unknown Train"),
    ],
)
def test_invalid_transport_service_is_rejected(
    category,
    invalid_service,
):
    with pytest.raises(ValueError):
        calculate_activity_emissions({
            "category": category,
            "quantity": 20,
            "unit": "km",
            "transport_service": invalid_service,
        })


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
