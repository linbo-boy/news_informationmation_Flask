from flask import request, abort, current_app, make_response

from . import passport_blu
from info.utils.captcha.captcha import captcha
from ... import redis_store, constants


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
