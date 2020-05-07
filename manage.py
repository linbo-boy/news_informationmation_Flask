from flask import Flask, session
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import pymysql
import redis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_migrate import Migrate, MigrateCommand
from config import Config


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
# 将app与db关联
Migrate(app, db)
# 将数据库迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session['name'] = '梁承嗣'
    return 'index33'


if __name__ == "__main__":
    manager.run()
