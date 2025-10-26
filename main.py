from fastapi import FastAPI
from model import Product
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (like Content-Type, Authorization)
)

@app.get("/")
def greetMsg():
    return "Hello World!"

products=[
    Product(id= 1,name= "xyz",description= "test description",price= 10.5,quantity= 5),
    Product(id= 9,name= "qwe",description= "test description 4",price= 20.5,quantity= 10),
    Product(id= 3,name= "asd",description= "test description 3",price= 10.5,quantity= 5),
    Product(id= 10,name= "asd",description= "test description 3",price= 10.5,quantity= 5)
]

#---------------------------------------------
# MongoDB connection URI (replace with your actual URI)
MONGO_URI = os.getenv("MONGO_URI")

# Database name
DB_NAME = "inventory_db"

# Initialize global variables
client = None
db = None
COLLECTION_NAME = "products"

# Connect and setup MongoDB
@app.on_event("startup")
async def startup_db_client():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Create collection if it doesn't exist
    collection_names = await db.list_collection_names()
    if COLLECTION_NAME not in collection_names:
        await db.create_collection(COLLECTION_NAME)
        print(f"✅ Created collection '{COLLECTION_NAME}'")

    # Ensure 'id' is unique
    await db[COLLECTION_NAME].create_index("id", unique=True)
    
    # ✅ Check if the collection is empty
    count = await db[COLLECTION_NAME].count_documents({})
    print(f"📊 Current product count in DB: {count}")

    # Insert default products only if not present individually
    inserted_count = 0
    for product in products:
        existing = await db[COLLECTION_NAME].find_one({"id": product.id})
        if not existing:
            await db[COLLECTION_NAME].insert_one(product.dict())
            inserted_count += 1
        else:
            print(f"⚠️ Product with id {product.id} already exists — skipping insert")

    print(f"✅ Inserted {inserted_count} new default products into '{COLLECTION_NAME}'")
    print(f"✅ Connected to MongoDB database: {DB_NAME}")    
    

# --- SHUTDOWN: Close the connection ---
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    print("🛑 MongoDB connection closed")

#---------------------------------------------

# @app.get("/products")
# def get_all_products():
#     return products

#-------------db upgraded---------------------------------

@app.get("/products")
async def get_all_products():
    # Fetch all documents from MongoDB collection
    cursor = db[COLLECTION_NAME].find({})  
    products_list = await cursor.to_list(length=None)  # convert cursor to list

    # Optional: remove MongoDB's internal "_id" field for cleaner output
    for product in products_list:
        product.pop("_id", None)

    #return {"count": len(products_list), "products": products_list}
    return products_list

# @app.get("/product/{id}")
# def get_product_by_id(id:int):
#     for product in products:
#         if product.id==id:
#             return product
        
#     return "Product not found"

#----------------db upgraded-----------------------------

@app.get("/products/{id}")
async def get_product_by_id(id: int):
    # Find a single document matching the given id
    product = await db[COLLECTION_NAME].find_one({"id": id})

    if product:
        # Remove MongoDB internal _id field for cleaner response
        product.pop("_id", None)
        return product
    else:
        return {"message": "Product not found"}

# @app.post("/product")
# def add_product(product:Product):
#     products.append(product)

#-------db upgraded--------------------------

@app.post("/products")
async def add_product(product: Product):
    # Check if a product with the same id already exists
    existing = await db[COLLECTION_NAME].find_one({"id": product.id})
    if existing:
        return {"message": f"Product with id {product.id} already exists."}

    # Insert new product into MongoDB
    result = await db[COLLECTION_NAME].insert_one(product.dict())

    if result.inserted_id:
        return {"message": "✅ Product added successfully", "product": product.dict()}
    else:
        return {"message": "❌ Failed to insert product"}
    
# @app.put("/product")
# def update_product(id:int,product:Product):
#     for i in range(len(products)):
#         if products[i].id==id:
#             products[i]=product
#             return "Product got added"
    
#     return "No product added"

#------db upgraded ----------------

@app.put("/products/{id}")
async def update_product(id: int, product: Product):
    # Check if product exists in DB
    existing = await db[COLLECTION_NAME].find_one({"id": id})
    if not existing:
        return {"message": f"❌ Product with id {id} not found"}

    # Update product fields (except id)
    update_data = product.dict()
    await db[COLLECTION_NAME].update_one(
        {"id": id},
        {"$set": update_data}
    )

    return {"message": f"✅ Product with id {id} updated successfully", "updated_data": update_data}


# @app.delete("/product")
# def delete_product(id:int):
#     for i in range(len(products)):
#         if products[i].id==id:
#             del products[i]
#             return "Product got deleted"
    
#     return "Product not found"

#---------db upgraded ---------------------

@app.delete("/products/{id}")
async def delete_product(id: int):
    # Check if product exists
    existing = await db[COLLECTION_NAME].find_one({"id": id})
    if not existing:
        return {"message": f"❌ Product with id {id} not found"}

    # Delete product from DB
    result = await db[COLLECTION_NAME].delete_one({"id": id})

    if result.deleted_count == 1:
        return {"message": f"✅ Product with id {id} deleted successfully"}
    else:
        return {"message": f"⚠️ Failed to delete product with id {id}"}
