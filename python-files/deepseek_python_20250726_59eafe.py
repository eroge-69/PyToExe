import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.exceptions import BadRequest

# --- Configuration ---
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db/farm_management.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
})

# Ensure database directory exists
os.makedirs('db', exist_ok=True)

db = SQLAlchemy(app)

# --- MODELS ---

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Purchase(BaseModel):
    """Purchase model for farm inputs and equipment"""
    __tablename__ = 'purchases'
    
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    production_type = db.Column(db.String(20))  # 'plant' or 'animal'
    description = db.Column(db.Text)
    supplier = db.Column(db.String(100))

class Crop(BaseModel):
    """Crop cultivation tracking"""
    __tablename__ = 'crops'
    
    crop_type = db.Column(db.String(50), nullable=False)
    planting_date = db.Column(db.Date)
    harvest_date = db.Column(db.Date)
    seed_cost = db.Column(db.Float)
    fertilizer_cost = db.Column(db.Float)
    labor_cost = db.Column(db.Float)
    yield_amount = db.Column(db.Float)
    quality = db.Column(db.String(100))
    status = db.Column(db.String(20), default='planned')  # planned, growing, harvested
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'))

class Field(BaseModel):
    """Farm fields management"""
    __tablename__ = 'fields'
    
    name = db.Column(db.String(50), nullable=False)
    area = db.Column(db.Float)  # in hectares
    soil_type = db.Column(db.String(50))
    crops = db.relationship('Crop', backref='field', lazy=True)

class Inventory(BaseModel):
    """Product inventory management"""
    __tablename__ = 'inventory'
    
    product = db.Column(db.String(100), nullable=False)
    production_type = db.Column(db.String(20))  # 'plant' or 'animal'
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), default='kg')
    storage_date = db.Column(db.Date)
    condition = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    threshold = db.Column(db.Float)  # minimum quantity before restocking

class Sale(BaseModel):
    """Sales records"""
    __tablename__ = 'sales'
    
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float)
    customer = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(20))
    invoice_number = db.Column(db.String(50))

# --- UTILITY FUNCTIONS ---

def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise BadRequest('Invalid date format. Use YYYY-MM-DD')

def handle_db_operation(func):
    """Decorator to handle database operations and errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequest as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database error: {str(e)}")
            return jsonify({'error': 'Database operation failed'}), 500
    return wrapper

# --- ROUTES ---

@app.route('/api/purchases', methods=['POST'])
@handle_db_operation
def add_purchase():
    data = request.get_json()
    
    purchase = Purchase(
        date=validate_date(data['date']),
        amount=float(data['amount']),
        category=data['category'],
        production_type=data.get('production_type'),
        description=data.get('description'),
        supplier=data.get('supplier')
    )
    
    db.session.add(purchase)
    db.session.commit()
    
    return jsonify({
        'message': 'Purchase added successfully',
        'id': purchase.id
    }), 201

@app.route('/api/crops', methods=['POST'])
@handle_db_operation
def add_crop():
    data = request.get_json()
    
    crop = Crop(
        crop_type=data['crop_type'],
        planting_date=validate_date(data['planting_date']),
        harvest_date=validate_date(data['harvest_date']),
        seed_cost=float(data.get('seed_cost', 0)),
        fertilizer_cost=float(data.get('fertilizer_cost', 0)),
        labor_cost=float(data.get('labor_cost', 0)),
        field_id=data.get('field_id')
    )
    
    db.session.add(crop)
    db.session.commit()
    
    return jsonify({
        'message': 'Crop added successfully',
        'id': crop.id
    }), 201

@app.route('/api/inventory', methods=['POST'])
@handle_db_operation
def add_inventory():
    data = request.get_json()
    
    inventory = Inventory(
        product=data['product'],
        production_type=data['production_type'],
        quantity=float(data['quantity']),
        unit=data.get('unit', 'kg'),
        storage_date=validate_date(data['storage_date']),
        condition=data.get('condition', 'good'),
        expiry_date=validate_date(data['expiry_date']) if data.get('expiry_date') else None
    )
    
    db.session.add(inventory)
    db.session.commit()
    
    return jsonify({
        'message': 'Inventory item added successfully',
        'id': inventory.id
    }), 201

@app.route('/api/sales', methods=['POST'])
@handle_db_operation
def add_sale():
    data = request.get_json()
    
    total = float(data['quantity']) * float(data['price'])
    
    sale = Sale(
        product=data['product'],
        quantity=float(data['quantity']),
        price=float(data['price']),
        total=total,
        customer=data.get('customer'),
        date=validate_date(data['date']),
        payment_method=data.get('payment_method', 'cash'),
        invoice_number=data.get('invoice_number')
    )
    
    db.session.add(sale)
    db.session.commit()
    
    # Update inventory (would need additional logic for proper inventory management)
    inventory = Inventory.query.filter_by(product=data['product']).first()
    if inventory:
        inventory.quantity -= float(data['quantity'])
        db.session.commit()
    
    return jsonify({
        'message': 'Sale recorded successfully',
        'id': sale.id,
        'total': total
    }), 201

# --- GET ENDPOINTS ---

@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    purchases = Purchase.query.all()
    return jsonify([p.to_dict() for p in purchases])

@app.route('/api/crops', methods=['GET'])
def get_crops():
    crops = Crop.query.all()
    return jsonify([c.to_dict() for c in crops])

# --- INITIALIZATION ---

def create_tables():
    with app.app_context():
        db.create_all()
        # Add initial data if needed

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    create_tables()
    print('Initialized the database.')

# --- MAIN ---

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)