from json import loads

from django.db import connection
from django.http import JsonResponse

from db_app.helper import codes
from db_app.queries.forum import SELECT_FORUM_ID_BY_SLUG
from db_app.queries.profile import SELECT_PROFILE_NAME_ID_BY_EMAIL
from db_app.queries.thread import SELECT_THREAD_BY_ID


def create(request):
    pass




def details(request):
    pass


def list_posts(request):
    pass


def remove(request):
    pass


def restore(request):
    pass


def update(request):
    pass


def vote(request):
    pass

