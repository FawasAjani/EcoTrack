
from datetime import date, timedelta
from types import SimpleNamespace
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


def configure_dashboard_queries(
    mock_client,
    food_entries,
    activities
):
    """Configure separate Supabase queries for food and activities."""

    food_query = MagicMock()
    activity_query = MagicMock()

    def table_query(table_name):
        if table_name == "food_entries":
            return food_query

        if table_name == "activities":
            return activity_query

        raise AssertionError(f"Unexpected table: {table_name}")

    mock_client.table.side_effect = table_query

    for query, records in [
        (food_query, food_entries),
        (activity_query, activities)
    ]:
        query.select.return_value = query
        query.eq.return_value = query
        query.order.return_value = query
        query.range.return_value = query
        query.execute.return_value = SimpleNamespace(data=records)

    return food_query, activity_query


def test_dashboard_summary_calculates_emissions(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    today = date(2026, 11, 19)
    yesterday = today - timedelta(days=1)
    previous_week = today - timedelta(days=10)

    food_entries = [
        {
            "user_id": "test-user-123",
            "activity_date": today.isoformat(),
            "emissions_kg_co2e": 2.0
        },
        {
            "user_id": "test-user-123",
            "activity_date": yesterday.isoformat(),
            "emissions_kg_co2e": 1.0
        },
        {
            "user_id": "test-user-123",
            "activity_date": previous_week.isoformat(),
            "emissions_kg_co2e": 10.0
        }
    ]

    activities = [
        {
            "user_id": "test-user-123",
            "activity_date": today.isoformat(),
            "emissions_kg_co2": 3.0,
            "emissions_kg_co2e": None
        },
        {
            "user_id": "test-user-123",
            "activity_date": yesterday.isoformat(),
            "emissions_kg_co2": None,
            "emissions_kg_co2e": 4.0
        },
        {
            "user_id": "test-user-123",
            "activity_date": previous_week.isoformat(),
            "emissions_kg_co2": None,
            "emissions_kg_co2e": 5.0
        }
    ]

    food_query, activity_query = configure_dashboard_queries(
        mock_client,
        food_entries,
        activities
    )

    with patch(
        "routes.dashboard.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get(
            "/api/dashboard/summary?today=2026-11-19"
        )

    assert response.status_code == 200

    result = response.get_json()
    summary = result["summary"]

    assert result["status"] == "success"

    assert summary["total_food_emissions"] == 13.0
    assert summary["total_activity_emissions"] == 12.0
    assert summary["total_emissions"] == 25.0

    assert summary["today_food_emissions"] == 2.0
    assert summary["today_activity_emissions"] == 3.0
    assert summary["today_emissions"] == 5.0

    assert summary["weekly_food_emissions"] == 3.0
    assert summary["weekly_activity_emissions"] == 7.0
    assert summary["weekly_emissions"] == 10.0

    assert len(result["weekly_breakdown"]) == 7

    today_breakdown = next(
        day for day in result["weekly_breakdown"]
        if day["date"] == "2026-11-19"
    )

    assert today_breakdown["food_emissions"] == 2.0
    assert today_breakdown["activity_emissions"] == 3.0
    assert today_breakdown["total_emissions"] == 5.0

    food_query.eq.assert_called_once_with(
        "user_id",
        "test-user-123"
    )

    activity_query.eq.assert_called_once_with(
        "user_id",
        "test-user-123"
    )

    food_query.order.assert_called_once_with("id")
    activity_query.order.assert_called_once_with("id")


def test_dashboard_summary_returns_zero_for_empty_history(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    configure_dashboard_queries(
        mock_client,
        [],
        []
    )

    with patch(
        "routes.dashboard.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get(
            "/api/dashboard/summary?today=2026-11-19"
        )

    assert response.status_code == 200

    result = response.get_json()

    assert result["status"] == "success"
    assert result["summary"]["total_food_emissions"] == 0
    assert result["summary"]["total_activity_emissions"] == 0
    assert result["summary"]["total_emissions"] == 0
    assert result["summary"]["today_emissions"] == 0
    assert result["summary"]["weekly_emissions"] == 0


def test_dashboard_summary_rejects_unauthenticated_request(
    client
):
    authentication_error = (
        None,
        None,
        (
            app.response_class(
                response=(
                    '{"status":"error",'
                    '"message":"A valid Bearer token is required."}'
                ),
                status=401,
                mimetype="application/json"
            ),
            401
        )
    )

    with patch(
        "routes.dashboard.get_authenticated_client",
        return_value=authentication_error
    ):
        response = client.get("/api/dashboard/summary")

    assert response.status_code == 401


def test_dashboard_summary_rejects_invalid_date(
    client,
    authenticated_user
):
    with patch(
        "routes.dashboard.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get(
            "/api/dashboard/summary?today=not-a-date"
        )

    assert response.status_code == 400

    result = response.get_json()
    assert result["status"] == "error"


def test_dashboard_summary_handles_database_error(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    food_query = MagicMock()
    activity_query = MagicMock()

    def table_query(table_name):
        if table_name == "food_entries":
            return food_query

        if table_name == "activities":
            return activity_query

        raise AssertionError(f"Unexpected table: {table_name}")

    mock_client.table.side_effect = table_query

    food_query.select.return_value = food_query
    food_query.eq.return_value = food_query
    food_query.order.return_value = food_query
    food_query.range.return_value = food_query

    food_query.execute.side_effect = Exception(
        "Database connection failed"
    )

    with patch(
        "routes.dashboard.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get(
            "/api/dashboard/summary?today=2026-11-19"
        )

    assert response.status_code == 500

    result = response.get_json()
    assert result["status"] == "error"


def test_dashboard_summary_retrieves_records_in_batches(
    client,
    authenticated_user
):
    mock_client = authenticated_user[0]

    food_query = MagicMock()
    activity_query = MagicMock()

    mock_client.table.side_effect = lambda table_name: (
        food_query if table_name == "food_entries"
        else activity_query
    )

    for query in [food_query, activity_query]:
        query.select.return_value = query
        query.eq.return_value = query
        query.order.return_value = query
        query.range.return_value = query

    # Return 500 records in the first food batch and one
    # additional record in the second batch.
    first_batch = [
        {
            "user_id": "test-user-123",
            "activity_date": "2026-11-19",
            "emissions_kg_co2e": 0.01
        }
        for _ in range(500)
    ]

    second_batch = [
        {
            "user_id": "test-user-123",
            "activity_date": "2026-11-19",
            "emissions_kg_co2e": 1.0
        }
    ]

    food_query.execute.side_effect = [
        SimpleNamespace(data=first_batch),
        SimpleNamespace(data=second_batch)
    ]

    activity_query.execute.return_value = SimpleNamespace(data=[])

    with patch(
        "routes.dashboard.get_authenticated_client",
        return_value=authenticated_user
    ):
        response = client.get(
            "/api/dashboard/summary?today=2026-11-19"
        )

    assert response.status_code == 200

    result = response.get_json()

    assert result["summary"]["total_food_emissions"] == 6.0

    assert food_query.range.call_count == 2
    food_query.range.assert_any_call(0, 499)
    food_query.range.assert_any_call(500, 999)
