import azure.functions as func
import json
import logging
from typing import Dict
from datetime import datetime

app = func.FunctionApp()

# POST /api/items - CREATE item in Cosmos DB
@app.route(route="items", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
@app.cosmos_db_output(
    arg_name="output_doc",
    database_name="TodoItems",  # Consistent with get_items
    container_name="Items",
    connection="AzureCosmosDB"  # Reference app setting, no hardcoded string
)
def create_item(req: func.HttpRequest, output_doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info("Creating new item in TodoItems/Items...")
    
    try:
        req_body = req.get_json()
    except ValueError:
        logging.error("Invalid JSON in request body")
        return func.HttpResponse("Invalid JSON", status_code=400)

    if not req_body:
        logging.error("Empty request body")
        return func.HttpResponse("Empty body", status_code=400)

    # Add unique ID and timestamp
    item = req_body.copy()
    item["id"] = item.get("id", str(hash(json.dumps(item))))
    item["createdAt"] = datetime.utcnow().isoformat()

    # Save to Cosmos DB
    try:
        output_doc.set(func.Document.from_dict(item))
        logging.info(f"Item created with id: {item['id']}")
    except Exception as e:
        logging.error(f"Failed to save to Cosmos DB: {str(e)}")
        return func.HttpResponse(f"Cosmos DB error: {str(e)}", status_code=500)

    return func.HttpResponse(
        json.dumps({"message": "Item created!", "id": item["id"]}),
        status_code=201,
        mimetype="application/json"
    )

# GET /api/items - READ all items
@app.route(route="items", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
@app.cosmos_db_input(
    arg_name="documents", 
    database_name="TodoItems",
    container_name="Items",
    connection="AzureCosmosDB",
    sql_query="SELECT * FROM c"
)
def get_items(req: func.HttpRequest, documents) -> func.HttpResponse:
    logging.info("Fetching all items from TodoItems/Items...")
    try:
        items = [doc for doc in documents]
        logging.info(f"Retrieved {len(items)} items")
        return func.HttpResponse(
            json.dumps(items, default=str),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Failed to fetch items: {str(e)}")
        return func.HttpResponse(f"Cosmos DB error: {str(e)}", status_code=500)

