
from datetime import date
from math import isfinite
from uuid import UUID

from flask import Blueprint, jsonify, request

from supabase_client import get_supabase_client

from emissions.calculator import (
    calculate_car_emissions,
    calculate_passenger_transport_emissions,
    calculate_zero_operational_emissions,
)


activities_bp = Blueprint(
    "activities",
    __name__,
    url_prefix="/api/activities"
)


def get_authenticated_client():
    """Validate the Supabase access token and identify the user."""

    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        return None, None, (
            jsonify({
                "status": "error",
                "message": "A valid Bearer token is required."
            }),
            401
        )

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        return None, None, (
            jsonify({
                "status": "error",
                "message": "A valid Bearer token is required."
            }),
            401
        )

    try:
        client = get_supabase_client(token)
        auth_response = client.auth.get_user(token)
        user = auth_response.user if auth_response else None

        if not user:
            return None, None, (
                jsonify({
                    "status": "error",
                    "message": "Invalid or expired access token."
                }),
                401
            )

        return client, user.id, None

    except Exception as error:
        print(
            f"Supabase authentication diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return None, None, (
            jsonify({
                "status": "error",
                "message": "Authentication failed."
            }),
            401
        )


def validate_activity_data(data, require_all=True):
    """Validate activity fields received from the frontend."""

    required_fields = [
        "category",
        "description",
        "quantity",
        "unit",
        "activity_date"
    ]

    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    if require_all:
        for field in required_fields:
            if field not in data:
                return None, f"Missing required field: {field}"

    validated = {}

    for field in required_fields:
        if field not in data:
            continue

        value = data[field]

        if field in ["category", "description", "unit"]:
            if not isinstance(value, str) or not value.strip():
                return None, f"{field} must be a non-empty string."

            validated[field] = value.strip()

        elif field == "quantity":
            try:
                quantity = float(value)
            except (TypeError, ValueError):
                return None, "quantity must be a valid number."

            if not isfinite(quantity) or quantity <= 0:
                return None, "quantity must be greater than zero."

            validated[field] = quantity

        elif field == "activity_date":
            try:
                if not isinstance(value, str):
                    raise ValueError

                date.fromisoformat(value)
            except (TypeError, ValueError):
                return None, "activity_date must use YYYY-MM-DD format."

            validated[field] = value

    for optional_field in ["fuel_type", "purpose"]:
        if optional_field in data:
            value = data[optional_field]

            if value is not None and not isinstance(value, str):
                return None, f"{optional_field} must be a string."

            validated[optional_field] = (
                value.strip() if isinstance(value, str) else None
            )

    return validated, None


def calculate_activity_emissions(activity):
    """
    Calculate emissions using backend-controlled factors.

    Car emissions are stored as direct CO2.
    Walking and cycling use the initial operational CO2e boundary.
    Bus and train remain uncalculated until verified factors exist.
    """

    category = activity.get("category")
    distance = activity.get("quantity")
    unit = activity.get("unit")

    if unit != "km":
        raise ValueError(
            "Transport distance must be recorded in kilometres (km)."
        )

    if category == "Car":
        fuel_type = activity.get("fuel_type")

        result = calculate_car_emissions(distance, fuel_type)

        return {
            "emissions_kg_co2": result["emissions"],
            "emissions_kg_co2e": None,
            "emission_factor": result["emission_factor"],
            "emission_factor_unit": result["emission_factor_unit"],
            "emission_factor_source": (
                f'{result["emission_factor_source"]}; '
                f'assumed fuel consumption: '
                f'{result["fuel_consumption_l_per_100km"]} L/100km'
            ),
            "emission_factor_year": result["emission_factor_year"],
        }

    if category in ["Walking", "Cycling"]:
        result = calculate_zero_operational_emissions(
            distance,
            category
        )

        return {
            "emissions_kg_co2": None,
            "emissions_kg_co2e": result["emissions"],
            "emission_factor": result["emission_factor"],
            "emission_factor_unit": result["emission_factor_unit"],
            "emission_factor_source": result["emission_factor_source"],
            "emission_factor_year": result["emission_factor_year"],
        }

    if category in ["Bus", "Train"]:
        try:
            calculate_passenger_transport_emissions(
                distance,
                category
            )
        except NotImplementedError:
            # Do not invent a factor. Save the activity with NULL emissions.
            return {
                "emissions_kg_co2": None,
                "emissions_kg_co2e": None,
                "emission_factor": None,
                "emission_factor_unit": None,
                "emission_factor_source": None,
                "emission_factor_year": None,
            }

    raise ValueError("Unsupported transport category.")


def is_valid_uuid(value):
    """Check whether an activity identifier is a valid UUID."""

    try:
        UUID(value)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


@activities_bp.route("", methods=["GET"])
def get_activities():
    """Retrieve activities belonging to the authenticated user."""

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    try:
        response = (
            client.table("activities")
            .select("*")
            .eq("user_id", user_id)
            .order("activity_date", desc=True)
            .execute()
        )

        return jsonify({
            "status": "success",
            "activities": response.data
        }), 200

    except Exception as error:
        print(
            f"Get activities diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to retrieve activities."
        }), 500


@activities_bp.route("", methods=["POST"])
def create_activity():
    """Create an activity and calculate its emissions."""

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    data, validation_error = validate_activity_data(
        request.get_json(silent=True)
    )

    if validation_error:
        return jsonify({
            "status": "error",
            "message": validation_error
        }), 400

    try:
        emissions = calculate_activity_emissions(data)

        # Only backend-calculated emissions are stored.
        data.update(emissions)
        data["user_id"] = user_id

        response = (
            client.table("activities")
            .insert(data)
            .execute()
        )

        return jsonify({
            "status": "success",
            "message": "Activity created successfully.",
            "activity": response.data[0] if response.data else None
        }), 201

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception as error:
        print(
            f"Create activity diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to create activity."
        }), 500


@activities_bp.route("/<activity_id>", methods=["PUT"])
def update_activity(activity_id):
    """Update an activity and recalculate its emissions."""

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    if not is_valid_uuid(activity_id):
        return jsonify({
            "status": "error",
            "message": "Invalid activity ID."
        }), 400

    data, validation_error = validate_activity_data(
        request.get_json(silent=True),
        require_all=False
    )

    if validation_error:
        return jsonify({
            "status": "error",
            "message": validation_error
        }), 400

    if not data:
        return jsonify({
            "status": "error",
            "message": "No activity fields were provided for updating."
        }), 400

    try:
        # Retrieve the existing record to preserve unchanged fields.
        existing_response = (
            client.table("activities")
            .select("*")
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data:
            return jsonify({
                "status": "error",
                "message": "Activity not found."
            }), 404

        updated_activity = dict(existing_response.data[0])
        updated_activity.update(data)

        emissions = calculate_activity_emissions(updated_activity)

        # Recalculate and replace the stored emissions metadata.
        data.update(emissions)

        response = (
            client.table("activities")
            .update(data)
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            return jsonify({
                "status": "error",
                "message": "Activity not found."
            }), 404

        return jsonify({
            "status": "success",
            "message": "Activity updated successfully.",
            "activity": response.data[0]
        }), 200

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception as error:
        print(
            f"Update activity diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to update activity."
        }), 500


@activities_bp.route("/<activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    """Delete an activity owned by the authenticated user."""

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    if not is_valid_uuid(activity_id):
        return jsonify({
            "status": "error",
            "message": "Invalid activity ID."
        }), 400

    try:
        response = (
            client.table("activities")
            .delete()
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            return jsonify({
                "status": "error",
                "message": "Activity not found."
            }), 404

        return jsonify({
            "status": "success",
            "message": "Activity deleted successfully."
        }), 200

    except Exception as error:
        print(
            f"Delete activity diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to delete activity."
        }), 500
