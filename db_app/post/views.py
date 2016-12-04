from json import loads

from django.db import connection
from django.http import JsonResponse

from db_app.helper import codes
from db_app.helper.helpers import get_post_by_id, get_profile_by_email, get_thread_by_id, get_forum_by_slug
from db_app.queries.forum import SELECT_FORUM_ID_BY_SLUG
from db_app.queries.post import INSERT_POST, SELECT_POST_BY_ID, UPDATE_POST_VOTES
from db_app.queries.profile import SELECT_PROFILE_NAME_ID_BY_EMAIL
from db_app.queries.thread import SELECT_THREAD_BY_ID, UPDATE_THREAD_POSTS


def create(request):
    json_request = loads(request.body)

    date = json_request['date']
    thread_id = json_request['thread']
    message = json_request['message']
    forum = json_request['forum']
    email = json_request['user']

    cursor = connection.cursor()
    cursor.execute(SELECT_PROFILE_NAME_ID_BY_EMAIL, [email, ])
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user not found'})
    name_id = cursor.fetchone()
    user_name = name_id[0]
    user_id = name_id[1]
    cursor.execute(SELECT_FORUM_ID_BY_SLUG, [forum, ])
    cursor.execute(SELECT_THREAD_BY_ID, [thread_id, ])
    thread_id = cursor.fetchone()[0]

    cursor.execute(INSERT_POST, [date, message, email, forum, thread_id])
    post_id = cursor.lastrowid

    #optional args
    query_params = []
    optional_args = ['isApproved', 'isDeleted', 'isEdited', 'isHighlighted', 'isSpam', 'parent']
    for optional_arg_name in optional_args:
        optional_arg_value = json_request.get(optional_arg_name)
        query_params.append([optional_arg_name, optional_arg_value])

    update_post_query = u''' UPDATE Posts SET '''
    if query_params:
        update_post_query += " , ".join(query_param[0] + "= %s " for query_param in query_params) + '''WHERE id = %s'''
        cursor.execute(update_post_query, [query_param[1] for query_param in query_params] + [post_id, ])
    post, related_ids = get_post_by_id(cursor, post_id)
    if not post['isDeleted']:
        cursor.execute(UPDATE_THREAD_POSTS, [1, thread_id])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': post})


def details(request):
    post_id = request.GET.get('post')
    cursor = connection.cursor()
    post, related_ids = get_post_by_id(cursor, post_id)
    related = request.GET.getlist('related')

    if 'user' in related:
        post['user'] = get_profile_by_email(cursor, related_ids['user'])
    elif 'thread' in related:
        post['thread'], related_ids_ = get_thread_by_id(cursor, related_ids['thread'])
    elif 'forum' in related:
        post['forum'], related_ids_ = get_forum_by_slug(cursor, related_ids['forum'])
    return JsonResponse({'code': codes.OK, 'response': post})


def list_posts(request):
    pass


def remove(request):
    pass


def restore(request):
    pass


def update(request):
    pass


def vote(request):
    json_request = loads(request.body)
    post_id = json_request['post']
    vote = json_request['vote']
    vote = int(vote)
    if vote == 1:
        column = 'likes'
    else:
        column = 'dislikes'
    cursor = connection.cursor()
    cursor.execute(SELECT_POST_BY_ID, [post_id])
    post_id = cursor.fetchone()[0]
    cursor.execute(UPDATE_POST_VOTES.format(column, column), [post_id, ])
    post, related_ = get_post_by_id(cursor, post_id)
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': post})
