"""消费类别模型"""
from app import db


class Category(db.Model):
    """消费类别表"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    code = db.Column(db.String(50), unique=True, nullable=True)
    
    # 自引用关系
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    
    # 关系
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'code': self.code
        }
    
    def __repr__(self):
        return f'<Category {self.id}: {self.name}>'

