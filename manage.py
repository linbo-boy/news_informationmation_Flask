import logging

from flask import session, current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

# 通过指定的配置文件创建对应配置的app
# create_app 就类似于工厂方法
app = create_app('development')
manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 将数据库迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
