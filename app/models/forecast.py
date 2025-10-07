"""预测结果模型"""
from datetime import datetime
from app import db


class Forecast(db.Model):
    """预测结果表"""
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    period = db.Column(db.String(20), nullable=False)  # day, month, year
    date = db.Column(db.Date, nullable=False, index=True)
    predicted_amount = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period': self.period,
            'date': self.date.isoformat() if self.date else None,
            'predicted_amount': self.predicted_amount,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Forecast {self.id}: {self.predicted_amount} on {self.date}>'

