"""数据导入记录模型"""
from datetime import datetime
from app import db


class ImportRecord(db.Model):
    """数据导入记录表"""
    __tablename__ = 'import_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    rows_total = db.Column(db.Integer, default=0)
    rows_success = db.Column(db.Integer, default=0)
    rows_failed = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, processing, success, failed
    error_report_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'rows_total': self.rows_total,
            'rows_success': self.rows_success,
            'rows_failed': self.rows_failed,
            'status': self.status,
            'error_report_path': self.error_report_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ImportRecord {self.id}: {self.filename}>'

