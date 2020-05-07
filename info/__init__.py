import pymysql
import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import config

app = Flask(__name__)
# 加载配置
app.config.from_object(config['testing'])
# 初始化数据库
db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()
# 初始化redis存储对象
redis_store = redis.StrictRedis(host=config['testing'].REDIS_HOST, port=config['testing'].REDIS_PORT)
# 开启当前项目CSRF保护,只做服务器验证功能
CSRFProtect(app)
# 设置Session保存指定位置
Session(app)
