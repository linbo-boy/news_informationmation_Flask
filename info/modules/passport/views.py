import re
import random

from flask import request, abort, current_app, make_response, jsonify

from . import passport_blu
from info.utils.captcha.captcha import captcha
from ... import redis_store, constants
from ...libs.yuntongxun.sms import CCP
from ...models import User
from ...utils.response_code import RET


@passport_blu.route('/sms_code', methods=["POST"])
def send_msg_code():
    """
    发送短信逻辑
    1.获取用户输入的参数：手机号，图片验证码内容，图片验证码编号(随机值)
    2.校验参数(参数是否符合规则，判断是否有值)
    3.从redis中取出真实的验证码内容
    4.与用户的验证码内容进行对比，如果不一致，返回验证码输入错误
    # 4.1. 校验该手机是否已经注册
    5.如果一致，生成验证码内容(随机数据)
    6.发送短信验证码
    7.redis中保存短信验证码内容
    8.告知发送结果
    :return:
    """
    # 1.获取用户输入的参数：手机号，图片验证码内容，图片验证码编号(随机值)
    param_dict = request.json
    mobile = param_dict.get('mobile')
    image_code = param_dict.get('image_code')
    image_code_id = param_dict.get('image_code_id')
    if not all([mobile, image_code_id, image_code]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 2.校验参数(参数是否符合规则，判断是否有值)
    if not re.match("^1[3578][0-9]{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")
    # 3.从redis中取出真实的验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="数据查询失败")
    #  判断验证码是否存在，已过期
    if not real_image_code:
        return jsonify(RET.NODATA, errmsg="图片验证码过期")
    # 4.与用户的验证码内容进行对比，如果不一致，返回验证码输入错误
    if real_image_code.upper() != image_code.upper():
        return jsonify(RET.DATAERR, errmsg="验证码输入错误")
    # 4.1. 校验该手机是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if user:
        # 该手机已被注册
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")
    # 5.如果一致，生成验证码内容(随机数据)
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.debug("短信验证码的内容：%s" % sms_code)
    result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    # 6.发送短信验证码
    if result != 0:
        # 发送短信失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    # 7.redis中保存短信验证码内容
    try:
        redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")
    # 8.告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送短信成功")


@passport_blu.route('/image_code')
def get_image_code():
    """
    生成图片验证码并返回
    1.获取到当前的图片编号id
    2.判断参数是否有值
    3.生成验证码
    4.保存图片验证码文字内容到redis
    5.返回图片
    :return:
    """
    # 1.取到参数
    image_code_id = request.args.get('imageCodeId', None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()
    # 4.保存图片验证码文字内容到redis
    try:
        # 保存当前生成的图片验证码内容
        redis_store.set('ImageCodeId_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型,以便浏览器更加只能识别其是什么类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
