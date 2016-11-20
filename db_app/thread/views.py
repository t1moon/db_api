from json import loads

from django.db import connection, IntegrityError
from django.http import JsonResponse

from db_app.helper import codes
from db_app.helper.helpers import get_profile_by_email, get_thread_by_id, get_forum_by_slug
from db_app.queries.forum import SELECT_FORUM_ID_BY_SLUG
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL
from db_app.queries.thread import INSERT_THREAD


def close_thread(request):
    pass


def open_thread(request):
    pass


def create(request):
    params = loads(request.body)
    forum_name = params['forum']
    title = params['title']
    is_closed = params['isClosed']
    date = params['date']
    message = params['message']
    slug = params['slug']
    email = params['user']
    try:
        is_deleted = params['isDeleted']
    except KeyError:
        is_deleted = False

    cursor = connection.cursor()
    # get forum id
    cursor.execute(SELECT_FORUM_ID_BY_SLUG, [forum_name, ])
    if cursor.rowcount == 0:
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'Forum not found'})
    forum_id = cursor.fetchone()[0]
    # get user id
    cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    if cursor.rowcount == 0:
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'User not found'})
    user_id = cursor.fetchone()[0]
    # add thread
    try:
        cursor.execute(INSERT_THREAD, [forum_name, title, is_closed, email, date, message, slug, is_deleted])
    except IntegrityError:
        cursor.close()
        return JsonResponse({'code': codes.ALREADY_EXIST, 'response': 'Thread already exists'})
    thread_id = cursor.lastrowid
    thread = {
        "date": date,
        "forum": forum_name,
        "id": thread_id,
        "isClosed": is_closed,
        "isDeleted": is_deleted,
        "message": message,
        "slug": slug,
        "title": title,
        "user": email
    }
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': thread})


def details(request):
    thread_id = request.GET['thread']
    cursor = connection.cursor()
    try:
        thread, related_ids = get_thread_by_id(cursor, thread_id)
    except TypeError:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'Thread doesn\'t exist'})

    related = request.GET.getlist('related')
    for related_ in related:
        if related_ is 'user':
            thread['user'] = get_profile_by_email(cursor, related_ids['user'])
        if related_ is 'forum':
            thread['forum'], related_ids_ = get_forum_by_slug(cursor, related_ids['forum'])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': thread})


def list_threads(request):
    pass


def remove(request):
    pass


def restore(request):
    pass


def update(request):
    pass


def vote(request):
    pass


def list_posts(request):
    pass


def subscribe(request):
    pass


def unsubscribe(request):
    pass
