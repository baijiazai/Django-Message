from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from app.models import Topic, LeaveWord


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


# 创建话题
def create_topic(user_id, title='Tomorrow?', content='Tomorrow will be better.'):
    return Topic.objects.create(user_id=user_id, title=title, content=content)


# 首页测试
class IndexViewTests(TestCase):
    # 没有话题发布
    def test_no_topic(self):
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['topic_list'], [])

    # 仅有一个话题
    def test_one_topic(self):
        user = create_user()
        topic = create_topic(user.id)
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['topic_list'], ['<Topic: Topic object (3)>'])
        self.assertContains(response, topic.title)

    # 有多个话题
    def test_more_topic(self):
        user = create_user()
        create_topic(user.id)
        create_topic(user.id)
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['topic_list'],
            ['<Topic: Topic object (2)>', '<Topic: Topic object (1)>']
        )


# 话题测试
class TopicViewTests(TestCase):
    def setUp(self) -> None:
        # 默认用户已登录
        self.user = create_user()
        self.client.get(reverse('app:get_ver_code'))
        ver_code = self.client.session.get('ver_code')
        self.client.post(reverse('app:login'), data={'user': 'user', 'pwd': '123', 'verCode': ver_code})

    # 发布话题成功
    def test_pub_topic_success(self):
        self.client.post(reverse('app:topic_pub'), data={'title': 'Tomorrow?', 'content': 'Tomorrow will be better.'})
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, 'Tomorrow?')
        self.assertQuerysetEqual(response.context['topic_list'], ['<Topic: Topic object (2)>'])

    # 删除成功
    def test_del_topic_success(self):
        topic = create_topic(self.user.id)
        response = self.client.get(reverse('app:index'))
        self.assertQuerysetEqual(response.context['topic_list'], ['<Topic: Topic object (1)>'])
        self.client.get(reverse('app:topic_del', kwargs={'topic_id': topic.id}))
        response = self.client.get(reverse('app:index'))
        self.assertQuerysetEqual(response.context['topic_list'], [])

    # 删除非本人发布的话题
    def test_del_topic_that_are_not_personal(self):
        user2 = create_user(username='user2')
        topic2 = create_topic(user_id=user2.id)
        response = self.client.get(reverse('app:topic_del', kwargs={'topic_id': topic2.id}))
        self.assertEqual(response.status_code, 404)

    # 话题查看
    def test_view_topic(self):
        topic = create_topic(self.user.id)
        response = self.client.get(reverse('app:topic_view', kwargs={'topic_id': topic.id}))
        self.assertContains(response, topic.title)
        self.assertContains(response, topic.content)


# 创建留言
def create_leave_word(user_id, topic_id, content='This good.'):
    return LeaveWord.objects.create(user_id=user_id, topic_id=topic_id, content=content)


# 留言测试
class LeaveWordViewTests(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.client.get(reverse('app:get_ver_code'))
        ver_code = self.client.session.get('ver_code')
        self.client.post(reverse('app:login'), data={'user': 'user', 'pwd': '123', 'verCode': ver_code})
        self.topic = create_topic(self.user.id)

    # 该话题没有留言
    def test_no_leave_word(self):
        response = self.client.get(reverse('app:topic_view', kwargs={'topic_id': self.topic.id}))
        self.assertQuerysetEqual(response.context['leave_word_list'], [])

    # 该话题仅有一个留言
    def test_one_topic(self):
        create_leave_word(user_id=self.user.id, topic_id=self.topic.id)
        response = self.client.get(reverse('app:topic_view', kwargs={'topic_id': self.topic.id}))
        self.assertQuerysetEqual(response.context['leave_word_list'], ['<LeaveWord: LeaveWord object (5)>'])

    # 该话题有多个留言
    def test_more_topic(self):
        create_leave_word(user_id=self.user.id, topic_id=self.topic.id)
        create_leave_word(user_id=self.user.id, topic_id=self.topic.id)
        response = self.client.get(reverse('app:topic_view', kwargs={'topic_id': self.topic.id}))
        self.assertQuerysetEqual(
            response.context['leave_word_list'],
            ['<LeaveWord: LeaveWord object (4)>', '<LeaveWord: LeaveWord object (3)>']
        )

    # 发表留言成功
    def test_pub_leave_word_success(self):
        self.client.post(reverse('app:leave_word_pub'), data={'topicId': self.topic.id, 'content': 'This good.'})
        response = self.client.get(reverse('app:topic_view', kwargs={'topic_id': self.topic.id}))
        self.assertContains(response, 'This good.')

    # 删除留言成功
    def test_del_leave_word_success(self):
        leave_word = create_leave_word(user_id=self.user.id, topic_id=self.topic.id)
        self.client.get(reverse('app:leave_word_del', kwargs={'leave_word_id': leave_word.id}))
        response = self.client.get(reverse('app:topic_view', kwargs={'topic_id': self.topic.id}))
        self.assertQuerysetEqual(response.context['leave_word_list'], [])

    # 删除非本人发表的留言
    def test_del_leave_word_that_are_not_personal(self):
        user2 = create_user(username='user2')
        leave_word2 = create_leave_word(user_id=user2.id, topic_id=self.topic.id)
        response = self.client.get(reverse('app:leave_word_del', kwargs={'leave_word_id': leave_word2.id}))
        self.assertEqual(response.status_code, 404)
