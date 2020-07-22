import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.contrib import auth
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse


# 登录
def login(request):
    if request.method == 'POST':
        username = request.POST.get('user')
        password = request.POST.get('pwd')
        ver_code = request.POST.get('verCode')
        # 验证码验证
        if ver_code.lower() == request.session.get('ver_code').lower():
            # 用户名密码验证
            user = auth.authenticate(username=username, password=password)
            # 如果 user 不为空，则给验证成功的用户加 session，将 request.user 赋值为用户对象
            if user:
                auth.login(request, user)
                return redirect(reverse('app:index', kwargs={'language': 'all'}))
            # 若 user 为空，则给出相应的提示
            return render(request, 'app/login.html', {'msg': '用户名或密码错误！'})
        return render(request, 'app/login.html', {'msg': '验证码错误！'})
    return render(request, 'app/login.html')


# 退出登录
def logout(request):
    auth.logout(request)
    return redirect(reverse('app:login'))


# 注册
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('user')
        password = request.POST.get('pwd')
        ver_code = request.POST.get('verCode')
        # 验证码验证
        if ver_code.lower() == request.session.get('ver_code').lower():
            # 如果用户名未被注册则新增用户，否则给出相应的提示
            try:
                User.objects.create_user(username=username, email=email, password=password)
            except IntegrityError:
                return render(request, 'app/register.html', {'msg': '用户名已被注册！'})
            return redirect(reverse('app:login'))
        return render(request, 'app/register.html', {'msg': '验证码错误！'})
    return render(request, 'app/register.html')


# 获取验证码
def get_verification_code(request):
    # 随机颜色的生成
    def create_color():
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        return red, green, blue

    # 创建画布，mode  模式,"RGB"，size  画布的尺寸
    width = 200
    height = 70
    image = Image.new("RGB", (width, height), create_color())
    image_draw = ImageDraw.Draw(image, "RGB")
    image_font = ImageFont.truetype("C:\Windows\Fonts\Inkfree.ttf", size=width // 4)
    # 字符源
    char_source = string.digits + string.ascii_letters
    # 验证码
    code = ""
    for i in range(4):
        ch = random.choice(char_source)
        image_draw.text((5 + i * width // 4, height // 7), ch, fill=create_color(), font=image_font)
        code += ch
    # 通过session记录这个验证码并且设置过期时间为60秒
    request.session['ver_code'] = code
    # request.session.set_expiry(60)
    # 画麻子
    for i in range(height * 10):
        x = random.randint(0, width)
        y = random.randint(0, height)
        image_draw.point((x, y), fill=create_color())
    # 创建一个字节流
    byteIO = BytesIO()
    # 把图片放在字节流里面去
    image.save(byteIO, "png")
    return HttpResponse(byteIO.getvalue(), "image/png")
