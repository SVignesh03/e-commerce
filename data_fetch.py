from db import conn

def fetch_sales_data():
    cursor = conn.cursor()
    cursor.execute("SELECT order_date, total_amount FROM tbl_orders")
    rows = cursor.fetchall()
    sales_data = [{'date': row[0].strftime('%Y-%m-%d'), 'amount': row[1]} for row in rows]
    cursor.close()
    return sales_data

# Function to fetch product data from the database
def fetch_product_data():
    cursor = conn.cursor()
    cursor.execute("SELECT p.name, SUM(c.quantity) FROM tbl_products p JOIN tbl_cart c ON p.id = c.product_id GROUP BY p.name")
    rows = cursor.fetchall()
    product_data = [{'name': row[0], 'quantity': row[1]} for row in rows]
    cursor.close()
    return product_data

# Function to fetch user data from the database
def fetch_user_data():
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM tbl_orders")
    total_users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM (SELECT user_id FROM tbl_orders GROUP BY user_id HAVING COUNT(*) > 1) AS repeated_users")
    repeated_users_count = cursor.fetchone()[0]
    cursor.close()
    return {'repeated_users_count': repeated_users_count, 'total_users_count': total_users_count}

def add_category_db(name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tbl_categories (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()

def fetch_cart_items(username):
    cursor = conn.cursor()
    cursor.execute("""SELECT p.name, p.image_url, p.price, c.quantity FROM tbl_products p JOIN tbl_cart c ON p.id = c.product_id JOIN tbl_users u ON c.user_id = u.id WHERE u.user_name = %s """, (username,))
    rows = cursor.fetchall()
    cursor.close()
    cart_items = [{'name': row[0], 'image_url': row[1], 'price': row[2], 'quantity': row[3]} for row in rows]
    return cart_items
