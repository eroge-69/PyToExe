from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoice.db'
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    quantity = db.Column(db.Integer, default=0)
    shippings = db.relationship('ShippingMethod', backref='book', lazy=True)

class ShippingMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

@app.before_first_request
def setup():
    db.create_all()
    initial_books = ['گام اول', 'گام دوم', 'گام سوم', 'گیاهی']
    shipping_methods = ['پست تک جلدی', 'پست دو جلدی', 'پست سه جلدی', 'پست 4 جلدی']

    for title in initial_books:
        if not Book.query.filter_by(title=title).first():
            db.session.add(Book(title=title))

    db.session.commit()

@app.route('/')
def index():
    books = Book.query.all()
    shipping_options = ['پست تک جلدی', 'پست دو جلدی', 'پست سه جلدی', 'پست 4 جلدی']
    return render_template('index.html', books=books, shipping_options=shipping_options)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    quantity = int(request.form['quantity'])
    book = Book.query.filter_by(title=title).first()
    if book:
        book.quantity += quantity
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_shipping/<int:book_id>', methods=['POST'])
def add_shipping(book_id):
    method = request.form['method']
    quantity = int(request.form['quantity'])

    shipping = ShippingMethod(method=method, quantity=quantity, book_id=book_id)
    db.session.add(shipping)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
