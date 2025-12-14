from app import db
from datetime import datetime
from models.user import User
from models.haircut import Haircut
from uuid import uuid4

class HaircutTransaction(db.Model):
    __tablename__ = 'haircut_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    haircut_id = db.Column(db.Integer, db.ForeignKey(Haircut.id), nullable=False)
    hairwash = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('haircut_transactions', lazy=True))
    haircut = db.relationship(Haircut, backref=db.backref('haircut_transactions', lazy=True))

    def __repr__(self):
        return f'<HaircutTransaction {self.id} - Hairwash: {self.hairwash} - Total Price: {self.total_price}>'