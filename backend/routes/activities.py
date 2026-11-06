
from flask import Blueprint, jsonify, request

activities_bp = Blueprint("activities", __name__)

# Temporary storage until Supabase database integration.
activities = []
next_activity_id = 1


@activities_bp.route("/api/activities", methods=["GET"])
def get_activities():
    """Return all recorded activities."""
    return jsonify({
        "status": "success",
        "activities": activities
    }), 200


@activities_bp.route("/api/activities", methods=["POST"])
def create_activity():
    """Record a new activity."""
    global next_activity_id

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON object is required."
        }), 400

    required_fields = ["category", "description"]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "status": "error",
                "message": f"{field.capitalize()} is required."
            }), 400

    activity = {
        "id": next_activity_id,
        "category": data["category"].strip(),
        "description": data["description"].strip()
    }

    activities.append(activity)
    next_activity_id += 1

    return jsonify({
        "status": "success",
        "message": "Activity recorded successfully.",
        "activity": activity
    }), 201


@activities_bp.route("/api/activities/<int:activity_id>", methods=["PUT"])
def update_activity(activity_id):
    """Update an existing activity."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON object is required."
        }), 400

    activity = next(
        (item for item in activities if item["id"] == activity_id),
        None
    )

    if activity is None:
        return jsonify({
            "status": "error",
            "message": "Activity not found."
        }), 404

    for field in ["category", "description"]:
        if field in data:
            if not isinstance(data[field], str) or not data[field].strip():
                return jsonify({
                    "status": "error",
                    "message": f"{field.capitalize()} must not be empty."
                }), 400

    if "category" in data:
        activity["category"] = data["category"].strip()

    if "description" in data:
        activity["description"] = data["description"].strip()

    return jsonify({
        "status": "success",
        "message": "Activity updated successfully.",
        "activity": activity
    }), 200


@activities_bp.route("/api/activities/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    """Delete an existing activity."""
    activity = next(
        (item for item in activities if item["id"] == activity_id),
        None
    )

    if activity is None:
        return jsonify({
            "status": "error",
            "message": "Activity not found."
        }), 404

    activities.remove(activity)

    return jsonify({
        "status": "success",
        "message": "Activity deleted successfully."
    }), 200
