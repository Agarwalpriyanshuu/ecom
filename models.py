from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

def init_db(app):
    with app.app_context():
        db.create_all()
        if not Product.query.first():
            db.session.add_all([
                Product(name="T-shirt", price=10.99),
                Product(name="Jeans", price=20.50),
                Product(name="Sneakers", price=45.00)
            ])
            db.session.commit()
