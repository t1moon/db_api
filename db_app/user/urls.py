from django.conf.urls import include, url
from views import create, details, follow, list_followers, list_followings, list_posts, unfollow, update_profile

urlpatterns = [
    url(r'^create/', create),
    url(r'^details/', details),
    url(r'^follow/', follow),
    url(r'^listFollowers/', list_followers),
    url(r'^listFollowing/', list_followings),
    url(r'^listPosts/', list_posts),
    url(r'^unfollow/', unfollow),
    url(r'^updateProfile/', update_profile),
]
