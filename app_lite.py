from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import sqlite3
import xlsxwriter
from io import BytesIO
import os
import json

app = Flask(__name__)
CORS(app)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('volunteer_points.db')
    c = conn.cursor()

    # 检查表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='volunteer_points'")
    table_exists = c.fetchone()

    if not table_exists:
        # 创建新表，activity_type 在最左侧
        c.execute('''
            CREATE TABLE volunteer_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT,
                activity_time_name TEXT,
                category TEXT,
                name TEXT,
                score TEXT
            )
        ''')
    
    # 创建志愿者积分使用情况表
    c.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            total_points INTEGER DEFAULT 0,
            used_points INTEGER DEFAULT 0,
            course_count INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# 提供 index.html 文件
@app.route('/')
def index():
    return render_template('volunteer_points_platform.html')

# 处理数据提交
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    try:
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()

        # 处理活动数据（第一个表格）
        activity_data = data.get('activityData', [])
        for row in activity_data:
            if len(row) == 5:
                # 新格式：[activity_type, activity_time_name, category, name, score]
                activity_type = row[0]

                # 如果是英文值，转换为中文
                if activity_type == 'offline':
                    activity_type = '线下活动'
                elif activity_type == 'online':
                    activity_type = '线上直播'

                c.execute('''
                    INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                    VALUES (?,?,?,?,?)
                ''', [activity_type, row[1], row[2], row[3], row[4]])
            elif len(row) == 4:
                # 兼容旧格式：[activity_time_name, category, name, score]，默认为线下活动
                c.execute('''
                    INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                    VALUES (?,?,?,?,?)
                ''', ['线下活动'] + row)

        # 处理积分使用数据（第二个表格）
        usage_data = data.get('usageData', [])
        for row in usage_data:
            if len(row) == 3:
                # 格式：[name, used_points, course_count]
                name, used_points, course_count = row

                # 计算该志愿者的总积分
                c.execute('''
                    SELECT SUM(CAST(score AS INTEGER))
                    FROM volunteer_points
                    WHERE name = ?
                ''', (name,))
                result = c.fetchone()
                total_points = result[0] if result[0] else 0

                # 检查是否已存在该志愿者的记录
                c.execute('''
                    SELECT used_points, course_count
                    FROM volunteer_usage
                    WHERE name = ?
                ''', (name,))
                existing_record = c.fetchone()

                if existing_record:
                    # 如果存在记录，累加已使用积分和兑换课程数量
                    existing_used_points = existing_record[0] or 0
                    existing_course_count = existing_record[1] or 0

                    new_used_points = existing_used_points + (int(used_points) if used_points else 0)
                    new_course_count = existing_course_count + (int(course_count) if course_count else 0)

                    c.execute('''
                        UPDATE volunteer_usage
                        SET total_points = ?, used_points = ?, course_count = ?
                        WHERE name = ?
                    ''', (total_points, new_used_points, new_course_count, name))
                else:
                    # 如果不存在记录，创建新记录
                    c.execute('''
                        INSERT INTO volunteer_usage (name, total_points, used_points, course_count)
                        VALUES (?, ?, ?, ?)
                    ''', (name, total_points, int(used_points) if used_points else 0, int(course_count) if course_count else 0))

        conn.commit()
        return jsonify({"message": "提交成功"}), 200
    except Exception as e:
        return jsonify({"message": f"提交失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 处理 Excel 导出 - 不使用 pandas
@app.route('/export', methods=['POST'])
def export():
    data = request.get_json()
    try:
        if not data:
            return jsonify({"message": "没有可导出的数据"}), 400

        # 创建Excel文件
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('志愿者积分')
        
        # 添加表头格式
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # 写入表头
        headers = ['活动时间与名称', '类别', '名字', '积分']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # 写入数据
        for row_idx, row_data in enumerate(data, 1):
            for col_idx, cell_data in enumerate(row_data):
                worksheet.write(row_idx, col_idx, cell_data)
        
        # 合并单元格
        if len(data) > 1:
            first_row_activity = data[0][0]
            worksheet.merge_range(1, 0, len(data), 0, first_row_activity)
        
        workbook.close()
        output.seek(0)
        
        return send_file(
            output, 
            as_attachment=True,
            download_name='volunteer_points.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"message": f"导出失败: {str(e)}"}), 500

# 获取汇总数据
@app.route('/get_summary', methods=['GET'])
def get_summary():
    try:
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()

        # 按名字分组并累加积分
        c.execute('''
            SELECT name, SUM(CAST(score AS INTEGER)) as total_score
            FROM volunteer_points
            GROUP BY name
            ORDER BY name
        ''')
        data = c.fetchall()

        # 转换为字典格式
        summary_data = []
        for name, total_score in data:
            summary_data.append({
                'name': name,
                'total_score': total_score
            })

        return jsonify(summary_data), 200

    except Exception as e:
        return jsonify({"message": f"获取汇总数据失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 处理数据库数据导出
@app.route('/export_db', methods=['GET'])
def export_db():
    try:
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()

        # 查询所有数据，包含活动类型
        c.execute('SELECT activity_type, activity_time_name, category, name, score FROM volunteer_points ORDER BY id')
        data = c.fetchall()

        if not data:
            return jsonify({"message": "数据库中没有数据可导出"}), 400

        # 创建Excel文件
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('志愿者积分数据')
        
        # 添加表头格式
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # 写入表头
        headers = ['活动类型', '活动时间与名称', '类别', '名字', '积分']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 15)  # 设置列宽
        
        # 写入数据
        for row_idx, row_data in enumerate(data, 1):
            for col_idx, cell_data in enumerate(row_data):
                worksheet.write(row_idx, col_idx, cell_data)
        
        workbook.close()
        output.seek(0)
        
        # 生成文件名（包含当前日期）
        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        filename = f'volunteer_points_database_{current_date}.xlsx'
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"message": f"导出失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 获取志愿者积分使用情况数据
@app.route('/get_usage_summary', methods=['GET'])
def get_usage_summary():
    try:
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()

        # 查询所有志愿者的积分使用情况
        c.execute('''
            SELECT name, total_points, used_points, course_count
            FROM volunteer_usage
            ORDER BY name
        ''')
        usage_data = c.fetchall()

        # 转换为字典格式
        result = []
        for row in usage_data:
            result.append({
                'name': row[0],
                'total_points': row[1],
                'used_points': row[2],
                'course_count': row[3]
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"获取数据失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 处理志愿者积分总表导出
@app.route('/export_volunteer_summary', methods=['GET'])
def export_volunteer_summary():
    try:
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()

        # 查询志愿者积分汇总数据
        c.execute('''
            SELECT name, SUM(CAST(score AS INTEGER)) as total_score
            FROM volunteer_points
            GROUP BY name
            ORDER BY name
        ''')
        data = c.fetchall()

        if not data:
            return jsonify({"message": "数据库中没有志愿者数据可导出"}), 400

        # 创建Excel文件
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('志愿者积分总表')
        
        # 添加表头格式
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # 写入表头
        headers = ['志愿者名字', '总积分', '已使用积分']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 15)  # 设置列宽
        
        # 写入数据
        for row_idx, (name, total_score) in enumerate(data, 1):
            worksheet.write(row_idx, 0, name)
            worksheet.write(row_idx, 1, total_score)
            worksheet.write(row_idx, 2, 0)  # 已使用积分默认为0
        
        workbook.close()
        output.seek(0)
        
        # 生成文件名（包含当前日期）
        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        filename = f'volunteer_points_summary_{current_date}.xlsx'
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"message": f"导出失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)