from datetime import datetime

from flask import render_template, request, current_app, session, redirect, url_for, g
import time
from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_login_data


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # 判断当前是否登录，如果是登录状态直接重定向到管理后台主页
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            # 跳转到后台管理主页
            return redirect(url_for("admin.admin_index"))
        return render_template("admin/login.html")

    # 取到登录参数
    username = request.form.get("username")
    password = request.form.get("password")
    # 判断参数
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数错误")
    # 从数据库查询当前用户
    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户信息查询失败")

    if not user:
        return render_template("admin/login.html", errmsg="未查询到用户信息")

    # 校验密码
    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="用户名或密码错误")

    if not user.is_admin:
        return render_template('admin/login.html', errmsg="用户权限错误")

    # 保存用户的登录信息
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = True

    # 跳转到后台管理主页
    return redirect(url_for("admin.admin_index"))


@admin_blu.route('/index')
@user_login_data
def admin_index():
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())


@admin_blu.route('/user_count')
def user_count():
    # 查询总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    now = time.localtime()
    mon_begin_date = datetime.strptime('%d-%02d-01' % (now.tm_year, now.tm_mon), '%Y-%m-%d')
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    day_begin_date = datetime.strptime('%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday), '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time >= day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count
    }
    return render_template('admin/user_count.html', data=data)
