from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List

app = FastAPI()

# MongoDB connection details
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.restaurant


class Product(BaseModel):
    name: str
    price: float


class Order(BaseModel):
    product_id: str
    quantity: int


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGO_DETAILS)
    app.mongodb = app.mongodb_client.restaurant


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# CRUD operations for Products


@app.post("/products/", response_description="Add new product", response_model=Product)
async def create_product(product: Product):
    await db["products"].insert_one(product.dict())
    return product


@app.get("/products/", response_description="List all products", response_model=List[Product])
async def list_products():
    products = await db["products"].find().to_list(1000)
    return products


@app.put("/products/{id}", response_description="Update a product", response_model=Product)
async def update_product(id: str, product: Product):
    await db["products"].update_one({"_id": id}, {"$set": product.dict()})
    return product


@app.delete("/products/{id}", response_description="Delete a product")
async def delete_product(id: str):
    delete_result = await db["products"].delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return {"message": "Product deleted"}
    raise HTTPException(status_code=404, detail=f"Product {id} not found")

# Operations for Orders


@app.post("/orders/", response_description="Place an order", response_model=Order)
async def place_order(order: Order):
    await db["orders"].insert_one(order.dict())
    return order


@app.get("/orders/", response_description="List all orders", response_model=List[Order])
async def list_orders():
    orders = await db["orders"].find().to_list(1000)
    return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
