from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from app.models import Topic, LeaveWord, LeaveWordReply


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
    # 话题对象
    topic = get_object_or_404(Topic, pk=topic_id)
    # 留言查询结果集
    leave_word_queryset = LeaveWord.objects.filter(topic_id=topic_id).order_by('-pub_date')
    # 留言回复查询结果集
    leave_word_reply_queryset = LeaveWordReply.objects.filter()
    context = {
        'topic': topic,
        'leave_word_list': leave_word_queryset
    }
    return render(request, 'app/topic_view.html', context)


# 发送留言
def leave_word_pub(request):
    if request.method == 'POST':
        user_id = request.user.id
        topic_id = request.POST.get('topicId')
        content = request.POST.get('content')
        LeaveWord.objects.create(user_id=user_id, topic_id=topic_id, content=content)
        return redirect(reverse('app:topic_view', kwargs={'topic_id': topic_id}))


# 删除留言
def leave_word_del(request, leave_word_id):
    leave_word = get_object_or_404(LeaveWord, pk=leave_word_id, user_id=request.user.id)
    topic_id = leave_word.topic.id
    leave_word.delete()
    return redirect(reverse('app:topic_view', kwargs={'topic_id': topic_id}))


# 留言回复发送
def leave_word_reply_pub(request):
    if request.method == 'POST':
        user_id = request.user.id
        leave_word_id = request.POST.get('leaveWordId')
        reply_content = request.POST.get('replyContent')
        leave_word = get_object_or_404(LeaveWord, pk=leave_word_id)
        LeaveWordReply.objects.create(user_id=user_id, leave_word_id=leave_word_id, content=reply_content)
        return redirect(reverse('app:topic_view', kwargs={'topic_id': leave_word.topic.id}))


# 留言回复删除
def leave_word_reply_del(request, leave_word_reply_id):
    user_id = request.user.id
    leave_word_reply = get_object_or_404(LeaveWordReply, pk=leave_word_reply_id, user_id=user_id)
    topic_id = leave_word_reply.leave_word.topic.id
    leave_word_reply.delete()
    return redirect(reverse('app:topic_view', kwargs={'topic_id': topic_id}))
