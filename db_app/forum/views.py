import json
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from db_app.helper import codes
from db_app.helper.helpers import error_json_response, ok_json_response, get_profile_by_email
from django.db import connection, DatabaseError, IntegrityError
from django.http import JsonResponse
from db_app.queries.forum import INSERT_FORUM, SELECT_FORUM_PROFILE_BY_SLUG
from db_app.queries.profile import SELECT_PROFILE_BY_EMAIL


@csrf_exempt
def create(request):
    try:
        json_args = json.loads(request.body)
    except ValueError as value_error:
        return error_json_response(codes.INVALID_QUERY, value_error)
    try:
        name = json_args["name"]
        short_name = json_args["short_name"]
        user = json_args["user"]
    except KeyError as key_error:
        return error_json_response(codes.INCORRECT_QUERY, key_error)

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
    if request.method != 'GET':
        return JsonResponse({'code': codes.INVALID_QUERY, 'response': 'request method should be GET'})
    forum_slug = request.GET.get('forum')
    if not forum_slug:
        return JsonResponse({'code': codes.INVALID_QUERY, 'response': 'forum name not found'})
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_FORUM_PROFILE_BY_SLUG, [forum_slug, ])
        if not cursor.rowcount:
            cursor.close()
            return JsonResponse({'code': codes.NOT_FOUND, 'response': 'forum does not exist'})
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
    forum = cursor.fetchone()
    response = {'id': forum[0],
                'name': forum[1],
                'short_name': forum[2]}
    # optional
    related = request.GET.get('related')
    if related:
        if related != 'user':
            cursor.close()
            return JsonResponse({'code': codes.INCORRECT_QUERY,
                                 'response': 'incorrect related parameter: {}'.format(related)})
        profile_email = forum[3]
        try:
            profile = get_profile_by_email(cursor, profile_email)
        except DatabaseError as db_error:
            cursor.close()
            return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
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
