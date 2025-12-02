from app import db
from datetime import datetime

class HaircutModels(db.Model):
    id = db.Column(db.UUID, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    image_url = db.Column(db.String(256), nullable=True)
    choosen_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HaircutModels {self.name}>'