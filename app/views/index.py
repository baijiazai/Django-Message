from django.shortcuts import render
from django.views.decorators.cache import cache_page

from app.models import Topic, Category
from app.utils.page import Pagination


@cache_page(timeout=15, cache='default')
def index(request, language):
    # 以语言为过滤条件
    if language == 'all':
        topic_queryset = Topic.objects.all().order_by('-reply_num', '-pub_date')
    else:
        topic_queryset = Topic.objects.filter(lang__language=language).order_by('-pub_date', '-reply_num')
    # 获取所有的分类
    category_queryset = Category.objects.all()
    # 总页数
    page_count = topic_queryset.count()
    # 当前页
    current_page_num = request.GET.get("page")
    pagination = Pagination(current_page_num, page_count, request)
    # 处理之后的数据
    topic_queryset = topic_queryset[pagination.start:pagination.end]
    context = {
        'topic_list': topic_queryset,
        'category_queryset': category_queryset,
        "pagination": pagination,
    }
    return render(request, 'app/index.html', context)
