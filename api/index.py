from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import os
import uuid

app = Flask(__name__)

# In-memory database to store user data
users = {}
sessions = {}
cart = {}

# Define a hardcoded product list (Replace with actual data)
products = {
    1: {'name': 'Product 1 Jean1', 'price': 19.99},
    2: {'name': 'Product 2 Jean2', 'price': 59.99},
    3: {'name': 'Product 3 Jean3', 'price': 79.99},
    4: {'name': 'Product 4 Jean4', 'price': 79.99},
    5: {'name': 'Product 5 Jean5', 'price': 179.99},
    6: {'name': 'Product 6 Jean6', 'price': 279.99}
}

# Function to set the 'logged_in' context variable
def set_logged_in(response):
    session_id = request.cookies.get('session_id')
    logged_in = session_id is not None and sessions.get(session_id, False)
    response.set_cookie('logged_in', str(logged_in), httponly=True)
    return response

@app.route('/')
def index():
    session_id = request.cookies.get('session_id')
    logged_in = session_id is not None and sessions.get(session_id, False)
    response = make_response(render_template('index.html', products=products, logged_in=logged_in))
    return set_logged_in(response)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cart')
def view_cart():
    session_id = request.cookies.get('session_id')
    logged_in = session_id is not None and sessions.get(session_id, False)
    if logged_in:
        total_price = sum(item['price'] * item['quantity'] for item in cart.values()) if cart else 0
        response = make_response(render_template('cart.html', cart=cart, total_price=total_price, logged_in=logged_in))  # Pass logged_in
        return set_logged_in(response)
    else:
        return redirect(url_for('login'))

@app.route('/add-to-cart', methods=['GET'])
def add_to_cart():
    session_id = request.cookies.get('session_id')
    logged_in = session_id is not None and sessions.get(session_id, False)

    if logged_in:
        product_id = request.args.get('productId')
        if product_id:
            if product_id in cart:
                cart[product_id]['quantity'] += 1
            else:
                product = products.get(int(product_id))
                if product:  # Check if the product exists
                    cart[product_id] = {'quantity': 1, 'name': product['name'], 'price': product['price']}
                else:
                    return "Invalid product ID", 400
        return redirect(url_for('view_cart'))
    else:
        return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login-submit', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        session_id = str(uuid.uuid4())
        sessions[session_id] = True
        response = redirect(url_for('index'))
        response.set_cookie('session_id', session_id, httponly=True)
        return set_logged_in(response)
    else:
        return redirect(url_for('login', error=1))

@app.route('/register-submit', methods=['POST'])
def register_submit():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    users[username] = {'password': password, 'email': email}
    return redirect(url_for('login'))

@app.route('/checkout')
def checkout_page():
    session_id = request.cookies.get('session_id')
    logged_in = session_id is not None and sessions.get(session_id, False)
    if logged_in:
        return render_template('checkout.html', logged_in=logged_in)
    else:
        return redirect(url_for('login'))

@app.route('/checkout', methods=['POST'])
def handle_checkout():
    # ... (Your existing checkout processing logic here)
    data = {
        "status": "success",
        "message": "Checkout completed successfully!" 
    }
    return jsonify(data)


@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id in sessions:
        sessions.pop(session_id)
    response = redirect(url_for('index'))
    response.set_cookie('session_id', '', expires=0)
    return set_logged_in(response)


if __name__ == '__main__':
    app.run(debug=True)