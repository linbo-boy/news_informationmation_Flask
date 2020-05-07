from flask import Flask, session
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import pymysql
import redis
from flask_wtf import CSRFProtect
from flask_session import Session


class Config(object):
    """工程配置信息"""
    DEBUG = True
    SECRET_KEY = 'j7g+RfhBHm5vlJKhWNOsqm9Jha0y536EQNE6Fw5TNQHyuylYkOVraAwxzMyrxYeX'

    """为数据库添加配置"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/news_information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """redis配置"""
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    """flask_session配置"""
    SESSION_TYPE = 'redis'  # Session保存位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置Session保存指定位置
    SESSION_USE_SIGNER = True  # 开启Session签名
    SESSION_PERMANENT = False  # 设置需要过期时间,而不是永久
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间为2天


app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()
# 初始化redis存储对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目CSRF保护,只做服务器验证功能
CSRFProtect(app)
# 设置Session保存指定位置
Session(app)

manager = Manager(app)


@app.route('/')
def index():
    session['name'] = '梁承嗣'
    return 'index333'


if __name__ == "__main__":
    manager.run()
