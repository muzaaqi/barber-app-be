from app import db
from datetime import datetime
from app.models.user import User
from app.models.product import Product
from uuid import uuid4

class ProductTransaction(db.Model):
    __tablename__ = 'product_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(User.id), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    expedition_service = db.Column(db.String(100), nullable=False)
    expedition_status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(50), nullable=False, default='cash') 
    payment_status = db.Column(db.String(50), nullable=False, default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('product_transactions', lazy=True))
    items = db.relationship('TransactionItem', backref='transaction', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        base_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        base_dict['items'] = [item.to_dict() for item in self.items]
        return base_dict

    def __repr__(self):
        return f'<ProductTransaction {self.id}>'


class TransactionItem(db.Model):
    __tablename__ = 'transaction_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_id = db.Column(db.String(36), db.ForeignKey(ProductTransaction.id), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey(Product.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False) 
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else "Unknown Product",
            'product_image': self.product.image_url if self.product else None,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase,
            'subtotal': self.quantity * self.price_at_purchase
        }
    
    def __repr__(self):
        return f'<TransactionItem Product:{self.product_id} | Qty:{self.quantity}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(User.id), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey(Product.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('cart_items', lazy=True, cascade="all, delete-orphan"))
    product = db.relationship(Product, backref=db.backref('cart_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product_name': self.product.name if self.product else None,
            'product_price': self.product.price if self.product else 0,
            'total_price': (self.product.price * self.quantity) if self.product else 0
        }

    def __repr__(self):
        return f'<CartItem User:{self.user_id} Product:{self.product_id} Qty:{self.quantity}>'