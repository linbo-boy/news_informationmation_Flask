from flask import render_template, current_app, session, g, abort, request, jsonify

from info import constants, db
from info.models import News, User, Comment
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """
    # 显示用户是否登录的逻辑
    user = g.user
    # 右侧新闻排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    news_dict_li = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询详情页新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)
    # 更新新闻的点击次数
    news.clicks += 1

    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True

    # 查询评论数据
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_dict_li = []
    for item in comments:
        comment_dict = item.to_dict()
        comment_dict_li.append(comment_dict)

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments": comment_dict_li
    }
    return render_template("news/detail.html", data=data)


@news_blu.route("/news_collect", methods=["POST"])
@user_login_data
def collect_news():
    """
    新闻收藏
    1.接受参数
    2.判断参数
    3.查询新闻并判断新闻是否存在
    :return:
    """
    # 显示用户是否登录的逻辑
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1.接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2.判断参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.查询新闻并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if action == "cancel_collect":
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        # 4.进行收藏
        if news not in user.collection_news:
            # 添加到用户的新闻收藏列表
            user.collection_news.append(news)

    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route('/news_comment', methods=["POST"])
@user_login_data
def add_news_comment():
    """
    评论新闻
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 1.获取参数
    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")

    # 2.判断参数
    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 查询新闻并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")

    # 3.初始化一个评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id

    # 4.保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())
