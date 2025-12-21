from app import db
from datetime import datetime, timedelta
from uuid import uuid4

def get_wib_time():
    return datetime.utcnow() + timedelta(hours=7)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=get_wib_time)
    updated_at = db.Column(db.DateTime, default=get_wib_time, onupdate=get_wib_time)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f'<User {self.name}>' 