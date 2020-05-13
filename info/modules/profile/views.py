from flask import render_template, redirect, g, request

from info.modules.profile import profile_blu
from info.utils.common import user_login_data


@profile_blu.route('/info')
@user_login_data
def get_user_info():
    """
    获取用户信息
    1. 获取到当前登录的用户模型
    2. 返回模型中指定内容
    :return:
    """
    user = g.user
    if not user:
        # 用户未登录，重定向到主页
        return redirect('/')
    data = {
        "user": user.to_dict(),
    }
    # 渲染模板
    return render_template("news/user.html", data=data)


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    """
    用户基本信息
    :return:
    """
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user": g.user.to_dict()})
    # 如果是POST，代表是修改用户数据
