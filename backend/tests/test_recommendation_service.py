from datetime import date, timedelta

from services.recommendation_service import generate_recommendations


def current_date():
    return date.today()


def previous_date():
    return date.today() - timedelta(days=8)


def make_food_entry(entry_date, emissions):
    return {
        "activity_date": entry_date.isoformat(),
        "emissions_kg_co2e": emissions,
    }


def make_electricity_entry(entry_date, emissions):
    return {
        "activity_date": entry_date.isoformat(),
        "emissions_kg_co2": emissions,
    }


def make_transport_entry(entry_date, transport_mode):
    return {
        "activity_date": entry_date.isoformat(),
        "category": transport_mode,
    }
# Food and Electricity recommendations
def test_generates_food_and_electricity_recommendations():
    food_entries = [
        make_food_entry(previous_date(), 10.0),
        make_food_entry(current_date(), 15.0),
    ]

    electricity_entries = [
        make_electricity_entry(previous_date(), 5.0),
        make_electricity_entry(current_date(), 10.0),
    ]

    recommendations = generate_recommendations(
        [], food_entries, electricity_entries
    )

    categories = [item["category"] for item in recommendations]

    assert "Food" in categories
    assert "Electricity" in categories


# Transport recommendation
def test_generates_transport_recommendation_for_car_journey():
    transport_entries = [
        make_transport_entry(previous_date(), "Car"),
        make_transport_entry(current_date(), "Car"),
    ]

    recommendations = generate_recommendations(
        transport_entries, [], []
    )

    transport_recommendation = next(
        item for item in recommendations
        if item["category"] == "Transport"
    )

    assert transport_recommendation["priority"] == "medium"


# General recommendation when no records exist
def test_generates_general_recommendation_when_no_records_exist():
    recommendations = generate_recommendations([], [], [])

    assert len(recommendations) > 0
    assert recommendations[0]["category"] == "General"


# Food emissions increase
def test_food_recommendation_high_priority_when_emissions_increase():
    food_entries = [
        make_food_entry(previous_date(), 10.0),
        make_food_entry(current_date(), 12.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert food_recommendation["priority"] == "high"
    assert "20.0% increase" in food_recommendation["message"]


# Food emissions decrease
def test_food_recommendation_low_priority_when_emissions_decrease():
    food_entries = [
        make_food_entry(previous_date(), 10.0),
        make_food_entry(current_date(), 8.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert food_recommendation["priority"] == "low"
    assert "20.0% decrease" in food_recommendation["message"]


# Stable Food emissions
def test_food_recommendation_medium_priority_when_emissions_stable():
    food_entries = [
        make_food_entry(previous_date(), 10.0),
        make_food_entry(current_date(), 10.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert food_recommendation["priority"] == "medium"
    assert "stable" in food_recommendation["message"].lower()


# Large percentage increase from a small baseline
def test_food_recommendation_large_percentage_from_small_baseline():
    food_entries = [
        make_food_entry(previous_date(), 0.1),
        make_food_entry(current_date(), 1.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert food_recommendation["priority"] == "high"
    assert "900.0% increase" in food_recommendation["message"]


# Missing historical data
def test_food_recommendation_when_previous_data_missing():
    food_entries = [
        make_food_entry(current_date(), 10.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert food_recommendation["priority"] == "medium"
    assert "not enough previous-period data" in food_recommendation["message"].lower()

# Zero current Food emissions
def test_zero_current_food_emissions_generates_food_recommendation():
    food_entries = [
        make_food_entry(previous_date(), 5.0),
        make_food_entry(current_date(), 0.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert food_recommendation["priority"] == "low"
    assert "100.0% decrease" in food_recommendation["message"]


# Invalid Food emissions
def test_invalid_food_emissions_do_not_crash():
    food_entries = [
        make_food_entry(previous_date(), "invalid"),
        make_food_entry(current_date(), 10.0),
    ]

    recommendations = generate_recommendations([], food_entries, [])

    assert isinstance(recommendations, list)


# Invalid Electricity emissions
def test_invalid_electricity_emissions_do_not_crash():
    electricity_entries = [
        make_electricity_entry(previous_date(), "invalid"),
        make_electricity_entry(current_date(), 10.0),
    ]

    recommendations = generate_recommendations(
        [], [], electricity_entries
    )

    assert isinstance(recommendations, list)


# Electricity emissions increase
def test_electricity_recommendation_high_priority_when_emissions_increase():
    electricity_entries = [
        make_electricity_entry(previous_date(), 10.0),
        make_electricity_entry(current_date(), 12.0),
    ]

    recommendations = generate_recommendations(
        [], [], electricity_entries
    )

    electricity_recommendation = next(
        item for item in recommendations
        if item["category"] == "Electricity"
    )

    assert electricity_recommendation["priority"] == "high"
    assert "20.0% increase" in electricity_recommendation["message"]


# Electricity emissions decrease
def test_electricity_recommendation_low_priority_when_emissions_decrease():
    electricity_entries = [
        make_electricity_entry(previous_date(), 10.0),
        make_electricity_entry(current_date(), 8.0),
    ]

    recommendations = generate_recommendations(
        [], [], electricity_entries
    )

    electricity_recommendation = next(
        item for item in recommendations
        if item["category"] == "Electricity"
    )

    assert electricity_recommendation["priority"] == "low"
    assert "20.0% decrease" in electricity_recommendation["message"]


# Transport with no historical data
def test_transport_recommendation_medium_priority_when_previous_data_missing():
    transport_entries = [
        make_transport_entry(current_date(), "Car"),
    ]

    recommendations = generate_recommendations(
        transport_entries, [], []
    )

    transport_recommendation = next(
        item for item in recommendations
        if item["category"] == "Transport"
    )

    assert transport_recommendation["priority"] == "medium"


# Transport increase
def test_transport_recommendation_high_priority_when_journeys_increase():
    transport_entries = [
        make_transport_entry(previous_date(), "Car"),
        make_transport_entry(current_date(), "Car"),
        make_transport_entry(current_date(), "Car"),
        make_transport_entry(current_date(), "Car"),
    ]

    recommendations = generate_recommendations(
        transport_entries, [], []
    )

    transport_recommendation = next(
        item for item in recommendations
        if item["category"] == "Transport"
    )

    assert transport_recommendation["priority"] == "high"
    assert "200.0% increase" in transport_recommendation["message"]

  # Reject NaN and infinite food emissions
def test_invalid_non_finite_food_emissions_are_handled():
    food_entries = [
        make_food_entry(current_date(), float("nan")),
        make_food_entry(current_date(), float("inf")),
        make_food_entry(current_date(), 10.0),
    ]

    recommendations = generate_recommendations(
        [], food_entries, []
    )

    food_recommendation = next(
        item for item in recommendations
        if item["category"] == "Food"
    )

    assert "10.00 kg CO2e" in food_recommendation["message"]


# Zero current electricity emissions still generate a recommendation
def test_zero_current_electricity_emissions_generate_recommendation():
    electricity_entries = [
        make_electricity_entry(previous_date(), 5.0),
        make_electricity_entry(current_date(), 0.0),
    ]

    recommendations = generate_recommendations(
        [], [], electricity_entries
    )

    electricity_recommendation = next(
        item for item in recommendations
        if item["category"] == "Electricity"
    )

    assert electricity_recommendation["priority"] == "low"
    assert "0.00 kg CO2" in electricity_recommendation["message"]
