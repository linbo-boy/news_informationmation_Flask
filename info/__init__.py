import pymysql
import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import config

# 初始化数据库，在Flask很多扩展里都可以先初始化扩展对象，然后调用init_app方法初始化
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 通过app初始化
    db.init_app(app)
    pymysql.install_as_MySQLdb()
    # 初始化redis存储对象
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启当前项目CSRF保护,只做服务器验证功能
    CSRFProtect(app)
    # 设置Session保存指定位置
    Session(app)
    return app
