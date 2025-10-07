"""设置路由"""
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.setting import Setting

bp = Blueprint('settings', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_settings():
    """获取用户设置"""
    current_user_id = get_jwt_identity()
    
    setting = Setting.query.filter_by(user_id=current_user_id).first()
    
    if not setting:
        # 创建默认设置
        setting = Setting(user_id=current_user_id)
        db.session.add(setting)
        db.session.commit()
    
    return jsonify({
        'settings': setting.to_dict()
    }), 200


@bp.route('/', methods=['PUT'])
@jwt_required()
def update_settings():
    """更新用户设置"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供设置数据'}), 400
    
    try:
        setting = Setting.query.filter_by(user_id=current_user_id).first()
        
        if not setting:
            setting = Setting(user_id=current_user_id)
            db.session.add(setting)
        
        # 更新字段
        if 'theme' in data:
            setting.theme = data['theme']
        
        if 'chart_prefs' in data:
            setting.chart_prefs = json.dumps(data['chart_prefs'], ensure_ascii=False)
        
        if 'refresh_interval_sec' in data:
            setting.refresh_interval_sec = int(data['refresh_interval_sec'])
        
        db.session.commit()
        
        current_app.logger.info(f'用户设置已更新: user_id={current_user_id}')
        
        return jsonify({
            'message': '设置更新成功',
            'settings': setting.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新设置失败: {e}')
        return jsonify({'error': '更新设置失败', 'message': str(e)}), 500

