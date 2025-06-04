from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
from flask_cors import CORS
import sqlite3
import tablib  # 替代 pandas
from io import BytesIO
import os

# 其余代码保持不变，但替换 pandas 相关功能