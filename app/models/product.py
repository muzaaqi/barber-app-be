from app import db
from uuid import uuid4
from app.modules.time import get_wib_time

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    image_key = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=get_wib_time)
    updated_at = db.Column(db.DateTime, default=get_wib_time, onupdate=get_wib_time)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f'<Product {self.name}>'