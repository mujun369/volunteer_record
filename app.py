from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
from flask_cors import CORS  # 新增导入
import sqlite3
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)  # 新增，解决跨域问题

# 初始化数据库
def init_db():
    conn = sqlite3.connect('volunteer_points.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_time_name TEXT,
            category TEXT,
            name TEXT,
            score TEXT
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
        for row in data:
            if len(row) == 4:
                c.execute('''
                    INSERT INTO volunteer_points (activity_time_name, category, name, score)
                    VALUES (?,?,?,?)
                ''', row)
        conn.commit()
        return jsonify({"message": "提交成功"}), 200
    except Exception as e:
        return jsonify({"message": f"提交失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 处理 Excel 导出
@app.route('/export', methods=['POST'])
def export():
    data = request.get_json()
    try:
        if not data:
            return jsonify({"message": "没有可导出的数据"}), 400

        # 验证每行数据长度是否为 4
        for index, row in enumerate(data):
            if len(row) != 4:
                print(f"第 {index + 1} 行数据格式错误，数据内容: {row}")
                return jsonify({"message": f"第 {index + 1} 行数据格式错误，每行数据应包含 4 个元素"}), 400

        # 确保被合并的行该格的数据即为单元格的数据
        if data:
            first_row_activity = data[0][0]
            for row in data[1:]:
                row[0] = first_row_activity

        # 尝试将数据转换为 DataFrame
        df = pd.DataFrame(data, columns=['活动时间与名称', '类别', '名字', '积分'])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='志愿者积分', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['志愿者积分']
            
            # 合并活动时间与名称列的单元格
            if len(data) > 1:
                worksheet.merge_range(1, 0, len(data), 0, first_row_activity)

        output.seek(0)
        return send_file(output, as_attachment=True, download_name='volunteer_points.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        # 捕获异常并返回错误信息
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

        # 查询所有数据
        c.execute('SELECT activity_time_name, category, name, score FROM volunteer_points ORDER BY id')
        data = c.fetchall()

        if not data:
            return jsonify({"message": "数据库中没有数据可导出"}), 400

        # 创建DataFrame
        df = pd.DataFrame(data, columns=['活动时间与名称', '类别', '名字', '积分'])

        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='志愿者积分数据', index=False)

            # 获取工作表和工作簿对象
            worksheet = writer.sheets['志愿者积分数据']
            workbook = writer.book

            # 设置列宽
            worksheet.set_column('A:A', 25)  # 活动时间与名称
            worksheet.set_column('B:B', 15)  # 类别
            worksheet.set_column('C:C', 15)  # 名字
            worksheet.set_column('D:D', 10)  # 积分

            # 添加表头格式
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            # 应用表头格式
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)