"""预测路由"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.expense import Expense
from app.models.forecast import Forecast
from sklearn.ensemble import IsolationForest
import numpy as np

bp = Blueprint('forecast', __name__)


@bp.route('/predict', methods=['GET'])
@jwt_required()
def predict():
    """预测未来消费趋势（简化版）"""
    current_user_id = get_jwt_identity()
    
    period = request.args.get('period', 'month')  # day, month
    days = request.args.get('days', 30, type=int)
    
    try:
        # 获取历史数据
        start_date = datetime.now() - timedelta(days=90)  # 使用最近90天数据
        expenses = Expense.query.filter(
            Expense.user_id == current_user_id,
            Expense.time >= start_date
        ).order_by(Expense.time).all()
        
        if len(expenses) < 7:
            return jsonify({
                'error': '历史数据不足',
                'message': '至少需要7天的消费数据才能进行预测'
            }), 400
        
        # 简单的移动平均预测
        daily_amounts = {}
        for expense in expenses:
            date_key = expense.time.date()
            daily_amounts[date_key] = daily_amounts.get(date_key, 0) + expense.amount
        
        # 计算平均值
        avg_daily = sum(daily_amounts.values()) / len(daily_amounts)
        
        # 生成预测数据
        predictions = []
        current_date = datetime.now().date()
        
        for i in range(1, days + 1):
            pred_date = current_date + timedelta(days=i)
            # 简单预测：使用历史平均值加上一些随机波动
            predicted_amount = avg_daily * (0.9 + np.random.random() * 0.2)
            
            predictions.append({
                'date': pred_date.isoformat(),
                'predicted_amount': round(predicted_amount, 2)
            })
            
            # 保存到数据库
            forecast = Forecast(
                user_id=current_user_id,
                period=period,
                date=pred_date,
                predicted_amount=predicted_amount,
                model_version='simple_ma_v1'
            )
            db.session.add(forecast)
        
        db.session.commit()
        
        return jsonify({
            'period': period,
            'predictions': predictions,
            'model': 'simple_moving_average',
            'historical_avg': round(avg_daily, 2)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'预测失败: {e}')
        return jsonify({'error': '预测失败', 'message': str(e)}), 500


@bp.route('/anomaly', methods=['GET'])
@jwt_required()
def detect_anomaly():
    """检测异常消费"""
    current_user_id = get_jwt_identity()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    method = request.args.get('method', 'isolation_forest')  # isolation_forest, zscore
    
    try:
        # 构建查询
        query = Expense.query.filter_by(user_id=current_user_id)
        
        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        else:
            query = query.filter(Expense.time >= datetime.now() - timedelta(days=30))
        
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
        
        expenses = query.all()
        
        if len(expenses) < 10:
            return jsonify({
                'error': '数据不足',
                'message': '至少需要10条消费记录才能进行异常检测'
            }), 400
        
        amounts = np.array([e.amount for e in expenses]).reshape(-1, 1)
        
        if method == 'isolation_forest':
            # 使用 Isolation Forest
            clf = IsolationForest(contamination=0.1, random_state=42)
            predictions = clf.fit_predict(amounts)
            
            anomalies = []
            for i, pred in enumerate(predictions):
                if pred == -1:  # 异常点
                    expense = expenses[i]
                    anomalies.append({
                        'id': expense.id,
                        'time': expense.time.isoformat(),
                        'amount': expense.amount,
                        'category': expense.category.name if expense.category else None,
                        'note': expense.note
                    })
        
        else:  # zscore
            # 使用 3σ 规则
            mean = np.mean(amounts)
            std = np.std(amounts)
            threshold = 3
            
            anomalies = []
            for expense in expenses:
                z_score = abs((expense.amount - mean) / std) if std > 0 else 0
                if z_score > threshold:
                    anomalies.append({
                        'id': expense.id,
                        'time': expense.time.isoformat(),
                        'amount': expense.amount,
                        'z_score': round(float(z_score), 2),
                        'category': expense.category.name if expense.category else None,
                        'note': expense.note
                    })
        
        # 计算统计信息
        stats = {
            'mean': round(float(np.mean(amounts)), 2),
            'std': round(float(np.std(amounts)), 2),
            'min': round(float(np.min(amounts)), 2),
            'max': round(float(np.max(amounts)), 2),
            'median': round(float(np.median(amounts)), 2)
        }
        
        return jsonify({
            'method': method,
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'total_count': len(expenses),
            'stats': stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'异常检测失败: {e}')
        return jsonify({'error': '异常检测失败', 'message': str(e)}), 500


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_forecast_history():
    """获取历史预测记录"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Forecast.query.filter_by(user_id=current_user_id)\
        .order_by(Forecast.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'forecasts': [f.to_dict() for f in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

