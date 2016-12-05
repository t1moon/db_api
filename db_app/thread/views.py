from json import loads

from django.db import connection, IntegrityError, DatabaseError
from django.http import JsonResponse

from db_app.helper import codes
from db_app.helper.helpers import get_profile_by_email, get_thread_by_id, get_forum_by_slug
from db_app.queries.forum import SELECT_FORUM_ID_BY_SLUG
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL
from db_app.queries.thread import INSERT_THREAD, SELECT_THREAD_BY_ID, INSERT_SUBSCRIPTION, DELETE_SUBSCRIPTION, \
    UPDATE_THREAD_VOTES, UPDATE_THREAD, UPDATE_THREAD_SET_IS_CLOSED_FLAG, UPDATE_THREAD_DELETED_FLAG, \
    UPDATE_THREAD_POSTS_DELETED_FLAG, SELECT_THREAD_BY_POST_ID, SELECT_THREAD_DELETED_FLAG_BY_ID, UPDATE_THREAD_POSTS


def close_thread(request):
    json_request = loads(request.body)
    thread = json_request['thread']

    cursor = connection.cursor()
    cursor.execute(UPDATE_THREAD_SET_IS_CLOSED_FLAG.format("true"), [thread, ])
    return JsonResponse({'code': codes.OK, 'response': thread})


def open_thread(request):
    json_request = loads(request.body)
    thread = json_request['thread']

    cursor = connection.cursor()
    cursor.execute(UPDATE_THREAD_SET_IS_CLOSED_FLAG.format("false"), [thread, ])
    return JsonResponse({'code': codes.OK, 'response': thread})



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
    json_request = loads(request.body)
    thread_id = json_request['thread']
    cursor = connection.cursor()
    cursor.execute(SELECT_THREAD_DELETED_FLAG_BY_ID, [thread_id, ])
    already_deleted = cursor.fetchone()[0]
    if not already_deleted:
        cursor.execute(UPDATE_THREAD_DELETED_FLAG.format(1), [thread_id, ])
        cursor.execute(UPDATE_THREAD_POSTS_DELETED_FLAG.format(1), [thread_id, ])
        posts_diff = cursor.rowcount    #  how much posts I deleted
        posts_diff = -posts_diff
        cursor.execute(UPDATE_THREAD_POSTS, [posts_diff, thread_id])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': {"thread": thread_id}})


def restore(request):
    json_request = loads(request.body)
    thread_id = json_request['thread']
    cursor = connection.cursor()
    cursor.execute(SELECT_THREAD_DELETED_FLAG_BY_ID, [thread_id, ])
    already_deleted = cursor.fetchone()[0]
    if already_deleted:
        cursor.execute(UPDATE_THREAD_DELETED_FLAG.format(0), [thread_id, ])
        cursor.execute(UPDATE_THREAD_POSTS_DELETED_FLAG.format(0), [thread_id, ])
        posts_diff = cursor.rowcount    #  how much posts I deleted
        cursor.execute(UPDATE_THREAD_POSTS, [posts_diff, thread_id])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': {"thread": thread_id}})



def update(request):
    json_request = loads(request.body)

    thread_id = json_request['thread']
    message = json_request['message']
    slug = json_request['slug']

    cursor = connection.cursor()
    cursor.execute(UPDATE_THREAD, [message, slug, thread_id, ])
    thread, related_obj = get_thread_by_id(cursor, thread_id)
    return JsonResponse({'code': codes.OK, 'response': thread})


def vote(request):
    json_request = loads(request.body)
    vote = int(json_request['vote'])
    thread = json_request['thread']
    if vote == 1:
        column = 'likes'
    else:
        column = 'dislikes'

    cursor = connection.cursor()
    cursor.execute(UPDATE_THREAD_VOTES.format(column, column), [thread, ])
    thread_obj, related_obj = get_thread_by_id(cursor, thread)
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': thread_obj})



def list_posts(request):
    pass


def subscribe(request):
    json_request = loads(request.body)
    email = json_request['user']
    thread = json_request['thread']
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    except DatabaseError as db_err:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_err)})
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user with not found'})
     # add sub
    query = INSERT_SUBSCRIPTION
    try:
        cursor.execute(query, [thread, email])
    except IntegrityError:
        cursor.close()
        return JsonResponse({'code': codes.OK, 'response': {'thread': thread, 'user': email}})
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': {'thread': thread, 'user': email}})


def unsubscribe(request):
    json_request = loads(request.body)
    email = json_request['user']
    thread = json_request['thread']
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    except DatabaseError as db_err:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_err)})
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user with not found'})
    #delete sub
    query = DELETE_SUBSCRIPTION
    cursor.execute(query, [thread, email])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': {'thread': thread, 'user': email}})
