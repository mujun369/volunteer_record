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
    else:
        # 检查是否已有 activity_type 列
        c.execute("PRAGMA table_info(volunteer_points)")
        columns = [column[1] for column in c.fetchall()]

        if 'activity_type' not in columns:
            # 添加 activity_type 列
            c.execute('ALTER TABLE volunteer_points ADD COLUMN activity_type TEXT')

            # 为现有数据设置默认值（假设为线下活动）
            c.execute('UPDATE volunteer_points SET activity_type = "线下活动" WHERE activity_type IS NULL')
        else:
            # 如果列已存在但位置不对，重新创建表
            c.execute("PRAGMA table_info(volunteer_points)")
            columns_info = c.fetchall()

            # 检查 activity_type 是否在正确位置（第2列，索引1）
            if len(columns_info) > 1 and columns_info[1][1] != 'activity_type':
                # 备份现有数据
                c.execute('SELECT * FROM volunteer_points')
                existing_data = c.fetchall()

                # 删除旧表
                c.execute('DROP TABLE volunteer_points')

                # 创建新表，activity_type 在正确位置
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

                # 恢复数据，重新排列列顺序
                for row in existing_data:
                    if len(row) == 6:  # 包含 activity_type
                        # 原格式：(id, activity_time_name, category, name, score, activity_type)
                        # 新格式：(id, activity_type, activity_time_name, category, name, score)
                        activity_type = row[5] or 'offline'

                        # 将英文值转换为中文
                        if activity_type == 'offline':
                            activity_type = '线下活动'
                        elif activity_type == 'online':
                            activity_type = '线上直播'

                        c.execute('''
                            INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                            VALUES (?,?,?,?,?)
                        ''', (activity_type, row[1], row[2], row[3], row[4]))
                    else:  # 旧格式，没有 activity_type
                        c.execute('''
                            INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                            VALUES (?,?,?,?,?)
                        ''', ('线下活动', row[1], row[2], row[3], row[4]))

    # 更新现有数据中的英文值为中文值
    c.execute('UPDATE volunteer_points SET activity_type = "线下活动" WHERE activity_type = "offline"')
    c.execute('UPDATE volunteer_points SET activity_type = "线上直播" WHERE activity_type = "online"')

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

        # 查询所有数据，包含活动类型
        c.execute('SELECT activity_type, activity_time_name, category, name, score FROM volunteer_points ORDER BY id')
        data = c.fetchall()

        if not data:
            return jsonify({"message": "数据库中没有数据可导出"}), 400

        # 创建DataFrame，活动类型在最左侧
        df = pd.DataFrame(data, columns=['活动类型', '活动时间与名称', '类别', '名字', '积分'])

        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='志愿者积分数据', index=False)

            # 获取工作表和工作簿对象
            worksheet = writer.sheets['志愿者积分数据']
            workbook = writer.book

            # 设置列宽
            worksheet.set_column('A:A', 15)  # 活动类型
            worksheet.set_column('B:B', 25)  # 活动时间与名称
            worksheet.set_column('C:C', 15)  # 类别
            worksheet.set_column('D:D', 15)  # 名字
            worksheet.set_column('E:E', 10)  # 积分

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

        # 创建DataFrame，包含志愿者名字、总积分、已使用积分
        summary_data = []
        for name, total_score in data:
            summary_data.append([name, total_score, 0])  # 已使用积分默认为0

        df = pd.DataFrame(summary_data, columns=['志愿者名字', '总积分', '已使用积分'])

        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='志愿者积分总表', index=False)

            # 获取工作表和工作簿对象
            worksheet = writer.sheets['志愿者积分总表']
            workbook = writer.book

            # 设置列宽
            worksheet.set_column('A:A', 20)  # 志愿者名字
            worksheet.set_column('B:B', 15)  # 总积分
            worksheet.set_column('C:C', 15)  # 已使用积分

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

            # 添加数据格式
            data_format = workbook.add_format({
                'border': 1,
                'align': 'center'
            })

            # 应用数据格式
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], data_format)

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
    app.run(debug=True, port=5001)