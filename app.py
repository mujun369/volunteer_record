import logging
import os
import sys

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

def get_environment():
    """安全地获取环境类型"""
    if app.debug:
        return "development"
    return "production"

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 内存存储
volunteer_data = []
usage_data = []

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    return render_template('volunteer_points_platform.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "database": "connected"})

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效的数据格式"}), 400
        
        if 'activityData' in data and data['activityData']:
            volunteer_data.extend(data['activityData'])
        
        if 'usageData' in data and data['usageData']:
            usage_data.extend(data['usageData'])
        
        return jsonify({
            "success": True,
            "message": "数据提交成功",
            "activity_count": len(data.get('activityData', [])),
            "usage_count": len(data.get('usageData', []))
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/get_summary')
def get_summary():
    try:
        summary = {}
        for record in volunteer_data:
            if len(record) >= 5:
                name = record[3]
                score = int(record[4]) if str(record[4]).isdigit() else 0
                summary[name] = summary.get(name, 0) + score
        
        result = [{"name": name, "total_score": score} for name, score in summary.items()]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_usage_summary')
def get_usage_summary():
    try:
        usage_summary = {}
        for record in usage_data:
            if len(record) >= 3:
                name = record[0]
                used_points = int(record[1]) if str(record[1]).isdigit() else 0
                course_count = int(record[2]) if str(record[2]).isdigit() else 0
                
                if name in usage_summary:
                    usage_summary[name]['used_points'] += used_points
                    usage_summary[name]['course_count'] += course_count
                else:
                    usage_summary[name] = {
                        'used_points': used_points,
                        'course_count': course_count
                    }
        
        result = [
            {
                "name": name,
                "used_points": data['used_points'],
                "course_count": data['course_count']
            }
            for name, data in usage_summary.items()
        ]
        return jsonify(result)
    except Exception as e:
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
