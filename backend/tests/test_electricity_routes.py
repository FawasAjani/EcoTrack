
from unittest.mock import MagicMock, patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def authenticated_user():
    return MagicMock(), "test-user-123", None


def configure_electricity_entries_query(mock_client, entries):
    query = MagicMock()

    mock_client.table.return_value.select.return_value = query
    query.eq.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.execute.return_value.data = entries

    return query


def configure_electricity_delete_query(mock_client, entries):
    query = MagicMock()

    mock_client.table.return_value.delete.return_value = query
    query.eq.return_value = query
    query.execute.return_value.data = entries

    return query


def test_create_electricity_entry_success(client, authenticated_user):
    mock_client = authenticated_user[0]

    saved_entry = {
        "id": "22222222-2222-4222-8222-222222222222",
        "user_id": "test-user-123",
        "quantity_kwh": 250,
        "emissions_kg_co2": 49.45,
        "emission_factor_snapshot": 0.1978,
        "emission_factor_unit": "kg CO2/kWh",
        "dataset_name_snapshot": "SEAI",
        "dataset_version_snapshot": "2025 provisional",
        "factor_year": 2025,
        "country_model_snapshot": "Ireland"
    }

    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        saved_entry
    ]

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/electricity/entries",
            json={"quantity_kwh": 250}
        )

    assert response.status_code == 201

    result = response.get_json()

    assert result["status"] == "success"
    assert result["entry"]["user_id"] == "test-user-123"
    assert result["entry"]["emissions_kg_co2"] == 49.45

    inserted_data = (
        mock_client.table.return_value
        .insert.call_args.args[0]
    )

    assert inserted_data["user_id"] == "test-user-123"
    assert inserted_data["quantity_kwh"] == 250
    assert inserted_data["emissions_kg_co2"] == 49.45
    assert inserted_data["emission_factor_snapshot"] == 0.1978
    assert inserted_data["dataset_name_snapshot"] == "SEAI"


def test_create_electricity_entry_rejects_zero_quantity(
    client,
    authenticated_user
):
    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/electricity/entries",
            json={"quantity_kwh": 0}
        )

    assert response.status_code == 400


def test_create_electricity_entry_rejects_negative_quantity(
    client,
    authenticated_user
):
    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/electricity/entries",
            json={"quantity_kwh": -10}
        )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "quantity",
    ["invalid", None, float("nan"), float("inf"), float("-inf"), True]
)
def test_create_electricity_entry_rejects_invalid_quantity(
    client,
    authenticated_user,
    quantity
):
    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/electricity/entries",
            json={"quantity_kwh": quantity}
        )

    assert response.status_code == 400


def test_create_electricity_entry_rejects_missing_json(
    client,
    authenticated_user
):
    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/electricity/entries",
            data="not-json",
            content_type="application/json"
        )

    assert response.status_code == 400


def test_create_electricity_entry_rejects_invalid_date(
    client,
    authenticated_user
):
    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/electricity/entries",
            json={
                "quantity_kwh": 100,
                "activity_date": "not-a-date"
            }
        )

    assert response.status_code == 400


def test_create_electricity_entry_rejects_unauthenticated_request(client):
    authentication_error = (
        None,
        None,
        (
            app.response_class(
                response='{"status":"error","message":"A valid Bearer token is required."}',
                status=401,
                mimetype="application/json"
            ),
            401
        )
    )

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.post(
            "/api/electricity/entries",
            json={"quantity_kwh": 100}
        )

    assert response.status_code == 401


def test_get_electricity_entries_success(client, authenticated_user):
    mock_client = authenticated_user[0]

    sample_entries = [
        {
            "id": "22222222-2222-4222-8222-222222222222",
            "user_id": "test-user-123",
            "quantity_kwh": 250,
            "emissions_kg_co2": 49.45,
            "activity_date": "2026-11-20"
        }
    ]

    query = configure_electricity_entries_query(
        mock_client,
        sample_entries
    )

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/electricity/entries")

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["count"] == 1
    assert len(result["electricity_entries"]) == 1
    assert result["electricity_entries"][0]["quantity_kwh"] == 250

    query.eq.assert_called_with("user_id", "test-user-123")
    query.limit.assert_called_with(100)


def test_get_electricity_entries_returns_empty_history(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    configure_electricity_entries_query(mock_client, [])

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/electricity/entries")

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["electricity_entries"] == []
    assert result["count"] == 0


def test_get_electricity_entries_rejects_unauthenticated_request(client):
    authentication_error = (
        None,
        None,
        (
            app.response_class(
                response='{"status":"error","message":"A valid Bearer token is required."}',
                status=401,
                mimetype="application/json"
            ),
            401
        )
    )

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.get("/api/electricity/entries")

    assert response.status_code == 401


def test_get_electricity_entries_handles_database_error(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    query = configure_electricity_entries_query(mock_client, [])
    query.execute.side_effect = Exception("Database connection failed")

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/electricity/entries")

    assert response.status_code == 500

    result = response.get_json()
    assert result["status"] == "error"


def test_delete_electricity_entry_success(client, authenticated_user):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    query = configure_electricity_delete_query(
        mock_client,
        [{"id": entry_id, "user_id": "test-user-123"}]
    )

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/electricity/entries/{entry_id}"
        )

    assert response.status_code == 200

    result = response.get_json()
    assert result["status"] == "success"

    query.eq.assert_any_call("id", entry_id)
    query.eq.assert_any_call("user_id", "test-user-123")


def test_delete_electricity_entry_rejects_invalid_id(
    client,
    authenticated_user
):
    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            "/api/electricity/entries/not-a-valid-id"
        )

    assert response.status_code == 400


def test_delete_electricity_entry_rejects_unauthenticated_request(client):
    authentication_error = (
        None,
        None,
        (
            app.response_class(
                response='{"status":"error","message":"A valid Bearer token is required."}',
                status=401,
                mimetype="application/json"
            ),
            401
        )
    )

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.delete(
            "/api/electricity/entries/22222222-2222-4222-8222-222222222222"
        )

    assert response.status_code == 401


def test_delete_electricity_entry_returns_404_when_not_found(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    query = configure_electricity_delete_query(mock_client, [])

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/electricity/entries/{entry_id}"
        )

    assert response.status_code == 404

    query.eq.assert_any_call("id", entry_id)
    query.eq.assert_any_call("user_id", "test-user-123")


def test_delete_electricity_entry_handles_database_error(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    query = configure_electricity_delete_query(mock_client, [])
    query.execute.side_effect = Exception("Database connection failed")

    with patch(
        "routes.electricity.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/electricity/entries/{entry_id}"
        )

    assert response.status_code == 500

    result = response.get_json()
    assert result["status"] == "error"
