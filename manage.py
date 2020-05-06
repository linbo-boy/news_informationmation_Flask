from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql


class Config(object):
    """工程配置信息"""
    Debug = True
    """为数据库添加配置"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/news_information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()


@app.route('/')
def index():
    return 'index333'


if __name__ == "__main__":
    app.run()
