from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


def create_user(username='user', password='123', email='user@qq.com'):
    # 创建一个用户
    return User.objects.create_user(username=username, password=password, email=email)


# 登录页测试
class UserLoginTests(TestCase):
    def setUp(self) -> None:
        # 默认创建一个用户
        create_user()
        # 默认请求验证码
        self.client.get(reverse('app:get_ver_code'))

    # 验证码错误
    def test_verification_code_error(self):
        response = self.client.post(reverse('app:login'), data={'user': 'lala', 'pwd': '123', 'verCode': 'ver_code'})
        self.assertContains(response, '验证码错误！')

    # 用户名错误
    def test_username_error(self):
        ver_code = self.client.session.get('ver_code')
        response = self.client.post(reverse('app:login'), data={'user': 'lala', 'pwd': '123', 'verCode': ver_code})
        self.assertContains(response, '用户名或密码错误！')

    # 密码错误
    def test_password_error(self):
        ver_code = self.client.session.get('ver_code')
        response = self.client.post(reverse('app:login'), data={'user': 'user', 'pwd': '456', 'verCode': ver_code})
        self.assertContains(response, '用户名或密码错误！')

    # 用户名密码正确，登录成功并重定向到首页显示用户名与退出登录
    def test_user_login_success_and_logout_success(self):
        # 登录成功
        ver_code = self.client.session.get('ver_code')
        self.client.post(reverse('app:login'), data={'user': 'user', 'pwd': '123', 'verCode': ver_code})
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, 'user')
        self.assertContains(response, '退出登录')
        # 退出登录
        self.client.get(reverse('app:logout'))
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, '登录')


# 注册页测试
class UserRegisterTest(TestCase):
    def setUp(self) -> None:
        # 默认创建一个用户
        create_user()
        # 默认请求验证码
        self.client.get(reverse('app:get_ver_code'))

    # 验证码错误
    def test_verification_code_error(self):
        data = {'email': 'lala@qq.com',
                'user': 'lala',
                'pwd': '123',
                'verCode': 'ver_code'}
        response = self.client.post(reverse('app:register'), data=data)
        self.assertContains(response, '验证码错误！')

    # 用户名已存在
    def test_username_is_exist(self):
        ver_code = self.client.session.get('ver_code')
        data = {'email': 'user@qq.com',
                'user': 'user',
                'pwd': '123',
                'verCode': ver_code}
        response = self.client.post(reverse('app:register'), data=data)
        self.assertContains(response, '用户名已被注册！')

    # 用户注册成功
    def test_user_register_success(self):
        self.client.get(reverse('app:get_ver_code'))
        ver_code = self.client.session.get('ver_code')
        data = {'email': 'lala@qq.com',
                'user': 'lala',
                'pwd': '123',
                'verCode': ver_code}
        self.client.post(reverse('app:register'), data=data)
        user = User.objects.get(username=data['user'])
        self.assertEqual(data['user'], user.username)
