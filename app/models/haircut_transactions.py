from app import db
from app.models.user import User
from app.models.haircut import Haircut
from uuid import uuid4
from app.modules.time import get_wib_time

class HaircutTransaction(db.Model):
    __tablename__ = 'haircut_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey(User.id), nullable=False)
    haircut_id = db.Column(db.String(36), db.ForeignKey(Haircut.id), nullable=False)
    hairwash = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Float, nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False)
    reservation_status = db.Column(db.String(50), nullable=False, default='pending')
    payment_method = db.Column(db.String(50), nullable=False, default='cash')
    payment_status = db.Column(db.String(50), nullable=False, default='unpaid')
    created_at = db.Column(db.DateTime, default=get_wib_time)
    updated_at = db.Column(db.DateTime, default=get_wib_time, onupdate=get_wib_time)

    user = db.relationship(User, backref=db.backref('haircut_transactions', lazy=True))
    haircut = db.relationship(Haircut, backref=db.backref('haircut_transactions', lazy=True))
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<HaircutTransaction {self.id} - Hairwash: {self.hairwash} - Total Price: {self.total_price}>'