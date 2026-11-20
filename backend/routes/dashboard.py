
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
        result = float(value or 0)

        if not math.isfinite(result) or result < 0:
            return 0.0

        return result

    except (TypeError, ValueError, OverflowError):
        return 0.0


def get_activity_emissions(activity):
    """
    Use CO2e when available; otherwise use direct CO2.

    The existing activity calculations store these values
    in separate fields.
    """

    co2e = activity.get("emissions_kg_co2e")

    if co2e is not None:
        return safe_emissions(co2e)

    return safe_emissions(activity.get("emissions_kg_co2"))


@dashboard_bp.route("/summary", methods=["GET"])
def get_dashboard_summary():

    # Authenticate the user.
    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    # Use the requested date when supplied.
    # This allows the frontend to use the user's local date.
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
        # Retrieve all food entries for this user.
        food_entries = get_all_user_records(
            client,
            "food_entries",
            "user_id, activity_date, emissions_kg_co2e",
            user_id
        )

        # Retrieve all activity entries for this user.
        activities = get_all_user_records(
            client,
            "activities",
            "user_id, activity_date, emissions_kg_co2, emissions_kg_co2e",
            user_id
        )

        # Initialise the weekly breakdown.
        weekly_breakdown = {}

        current_day = week_start

        while current_day <= week_end:
            day_key = current_day.isoformat()

            weekly_breakdown[day_key] = {
                "date": day_key,
                "food_emissions": 0.0,
                "activity_emissions": 0.0,
                "total_emissions": 0.0
            }

            current_day += timedelta(days=1)

        # Calculate food emissions.
        total_food_emissions = 0.0
        today_food_emissions = 0.0
        weekly_food_emissions = 0.0

        for entry in food_entries:
            emissions = safe_emissions(
                entry.get("emissions_kg_co2e")
            )

            total_food_emissions += emissions

            entry_date = entry.get("activity_date")

            if not entry_date:
                continue

            try:
                parsed_date = date.fromisoformat(entry_date)
            except (ValueError, TypeError):
                continue

            if parsed_date == today:
                today_food_emissions += emissions

            if week_start <= parsed_date <= week_end:
                weekly_food_emissions += emissions

                day_key = parsed_date.isoformat()

                weekly_breakdown[day_key][
                    "food_emissions"
                ] += emissions

        # Calculate activity emissions.
        total_activity_emissions = 0.0
        today_activity_emissions = 0.0
        weekly_activity_emissions = 0.0

        for activity in activities:
            emissions = get_activity_emissions(activity)

            total_activity_emissions += emissions

            activity_date = activity.get("activity_date")

            if not activity_date:
                continue

            try:
                parsed_date = date.fromisoformat(activity_date)
            except (ValueError, TypeError):
                continue

            if parsed_date == today:
                today_activity_emissions += emissions

            if week_start <= parsed_date <= week_end:
                weekly_activity_emissions += emissions

                day_key = parsed_date.isoformat()

                weekly_breakdown[day_key][
                    "activity_emissions"
                ] += emissions

        # Calculate the combined totals.
        total_emissions = (
            total_food_emissions + total_activity_emissions
        )

        today_emissions = (
            today_food_emissions + today_activity_emissions
        )

        weekly_emissions = (
            weekly_food_emissions + weekly_activity_emissions
        )

        # Calculate each day's combined emissions.
        for day in weekly_breakdown.values():
            day["food_emissions"] = round(
                day["food_emissions"], 6
            )

            day["activity_emissions"] = round(
                day["activity_emissions"], 6
            )

            day["total_emissions"] = round(
                day["food_emissions"] + day["activity_emissions"],
                6
            )

        return jsonify({
            "status": "success",
            "period": {
                "today": today.isoformat(),
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat()
            },
            "summary": {
                "total_food_emissions": round(
                    total_food_emissions, 6
                ),
                "total_activity_emissions": round(
                    total_activity_emissions, 6
                ),
                "total_emissions": round(
                    total_emissions, 6
                ),
                "today_food_emissions": round(
                    today_food_emissions, 6
                ),
                "today_activity_emissions": round(
                    today_activity_emissions, 6
                ),
                "today_emissions": round(
                    today_emissions, 6
                ),
                "weekly_food_emissions": round(
                    weekly_food_emissions, 6
                ),
                "weekly_activity_emissions": round(
                    weekly_activity_emissions, 6
                ),
                "weekly_emissions": round(
                    weekly_emissions, 6
                )
            },
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
