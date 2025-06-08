FROM python:3.9-slim

WORKDIR /app

# 复制应用文件
COPY . .

# 安装依赖，明确避免 NumPy
RUN pip install --upgrade pip && \
    pip install flask==2.0.1 flask-cors==3.0.10 gunicorn==20.1.0 \
    xlsxwriter==3.0.2 itsdangerous==2.0.1 Jinja2==3.0.1 \
    MarkupSafe==2.0.1 Werkzeug==2.0.1 click==8.0.1 --no-deps && \
    pip list

# 设置环境变量
ENV FLASK_APP=app_lite.py
ENV PORT=5001

# 暴露端口
EXPOSE 5001

# 启动应用
CMD gunicorn app_lite:app --bind 0.0.0.0:$PORT