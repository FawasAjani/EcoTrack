
from datetime import date
from uuid import UUID
import math

from flask import Blueprint, jsonify, request

from routes.activities import get_authenticated_client
from emissions.electricity_calculator import (
    calculate_electricity_emissions
)


electricity_bp = Blueprint(
    "electricity",
    __name__,
    url_prefix="/api/electricity"
)


# ==========================================================
# GET USER ELECTRICITY HISTORY
# ==========================================================

@electricity_bp.route("/entries", methods=["GET"])
def get_electricity_entries():

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    try:
        response = (
            client.table("electricity_entries")
            .select(
                "id, user_id, quantity_kwh, activity_date, "
                "emissions_kg_co2, emission_factor_snapshot, "
                "emission_factor_unit, dataset_name_snapshot, "
                "dataset_version_snapshot, factor_year, "
                "country_model_snapshot, created_at"
            )
            .eq("user_id", user_id)
            .order("activity_date", desc=True)
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        entries = response.data or []

        return jsonify({
            "status": "success",
            "electricity_entries": entries,
            "count": len(entries)
        }), 200

    except Exception as error:
        print(
            f"Get electricity entries diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to retrieve electricity history."
        }), 500


# ==========================================================
# CREATE ELECTRICITY ENTRY
# ==========================================================

@electricity_bp.route("/entries", methods=["POST"])
def create_electricity_entry():

    # Authenticate the user.
    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    # Read and validate the request body.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON request body is required."
        }), 400

    quantity_kwh = data.get("quantity_kwh")
    activity_date = data.get("activity_date")

    # Validate the electricity quantity.
    if isinstance(quantity_kwh, bool):
        return jsonify({
            "status": "error",
            "message": "Electricity consumption must be a valid number."
        }), 400

    try:
        quantity = float(quantity_kwh)

        if not math.isfinite(quantity) or quantity <= 0:
            raise ValueError()

    except (TypeError, ValueError, OverflowError):
        return jsonify({
            "status": "error",
            "message": (
                "Electricity consumption must be a finite number "
                "greater than zero."
            )
        }), 400

    # Validate the optional activity date.
    if activity_date is not None:
        try:
            parsed_date = date.fromisoformat(activity_date)

            if parsed_date.isoformat() != activity_date:
                raise ValueError()

        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Activity date must use YYYY-MM-DD format."
            }), 400

    try:
        # Calculate emissions using the backend calculator.
        calculation = calculate_electricity_emissions(quantity)

        # Prepare the database record.
        entry = {
            "user_id": user_id,
            "quantity_kwh": calculation["quantity_kwh"],
            "emissions_kg_co2": calculation["emissions_kg_co2"],
            "emission_factor_snapshot": calculation["emission_factor"],
            "emission_factor_unit": calculation["emission_factor_unit"],
            "dataset_name_snapshot": calculation["dataset_name"],
            "dataset_version_snapshot": calculation["dataset_version"],
            "factor_year": calculation["factor_year"],
            "country_model_snapshot": calculation["country_model"]
        }

        # Supply the date only when the user provided one.
        if activity_date is not None:
            entry["activity_date"] = activity_date

        # Save the entry.
        save_response = (
            client.table("electricity_entries")
            .insert(entry)
            .execute()
        )

        if not save_response.data:
            raise RuntimeError(
                "The electricity entry was not returned after insertion."
            )

        saved_entry = save_response.data[0]

        return jsonify({
            "status": "success",
            "message": "Electricity entry saved successfully.",
            "entry": saved_entry
        }), 201

    except Exception as error:
        print(
            f"Create electricity entry diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to save the electricity entry."
        }), 500


# ==========================================================
# DELETE USER ELECTRICITY ENTRY
# ==========================================================

@electricity_bp.route("/entries/<entry_id>", methods=["DELETE"])
def delete_electricity_entry(entry_id):

    # Authenticate the user.
    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    # Validate the electricity entry ID.
    try:
        entry_id = str(UUID(str(entry_id)))

    except (ValueError, TypeError, AttributeError):
        return jsonify({
            "status": "error",
            "message": "A valid electricity entry ID is required."
        }), 400

    try:
        # Only delete an entry belonging to this user.
        response = (
            client.table("electricity_entries")
            .delete()
            .eq("id", entry_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            return jsonify({
                "status": "error",
                "message": "Electricity entry not found."
            }), 404

        return jsonify({
            "status": "success",
            "message": "Electricity entry deleted successfully."
        }), 200

    except Exception as error:
        print(
            f"Delete electricity entry diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to delete the electricity entry."
        }), 500
