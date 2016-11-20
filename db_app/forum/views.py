import json

from db_app.queries.post import SELECT_ALL_POSTS_BY_FORUM_UNSPECIFIED
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from db_app.helper import codes
from db_app.helper.helpers import error_json_response, ok_json_response, get_profile_by_email
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
    pass


def list_threads(request):
    pass


def list_users(request):
    pass
