from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from app.models import Topic, LeaveWord, LeaveWordReply, LeaveWordZan, LeaveWordReplyZan, Category


# 发布话题
def topic_pub(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('categoryId')
        # 新增话题
        Topic.objects.create(user_id=request.user.id, title=title, content=content, lang_id=category_id)
        return redirect(reverse('app:index'))
    return render(request, 'app/topic_pub.html', {'category_list': Category.objects.all()})


# 删除话题
def topic_del(request, topic_id):
    # 话题为该用户发布的话题方可删除
    topic = get_object_or_404(Topic, pk=topic_id, user_id=request.user.id)
    leave_word_queryset = LeaveWord.objects.filter(topic_id=topic.id)
    for leave_word in leave_word_queryset:
        leave_word_reply_queryset = LeaveWordReply.objects.filter(leave_word_id=leave_word.id)
        # 删除该话题 -> 留言 -> 所有留言回复
        for leave_word_reply in leave_word_reply_queryset:
            leave_word_reply.delete()
        # 删除该话题的留言
        leave_word.delete()
    # 删除话题
    topic.delete()
    return redirect(reverse('app:index'))


# 话题详情
def topic_view(request, topic_id):
    # 话题对象
    topic = get_object_or_404(Topic, pk=topic_id)
    # 留言查询结果集
    leave_word_queryset = LeaveWord.objects.filter(topic_id=topic_id).order_by('-pub_date', '-zan_num')
    # 用户点赞了的留言
    leave_word_zan_queryset = LeaveWordZan.objects.filter(topic_id=topic_id, user_id=request.user.id)
    leave_word_zan_ids = [i.leave_word.id for i in leave_word_zan_queryset]
    # 用户点赞了的留言回复
    leave_word_reply_zan_queryset = LeaveWordReplyZan.objects.filter(topic_id=topic_id, user_id=request.user.id)
    leave_word_reply_zan_ids = [i.leave_word_reply.id for i in leave_word_reply_zan_queryset]
    context = {
        'topic': topic,
        'leave_word_list': leave_word_queryset,
        'leave_word_zan_ids': leave_word_zan_ids,
        'leave_word_reply_zan_ids': leave_word_reply_zan_ids
    }
    return render(request, 'app/topic_view.html', context)


# 发送留言
def leave_word_pub(request):
    if request.method == 'POST':
        user_id = request.user.id
        topic_id = request.POST.get('topicId')
        content = request.POST.get('content')
        # 新增留言
        LeaveWord.objects.create(user_id=user_id, topic_id=topic_id, content=content)
        # 话题的回复数量加一
        topic = get_object_or_404(Topic, pk=topic_id)
        topic.reply_num += 1
        topic.save()
        return redirect(reverse('app:topic_view', kwargs={'topic_id': topic_id}))


# 删除留言
def leave_word_del(request, leave_word_id):
    leave_word = get_object_or_404(LeaveWord, pk=leave_word_id, user_id=request.user.id)
    topic = get_object_or_404(Topic, pk=leave_word.topic.id)
    # 删除该留言的所有回复及其所有点赞记录
    leave_word_reply_queryset = LeaveWordReply.objects.filter(leave_word_id=leave_word_id)
    leave_word_reply_count = leave_word_reply_queryset.count()
    for leave_word_reply in leave_word_reply_queryset:
        for reply_zan in leave_word_reply.leavewordreplyzan_set.all():
            reply_zan.delete()
        leave_word_reply.delete()
    # 话题回复数量减去 leave_word_reply_count 个
    topic.reply_num -= leave_word_reply_count
    topic.save()
    # 删除该留言的所有点赞记录
    for zan in leave_word.leavewordzan_set.all():
        zan.delete()
    # 删除留言记录
    leave_word.delete()
    # 话题回复数量减一
    topic.reply_num -= 1
    topic.save()
    return redirect(reverse('app:topic_view', kwargs={'topic_id': topic.id}))


# 留言回复发送
def leave_word_reply_pub(request):
    if request.method == 'POST':
        user_id = request.user.id
        leave_word_id = request.POST.get('leaveWordId')
        reply_content = request.POST.get('replyContent')
        # 获取留言对象
        leave_word = get_object_or_404(LeaveWord, pk=leave_word_id)
        # 新增留言回复
        LeaveWordReply.objects.create(user_id=user_id, leave_word_id=leave_word_id, content=reply_content)
        # 话题回复数量加一
        topic = get_object_or_404(Topic, pk=leave_word.topic.id)
        topic.reply_num += 1
        topic.save()
        return redirect(reverse('app:topic_view', kwargs={'topic_id': leave_word.topic.id}))


# 留言回复删除
def leave_word_reply_del(request, leave_word_reply_id):
    user_id = request.user.id
    leave_word_reply = get_object_or_404(LeaveWordReply, pk=leave_word_reply_id, user_id=user_id)
    topic = get_object_or_404(Topic, pk=leave_word_reply.leave_word.topic.id)
    # 删除所有留言回复点赞记录
    for reply_zan in leave_word_reply.leavewordreplyzan_set.all():
        reply_zan.delete()
    # 删除留言回复记录
    leave_word_reply.delete()
    # 话题回复数量减一
    topic.reply_num -= 1
    topic.save()
    return redirect(reverse('app:topic_view', kwargs={'topic_id': topic.id}))


# 留言点赞
def leave_word_zan(request, leave_word_id, op):
    user_id = request.user.id
    leave_word = get_object_or_404(LeaveWord, pk=leave_word_id)
    if op == 'add':
        # 点赞，新增留言点赞记录
        LeaveWordZan.objects.create(user_id=user_id, topic_id=leave_word.topic.id, leave_word_id=leave_word_id)
        # 留言点赞数量加一
        leave_word.zan_num += 1
        leave_word.save()
    elif op == 'sub':
        # 取消点赞，删除留言点赞记录
        zan = get_object_or_404(LeaveWordZan, leave_word_id=leave_word_id, user_id=user_id,
                                topic_id=leave_word.topic.id)
        zan.delete()
        # 留言点赞数量减一
        leave_word.zan_num -= 1
        leave_word.save()
    return redirect(reverse('app:topic_view', kwargs={'topic_id': leave_word.topic.id}))


# 留言回复点赞
def leave_word_reply_zan(request, leave_word_reply_id, op):
    user_id = request.user.id
    leave_word_reply = get_object_or_404(LeaveWordReply, pk=leave_word_reply_id)
    topic_id = leave_word_reply.leave_word.topic.id
    if op == 'add':
        # 点赞，新增留言回复点赞记录
        LeaveWordReplyZan.objects.create(user_id=user_id, topic_id=topic_id, leave_word_reply_id=leave_word_reply_id)
        # 留言回复点赞数量加一
        leave_word_reply.zan_num += 1
        leave_word_reply.save()
    elif op == 'sub':
        # 取消点赞，删除留言回复点赞记录
        reply_zan = get_object_or_404(LeaveWordReplyZan, leave_word_reply_id=leave_word_reply_id, user_id=user_id,
                                      topic_id=topic_id)
        reply_zan.delete()
        # 留言回复点赞数量减一
        leave_word_reply.zan_num -= 1
        leave_word_reply.save()
    return redirect(reverse('app:topic_view', kwargs={'topic_id': topic_id}))
