"""数据库初始化脚本"""
from app import create_app, db
from app.models import User, Category

def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        # 创建所有表
        print('创建数据库表...')
        db.create_all()
        print('✓ 数据库表创建成功')
        
        # 创建默认类别
        print('创建默认类别...')
        default_categories = [
            {'name': '餐饮', 'code': 'food'},
            {'name': '购物', 'code': 'shopping'},
            {'name': '交通', 'code': 'transport'},
            {'name': '娱乐', 'code': 'entertainment'},
            {'name': '医疗', 'code': 'medical'},
            {'name': '教育', 'code': 'education'},
            {'name': '住房', 'code': 'housing'},
            {'name': '通讯', 'code': 'communication'},
            {'name': '其他', 'code': 'other'}
        ]
        
        for cat_data in default_categories:
            if not Category.query.filter_by(code=cat_data['code']).first():
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        print('✓ 默认类别创建成功')
        
        # 创建测试用户（可选）
        print('创建测试用户...')
        if not User.query.filter_by(email='test@example.com').first():
            test_user = User(
                email='test@example.com',
                phone='13800138000'
            )
            test_user.set_password('test123456')
            db.session.add(test_user)
            db.session.commit()
            print('✓ 测试用户创建成功')
            print('  邮箱: test@example.com')
            print('  密码: test123456')
        else:
            print('✓ 测试用户已存在')
        
        print('\n数据库初始化完成！')
        print('现在可以运行: python run.py')

if __name__ == '__main__':
    init_database()

