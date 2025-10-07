"""Flask 应用工厂"""
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    limiter.init_app(app)
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app


def setup_logging(app):
    """配置日志"""
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # 文件处理器
    file_handler = logging.FileHandler(app.config['LOG_FILE'], encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    # 添加处理器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)


def register_blueprints(app):
    """注册蓝图"""
    from app.routes import auth, data, analytics, forecast, reports, settings
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(data.bp, url_prefix='/api/data')
    app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
    app.register_blueprint(forecast.bp, url_prefix='/api/forecast')
    app.register_blueprint(reports.bp, url_prefix='/api/reports')
    app.register_blueprint(settings.bp, url_prefix='/api/settings')


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': '请求参数错误', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': '未授权', 'message': '请先登录'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': '禁止访问', 'message': '权限不足'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源不存在', 'message': str(error)}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'服务器错误: {error}')
        db.session.rollback()
        return jsonify({'error': '服务器内部错误', 'message': '请稍后重试'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'未处理的异常: {error}', exc_info=True)
        return jsonify({'error': '服务器错误', 'message': str(error)}), 500

