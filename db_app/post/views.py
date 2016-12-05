from json import loads

from django.db import connection, IntegrityError
from django.http import JsonResponse

from db_app.helper import codes
from db_app.helper.helpers import get_post_by_id, get_profile_by_email, get_thread_by_id, get_forum_by_slug
from db_app.queries.forum import SELECT_FORUM_ID_BY_SLUG
from db_app.queries.post import INSERT_POST, SELECT_POST_BY_ID, UPDATE_POST_VOTES, SELECT_DELETED_FLAG_BY_ID, \
    UPDATE_POST_DELETE_FLAG, SELECT_POSTS_BY_FORUM_OR_THREAD_UNSPECIFIED
from db_app.queries.profile import SELECT_PROFILE_NAME_ID_BY_EMAIL, INSERT_USER_FORUM
from db_app.queries.thread import SELECT_THREAD_BY_ID, UPDATE_THREAD_POSTS, SELECT_THREAD_BY_POST_ID


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
    try:
        cursor.execute(INSERT_USER_FORUM, [email, forum, user_name, user_id])
    except IntegrityError:
        pass

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
    thread_id = request.GET.get('thread')
    forum = request.GET.get('forum')
    if thread_id:
        related_name = 'thread'
        related_query = SELECT_THREAD_BY_ID
        related_params = [thread_id, ]
    else:
        related_name = 'forum'
        related_query = SELECT_FORUM_ID_BY_SLUG
        related_params = [forum, ]
    cursor = connection.cursor()
    cursor.execute(related_query, related_params)

    get_post_list_specified_query = SELECT_POSTS_BY_FORUM_OR_THREAD_UNSPECIFIED
    query_params = [related_params[0], ]

    since_date = request.GET.get('since')
    if since_date:
        get_post_list_specified_query += '''AND Posts.date >= %s '''
        query_params.append(since_date)

    order = request.GET.get('order', 'desc')
    get_post_list_specified_query += ''' ORDER BY Posts.date ''' + order

    limit = request.GET.get('limit')
    if limit:
        limit = int(limit)
        get_post_list_specified_query += ''' LIMIT %s '''
        query_params.append(limit)

    cursor.execute(get_post_list_specified_query.format(related_name), query_params)
    posts = []
    for post in cursor.fetchall():
        posts.append({
            "date": post[0].strftime("%Y-%m-%d %H:%M:%S"),
            "dislikes": post[1],
            "forum": post[2],
            "id": post[3],
            "isApproved": post[4],
            "isDeleted": post[5],
            "isEdited": post[6],
            "isHighlighted": post[7],
            "isSpam": post[8],
            "likes": post[9],
            "message": post[10],
            "parent": post[11],
            "points": post[12],
            "thread": post[13],
            "user": post[14]
        })
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': posts})


def remove(request):
    json_request = loads(request.body)
    post_id = json_request['post']
    cursor = connection.cursor()
    cursor.execute(SELECT_THREAD_BY_POST_ID, [post_id, ])
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'post not found'})
    thread_id = cursor.fetchone()[0]
    cursor.execute(SELECT_DELETED_FLAG_BY_ID, [post_id, ])
    already_deleted = cursor.fetchone()[0]
    if not already_deleted:
        cursor.execute(UPDATE_THREAD_POSTS, [-1, thread_id])
        cursor.execute(UPDATE_POST_DELETE_FLAG.format(1), [post_id, ])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': {"post": post_id}})


def restore(request):
    json_request = loads(request.body)
    post_id = json_request['post']
    cursor = connection.cursor()
    cursor.execute(SELECT_THREAD_BY_POST_ID, [post_id, ])
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'post not found'})
    thread_id = cursor.fetchone()[0]
    cursor.execute(SELECT_DELETED_FLAG_BY_ID, [post_id, ])
    already_deleted = cursor.fetchone()[0]
    if already_deleted:
        cursor.execute(UPDATE_THREAD_POSTS, [1, thread_id])
        cursor.execute(UPDATE_POST_DELETE_FLAG.format(0), [post_id, ])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': {"post": post_id}})


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
