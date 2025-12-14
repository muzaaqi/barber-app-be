from app import db
from datetime import datetime
from uuid import uuid4

class Haircut(db.Model):
    __tablename__ = 'haircuts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    image_url = db.Column(db.String(256), nullable=False)
    choosen_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f'<Haircut {self.name}>'