from flask import Flask, render_template, redirect, url_for, jsonify, request, session
from data_fetch import fetch_product_data, fetch_sales_data, fetch_user_data, add_category_db, fetch_cart_items
from db import conn

app = Flask(__name__)
app.secret_key = "Iw+f@R}q,D>?2u]4"

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# User registration
@app.route('/submit_registeration_form', methods=['POST'])
def submit_registeration_form():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Insert data into the MongoDB collection
    users_collection = conn["tbl_users"]
    users_collection.insert_one({"user_name": username, "e_mail": email, "password": password})
    
    return redirect(url_for('index', success='1'))

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Attempting login with username: {username}, password: {password}")

        # Query the MongoDB collection
        users_collection = conn["tbl_users"]
        user = users_collection.find_one({"user_name": username, "password": password})

        print(f"Query result: {user}")

        if user:
            session['username'] = user['user_name']
            session['is_admin'] = user.get('is_admin', False)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password. Please try again."
    return redirect(url_for('index'))


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'], is_admin=session['is_admin'])
    else:
        return redirect(url_for('index'))

# Admin panel
@app.route('/admin')
def admin():
    if 'username' in session and session['is_admin']:
        return redirect(url_for('admin_dashboard'))
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

# Fetch all products
@app.route('/products')
def products():
    products_collection = conn["tbl_products"]
    products = list(products_collection.find())  # Convert cursor to list
    return render_template('products.html', products=products)

# Add a new product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' in session and session['is_admin']:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            image_url = request.form['image_url']
            
            # Insert the product into MongoDB
            products_collection = conn["tbl_products"]
            products_collection.insert_one({"name": name, "description": description, "price": price, "image_url": image_url})
            
            return redirect(url_for('products'))
        return render_template('add_product.html')
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

# Add a category
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        if 'username' in session and session['is_admin']:
            category = request.form['category']
            add_category_db(category)
            return redirect(url_for('add_category'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('add_category.html')

# Promote a user to admin
@app.route('/promote_admin', methods=['GET', 'POST'])
def promote_admin():
    if 'username' in session and session['is_admin']:
        if request.method == 'POST':
            username = request.form['username']
            users_collection = conn["tbl_users"]
            user = users_collection.find_one({"user_name": username})
            
            if user:
                users_collection.update_one({"user_name": username}, {"$set": {"is_admin": True}})
                return "User has been promoted to admin."
            else:
                return "User does not exist."
        return render_template('promote_admin.html')
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

# Remove admin privileges
@app.route('/remove_admin', methods=['GET', 'POST'])
def remove_admin():
    if 'username' in session and session['is_admin']:
        if request.method == 'POST':
            username = request.form['username']
            users_collection = conn["tbl_users"]
            user = users_collection.find_one({"user_name": username})
            
            if user:
                users_collection.update_one({"user_name": username}, {"$set": {"is_admin": False}})
                return "Admin privileges have been removed from the user."
            else:
                return "User does not exist."
        return render_template('remove_admin.html')
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

# Reports
@app.route('/report')
def report():
    sales_data = fetch_sales_data()
    product_data = fetch_product_data()
    user_data = fetch_user_data()
    return jsonify({'sales_data': sales_data, 'product_data': product_data, 'user_data': user_data})

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['is_admin']:
        return render_template('admin_dashboard.html')

# Cart
@app.route('/cart')
def cart():
    if 'username' in session:
        username = session['username']
        cart_items = fetch_cart_items(username)
        return render_template('cart.html', cart_items=cart_items)
    else:
        return "You are not logged in."

if __name__ == '__main__':
    app.run()
