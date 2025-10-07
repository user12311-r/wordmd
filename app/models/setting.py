"""系统设置模型"""
from datetime import datetime
from app import db


class Setting(db.Model):
    """系统设置表"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    theme = db.Column(db.String(50), default='light')  # light, dark
    chart_prefs = db.Column(db.Text, nullable=True)  # JSON 格式的图表偏好设置
    refresh_interval_sec = db.Column(db.Integer, default=300)  # 刷新间隔（秒）
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'chart_prefs': json.loads(self.chart_prefs) if self.chart_prefs else {},
            'refresh_interval_sec': self.refresh_interval_sec,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Setting {self.id}: User {self.user_id}>'

