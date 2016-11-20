from django.conf.urls import url
from views import create, details, list_posts, list_threads, list_users

urlpatterns = [
    url(r'^create/', create),
    url(r'^details/', details),
    url(r'^listPosts/', list_posts),
    url(r'^listThreads/', list_threads),
    url(r'^listUsers/', list_users),
]
