
from celery import shared_task



@shared_task
def create_wordcloud(yt_url):
    print("NOT HERE")
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

    VIDEO_ID = yt_url


    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get('DEVELOPER_KEY')
    # VIDEO_ID = "nMwbe45OiIg" 

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version,  cache_discovery=False, developerKey = DEVELOPER_KEY)

    # Set the current directory
    d = os.path.dirname(__file__)

    # Variable to hold the total number of comments
    total_comments = 0


    with open(path.join(d, 'wordcloud_text.txt'), "w") as write_file:

        request = youtube.commentThreads().list(
            part="snippet,replies",
            maxResults=100,
            videoId=VIDEO_ID,
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

        while another_page: #nextPageToken:
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

    # I don't know why, but sometimes the VIDEO_ID gets added, so add VIDEO_ID to STOPWORDS
    if '-' in VIDEO_ID:
        #parse string so that you get both halves of vid id so can add each one to exclude list
        both_halves = VIDEO_ID.split('-')
        STOPWORDS.update(both_halves)

    if len(items) > 0: # Only process commments if there ARE comments on this video
        # This will be the built in list of words that will not be included in the wordcloud
        STOPWORDS.update(['quot', 'amp', 'video','search_query', 'https', 'br','href','watch', 'youtube',VIDEO_ID])
        stopwords = STOPWORDS
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
    else:
        return "noComments" # If the video has 0 comments than it will return this. So that we can display an error to the user
