from flask import Flask, render_template, request, redirect, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Data storage (replace with database in production)
PRODUCTS_FILE = 'products.json'
ORDERS_FILE = 'orders.json'
CART = []

# Load products
def load_products():
    try:
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # default demo products
        products = [
            {"id":"1","name":"Shirt","price":2500,"stock":5,"category":"Clothing","images":["https://via.placeholder.com/300?text=Shirt1","https://via.placeholder.com/300?text=Shirt2"],"desc":"Nice cotton shirt"},
            {"id":"2","name":"Mug","price":1200,"stock":10,"category":"Home","images":["https://via.placeholder.com/300?text=Mug"],"desc":"Ceramic mug"},
            {"id":"3","name":"Shoes","price":5000,"stock":3,"category":"Footwear","images":["https://via.placeholder.com/300?text=Shoes"],"desc":"Running shoes"}
        ]
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f)
        return products

# Load orders
def load_orders():
    try:
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f)

@app.route('/')
def index():
    products = load_products()
    categories = sorted(list(set([p['category'] for p in products if p.get('category')])))
    return render_template('index.html', products=products, categories=categories, cart_count=sum([item['qty'] for item in CART]))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('id')
    qty = int(request.form.get('qty', 1))
    existing = next((c for c in CART if c['id']==product_id), None)
    if existing:
        existing['qty'] += qty
    else:
        CART.append({'id': product_id, 'qty': qty})
    return jsonify({'success': True, 'cart_count': sum([i['qty'] for i in CART])})

@app.route('/cart')
def view_cart():
    products = load_products()
    cart_items = []
    for item in CART:
        p = next((prod for prod in products if prod['id']==item['id']), None)
        if p:
            cart_items.append({'id':p['id'], 'name':p['name'], 'price':p['price'], 'qty':item['qty'], 'img':p['images'][0] if p.get('images') else ''})
    return jsonify(cart_items)

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    name = data.get('name')
    address = data.get('address')
    phone = data.get('phone')
    if not name or not address or not phone:
        return jsonify({'error':'Missing info'}), 400
    orders = load_orders()
    orders.append({
        'name': name,
        'address': address,
        'phone': phone,
        'items': CART.copy(),
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_orders(orders)
    CART.clear()
    return jsonify({'success': True})

@app.route('/orders')
def dashboard_orders():
    orders = load_orders()
    return jsonify(orders)

@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    save_orders([])
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True)
