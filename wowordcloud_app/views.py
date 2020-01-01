from django.shortcuts import render, HttpResponse
from .models import YoutubeUrl
from django.contrib import messages
from django.http import JsonResponse # for ajax resonse
from django.views.decorators.http import require_POST

# celery
from .tasks import create_wordcloud
from celery import current_app # used when checking task status

def index(request):
    import os
    from os import path
    # Set the current directory
    d = os.path.dirname(__file__)
    with open(path.join(d,'logo_base64_image.txt'), 'r') as file:
        logo_image = file.read().replace('\n', '')
    with open(path.join(d,'sample_image64.txt'), 'r') as file:
        sample_image = file.read().replace('\n', '')
    context = {
        'logo_image':logo_image,
        'sample_image': sample_image 
    }
    return render(request, 'wowordcloud_app/index.html', context)


@require_POST
def display_wordcloud(request):
    import re

    yt_url = request.POST.get('yt_url') # get url from form

    # Allow user to enter a url and we will grab the id with regex [https://gist.github.com/silentsokolov/f5981f314bc006c82a41]
    regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
    match = regex.match(yt_url)
    if not match:
        response = JsonResponse({"error": "Please enter a valid YouTube URL"})
        response.status_code = 404 # To announce that the user isn't allowed to publish
        return response
    # Get video id from url
    VIDEO_ID = match.group('id')
    
    # save url to model
    YoutubeUrl(yt_url=yt_url).save()

    # return HttpResponse("Not valid url")
    image_task = create_wordcloud.delay(VIDEO_ID) # This is calling the celery task

    context = {
        'image_task_id': image_task.id,
        'image_task_status': image_task.status
    }
    return HttpResponse(image_task)
    # return render(request, 'wowordcloud_app/index.html', context)

# Use this with AJAX to check up on task status
def get_status(request):
    task_id = request.GET.get('image_task_id')
    task = current_app.AsyncResult(task_id)
    response_data = {'task_status': task.status, 'task_id': task.id}

    if task.status == 'SUCCESS':
        response_data['results'] = task.get()

    return JsonResponse(response_data)
