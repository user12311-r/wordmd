"""消费记录模型"""
from datetime import datetime
from app import db


class Expense(db.Model):
    """消费记录表"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    time = db.Column(db.DateTime, nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    
    # 地点信息（可以是经纬度或文本）
    location_lat = db.Column(db.Float, nullable=True)
    location_lon = db.Column(db.Float, nullable=True)
    location_text = db.Column(db.String(200), nullable=True)
    
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'time': self.time.isoformat() if self.time else None,
            'amount': self.amount,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'location': {
                'lat': self.location_lat,
                'lon': self.location_lon,
                'text': self.location_text
            },
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Expense {self.id}: {self.amount} at {self.time}>'

