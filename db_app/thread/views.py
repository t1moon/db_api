from json import loads

from django.db import connection, IntegrityError, DatabaseError
from django.http import JsonResponse

from db_app.helper import codes
from db_app.helper.helpers import get_profile_by_email, get_thread_by_id, get_forum_by_slug
from db_app.queries.forum import SELECT_FORUM_ID_BY_SLUG
from db_app.queries.post import SELECT_ALL_POSTS_BY_THREAD
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL
from db_app.queries.thread import INSERT_THREAD, SELECT_THREAD_BY_ID, INSERT_SUBSCRIPTION, DELETE_SUBSCRIPTION, \
    UPDATE_THREAD_VOTES, UPDATE_THREAD, UPDATE_THREAD_SET_IS_CLOSED_FLAG, UPDATE_THREAD_DELETED_FLAG, \
    UPDATE_THREAD_POSTS_DELETED_FLAG, SELECT_THREAD_BY_POST_ID, SELECT_THREAD_DELETED_FLAG_BY_ID, UPDATE_THREAD_POSTS, \
    SELECT_THREADS_BY_FORUM_OR_USER


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
    short_name = request.GET.get('forum')
    email = request.GET.get('user')
    if email:
        related_table_name = 'user'
        related_query = SELECT_PROFILE_BY_EMAIL
        related_params = [email, ]
    else:
        related_table_name = 'forum'
        related_query = SELECT_FORUM_ID_BY_SLUG
        related_params = [short_name, ]
    cursor = connection.cursor()
    cursor.execute(related_query, related_params)

    query_params = [related_params[0], ]
    get_thread_list_specified_query = SELECT_THREADS_BY_FORUM_OR_USER
    since_date = request.GET.get('since')
    if since_date:
        get_thread_list_specified_query += ''' AND date >= %s '''
        query_params.append(since_date)

    order = request.GET.get('order', 'desc')
    get_thread_list_specified_query += ''' ORDER BY date ''' + order

    limit = request.GET.get('limit')
    if limit:
        limit = int(limit)
        get_thread_list_specified_query += ''' LIMIT %s '''
        query_params.append(limit)
    cursor.execute(get_thread_list_specified_query.format(related_table_name), query_params)

    threads = []
    for thread in cursor.fetchall():
        threads.append({
            "date": thread[0].strftime("%Y-%m-%d %H:%M:%S"),
            "dislikes": thread[1],
            "forum": thread[2],
            "id": thread[3],
            "isClosed": thread[4],
            "isDeleted": thread[5],
            "likes": thread[6],
            "message": thread[7],
            "points": thread[8],
            "posts": thread[9],
            "slug": thread[10],
            "title": thread[11],
            "user": thread[12]
            })
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': threads})


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
    # thread_id = request.GET.get('thread')
    #
    # cursor = connection.cursor()
    #
    # get_all_posts_specified_query = SELECT_ALL_POSTS_BY_THREAD
    # query_params = [thread_id, ]
    # since_date = request.GET.get('since')
    # if since_date:
    #     get_all_posts_specified_query += ''' AND date >= %s '''
    #     query_params.append(since_date)
    #
    # order = request.GET.get('order', 'desc')
    # sort = request.GET.get('sort', 'flat')
    # limit = request.GET.get('limit')
    # get_all_posts_specified_query, query_params = add_sorting_part(get_all_posts_specified_query, order, sort,
    #                                                                    limit, query_params, thread_id, cursor)
    #
    # cursor.execute(get_all_posts_specified_query, query_params)
    #
    # posts = []
    # for post in cursor.fetchall():
    #     posts.append({
    #         "date": post[0].strftime("%Y-%m-%d %H:%M:%S"),
    #         "dislikes": post[1],
    #         "forum": post[2],
    #         "id": post[3],
    #         "isApproved": post[4],
    #         "isDeleted": post[5],
    #         "isEdited": post[6],
    #         "isHighlighted": post[7],
    #         "isSpam": post[8],
    #         "likes": post[9],
    #         "message": post[10],
    #         "parent": post[11],
    #         "points": post[12],
    #         "thread": post[13],
    #         "user": post[14]
    #         })
    # cursor.close()
    # return JsonResponse({'code': codes.OK, 'response': posts})


# def add_sorting_part(query_prefix, order, sort, limit, query_params, thread_id, cursor):
#     if sort == 'flat':
#         query_prefix += u''' ORDER BY date ''' + order
#         if limit:
#             query_prefix += ''' LIMIT %s '''
#             query_params.append(int(limit))
#         return query_prefix, query_params
#
#     if sort == 'tree':
#         query_prefix += u''' ORDER BY SUBSTRING_INDEX(hierarchy_id, '/', 1) ''' + order + u''' , hierarchy_id ASC '''
#         if limit:
#             query_prefix += ''' LIMIT %s '''
#             query_params.append(int(limit))
#         return query_prefix, query_params
#
#     if sort == 'parent_tree':
#         query_postfix = u''' ORDER BY SUBSTRING_INDEX(hierarchy_id, '/', 1) ''' + order + u''' , hierarchy_id ASC '''
#         if limit:
#             if order == 'asc':
#                 operation = '<='
#                 limit = int(limit) + 1
#             else:
#                 operation = '>='
#                 cursor.execute(SELECT_TOP_POST_NUMBER, [thread_id, ])
#                 if cursor.rowcount == 0:
#                     max_posts_number = 0
#                 else:
#                     max_posts_number = cursor.fetchone()[0]
#                 limit = int(max_posts_number) - int(limit) + 1
#                 if limit < 1:
#                     limit = 1
#             query_prefix += u''' AND hierarchy_id {} '{}' '''.format(operation, limit) + query_postfix
#             return query_prefix, query_params
#         else:
#             return query_prefix + query_postfix, query_params
#

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
