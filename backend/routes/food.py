
from datetime import date
from uuid import UUID

from flask import Blueprint, jsonify, request

from routes.activities import get_authenticated_client
from emissions.food_calculator import calculate_food_emissions


food_bp = Blueprint("food", __name__, url_prefix="/api/food")


@food_bp.route("/items", methods=["GET"])
def get_food_items():
    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    try:
        response = (
            client.table("food_items")
            .select(
                "id, name, category, "
                "emission_factor_kg_co2e_per_kg, "
                "emission_factor_unit, "
                "dataset_name, dataset_version, "
                "country_model, source_indicator"
            )
            .eq("is_active", True)
            .order("category")
            .order("name")
            .execute()
        )

        return jsonify({
            "status": "success",
            "food_items": response.data,
            "count": len(response.data)
        }), 200

    except Exception as error:
        print(
            f"Get food items diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to retrieve food items."
        }), 500


@food_bp.route("/entries", methods=["POST"])
def create_food_entry():
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

    food_item_id = data.get("food_item_id")
    quantity_grams = data.get("quantity_grams")
    activity_date = data.get("activity_date")

    # Validate the food item ID.
    try:
        food_item_id = str(UUID(str(food_item_id)))
    except (ValueError, TypeError, AttributeError):
        return jsonify({
            "status": "error",
            "message": "A valid food item ID is required."
        }), 400

    # Validate the quantity.
    if isinstance(quantity_grams, bool):
        return jsonify({
            "status": "error",
            "message": "Food quantity must be a valid number."
        }), 400

    try:
        quantity = float(quantity_grams)

        if not quantity > 0 or not __import__("math").isfinite(quantity):
            raise ValueError()

    except (TypeError, ValueError, OverflowError):
        return jsonify({
            "status": "error",
            "message": "Food quantity must be a finite number greater than zero."
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
        # Retrieve the active food item from the database.
        food_response = (
            client.table("food_items")
            .select(
                "id, safad_code, name, "
                "emission_factor_kg_co2e_per_kg, "
                "emission_factor_unit, "
                "dataset_name, dataset_version, "
                "country_model, source_indicator"
            )
            .eq("id", food_item_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        if not food_response.data:
            return jsonify({
                "status": "error",
                "message": "The selected food item was not found or is inactive."
            }), 404

        food = food_response.data[0]

        # Calculate emissions on the backend.
        calculation = calculate_food_emissions(
            quantity,
            food["emission_factor_kg_co2e_per_kg"]
        )

        # Prepare the database record.
        entry = {
            "user_id": user_id,
            "food_item_id": food["id"],
            "quantity_grams": calculation["quantity_grams"],
            "food_name_snapshot": food["name"],
            "safad_code_snapshot": food["safad_code"],
            "emission_factor_snapshot": calculation["emission_factor"],
            "emission_factor_unit": food["emission_factor_unit"],
            "emissions_kg_co2e": calculation["emissions_kg_co2e"],
            "dataset_name_snapshot": food["dataset_name"],
            "dataset_version_snapshot": food["dataset_version"],
            "country_model_snapshot": food["country_model"],
            "source_indicator_snapshot": food["source_indicator"]
        }

        # Only supply the date when the user provided one.
        # Otherwise, the database CURRENT_DATE default is used.
        if activity_date is not None:
            entry["activity_date"] = activity_date

        # Save the entry.
        save_response = (
            client.table("food_entries")
            .insert(entry)
            .execute()
        )

        if not save_response.data:
            raise RuntimeError("The food entry was not returned after insertion.")

        saved_entry = save_response.data[0]

        return jsonify({
            "status": "success",
            "message": "Food entry saved successfully.",
            "entry": saved_entry
        }), 201

    except Exception as error:
        print(
            f"Create food entry diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to save the food entry."
        }), 500
