from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from app.models import Topic


# 发布话题
def topic_pub(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        # 新增话题
        Topic.objects.create(user_id=request.user.id, title=title, content=content)
        return redirect(reverse('app:index'))
    return render(request, 'app/topic_pub.html')


# 删除话题
def topic_del(request, topic_id):
    # 话题为该用户发布的话题方可删除
    topic = get_object_or_404(Topic, pk=topic_id, user_id=request.user.id)
    topic.delete()
    return redirect(reverse('app:index'))


# 话题详情
def topic_view(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    context = {
        'topic': topic
    }
    return render(request, 'app/topic_view.html', context)