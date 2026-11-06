
import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from routes.activities import activities_bp

load_dotenv()

app = Flask(__name__)

# Allow requests from the Angular development server.
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv(
            "FRONTEND_URL",
            "http://localhost:4200"
        )
    }
})

# Register the activity management endpoints.
app.register_blueprint(activities_bp)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Confirm that the EcoTrack backend is running."""
    return jsonify({
        "status": "success",
        "message": "EcoTrack backend is running."
    }), 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "true").lower() == "true"
    )
