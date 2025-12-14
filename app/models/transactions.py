from app import db
from datetime import datetime
from models.haircut_transactions import HaircutTransaction
from models.user import User
from uuid import uuid4

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey(HaircutTransaction.id), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship(User, backref=db.backref('transactions', lazy=True))
    haircut_transaction = db.relationship(HaircutTransaction, backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.id} - {self.transaction_id}>'