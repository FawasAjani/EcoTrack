
import pytest

from emissions.calculator import (
    calculate_car_emissions,
    calculate_passenger_transport_emissions,
    calculate_zero_operational_emissions,
)


def test_petrol_car_emissions():
    result = calculate_car_emissions(100, "Petrol")

    assert result["emissions"] == pytest.approx(16.177)
    assert result["metric"] == "CO2"
    assert result["unit"] == "kg CO2"
    assert result["emission_factor"] == 2.311


def test_diesel_car_emissions():
    result = calculate_car_emissions(100, "Diesel")

    assert result["emissions"] == pytest.approx(16.092)
    assert result["metric"] == "CO2"
    assert result["unit"] == "kg CO2"
    assert result["emission_factor"] == 2.682


def test_electric_car_emissions():
    result = calculate_car_emissions(100, "Electric")

    assert result["emissions"] == pytest.approx(3.176668)
    assert result["metric"] == "CO2"
    assert result["unit"] == "kg CO2"
    assert result["emission_factor"] == 0.1978
    assert result["electricity_used_kwh"] == pytest.approx(16.06)
    assert result["energy_consumption_kwh_per_100km"] == 16.06


def test_hybrid_car_emissions():
    result = calculate_car_emissions(100, "Hybrid")

    assert result["emissions"] == pytest.approx(12.2483)
    assert result["metric"] == "CO2"
    assert result["unit"] == "kg CO2"
    assert result["emission_factor"] == 2.311
    assert result["fuel_consumption_l_per_100km"] == 5.3
    assert "hybrid" in result["emission_factor_source"].lower()


def test_zero_distance_car_journey():
    result = calculate_car_emissions(0, "Petrol")

    assert result["emissions"] == 0


@pytest.mark.parametrize("fuel_type", ["Petrol", "Diesel", "Electric", "Hybrid"])
def test_zero_distance_for_all_car_types(fuel_type):
    result = calculate_car_emissions(0, fuel_type)

    assert result["emissions"] == 0


def test_negative_car_distance_is_rejected():
    with pytest.raises(ValueError):
        calculate_car_emissions(-10, "Petrol")


@pytest.mark.parametrize("fuel_type", ["Petrol", "Diesel", "Electric", "Hybrid"])
def test_negative_distance_is_rejected_for_all_car_types(fuel_type):
    with pytest.raises(ValueError):
        calculate_car_emissions(-10, fuel_type)


def test_unsupported_car_fuel_is_rejected():
    with pytest.raises(ValueError):
        calculate_car_emissions(100, "Hydrogen")


def test_cycling_has_zero_operational_emissions():
    result = calculate_zero_operational_emissions(10, "Cycling")

    assert result["emissions"] == 0
    assert result["metric"] == "CO2e"


def test_walking_has_zero_operational_emissions():
    result = calculate_zero_operational_emissions(5, "Walking")

    assert result["emissions"] == 0


def test_negative_walking_distance_is_rejected():
    with pytest.raises(ValueError):
        calculate_zero_operational_emissions(-5, "Walking")


@pytest.mark.parametrize(
    "transport_type,transport_service,expected_factor,expected_emissions",
    [
        ("Bus", "Dublin Bus", 0.024, 0.48),
        ("Bus", "Bus Éireann", 0.031, 0.62),
        ("Train", "Irish Rail", 0.024, 0.48),
        ("Train", "DART", 0.014, 0.28),
    ],
)
def test_passenger_transport_emissions(
    transport_type,
    transport_service,
    expected_factor,
    expected_emissions,
):
    result = calculate_passenger_transport_emissions(
        20,
        transport_type,
        transport_service,
    )

    assert result["emissions"] == pytest.approx(expected_emissions)
    assert result["emission_factor"] == expected_factor
    assert result["emission_factor_unit"] == (
        "kg CO2e/passenger-km"
    )
    assert result["metric"] == "CO2e"
    assert result["emission_factor_source"]
    assert result["emission_factor_year"] == 2023


@pytest.mark.parametrize(
    "transport_type,invalid_service",
    [
        ("Bus", "Irish Rail"),
        ("Train", "Dublin Bus"),
        ("Bus", "Unknown Bus"),
        ("Train", "Unknown Train"),
    ],
)
def test_invalid_passenger_transport_service_is_rejected(
    transport_type,
    invalid_service,
):
    with pytest.raises(ValueError):
        calculate_passenger_transport_emissions(
            20,
            transport_type,
            invalid_service,
        )


@pytest.mark.parametrize("transport_type", ["Bus", "Train"])
def test_passenger_transport_requires_service(transport_type):
    with pytest.raises(ValueError):
        calculate_passenger_transport_emissions(
            20,
            transport_type,
            None,
        )


def test_negative_passenger_transport_distance_is_rejected():
    with pytest.raises(ValueError):
        calculate_passenger_transport_emissions(
            -20,
            "Bus",
            "Dublin Bus",
        )
