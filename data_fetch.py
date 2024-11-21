from db import conn

# Function to fetch sales data
def fetch_sales_data():
    # Access the 'tbl_orders' collection
    orders_collection = conn["tbl_orders"]
    # Aggregate to fetch order_date and total_amount
    rows = orders_collection.find({}, {"order_date": 1, "total_amount": 1})
    # Format the output
    sales_data = [{'date': row['order_date'].strftime('%Y-%m-%d'), 'amount': row['total_amount']} for row in rows]
    return sales_data

# Function to fetch product data
def fetch_product_data():
    # Access the collections
    products_collection = conn["tbl_products"]
    cart_collection = conn["tbl_cart"]

    # Aggregate to get product name and sum of quantities
    pipeline = [
        {
            "$lookup": {
                "from": "tbl_cart",  # Name of the collection to join
                "localField": "id",  # Field in tbl_products
                "foreignField": "product_id",  # Field in tbl_cart
                "as": "cart_items"  # Name for the joined results
            }
        },
        {
            "$unwind": "$cart_items"  # Deconstruct the array
        },
        {
            "$group": {
                "_id": "$name",
                "quantity": {"$sum": "$cart_items.quantity"}
            }
        },
        {
            "$project": {
                "name": "$_id",
                "quantity": 1,
                "_id": 0
            }
        }
    ]
    rows = list(products_collection.aggregate(pipeline))
    product_data = [{'name': row['name'], 'quantity': row['quantity']} for row in rows]
    return product_data

# Function to fetch user data
def fetch_user_data():
    # Access the 'tbl_orders' collection
    orders_collection = conn["tbl_orders"]

    # Fetch distinct user counts
    total_users_count = orders_collection.distinct("user_id")
    total_users_count = len(total_users_count)

    # Fetch repeated user counts
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "order_count": {"$sum": 1}
            }
        },
        {
            "$match": {"order_count": {"$gt": 1}}
        }
    ]
    repeated_users = list(orders_collection.aggregate(pipeline))
    repeated_users_count = len(repeated_users)

    return {
        'repeated_users_count': repeated_users_count,
        'total_users_count': total_users_count
    }

# Function to add a category to the database
def add_category_db(name):
    # Access the 'tbl_categories' collection
    categories_collection = conn["tbl_categories"]
    # Insert the category
    categories_collection.insert_one({"name": name})

# Function to fetch cart items for a user
def fetch_cart_items(username):
    # Access the collections
    users_collection = conn["tbl_users"]
    cart_collection = conn["tbl_cart"]
    products_collection = conn["tbl_products"]

    # Fetch user by username
    user = users_collection.find_one({"user_name": username})
    if not user:
        return []  # User not found

    # Fetch cart items for the user
    pipeline = [
        {
            "$match": {"user_id": user["_id"]}
        },
        {
            "$lookup": {
                "from": "tbl_products",
                "localField": "product_id",
                "foreignField": "id",
                "as": "product_details"
            }
        },
        {
            "$unwind": "$product_details"
        },
        {
            "$project": {
                "name": "$product_details.name",
                "image_url": "$product_details.image_url",
                "price": "$product_details.price",
                "quantity": "$quantity",
                "_id": 0
            }
        }
    ]
    cart_items = list(cart_collection.aggregate(pipeline))
    return cart_items
