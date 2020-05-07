import redis


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
