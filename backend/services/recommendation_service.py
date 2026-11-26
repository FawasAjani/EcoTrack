
import math
from datetime import date, timedelta


def generate_recommendations(
    activities,
    food_entries,
    electricity_entries
):
    """
    Generate personalised sustainability recommendations.

    Compare the latest seven days with the preceding seven days.
    Food uses CO2e, while electricity and transport use CO2.

    Priority is based on percentage change, not absolute
    emissions across different categories.
    """

    recommendations = []

    today = date.today()
    current_start = today - timedelta(days=6)
    previous_start = today - timedelta(days=13)
    previous_end = today - timedelta(days=7)

    def get_record_date(record):
        try:
            return date.fromisoformat(
                str(record.get("activity_date", ""))[:10]
            )
        except (ValueError, TypeError):
            return None

    def is_valid_amount(value):
        try:
            amount = float(value or 0)

            if not math.isfinite(amount) or amount < 0:
                return 0.0

            return amount

        except (ValueError, TypeError, OverflowError):
            return 0.0

    def split_period(records):
        current = []
        previous = []

        for record in records:
            record_date = get_record_date(record)

            if record_date is None:
                continue

            if current_start <= record_date <= today:
                current.append(record)
            elif previous_start <= record_date <= previous_end:
                previous.append(record)

        return current, previous

    def calculate_total(records, field):
        return sum(
            is_valid_amount(item.get(field))
            for item in records
        )

    def calculate_priority(current, previous):
        """
        Return priority based on change from the previous period.

        Changes of 20% or more determine high or low priority.
        Insufficient historical data defaults to medium.
        """

        if previous <= 0:
            return "medium", None

        percentage_change = (
            (current - previous) / previous
        ) * 100

        if percentage_change >= 20:
            return "high", percentage_change

        if percentage_change <= -20:
            return "low", percentage_change

        return "medium", percentage_change

    def comparison_message(change):
        if change is None:
            return (
                " There is not enough previous-period data "
                "to compare your progress yet."
            )

        if change >= 20:
            return (
                f" This is a {change:.1f}% increase compared "
                "with the previous seven days."
            )

        if change <= -20:
            return (
                f" This is a {abs(change):.1f}% decrease "
                "compared with the previous seven days."
            )

        return (
            " Your recorded impact has remained relatively "
            "stable compared with the previous seven days."
        )

    # FOOD: CO2e
    current_food, previous_food = split_period(food_entries)

    food_total = calculate_total(
        current_food, "emissions_kg_co2e"
    )

    previous_food_total = calculate_total(
        previous_food, "emissions_kg_co2e"
    )

    if current_food:
        priority, change = calculate_priority(
            food_total, previous_food_total
        )

        recommendations.append({
            "category": "Food",
            "title": "Review your food-related footprint",
            "message": (
                f"Your recorded food entries produced "
                f"{food_total:.2f} kg CO2e over the last "
                f"seven days."
                f"{comparison_message(change)} "
                "Consider including more lower-emission "
                "foods in your meals."
            ),
            "impact_type": "CO2e",
            "priority": priority
        })

    # ELECTRICITY: Direct CO2
    current_electricity, previous_electricity = split_period(
        electricity_entries
    )

    electricity_total = calculate_total(
        current_electricity, "emissions_kg_co2"
    )

    previous_electricity_total = calculate_total(
        previous_electricity, "emissions_kg_co2"
    )

    if current_electricity:
        priority, change = calculate_priority(
            electricity_total,
            previous_electricity_total
        )

        recommendations.append({
            "category": "Electricity",
            "title": "Look for opportunities to save electricity",
            "message": (
                f"Your recorded electricity use produced "
                f"{electricity_total:.2f} kg CO2 over the last "
                f"seven days."
                f"{comparison_message(change)} "
                "Switching off unused devices and reducing "
                "unnecessary electricity use may help."
            ),
            "impact_type": "CO2",
            "priority": priority
        })

    # TRANSPORT: Compare car journey counts
    current_activities, previous_activities = split_period(
        activities
    )

    def count_car_journeys(records):
        return sum(
            1 for item in records
            if str(item.get("category", "")).strip().lower()
            == "car"
        )

    current_car_journeys = count_car_journeys(
        current_activities
    )

    previous_car_journeys = count_car_journeys(
        previous_activities
    )

    if current_car_journeys > 0:
        priority, change = calculate_priority(
            current_car_journeys,
            previous_car_journeys
        )

        recommendations.append({
            "category": "Transport",
            "title": "Consider alternatives for some car journeys",
            "message": (
                f"You recorded {current_car_journeys} car "
                f"journeys over the last seven days."
                f"{comparison_message(change)} "
                "Where practical, consider walking, cycling "
                "or public transport for suitable journeys."
            ),
            "impact_type": "CO2",
            "priority": priority
        })

    # FALLBACK
    if not recommendations:
        recommendations.append({
            "category": "General",
            "title": "Keep building your sustainability history",
            "message": (
                "Add activity, food or electricity records "
                "to receive recommendations based on your "
                "own tracking data."
            ),
            "impact_type": "General",
            "priority": "low"
        })

    return recommendations
