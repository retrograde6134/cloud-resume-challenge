import json
from unittest.mock import MagicMock, patch

import azure.functions as func

from function_app import visitor, visitor_preflight


def make_request(method="POST"):
    return func.HttpRequest(
        method=method,
        url="/api/visitor",
        headers={"Content-Type": "application/json"},
        body=b"",
    )


@patch("function_app.TableClient")
def test_first_visit_returns_one(mock_table_client):
    """No entity exists yet — counter starts at 1."""
    mock_instance = MagicMock()
    mock_instance.get_entity.side_effect = Exception("Not found")
    mock_table_client.from_connection_string.return_value = mock_instance

    resp = visitor(make_request())

    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body["count"] == 1
    assert resp.headers["Access-Control-Allow-Origin"] == "*"

    # Assert the upsert was called with the expected count
    mock_instance.upsert_entity.assert_called_once()
    entity = mock_instance.upsert_entity.call_args.kwargs["entity"]
    assert entity["count"] == 1
    assert entity["PartitionKey"] == "counter"
    assert entity["RowKey"] == "visits"


@patch("function_app.TableClient")
def test_subsequent_visit_increments(mock_table_client):
    """Existing entity with count=5 → response should be 6."""
    mock_instance = MagicMock()
    mock_instance.get_entity.return_value = {"count": 5}
    mock_table_client.from_connection_string.return_value = mock_instance

    resp = visitor(make_request())

    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body["count"] == 6

    entity = mock_instance.upsert_entity.call_args.kwargs["entity"]
    assert entity["count"] == 6


@patch("function_app.TableClient")
def test_cosmos_failure_returns_500(mock_table_client):
    """A Cosmos DB error should return 500 with a JSON error body."""
    mock_table_client.from_connection_string.side_effect = Exception("boom")

    resp = visitor(make_request())

    assert resp.status_code == 500
    body = json.loads(resp.get_body())
    assert "error" in body
    assert resp.headers["Access-Control-Allow-Origin"] == "*"


def test_options_returns_204_with_cors():
    """Preflight must return 204 with CORS headers."""
    resp = visitor_preflight(make_request(method="OPTIONS"))

    assert resp.status_code == 204
    assert resp.headers["Access-Control-Allow-Origin"] == "*"
    assert "POST" in resp.headers["Access-Control-Allow-Methods"]