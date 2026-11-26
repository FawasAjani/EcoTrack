
from flask import Blueprint, jsonify, request

from routes.activities import get_authenticated_client
from routes.dashboard import get_all_user_records
from services.recommendation_service import generate_recommendations
from services.ai_service import generate_ai_response


eco_assistant_bp = Blueprint(
    "eco_assistant",
    __name__,
    url_prefix="/api/eco-assistant"
)


def get_user_recommendations(client, user_id):
    """Generate recommendations using the authenticated user's data."""

    activities = get_all_user_records(
        client,
        "activities",
        "id, user_id, category, activity_date, emissions_kg_co2, emissions_kg_co2e",
        user_id
    )

    food_entries = get_all_user_records(
        client,
        "food_entries",
        "id, user_id, activity_date, emissions_kg_co2e",
        user_id
    )

    electricity_entries = get_all_user_records(
        client,
        "electricity_entries",
        "id, user_id, activity_date, emissions_kg_co2",
        user_id
    )

    return generate_recommendations(
        activities,
        food_entries,
        electricity_entries
    )


@eco_assistant_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    """Return personalised recommendations for the authenticated user."""

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    try:
        recommendations = get_user_recommendations(client, user_id)

        return jsonify({
            "status": "success",
            "recommendations": recommendations
        }), 200

    except Exception as error:
        print(
            f"Eco Assistant diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to generate recommendations at this time."
        }), 500


@eco_assistant_bp.route("/chat", methods=["POST"])
def chat():
    """Generate an AI response using the authenticated user's data."""

    client, user_id, error_response = get_authenticated_client()

    if error_response:
        return error_response

    data = request.get_json(silent=True) or {}
    user_message = data.get("message")

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({
            "status": "error",
            "message": "Please enter a message."
        }), 400

    user_message = user_message.strip()

    if len(user_message) > 2000:
        return jsonify({
            "status": "error",
            "message": "Your message must be 2000 characters or fewer."
        }), 400

    try:
        recommendations = get_user_recommendations(client, user_id)

        ai_response = generate_ai_response(
            user_message,
            recommendations
        )

        return jsonify({
            "status": "success",
            "response": ai_response
        }), 200

    except Exception as error:
        print(
            f"Eco Assistant chat diagnostic: "
            f"{type(error).__name__}: {error}"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to generate a response at this time."
        }), 500
