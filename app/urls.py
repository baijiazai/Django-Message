from django.urls import path, include

from app.views import user_login, index, topic

app_name = 'app'
urlpatterns = [
    # 首页
    path('<language>', index.index, name='index'),
    # 登录、退出登录、注册、验证码
    path('login', user_login.login, name='login'),
    path('logout', user_login.logout, name='logout'),
    path('register', user_login.register, name='register'),
    path('get_ver_code', user_login.get_verification_code, name='get_ver_code'),
    # 话题查看、发布、删除
    path('topic/', include([
        path('<int:topic_id>', topic.topic_view, name='topic_view'),
        path('pub', topic.topic_pub, name='topic_pub'),
        path('del/<int:topic_id>', topic.topic_del, name='topic_del')
    ])),
    # 留言发送、删除
    path('leave_word/', include([
        path('pub', topic.leave_word_pub, name='leave_word_pub'),
        path('del/<int:leave_word_id>', topic.leave_word_del, name='leave_word_del'),
        path('zan/<int:leave_word_id>/<op>', topic.leave_word_zan, name='leave_word_zan'),
        # 留言回复发送、删除
        path('reply/', include([
            path('pub', topic.leave_word_reply_pub, name='leave_word_reply_pub'),
            path('del/<int:leave_word_reply_id>', topic.leave_word_reply_del, name='leave_word_reply_del'),
            path('zan/<int:leave_word_reply_id>/<op>', topic.leave_word_reply_zan, name='leave_word_reply_zan')
        ]))
    ]))
]
