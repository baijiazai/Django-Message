from django.urls import path

from app import views
from app.views import user_login

app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    # 登录、退出登录、注册、验证码
    path('login', user_login.login, name='login'),
    path('logout', user_login.logout, name='logout'),
    path('register', user_login.register, name='register'),
    path('get_ver_code', user_login.get_verification_code, name='get_ver_code'),
]
