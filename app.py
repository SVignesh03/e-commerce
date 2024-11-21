from flask import Flask, render_template, redirect, url_for, jsonify, request, session
from data_fetch import fetch_product_data, fetch_sales_data, fetch_user_data, add_category_db, fetch_cart_items
from db import conn

# print('connection')

app = Flask(__name__)

app.secret_key = "Iw+f@R}q,D>?2u]4"

@app.route('/')
def index():
    # print('index.html')
    return render_template('index.html')

@app.route('/submit_registeration_form', methods = ['POST'])
def submit_registeration_form():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Insert data into the database
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tbl_users (user_name, e_mail, password) VALUES (%s, %s, %s)", (username, email, password))
    conn.commit()
    cursor.close()
    
    return redirect(url_for('index', success = '1'))#jsonify({'message': '1'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(username)
        print(password)

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_users WHERE user_name = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = user['user_name']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password. Please try again."
    return redirect(url_for('index'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('index'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'], is_admin=session['is_admin'])
    else:
        return redirect(url_for('index'))

# Admin route
@app.route('/admin')
def admin():
    if 'username' in session and session['is_admin']:
        return redirect(url_for('admin_dashboard'))
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

@app.route('/products')
def products():
    # Query the database to fetch all products
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Render the template and pass products data
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' in session and session['is_admin']:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            image_url = request.form['image_url']
            
            # Insert the product into the database
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                           (name, description, price, image_url))
            conn.commit()
            
            return redirect(url_for('products'))
        return render_template('add_product.html')
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."
    
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

@app.route('/promote_admin', methods=['GET', 'POST'])
def promote_admin():
    if 'username' in session and session['is_admin']:
        if request.method == 'POST':
            username = request.form['username']
            
            # Check if the user exists in the database
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                # Update the user's role to admin
                cursor.execute("UPDATE users SET is_admin = 1 WHERE username = %s", (username,))
                conn.commit()
                return "User has been promoted to admin."
            else:
                return "User does not exist."
        return render_template('promote_admin.html')
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

@app.route('/remove_admin', methods=['GET', 'POST'])
def remove_admin():
    if 'username' in session and session['is_admin']:
        if request.method == 'POST':
            username = request.form['username']
            
            # Check if the user exists in the database
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                # Update the user's role to regular user
                cursor.execute("UPDATE users SET is_admin = 0 WHERE username = %s", (username,))
                conn.commit()
                return "Admin privileges have been removed from the user."
            else:
                return "User does not exist."
        return render_template('remove_admin.html')
    else:
        return "Access Denied! You need to be logged in as an admin to access this page."

@app.route('/report')
def report():
    # Fetch data from the database
    sales_data = fetch_sales_data()
    product_data = fetch_product_data()
    user_data = fetch_user_data()
    # Return JSON response using jsonify
    return jsonify({'sales_data': sales_data, 'product_data': product_data, 'user_data': user_data})

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['is_admin']:
        return render_template('admin_dashboard.html')
    
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