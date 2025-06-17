import logging
import os
import sys
import io
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 在应用初始化后立即添加
logger.info("=" * 50)
logger.info("应用初始化")
logger.info(f"Python版本: {sys.version}")
logger.info(f"工作目录: {os.getcwd()}")
logger.info(f"__file__: {__file__}")
logger.info(f"模块搜索路径: {sys.path}")
logger.info("=" * 50)

app = Flask(__name__)
CORS(app)

# Supabase配置
try:
    from supabase import create_client, Client

    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    # 优先使用服务密钥，如果没有则使用匿名密钥
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_ANON_KEY')

    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase客户端初始化成功")
        USE_SUPABASE = True
    else:
        logger.warning("Supabase环境变量未设置，使用内存存储")
        USE_SUPABASE = False
        supabase = None
except ImportError:
    logger.warning("Supabase包未安装，使用内存存储")
    USE_SUPABASE = False
    supabase = None

# 内存存储（备用）
volunteer_data = []
usage_data = []

@app.route('/')
def index():
    return render_template('volunteer_points_platform.html')

@app.route('/api/health')
def health():
    db_status = "supabase" if USE_SUPABASE else "memory"
    supabase_url = os.environ.get('SUPABASE_URL', 'Not set')
    supabase_key_set = bool(os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_ANON_KEY'))

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "supabase_url": supabase_url[:50] + "..." if len(supabase_url) > 50 else supabase_url,
        "supabase_key_set": supabase_key_set,
        "use_supabase": USE_SUPABASE,
        "supabase_client": supabase is not None
    })

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效的数据格式"}), 400

        activity_count = 0
        usage_count = 0
        errors = []

        # 检查Supabase连接
        if not USE_SUPABASE or not supabase:
            return jsonify({
                "success": False,
                "message": "数据库连接失败，请联系管理员"
            }), 500

        # 处理活动数据
        if 'activityData' in data and data['activityData']:
            for row in data['activityData']:
                if len(row) >= 5:
                    try:
                        result = supabase.table('volunteer_points').insert({
                            'activity_type': row[0],
                            'activity_time_name': row[1],
                            'category': row[2],
                            'name': row[3],
                            'score': int(row[4]) if str(row[4]).isdigit() else 0
                        }).execute()
                        if result.data:
                            activity_count += 1
                        else:
                            errors.append(f"保存活动数据失败: {row}")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"保存活动数据失败: {error_msg}")
                        errors.append(f"保存活动数据失败: {error_msg}")

        # 处理使用数据
        if 'usageData' in data and data['usageData']:
            for row in data['usageData']:
                if len(row) >= 3:
                    try:
                        result = supabase.table('volunteer_usage').insert({
                            'name': row[0],
                            'used_points': int(row[1]) if str(row[1]).isdigit() else 0,
                            'course_count': int(row[2]) if str(row[2]).isdigit() else 0
                        }).execute()
                        if result.data:
                            usage_count += 1
                        else:
                            errors.append(f"保存使用数据失败: {row}")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"保存使用数据失败: {error_msg}")
                        errors.append(f"保存使用数据失败: {error_msg}")

        if errors:
            return jsonify({
                "success": False,
                "message": f"部分数据保存失败: {'; '.join(errors[:3])}",
                "activity_count": activity_count,
                "usage_count": usage_count,
                "errors": errors
            }), 400

        return jsonify({
            "success": True,
            "message": "数据提交成功",
            "activity_count": activity_count,
            "usage_count": usage_count
        })
    except Exception as e:
        logger.error(f"提交数据失败: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/get_summary')
def get_summary():
    try:
        if not USE_SUPABASE or not supabase:
            return jsonify({"error": "数据库连接失败"}), 500

        # 从Supabase获取数据
        result = supabase.table('volunteer_points').select('name, score').execute()
        logger.info(f"从Supabase获取到 {len(result.data)} 条记录")

        summary = {}
        for record in result.data:
            name = record['name']
            score = int(record['score']) if record['score'] is not None else 0
            summary[name] = summary.get(name, 0) + score

        result_list = [{"name": name, "total_score": score} for name, score in summary.items()]
        logger.info(f"返回汇总数据: {result_list}")
        return jsonify(result_list)
    except Exception as e:
        logger.error(f"获取汇总数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_usage_summary')
def get_usage_summary():
    try:
        client = supabase_admin or supabase
        if not USE_SUPABASE or not client:
            return jsonify({"error": "数据库连接失败"}), 500

        # 从Supabase获取数据
        result = client.table('volunteer_usage').select('name, used_points, course_count').execute()
        logger.info(f"从Supabase获取到 {len(result.data)} 条使用记录")

        usage_summary = {}
        for record in result.data:
            name = record['name']
            used_points = record['used_points']
            course_count = record['course_count']

            if name in usage_summary:
                usage_summary[name]['used_points'] += used_points
                usage_summary[name]['course_count'] += course_count
            else:
                usage_summary[name] = {
                    'used_points': used_points,
                    'course_count': course_count
                }

        result_list = [
            {
                "name": name,
                "used_points": data['used_points'],
                "course_count": data['course_count']
            }
            for name, data in usage_summary.items()
        ]
        logger.info(f"返回使用汇总数据: {result_list}")
        return jsonify(result_list)
    except Exception as e:
        logger.error(f"获取使用汇总数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_db')
def export_db():
    """导出活动总览表"""
    try:
        client = supabase_admin or supabase
        if not USE_SUPABASE or not client:
            return jsonify({"error": "数据库连接失败"}), 500

        # 创建Excel文件
        import pandas as pd

        # 从Supabase获取数据
        result = client.table('volunteer_points').select('*').execute()
        data = result.data
        logger.info(f"导出数据: 获取到 {len(data)} 条记录")

        if not data:
            return jsonify({"error": "没有数据可导出"}), 400

        df = pd.DataFrame(data)
        # 重命名列为中文
        df = df.rename(columns={
            'activity_type': '活动类型',
            'activity_time_name': '活动时间与名称',
            'category': '类别',
            'name': '姓名',
            'score': '积分'
        })

        # 只保留需要的列
        columns_to_keep = ['活动类型', '活动时间与名称', '类别', '姓名', '积分']
        df = df[columns_to_keep]

        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='活动总览', index=False)

        output.seek(0)
        filename = f'volunteer_activity_overview_{datetime.now().strftime("%Y%m%d")}.xlsx'

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"导出活动总览失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_volunteer_summary')
def export_volunteer_summary():
    """导出志愿者积分总表"""
    try:
        client = supabase_admin or supabase
        if not USE_SUPABASE or not client:
            return jsonify({"error": "数据库连接失败"}), 500

        import pandas as pd

        # 从Supabase获取数据并汇总
        result = client.table('volunteer_points').select('name, score').execute()
        logger.info(f"导出汇总数据: 获取到 {len(result.data)} 条记录")

        summary = {}
        for record in result.data:
            name = record['name']
            score = int(record['score']) if record['score'] is not None else 0
            summary[name] = summary.get(name, 0) + score

        if not summary:
            return jsonify({"error": "没有数据可导出"}), 400

        # 创建DataFrame
        df = pd.DataFrame([
            {"姓名": name, "总积分": score}
            for name, score in summary.items()
        ])

        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='志愿者积分总表', index=False)

        output.seek(0)
        filename = f'volunteer_points_summary_{datetime.now().strftime("%Y%m%d")}.xlsx'

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"导出志愿者积分总表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """处理404错误"""
    logger.warning(f"404错误: {request.path}")
    return jsonify({
        "error": "Not Found",
        "message": f"路径 '{request.path}' 不存在",
        "status_code": 404,
        "available_routes": [str(rule) for rule in app.url_map.iter_rules()]
    }), 404

@app.errorhandler(500)
def internal_server_error(e):
    """处理500错误"""
    logger.error(f"500错误: {str(e)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": str(e),
        "status_code": 500
    }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
