import azure.functions as func
import json
import logging
from typing import Dict
from datetime import datetime

app = func.FunctionApp()

# POST /api/items - CREATE item in Cosmos DB
@app.route(route="items", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_output(
    arg_name="output_doc",
    database_name="StudentDB",  # Change to your DB name
    container_name="Items",     # Change to your container name
    connection="AccountEndpoint=https://cosmos-midsem.documents.azure.com:443/;AccountKey=u6e6LwoDPsLKU4QM49p6aH7oxs9HDF0Qafm5LREZPQ07ycvqeJUEnOxmwHqXAzIVFhFaZ6Mm3axLACDbM930Fw=="  # Uses your existing connection
)
def create_item(req: func.HttpRequest, output_doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info("Creating new item...")
    
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    if not req_body:
        return func.HttpResponse("Empty body", status_code=400)

    # Add unique ID
    item = req_body.copy()
    item["id"] = item.get("id", str(hash(json.dumps(item))))
    item["createdAt"] = datetime.utcnow().isoformat()

    # Save to Cosmos DB
    output_doc.set(func.Document.from_dict(item))

    return func.HttpResponse(
        json.dumps({"message": "Item created!", "id": item["id"]}),
        status_code=201,
        mimetype="application/json"
    )

# GET /api/items - READ all items
@app.route(route="items", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_input(
    arg_name="documents", 
    database_name="TodoItems",
    container_name="Items",
    connection="AzureCosmosDB",
    sql_query="SELECT * FROM c"
)
def get_items(req: func.HttpRequest, documents) -> func.HttpResponse:
    items = [doc for doc in documents]
    return func.HttpResponse(
        json.dumps(items, default=str),
        mimetype="application/json"
    )