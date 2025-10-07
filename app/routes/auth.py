"""认证路由"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.models.login_log import LoginLog
from app.models.setting import Setting

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    if not data:
        return jsonify({'error': '请提供注册信息'}), 400
    
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    if not password:
        return jsonify({'error': '密码不能为空'}), 400
    
    if not email and not phone:
        return jsonify({'error': '邮箱或手机号至少提供一个'}), 400
    
    # 检查用户是否已存在
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': '该邮箱已被注册'}), 400
    
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'error': '该手机号已被注册'}), 400
    
    try:
        # 创建新用户
        user = User(email=email, phone=phone)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 创建默认设置
        setting = Setting(user_id=user.id)
        db.session.add(setting)
        db.session.commit()
        
        current_app.logger.info(f'新用户注册: {user.email or user.phone}')
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'注册失败: {e}')
        return jsonify({'error': '注册失败', 'message': str(e)}), 500


@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请提供登录信息'}), 400
    
    identifier = data.get('email') or data.get('phone')
    password = data.get('password')
    
    if not identifier or not password:
        return jsonify({'error': '请提供邮箱/手机号和密码'}), 400
    
    # 查找用户
    user = User.query.filter(
        (User.email == identifier) | (User.phone == identifier)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': '邮箱/手机号或密码错误'}), 401
    
    if user.status != 'active':
        return jsonify({'error': '账号已被禁用'}), 403
    
    try:
        # 创建 JWT token
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # 记录登录日志
        login_log = LoginLog(
            user_id=user.id,
            ip=request.remote_addr,
            ua=request.headers.get('User-Agent', '')
        )
        db.session.add(login_log)
        db.session.commit()
        
        current_app.logger.info(f'用户登录: {user.email or user.phone}')
        
        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'登录失败: {e}')
        return jsonify({'error': '登录失败', 'message': str(e)}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新 token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200


@bp.route('/forgot', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """忘记密码（占位实现）"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请提供邮箱或手机号'}), 400
    
    identifier = data.get('email') or data.get('phone')
    
    if not identifier:
        return jsonify({'error': '请提供邮箱或手机号'}), 400
    
    # TODO: 实现发送重置密码邮件/短信的逻辑
    current_app.logger.info(f'密码重置请求: {identifier}')
    
    return jsonify({
        'message': '密码重置链接已发送，请查收邮件/短信'
    }), 200


@bp.route('/reset', methods=['POST'])
@limiter.limit("3 per hour")
def reset_password():
    """重置密码（占位实现）"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '请提供重置信息'}), 400
    
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'error': '请提供重置令牌和新密码'}), 400
    
    # TODO: 验证 token 并重置密码
    current_app.logger.info(f'密码重置: token={token}')
    
    return jsonify({
        'message': '密码重置成功'
    }), 200

