import os
import json
import logging

import azure.functions as func
from azure.data.tables import TableClient, UpdateMode

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

CONNECTION_STRING = os.environ["COSMOS_CONNECTION_STRING"]
TABLE_NAME = "visitors"
PARTITION_KEY = "counter"
ROW_KEY = "visits"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


@app.route(route="visitor", methods=["GET", "POST"])
def visitor(req: func.HttpRequest) -> func.HttpResponse:
    """Increment the visitor counter and return the new value."""
    try:
        table_client = TableClient.from_connection_string(
            conn_str=CONNECTION_STRING,
            table_name=TABLE_NAME,
        )

        try:
            entity = table_client.get_entity(
                partition_key=PARTITION_KEY,
                row_key=ROW_KEY,
            )
            current_count = int(entity.get("count", 0))
        except Exception:
            current_count = 0

        new_count = current_count + 1

        table_client.upsert_entity(
            entity={
                "PartitionKey": PARTITION_KEY,
                "RowKey": ROW_KEY,
                "count": new_count,
            },
            mode=UpdateMode.REPLACE,
        )

        return func.HttpResponse(
            body=json.dumps({"count": new_count}),
            status_code=200,
            mimetype="application/json",
            headers=CORS_HEADERS,
        )

    except Exception as e:
        logging.exception("Visitor counter error")
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers=CORS_HEADERS,
        )


@app.route(route="visitor", methods=["OPTIONS"])
def visitor_preflight(req: func.HttpRequest) -> func.HttpResponse:
    """Handle CORS preflight requests from the browser."""
    return func.HttpResponse(status_code=204, headers=CORS_HEADERS)