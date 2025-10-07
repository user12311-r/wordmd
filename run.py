"""应用启动文件"""
import os
from app import create_app

# 获取配置环境
config_name = os.getenv('FLASK_ENV', 'development')

# 创建应用
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(config_name == 'development')
    )

