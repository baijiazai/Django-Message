from django.urls import path, include

from app.views import user_login, index, topic

app_name = 'app'
urlpatterns = [
    # 首页
    path('', index.index, name='index'),
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
    ]))
]
