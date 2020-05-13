from flask import render_template, redirect, g, request, jsonify, current_app

from info import constants
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


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
    1. 获取用户登录信息
    2. 获取到传入参数
    3. 更新并保存数据
    4. 返回结果
    :return:
    """
    # 1. 获取当前登录用户的信息
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user": user.to_dict()})
    # 如果是POST，代表是修改用户数据
    # 2. 获取到传入参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    # 校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    if gender not in (['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 3. 更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user": user.to_dict()})
    # 1. 获取到上传的文件
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")

    # 2. 再将文件上传到七牛云
    try:
        key = storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 3. 将头像信息更新到当前用户的模型中

    # 设置用户模型相关数据
    user.avatar_url = key
    return jsonify(errno=RET.OK, errmsg="OK", avatar_url=constants.QINIU_DOMIN_PREFIX)


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    if request.method == "GET":
        return render_template('news/user_pass_info.html')
    # 1. 获取到传入参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 2. 获取当前登录用户的信息
    user = g.user
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")
    # 3.更新新密码数据
    user.password = new_password
    return jsonify(errno=RET.OK, errmsg="保存成功")