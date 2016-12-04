import json

from db_app.queries.post import SELECT_ALL_POSTS_BY_FORUM_UNSPECIFIED
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from db_app.helper import codes
from db_app.helper.helpers import error_json_response, ok_json_response, get_profile_by_email, get_thread_by_id, \
    get_forum_by_slug
from django.db import connection, DatabaseError, IntegrityError
from django.http import JsonResponse
from db_app.queries.forum import INSERT_FORUM, SELECT_FORUM_PROFILE_BY_SLUG, SELECT_FORUM_ID_BY_SLUG
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL


@csrf_exempt
def create(request):
    json_args = json.loads(request.body)
    name = json_args["name"]
    short_name = json_args["short_name"]
    user = json_args["user"]
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [user, ])
    except DatabaseError as db_error:
        cursor.close()
        return error_json_response(codes.UNKNOWN, db_error)
    if cursor.rowcount == 0:
        cursor.close()
        return error_json_response(codes.NOT_FOUND, 'User does not exist')
    try:
        cursor.execute(INSERT_FORUM, [name, short_name, user])  #
        forum_id = cursor.lastrowid
        cursor.close()
        return ok_json_response(codes.OK, {
                                        'id': forum_id,
                                        'name': name,
                                        'short_name': short_name,
                                        'user': user
                                         })
    except IntegrityError:
        cursor.execute(SELECT_FORUM_PROFILE_BY_SLUG, [short_name, ])
        existed_forum = cursor.fetchone()
        cursor.close()
        return JsonResponse({'code': codes.OK, 'response': {
                                        'id': existed_forum[0],
                                        'name': existed_forum[1],
                                        'short_name': existed_forum[2],
                                        'user': existed_forum[3]
                                         }})
    except DatabaseError as db_error:
        cursor.close()
        return error_json_response(codes.UNKNOWN, db_error)


@csrf_exempt
def details(request):
    forum_slug = request.GET.get('forum')
    cursor = connection.cursor()
    cursor.execute(SELECT_FORUM_PROFILE_BY_SLUG, [forum_slug, ])
    forum = cursor.fetchone()
    response = {'id': forum[0],
                'name': forum[1],
                'short_name': forum[2]}
    # optional
    related = request.GET.get('related')
    if related:
        profile_email = forum[3]
        profile = get_profile_by_email(cursor, profile_email)
        response['user'] = profile
    else:
        response['user'] = forum[3]
        cursor.close()
    return JsonResponse({'code': codes.OK, 'response': response})


def list_posts(request):
    short_name = request.GET.get('forum')

    cursor = connection.cursor()
    cursor.execute(SELECT_FORUM_ID_BY_SLUG, [short_name, ])
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'forum not found'})

    query_params = [short_name, ]
    get_post_list_specified_query = SELECT_ALL_POSTS_BY_FORUM_UNSPECIFIED
    since_date = request.GET.get('since')

    if since_date:
        get_post_list_specified_query += ''' AND date >= %s '''
        query_params.append(since_date)

    order = request.GET.get('order', 'desc')
    if order:
        get_post_list_specified_query += ''' ORDER BY date ''' + order

    limit = request.GET.get('limit')
    if limit:
        limit = int(limit)
        get_post_list_specified_query += ''' LIMIT %s'''
        query_params.append(limit)
    print query_params
    cursor.execute(get_post_list_specified_query, query_params)

    posts = []
    related = set(request.GET.getlist('related'))
    related_functions_dict = {'user': get_profile_by_email,
                              'thread': get_thread_by_id,
                              'forum': get_forum_by_slug
                              }
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
        related_ids = {'forum': short_name,
                       'thread': post[13],
                       'user': post[14]
                       }
        for related_ in related:
            if related_ in ['thread', 'forum', 'user']:
                get_related_info_func = related_functions_dict[related_]  # get_forum or get_thread
                # let's place on the last position
                posts[-1][related_], related_ids_ = get_related_info_func(cursor, related_ids[related_])
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': posts})


def list_threads(request):
    pass


def list_users(request):
    pass
