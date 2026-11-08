
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
    assert result["emission_factor"] == 2.311


def test_diesel_car_emissions():
    result = calculate_car_emissions(100, "Diesel")

    assert result["emissions"] == pytest.approx(16.092)
    assert result["metric"] == "CO2"
    assert result["emission_factor"] == 2.682


def test_zero_distance_car_journey():
    result = calculate_car_emissions(0, "Petrol")

    assert result["emissions"] == 0


def test_negative_car_distance_is_rejected():
    with pytest.raises(ValueError):
        calculate_car_emissions(-10, "Petrol")


def test_unsupported_car_fuel_is_rejected():
    with pytest.raises(ValueError):
        calculate_car_emissions(100, "Electric")


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


def test_bus_calculation_waits_for_verified_factor():
    with pytest.raises(NotImplementedError):
        calculate_passenger_transport_emissions(20, "Bus")


def test_train_calculation_waits_for_verified_factor():
    with pytest.raises(NotImplementedError):
        calculate_passenger_transport_emissions(20, "Train")
