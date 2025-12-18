from app import db
from datetime import datetime
from models.user import User
from models.product import Product
from uuid import uuid4

class ProductTransaction(db.Model):
    __tablename__ = 'product_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(User.id), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey(Product.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    expedition_service = db.Column(db.String(100), nullable=False)
    expedition_status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(50), nullable=False, default='cash') 
    payment_status = db.Column(db.String(50), nullable=False, default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('product_transactions', lazy=True))
    product = db.relationship(Product, backref=db.backref('product_transactions', lazy=True))
    
    def __repr__(self):
        return f'<ProductTransaction {self.id}>'