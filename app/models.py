from django.contrib.auth.models import User
from django.db import models


# 话题表
class Topic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField('题目', max_length=64)
    content = models.TextField('内容')
    pub_date = models.DateTimeField('发布时间', auto_now=True)
    reply_num = models.IntegerField('回复数量', default=0)

    class Meta:
        verbose_name_plural = '话题'
        ordering = ['-pub_date']


# 留言
class LeaveWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name='话题')
    content = models.TextField('内容')
    pub_date = models.DateTimeField('发布时间', auto_now=True)
    zan_num = models.IntegerField('点赞数量', default=0)

    class Meta:
        verbose_name_plural = '留言'


# 留言回复
class LeaveWordReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    leave_word = models.ForeignKey(LeaveWord, on_delete=models.CASCADE, verbose_name='留言')
    content = models.CharField('内容', max_length=255)
    pub_date = models.DateTimeField('发布时间', auto_now=True)
    zan_num = models.IntegerField('点赞数量', default=0)

    class Meta:
        verbose_name_plural = '留言回复'


# 留言点赞
class LeaveWordZan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name='话题')
    leave_word = models.ForeignKey(LeaveWord, on_delete=models.CASCADE, verbose_name='留言')

    class Meta:
        verbose_name_plural = '留言点赞'


# 留言回复点赞
class LeaveWordReplyZan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name='话题')
    leave_word_reply = models.ForeignKey(LeaveWordReply, on_delete=models.CASCADE, verbose_name='留言回复')

    class Meta:
        verbose_name_plural = '留言回复点赞'
