import time
import re

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.deprecation import MiddlewareMixin

# 不需要登录都能访问的路径
NOT_NEED_LOGIN = [
    reverse('app:login'),
    reverse('app:register'),
    reverse('app:get_ver_code'),
]


# 登录拦截
class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 访问路径不在可匿名访问路径列表的都重定向到登录页
        # 首页可匿名访问
        pattern_url_index = r'^/app/[A-Za-z+#]+/$'
        res_url_index = re.search(pattern_url_index, request.path)
        # 话题详情页可匿名访问
        pattern_url_topic_detail = r'^/app/topic/\d+'
        res_url_topic_detail = re.search(pattern_url_topic_detail, request.path)
        # 登录页相关可匿名访问
        res_url_login = request.path not in NOT_NEED_LOGIN
        res = not (res_url_index or res_url_topic_detail) and request.user.id is None and res_url_login
        if res:
            return redirect(reverse('app:login'))


# 请求限频
class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = request.META.get('REMOTE_ADDR')
        black_list = cache.get('black', [])
        # 单个ip的请求队列
        requests = cache.get(ip, [])
        # 单个ip请求缓存一分钟，一分钟后弹出过期的请求
        while requests and time.time() - requests[-1] > 30:
            requests.pop()
        requests.insert(0, time.time())
        cache.set(ip, requests, timeout=10)
        # 如果30秒内单个ip请求次数大于30次则封ip一天
        if len(requests) > 30:
            black_list.append(ip)
            cache.set('black', black_list, timeout=60 * 60 * 24)
            return HttpResponse("请求频率超出标准")
        # 如果30秒内单个ip请求次数大于10次则封ip，等请求队列长度少于等于10才可再次访问
        elif len(requests) > 10:
            return HttpResponse("请求过于频繁，请稍后再试")
