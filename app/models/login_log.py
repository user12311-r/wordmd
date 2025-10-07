"""登录日志模型"""
from datetime import datetime
from app import db


class LoginLog(db.Model):
    """登录日志表"""
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip = db.Column(db.String(50), nullable=True)
    ua = db.Column(db.String(500), nullable=True)  # User Agent
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'ip': self.ip,
            'ua': self.ua
        }
    
    def __repr__(self):
        return f'<LoginLog {self.id}: User {self.user_id} at {self.login_time}>'

