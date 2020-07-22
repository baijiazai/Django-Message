from django.shortcuts import render

from app.models import Topic


def index(request):
    topic_queryset = Topic.objects.all().order_by('-pub_date', '-reply_num')
    context = {
        'topic_list': topic_queryset
    }
    print(topic_queryset)
    return render(request, 'app/index.html', context)
