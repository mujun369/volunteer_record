import sqlite3

def clear_database():
    try:
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()
        
        # 清空志愿者积分表
        c.execute('DELETE FROM volunteer_points')
        
        # 清空志愿者积分使用情况表
        c.execute('DELETE FROM volunteer_usage')
        
        # 重置自增ID
        c.execute('DELETE FROM sqlite_sequence WHERE name="volunteer_points"')
        c.execute('DELETE FROM sqlite_sequence WHERE name="volunteer_usage"')
        
        conn.commit()
        print("数据库已成功清空")
    except Exception as e:
        print(f"清空数据库失败: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_database()