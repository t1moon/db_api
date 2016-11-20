from django.conf.urls import include, url

urlpatterns = [
    url(r'^forum/', include('db_app.forum.urls')),
    url(r'^user/', include('db_app.user.urls')),
    url(r'^post/', include('db_app.post.urls')),
    url(r'^thread/', include('db_app.thread.urls')),
    url(r'^', include('db_app.common.urls'))
]