from flask import render_template, request, current_app, session, redirect, url_for

from info.models import User
from info.modules.admin import admin_blu


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
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

    # 跳转到后台管理主页,暂未实现
    return redirect(url_for("admin.admin_index"))


@admin_blu.route('/index')
def admin_index():
    return render_template('admin/index.html')
