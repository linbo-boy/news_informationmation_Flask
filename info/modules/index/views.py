from . import index_blu
from ... import redis_store


@index_blu.route('/')
def index():
    # 向redis中保存一个值name lin
    redis_store.set('name', 'linbo')
    return 'index'
