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
    return (
        MagicMock(),
        "test-user-123",
        None
    )


@pytest.fixture
def sample_food():
    return {
        "id": "11111111-1111-4111-8111-111111111111",
        "safad_code": "TEST001",
        "name": "Beef meat",
        "emission_factor_kg_co2e_per_kg": 32.1932,
        "emission_factor_unit": "kg CO2e/kg",
        "dataset_name": "SAFAD",
        "dataset_version": "v1.4.4",
        "country_model": "Ireland",
        "source_indicator": "Carbon footprint, total (kg CO2e)"
    }


def mock_food_lookup(mock_client, food):
    query = mock_client.table.return_value.select.return_value
    query.eq.return_value = query
    query.limit.return_value = query
    query.execute.return_value.data = [food]


def test_create_food_entry_success(
    client,
    authenticated_user,
    sample_food
):
    mock_client = authenticated_user[0]
    mock_food_lookup(mock_client, sample_food)

    saved_entry = {
        "id": "22222222-2222-4222-8222-222222222222",
        "user_id": "test-user-123",
        "food_item_id": sample_food["id"],
        "quantity_grams": 200,
        "food_name_snapshot": "Beef meat",
        "safad_code_snapshot": "TEST001",
        "emission_factor_snapshot": 32.1932,
        "emission_factor_unit": "kg CO2e/kg",
        "emissions_kg_co2e": 6.43864,
        "dataset_name_snapshot": "SAFAD",
        "dataset_version_snapshot": "v1.4.4",
        "country_model_snapshot": "Ireland",
        "source_indicator_snapshot": "Carbon footprint, total (kg CO2e)"
    }

    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        saved_entry
    ]

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": sample_food["id"],
                "quantity_grams": 200
            }
        )

    assert response.status_code == 201

    result = response.get_json()

    assert result["status"] == "success"
    assert result["entry"]["user_id"] == "test-user-123"
    assert result["entry"]["emissions_kg_co2e"] == 6.43864

    inserted_data = (
        mock_client.table.return_value
        .insert.call_args.args[0]
    )

    assert inserted_data["user_id"] == "test-user-123"
    assert inserted_data["food_name_snapshot"] == "Beef meat"
    assert inserted_data["emission_factor_snapshot"] == 32.1932


def test_create_food_entry_rejects_missing_food_id(client, authenticated_user):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={"quantity_grams": 200}
        )

    assert response.status_code == 400


def test_create_food_entry_rejects_zero_quantity(
    client,
    authenticated_user,
    sample_food
):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": sample_food["id"],
                "quantity_grams": 0
            }
        )

    assert response.status_code == 400


def test_create_food_entry_rejects_negative_quantity(
    client,
    authenticated_user,
    sample_food
):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": sample_food["id"],
                "quantity_grams": -100
            }
        )

    assert response.status_code == 400


def test_create_food_entry_rejects_invalid_food_id(
    client,
    authenticated_user
):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": "not-a-valid-id",
                "quantity_grams": 200
            }
        )

    assert response.status_code == 400


def test_create_food_entry_rejects_invalid_date(
    client,
    authenticated_user,
    sample_food
):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": sample_food["id"],
                "quantity_grams": 200,
                "activity_date": "not-a-date"
            }
        )

    assert response.status_code == 400


def test_create_food_entry_rejects_inactive_or_missing_food(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    query = mock_client.table.return_value.select.return_value
    query.eq.return_value = query
    query.limit.return_value = query
    query.execute.return_value.data = []

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": "11111111-1111-4111-8111-111111111111",
                "quantity_grams": 200
            }
        )

    assert response.status_code == 404


def test_create_food_entry_rejects_unauthenticated_request(client):
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
        "routes.food.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.post(
            "/api/food/entries",
            json={
                "food_item_id": "11111111-1111-4111-8111-111111111111",
                "quantity_grams": 200
            }
        )

    assert response.status_code == 401


def test_create_food_entry_rejects_missing_json(client, authenticated_user):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.post(
            "/api/food/entries",
            data="not-json",
            content_type="application/json"
        )

    assert response.status_code == 400


def configure_food_entries_query(mock_client, entries):
    """Configure the Supabase query used to retrieve food history."""
    query = MagicMock()

    mock_client.table.return_value.select.return_value = query
    query.eq.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.execute.return_value.data = entries

    return query


def test_get_food_entries_success(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    sample_entries = [
        {
            "id": "22222222-2222-4222-8222-222222222222",
            "user_id": "test-user-123",
            "food_name_snapshot": "Beef meat",
            "quantity_grams": 200,
            "emissions_kg_co2e": 6.43864,
            "activity_date": "2026-11-19"
        }
    ]

    query = configure_food_entries_query(
        mock_client,
        sample_entries
    )

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/food/entries")

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["count"] == 1
    assert len(result["food_entries"]) == 1
    assert result["food_entries"][0]["food_name_snapshot"] == "Beef meat"
    assert result["food_entries"][0]["emissions_kg_co2e"] == 6.43864

    query.eq.assert_called_with("user_id", "test-user-123")
    query.limit.assert_called_with(100)


def test_get_food_entries_returns_empty_history(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    configure_food_entries_query(mock_client, [])

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/food/entries")

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["food_entries"] == []
    assert result["count"] == 0


def test_get_food_entries_rejects_unauthenticated_request(client):
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
        "routes.food.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.get("/api/food/entries")

    assert response.status_code == 401


def test_get_food_entries_filters_by_authenticated_user(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    query = configure_food_entries_query(mock_client, [])

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/food/entries")

    assert response.status_code == 200

    # Confirm the query restricts results to the logged-in user.
    query.eq.assert_called_once_with(
        "user_id",
        "test-user-123"
    )


def test_get_food_entries_handles_database_error(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    query = configure_food_entries_query(mock_client, [])
    query.execute.side_effect = Exception("Database connection failed")

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get("/api/food/entries")

    assert response.status_code == 500

    result = response.get_json()
    assert result["status"] == "error"


# ==========================================================
# DELETE FOOD ENTRY TESTS
# ==========================================================

def configure_food_delete_query(mock_client, deleted_entries):
    """Configure the Supabase query used to delete food entries."""
    query = MagicMock()

    mock_client.table.return_value.delete.return_value = query

    query.eq.return_value = query
    query.execute.return_value.data = deleted_entries

    return query


def test_delete_food_entry_success(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    deleted_entry = {
        "id": entry_id,
        "user_id": "test-user-123",
        "food_name_snapshot": "Beef meat"
    }

    query = configure_food_delete_query(
        mock_client,
        [deleted_entry]
    )

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/food/entries/{entry_id}"
        )

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["message"] == "Food entry deleted successfully."

    query.eq.assert_any_call("id", entry_id)
    query.eq.assert_any_call("user_id", "test-user-123")


def test_delete_food_entry_rejects_invalid_id(
    client,
    authenticated_user
):
    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            "/api/food/entries/not-a-valid-id"
        )

    assert response.status_code == 400

    result = response.get_json()
    assert result["status"] == "error"


def test_delete_food_entry_rejects_unauthenticated_request(
    client
):
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
        "routes.food.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.delete(
            "/api/food/entries/22222222-2222-4222-8222-222222222222"
        )

    assert response.status_code == 401

    result = response.get_json()
    assert result["status"] == "error"


def test_delete_food_entry_returns_404_when_not_found(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    query = configure_food_delete_query(
        mock_client,
        []
    )

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/food/entries/{entry_id}"
        )

    assert response.status_code == 404

    result = response.get_json()
    assert result["status"] == "error"

    query.eq.assert_any_call("id", entry_id)
    query.eq.assert_any_call("user_id", "test-user-123")


def test_delete_food_entry_cannot_delete_another_users_entry(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    # Simulate an entry that does not belong to the logged-in user.
    query = configure_food_delete_query(
        mock_client,
        []
    )

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/food/entries/{entry_id}"
        )

    assert response.status_code == 404

    # Confirm that the deletion query includes the authenticated user ID.
    query.eq.assert_any_call(
        "user_id",
        "test-user-123"
    )


def test_delete_food_entry_handles_database_error(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    entry_id = "22222222-2222-4222-8222-222222222222"

    query = configure_food_delete_query(
        mock_client,
        []
    )

    query.execute.side_effect = Exception(
        "Database connection failed"
    )

    with patch(
        "routes.food.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.delete(
            f"/api/food/entries/{entry_id}"
        )

    assert response.status_code == 500

    result = response.get_json()
    assert result["status"] == "error"
