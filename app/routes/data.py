"""数据导入/导出路由"""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import pandas as pd
from app import db
from app.models.expense import Expense
from app.models.category import Category
from app.models.import_record import ImportRecord

bp = Blueprint('data', __name__)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/import', methods=['POST'])
@jwt_required()
def import_data():
    """导入消费数据（Excel/CSV）"""
    current_user_id = get_jwt_identity()
    
    # 检查文件
    if 'file' not in request.files:
        return jsonify({'error': '未找到上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，仅支持 CSV、XLSX、XLS'}), 400
    
    try:
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 创建导入记录
        import_record = ImportRecord(
            user_id=current_user_id,
            filename=filename,
            status='processing'
        )
        db.session.add(import_record)
        db.session.commit()
        
        # 读取文件
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # 验证必需列
        required_columns = ['time', 'amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            import_record.status = 'failed'
            db.session.commit()
            return jsonify({
                'error': f'缺少必需列: {", ".join(missing_columns)}',
                'required_columns': required_columns,
                'found_columns': list(df.columns)
            }), 400
        
        # 处理数据
        rows_total = len(df)
        rows_success = 0
        rows_failed = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # 解析时间
                expense_time = pd.to_datetime(row['time'])
                
                # 解析金额
                amount = float(row['amount'])
                
                # 查找或创建类别
                category_id = None
                if 'category' in row and pd.notna(row['category']):
                    category_name = str(row['category'])
                    category = Category.query.filter_by(name=category_name).first()
                    if not category:
                        category = Category(name=category_name)
                        db.session.add(category)
                        db.session.flush()
                    category_id = category.id
                
                # 创建消费记录
                expense = Expense(
                    user_id=current_user_id,
                    time=expense_time,
                    amount=amount,
                    category_id=category_id,
                    location_text=row.get('location') if 'location' in row else None,
                    note=row.get('note') if 'note' in row else None
                )
                
                db.session.add(expense)
                rows_success += 1
                
            except Exception as e:
                rows_failed += 1
                errors.append({
                    'row': idx + 2,  # Excel 行号（从1开始，加上表头）
                    'error': str(e)
                })
        
        # 更新导入记录
        import_record.rows_total = rows_total
        import_record.rows_success = rows_success
        import_record.rows_failed = rows_failed
        import_record.status = 'success' if rows_failed == 0 else 'partial'
        
        # 保存错误报告
        if errors:
            error_filename = f"errors_{timestamp}.json"
            error_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], error_filename)
            import json
            with open(error_filepath, 'w', encoding='utf-8') as f:
                json.dump(errors, f, ensure_ascii=False, indent=2)
            import_record.error_report_path = error_filepath
        
        db.session.commit()
        
        current_app.logger.info(f'数据导入完成: {rows_success}/{rows_total} 成功')
        
        return jsonify({
            'message': '导入完成',
            'import_record': import_record.to_dict(),
            'errors': errors[:10] if errors else []  # 只返回前10个错误
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'导入失败: {e}')
        return jsonify({'error': '导入失败', 'message': str(e)}), 500


@bp.route('/export', methods=['GET'])
@jwt_required()
def export_data():
    """导出消费数据"""
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    format_type = request.args.get('format', 'csv')  # csv 或 xlsx
    
    try:
        # 构建查询
        query = Expense.query.filter_by(user_id=current_user_id)
        
        if start_date:
            query = query.filter(Expense.time >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(Expense.time <= datetime.fromisoformat(end_date))
        
        if category_id:
            query = query.filter_by(category_id=int(category_id))
        
        expenses = query.order_by(Expense.time.desc()).all()
        
        # 转换为 DataFrame
        data = []
        for expense in expenses:
            data.append({
                'id': expense.id,
                'time': expense.time.isoformat(),
                'amount': expense.amount,
                'category': expense.category.name if expense.category else '',
                'location': expense.location_text or '',
                'note': expense.note or ''
            })
        
        df = pd.DataFrame(data)
        
        # 生成文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'xlsx':
            filename = f'expenses_{timestamp}.xlsx'
            filepath = os.path.join(current_app.config['EXPORT_FOLDER'], filename)
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            filename = f'expenses_{timestamp}.csv'
            filepath = os.path.join(current_app.config['EXPORT_FOLDER'], filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        current_app.logger.info(f'数据导出: {len(expenses)} 条记录')
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f'导出失败: {e}')
        return jsonify({'error': '导出失败', 'message': str(e)}), 500


@bp.route('/imports', methods=['GET'])
@jwt_required()
def get_import_records():
    """获取导入记录列表"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = ImportRecord.query.filter_by(user_id=current_user_id)\
        .order_by(ImportRecord.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'records': [record.to_dict() for record in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

