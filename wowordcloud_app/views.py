from django.shortcuts import render, HttpResponse
# Create your views here.



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


def create_wordcloud(yt_url):
    import os
    from os import path
    import json
    import googleapiclient.discovery
    from wordcloud import WordCloud, STOPWORDS
    import re

    import numpy as np
# Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python


    
    # Allow user to enter a url and we will grab the id with regex [https://gist.github.com/silentsokolov/f5981f314bc006c82a41]
    regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
    match = regex.match(yt_url)
    if not match:
        return 'none'
    VIDEO_ID = match.group('id')


    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get('DEVELOPER_KEY')
    # VIDEO_ID = "nMwbe45OiIg" 

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    # Set the current directory
    d = os.path.dirname(__file__)

    # Variable to hold the total number of comments
    total_comments = 0


    with open(path.join(d, 'wordcloud_text.txt'), "w") as write_file:

        request = youtube.commentThreads().list(
            part="snippet,replies",
            maxResults=100,
            videoId=VIDEO_ID,
            # videoId='ddKQIUsmJpU',#"0Y6-LjDnKD0",
        )
        response = request.execute()
        

        # Write the first set of 100 comments to the textFile
        items = response["items"]
        for item in items:
            this_item = item["snippet"]
            write_file.write(this_item["topLevelComment"]["snippet"]["textDisplay"])
            total_comments += 1

        # Retrieve all the rest of the pages
        if "nextPageToken" in response:
            nextPageToken = response["nextPageToken"]
            another_page = True
        else:
            another_page = False

        while another_page:#nextPageToken:
            request = youtube.commentThreads().list(
                part="snippet,replies",
                maxResults=100,
                videoId=VIDEO_ID,
                pageToken=nextPageToken
            )
            response = request.execute()

            items = response["items"]
             # Write the rest of 100 comments to the textFile
            for item in items:
                this_item = item["snippet"]
                write_file.write(this_item["topLevelComment"]["snippet"]["textDisplay"])
                total_comments += 1

            # if total_comments >= 4000:
            #     another_page = False

            if "nextPageToken" in response:
                nextPageToken = response["nextPageToken"]
            else:
                another_page = False


    # I don't know why, but somtimes the VIDEO_ID gets added, so add VIDEO_ID to STOPWORDS
    if '-' in VIDEO_ID:
        #parse string so that you get both halves of vid id so can add each one to exclude list
        both_halves = VIDEO_ID.split('-')
        STOPWORDS.update(both_halves)

    # This will be the built in list of words that will not be included in the wordcloud
    STOPWORDS.update(['quot', 'amp', 'candidate', 'video','search_query','people', 'will', 'https', 'debate', 'br','href','watch', 'youtube',VIDEO_ID])
    stopwords = STOPWORDS
    # print(f"The total number of comments ======= {total_comments}")
    text = open(path.join(d, 'wordcloud_text.txt')).read()
    wordcloud = WordCloud(background_color='white',width=800, height=600, stopwords=stopwords).generate(text)

    # Display the generated image:
    # the matplotlib way:
    import matplotlib.pyplot as plt
    import io
    import urllib, base64
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    # plt.savefig(path.join(d, 'wordcloud_pic.png'))
    # hello = plt.show()


    # New
    imgdata = io.BytesIO()
    plt.savefig(imgdata, format='png')
    imgdata.seek(0)  # rewind the data
    string = base64.b64encode(imgdata.read())

    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    return uri

def display_wordcloud(request):
    yt_url = request.POST.get('yt_url')
    image = create_wordcloud(yt_url)
    # context = {
    #     'image': image,
    #     'url': yt_url
    # }
    # TODO: bring url functionality here, and only pass kosher url up
    if image == 'none':
        return HttpResponse("Not valid url")
    return HttpResponse(image)
    #return render(request, 'wowordcloud_app/result.html', context)
