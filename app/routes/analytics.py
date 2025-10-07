"""数据分析路由"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from app import db
from app.models.expense import Expense
from app.models.category import Category

bp = Blueprint('analytics', __name__)


@bp.route('/trend', methods=['GET'])
@jwt_required()
def get_trend():
    """获取消费趋势数据（折线图）"""
    current_user_id = get_jwt_identity()
    
    # 获取参数
    period = request.args.get('period', 'month')  # day, month, year
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # 构建查询
        query = db.session.query(
            func.date(Expense.time).label('date'),
            func.sum(Expense.amount).label('total')
        ).filter_by(user_id=current_user_id)
        
        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        else:
            # 默认最近30天
            query = query.filter(Expense.time >= datetime.now() - timedelta(days=30))
        
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
        
        # 按日期分组
        if period == 'year':
            query = db.session.query(
                extract('year', Expense.time).label('year'),
                func.sum(Expense.amount).label('total')
            ).filter_by(user_id=current_user_id)
            
            if start_date:
                query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
            
            results = query.group_by('year').order_by('year').all()
            
            data = [{'date': str(int(r.year)), 'amount': float(r.total)} for r in results]
            
        elif period == 'month':
            query = db.session.query(
                func.strftime('%Y-%m', Expense.time).label('month'),
                func.sum(Expense.amount).label('total')
            ).filter_by(user_id=current_user_id)
            
            if start_date:
                query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
            
            results = query.group_by('month').order_by('month').all()
            
            data = [{'date': r.month, 'amount': float(r.total)} for r in results]
            
        else:  # day
            results = query.group_by('date').order_by('date').all()
            data = [{'date': str(r.date), 'amount': float(r.total)} for r in results]
        
        return jsonify({
            'period': period,
            'data': data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'获取趋势数据失败: {e}')
        return jsonify({'error': '获取趋势数据失败', 'message': str(e)}), 500


@bp.route('/category-share', methods=['GET'])
@jwt_required()
def get_category_share():
    """获取类别占比数据（饼图）"""
    current_user_id = get_jwt_identity()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # 构建查询
        query = db.session.query(
            Category.name,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).join(Expense).filter(Expense.user_id == current_user_id)
        
        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
        
        results = query.group_by(Category.name).order_by(func.sum(Expense.amount).desc()).all()
        
        # 计算总额
        total_amount = sum(r.total for r in results)
        
        data = [{
            'category': r.name,
            'amount': float(r.total),
            'count': r.count,
            'percentage': round(float(r.total) / total_amount * 100, 2) if total_amount > 0 else 0
        } for r in results]
        
        return jsonify({
            'data': data,
            'total_amount': float(total_amount)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'获取类别占比失败: {e}')
        return jsonify({'error': '获取类别占比失败', 'message': str(e)}), 500


@bp.route('/amount-hist', methods=['GET'])
@jwt_required()
def get_amount_histogram():
    """获取金额分布数据（柱状图）"""
    current_user_id = get_jwt_identity()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    bins = request.args.get('bins', 10, type=int)
    
    try:
        # 构建查询
        query = Expense.query.filter_by(user_id=current_user_id)
        
        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
        
        expenses = query.all()
        
        if not expenses:
            return jsonify({'data': []}), 200
        
        # 计算分布
        amounts = [e.amount for e in expenses]
        min_amount = min(amounts)
        max_amount = max(amounts)
        
        # 创建区间
        bin_width = (max_amount - min_amount) / bins
        histogram = []
        
        for i in range(bins):
            bin_start = min_amount + i * bin_width
            bin_end = bin_start + bin_width
            
            count = sum(1 for a in amounts if bin_start <= a < bin_end or (i == bins - 1 and a == bin_end))
            
            histogram.append({
                'range': f'{bin_start:.2f}-{bin_end:.2f}',
                'start': round(bin_start, 2),
                'end': round(bin_end, 2),
                'count': count
            })
        
        return jsonify({
            'data': histogram,
            'min': round(min_amount, 2),
            'max': round(max_amount, 2)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'获取金额分布失败: {e}')
        return jsonify({'error': '获取金额分布失败', 'message': str(e)}), 500


@bp.route('/heatmap', methods=['GET'])
@jwt_required()
def get_heatmap():
    """获取地点热力图数据"""
    current_user_id = get_jwt_identity()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # 构建查询
        query = Expense.query.filter_by(user_id=current_user_id)\
            .filter(Expense.location_lat.isnot(None), Expense.location_lon.isnot(None))
        
        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
        
        expenses = query.all()
        
        # 聚合地点数据
        location_data = {}
        for expense in expenses:
            key = f"{expense.location_lat:.4f},{expense.location_lon:.4f}"
            if key not in location_data:
                location_data[key] = {
                    'lat': expense.location_lat,
                    'lon': expense.location_lon,
                    'count': 0,
                    'total_amount': 0
                }
            location_data[key]['count'] += 1
            location_data[key]['total_amount'] += expense.amount
        
        data = [
            {
                'lat': v['lat'],
                'lon': v['lon'],
                'count': v['count'],
                'amount': round(v['total_amount'], 2),
                'intensity': v['count']  # 热力强度
            }
            for v in location_data.values()
        ]
        
        return jsonify({'data': data}), 200

    except Exception as e:
        current_app.logger.error(f'获取热力图数据失败: {e}')
        return jsonify({'error': '获取热力图数据失败', 'message': str(e)}), 500


@bp.route('/time-radar', methods=['GET'])
@jwt_required()
def get_time_radar():
    """获取时间分布数据（雷达图）"""
    current_user_id = get_jwt_identity()

    dimension = request.args.get('dimension', 'hour')  # hour, weekday, month
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        # 构建查询
        query = Expense.query.filter_by(user_id=current_user_id)

        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))

        expenses = query.all()

        # 按维度聚合
        distribution = {}

        if dimension == 'hour':
            for expense in expenses:
                hour = expense.time.hour
                distribution[hour] = distribution.get(hour, 0) + expense.amount

            data = [{'label': f'{h}时', 'value': round(distribution.get(h, 0), 2)} for h in range(24)]

        elif dimension == 'weekday':
            weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            for expense in expenses:
                weekday = expense.time.weekday()
                distribution[weekday] = distribution.get(weekday, 0) + expense.amount

            data = [{'label': weekday_names[i], 'value': round(distribution.get(i, 0), 2)} for i in range(7)]

        else:  # month
            month_names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            for expense in expenses:
                month = expense.time.month - 1
                distribution[month] = distribution.get(month, 0) + expense.amount

            data = [{'label': month_names[i], 'value': round(distribution.get(i, 0), 2)} for i in range(12)]

        return jsonify({
            'dimension': dimension,
            'data': data
        }), 200

    except Exception as e:
        current_app.logger.error(f'获取时间分布失败: {e}')
        return jsonify({'error': '获取时间分布失败', 'message': str(e)}), 500


@bp.route('/behavior-tree', methods=['GET'])
@jwt_required()
def get_behavior_tree():
    """获取消费行为关联数据（树状图/桑基图）"""
    current_user_id = get_jwt_identity()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        # 构建查询
        query = db.session.query(
            Category.name,
            Category.parent_id,
            func.sum(Expense.amount).label('total')
        ).join(Expense).filter(Expense.user_id == current_user_id)

        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))

        results = query.group_by(Category.id).all()

        # 构建树形结构
        nodes = []
        links = []

        for r in results:
            nodes.append({
                'name': r.name,
                'value': float(r.total)
            })

            if r.parent_id:
                parent = Category.query.get(r.parent_id)
                if parent:
                    links.append({
                        'source': parent.name,
                        'target': r.name,
                        'value': float(r.total)
                    })

        return jsonify({
            'nodes': nodes,
            'links': links
        }), 200

    except Exception as e:
        current_app.logger.error(f'获取行为关联失败: {e}')
        return jsonify({'error': '获取行为关联失败', 'message': str(e)}), 500


@bp.route('/level-scatter', methods=['GET'])
@jwt_required()
def get_level_scatter():
    """获取消费水平分布数据（散点图）"""
    current_user_id = get_jwt_identity()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        # 构建查询
        query = db.session.query(
            Category.name,
            func.count(Expense.id).label('frequency'),
            func.avg(Expense.amount).label('avg_amount'),
            func.sum(Expense.amount).label('total_amount')
        ).join(Expense).filter(Expense.user_id == current_user_id)

        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))

        results = query.group_by(Category.id).all()

        data = [{
            'category': r.name,
            'frequency': r.frequency,
            'avg_amount': round(float(r.avg_amount), 2),
            'total_amount': round(float(r.total_amount), 2)
        } for r in results]

        return jsonify({'data': data}), 200

    except Exception as e:
        current_app.logger.error(f'获取水平分布失败: {e}')
        return jsonify({'error': '获取水平分布失败', 'message': str(e)}), 500


@bp.route('/rank', methods=['GET'])
@jwt_required()
def get_rank():
    """获取消费排行榜数据（条形图）"""
    current_user_id = get_jwt_identity()

    rank_by = request.args.get('rank_by', 'category')  # category, location, day
    top_n = request.args.get('top_n', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        if rank_by == 'category':
            # 按类别排行
            query = db.session.query(
                Category.name,
                func.sum(Expense.amount).label('total')
            ).join(Expense).filter(Expense.user_id == current_user_id)

            if start_date:
                query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Expense.time <= datetime.fromisoformat(end_date))

            results = query.group_by(Category.id)\
                .order_by(func.sum(Expense.amount).desc())\
                .limit(top_n).all()

            data = [{'name': r.name, 'value': float(r.total)} for r in results]

        elif rank_by == 'location':
            # 按地点排行
            query = db.session.query(
                Expense.location_text,
                func.sum(Expense.amount).label('total')
            ).filter(
                Expense.user_id == current_user_id,
                Expense.location_text.isnot(None)
            )

            if start_date:
                query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Expense.time <= datetime.fromisoformat(end_date))

            results = query.group_by(Expense.location_text)\
                .order_by(func.sum(Expense.amount).desc())\
                .limit(top_n).all()

            data = [{'name': r.location_text, 'value': float(r.total)} for r in results]

        else:  # day
            # 按日期排行
            query = db.session.query(
                func.date(Expense.time).label('date'),
                func.sum(Expense.amount).label('total')
            ).filter_by(user_id=current_user_id)

            if start_date:
                query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Expense.time <= datetime.fromisoformat(end_date))

            results = query.group_by('date')\
                .order_by(func.sum(Expense.amount).desc())\
                .limit(top_n).all()

            data = [{'name': str(r.date), 'value': float(r.total)} for r in results]

        return jsonify({
            'rank_by': rank_by,
            'data': data
        }), 200

    except Exception as e:
        current_app.logger.error(f'获取排行榜失败: {e}')
        return jsonify({'error': '获取排行榜失败', 'message': str(e)}), 500

