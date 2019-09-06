web: waitress-serve --port=$PORT my_wordcloud.wsgi:application
worker: celery -A my_wordcloud worker -B -l INFO