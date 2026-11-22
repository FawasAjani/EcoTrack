
from datetime import date, timedelta
import math

from flask import Blueprint, jsonify, request

from routes.activities import get_authenticated_client


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)

BATCH_SIZE = 500


def get_all_user_records(client, table_name, columns, user_id):
    """Retrieve all records for a user in batches."""

    records = []
    offset = 0

    while True:
        response = (
            client.table(table_name)
            .select(columns)
            .eq("user_id", user_id)
            .order("id")
            .range(offset, offset + BATCH_SIZE - 1)
            .execute()
        )

        batch = response.data or []
        records.extend(batch)

        if len(batch) < BATCH_SIZE:
            break

        offset += BATCH_SIZE

    return records


def safe_emissions(value):
    """Convert an emissions value into a safe, non-negative number."""

    try:
        result = float(value)

        if not math.isfinite(result) or result < 0:
            return None

        return result

    except (TypeError, ValueError, OverflowError):
        return None


def parse_activity_date(value):
    """Safely parse a date returned by Supabase."""

    if not value:
        return None

    try:
        if isinstance(value, date):
            return date.fromisoformat(value.isoformat()[:10])

        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def create_daily_summary(day_key):
    return {
        "date": day_key,
        "food_co2e": 0.0,
        "activity_co2": 0.0,
        "activity_co2e": 0.0,
        "electricity_co2": 0.0,
        "total_co2": 0.0,
        "total_co2e": 0.0
    }


def round_summary_values(summary):
    """Round emissions values consistently for API output."""

    for key, value in summary.items():
        if key != "date" and isinstance(value, (int, float)):
            summary[key] = round(value, 6)

    return summary


@dashboard_bp.route("/summary", methods=["GET"])
def get_dashboard_summary():

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    today_value = request.args.get("today")

    if today_value:
        try:
            today = date.fromisoformat(today_value)

            if today.isoformat() != today_value:
                raise ValueError()

        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Today must use YYYY-MM-DD format."
            }), 400
    else:
        today = date.today()

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    try:
        food_entries = get_all_user_records(
            client,
            "food_entries",
            "user_id, activity_date, emissions_kg_co2e",
            user_id
        )

        activities = get_all_user_records(
            client,
            "activities",
            (
                "user_id, activity_date, "
                "emissions_kg_co2, emissions_kg_co2e"
            ),
            user_id
        )

        electricity_entries = get_all_user_records(
            client,
            "electricity_entries",
            "user_id, activity_date, emissions_kg_co2",
            user_id
        )

        weekly_breakdown = {}

        current_day = week_start

        while current_day <= week_end:
            day_key = current_day.isoformat()
            weekly_breakdown[day_key] = create_daily_summary(day_key)
            current_day += timedelta(days=1)

        totals = {
            "food_co2e": 0.0,
            "activity_co2": 0.0,
            "activity_co2e": 0.0,
            "electricity_co2": 0.0
        }

        today_totals = {
            "food_co2e": 0.0,
            "activity_co2": 0.0,
            "activity_co2e": 0.0,
            "electricity_co2": 0.0
        }

        weekly_totals = {
            "food_co2e": 0.0,
            "activity_co2": 0.0,
            "activity_co2e": 0.0,
            "electricity_co2": 0.0
        }

        uncalculated_activities = 0
        ambiguous_activities = 0
        today_uncalculated_activities = 0
        weekly_uncalculated_activities = 0

        # Food entries: CO2e.
        for entry in food_entries:
            emissions = safe_emissions(
                entry.get("emissions_kg_co2e")
            )

            if emissions is None:
                continue

            totals["food_co2e"] += emissions

            entry_date = parse_activity_date(
                entry.get("activity_date")
            )

            if entry_date == today:
                today_totals["food_co2e"] += emissions

            if entry_date and week_start <= entry_date <= week_end:
                weekly_totals["food_co2e"] += emissions
                weekly_breakdown[entry_date.isoformat()][
                    "food_co2e"
                ] += emissions

        # Activity entries: keep CO2 and CO2e separate.
        for activity in activities:
            raw_co2 = activity.get("emissions_kg_co2")
            raw_co2e = activity.get("emissions_kg_co2e")

            co2 = safe_emissions(raw_co2)
            co2e = safe_emissions(raw_co2e)

            has_co2 = raw_co2 is not None
            has_co2e = raw_co2e is not None

            activity_date = parse_activity_date(
                activity.get("activity_date")
            )

            # Both fields populated: ambiguous classification.
            if has_co2 and has_co2e:
                ambiguous_activities += 1
                continue

            # Neither field populated, or invalid emissions value.
            if (
                not has_co2 and not has_co2e
            ) or (
                has_co2 and co2 is None
            ) or (
                has_co2e and co2e is None
            ):
                uncalculated_activities += 1

                if activity_date == today:
                    today_uncalculated_activities += 1

                if (
                    activity_date
                    and week_start <= activity_date <= week_end
                ):
                    weekly_uncalculated_activities += 1

                continue

            if has_co2:
                metric = "activity_co2"
                emissions = co2
            else:
                metric = "activity_co2e"
                emissions = co2e

            totals[metric] += emissions

            if activity_date == today:
                today_totals[metric] += emissions

            if activity_date and week_start <= activity_date <= week_end:
                weekly_totals[metric] += emissions
                weekly_breakdown[activity_date.isoformat()][
                    metric
                ] += emissions

        # Household electricity entries: direct CO2.
        for entry in electricity_entries:
            emissions = safe_emissions(
                entry.get("emissions_kg_co2")
            )

            if emissions is None:
                continue

            totals["electricity_co2"] += emissions

            entry_date = parse_activity_date(
                entry.get("activity_date")
            )

            if entry_date == today:
                today_totals["electricity_co2"] += emissions

            if entry_date and week_start <= entry_date <= week_end:
                weekly_totals["electricity_co2"] += emissions
                weekly_breakdown[entry_date.isoformat()][
                    "electricity_co2"
                ] += emissions

        def calculate_combined_values(values):
            return {
                "total_co2": (
                    values["activity_co2"]
                    + values["electricity_co2"]
                ),
                "total_co2e": (
                    values["food_co2e"]
                    + values["activity_co2e"]
                )
            }

        combined_totals = calculate_combined_values(totals)
        today_combined = calculate_combined_values(today_totals)
        weekly_combined = calculate_combined_values(weekly_totals)

        # Calculate separate daily CO2 and CO2e totals.
        for day in weekly_breakdown.values():
            day["total_co2"] = (
                day["activity_co2"] + day["electricity_co2"]
            )

            day["total_co2e"] = (
                day["food_co2e"] + day["activity_co2e"]
            )

            round_summary_values(day)

        summary = {
            "total_food_co2e": totals["food_co2e"],
            "total_activity_co2": totals["activity_co2"],
            "total_activity_co2e": totals["activity_co2e"],
            "total_electricity_co2": totals["electricity_co2"],
            "total_co2": combined_totals["total_co2"],
            "total_co2e": combined_totals["total_co2e"],

            "today_food_co2e": today_totals["food_co2e"],
            "today_activity_co2": today_totals["activity_co2"],
            "today_activity_co2e": today_totals["activity_co2e"],
            "today_electricity_co2": today_totals["electricity_co2"],
            "today_co2": today_combined["total_co2"],
            "today_co2e": today_combined["total_co2e"],

            "weekly_food_co2e": weekly_totals["food_co2e"],
            "weekly_activity_co2": weekly_totals["activity_co2"],
            "weekly_activity_co2e": weekly_totals["activity_co2e"],
            "weekly_electricity_co2": weekly_totals["electricity_co2"],
            "weekly_co2": weekly_combined["total_co2"],
            "weekly_co2e": weekly_combined["total_co2e"],

            "uncalculated_activities": uncalculated_activities,
            "ambiguous_activities": ambiguous_activities,
            "today_uncalculated_activities": today_uncalculated_activities,
            "weekly_uncalculated_activities": weekly_uncalculated_activities
        }

        round_summary_values(summary)

        return jsonify({
            "status": "success",
            "period": {
                "today": today.isoformat(),
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat()
            },
            "summary": summary,
            "weekly_breakdown": list(
                weekly_breakdown.values()
            )
        }), 200

    except Exception as error:
        print(
            f"Dashboard summary diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to retrieve the Dashboard summary."
        }), 500
