import time
from django.http import JsonResponse
from json import loads
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import connection, DatabaseError, IntegrityError

from db_app.helper.helpers import get_profile_by_email
from db_app.queries.post import SELECT_ALL_POSTS_BY_USER_EMAIL_UNSPECIFIED
from db_app.queries.profile import INSERT_PROFILE, SELECT_PROFILE_BY_EMAIL, INSERT_FOLLOWER, DELETE_FOLLOWER, \
    SELECT_FOLLOW_RELATIONS, UPDATE_PROFILE, UPDATE_USER_FORUM
from db_app.helper import codes


# Create your views here.


@csrf_exempt
def create(request):
    params = loads(request.body)
    email = params['email']
    username = params['username']
    about = params['about']
    name = params['name']
    # optional
    is_anonymous = params['isAnonymous']
    if is_anonymous:
        pass
    else:
        is_anonymous = False  # default

    cursor = connection.cursor()
    try:
        cursor.execute(INSERT_PROFILE, [username, about, name, email, is_anonymous])
        user_id = cursor.lastrowid
    except IntegrityError:
        cursor.close()
        return JsonResponse({'code': codes.ALREADY_EXIST, 'response': 'User already exists'})
    user = {"about": about,
            "email": email,
            "id": user_id,
            "isAnonymous": is_anonymous,
            "name": name,
            "username": username
            }
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': user})


def details(request):
    email = request.GET.get('user')
    cursor = connection.cursor()

    cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user not found'})
    profile = get_profile_by_email(cursor, email)
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': profile})


def follow(request):
    params = loads(request.body)
    follower = params['follower']
    followee = params['followee']

    cursor = connection.cursor()
    user_emails = []
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [follower, ])
        user_emails.append(follower)
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [followee, ])
        user_emails.append(followee)
    except DatabaseError as db_err:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_err)})

    if len(user_emails) != 2:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'User not found'})
    try:
        cursor.execute(INSERT_FOLLOWER, [user_emails[0], user_emails[1], ])
    except IntegrityError:
        pass
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
    # else:
    #     try:
    #         cursor.execute(DELETE_FOLLOWER, [user_emails[0], user_emails[1], ])
    #     except IntegrityError:
    #         pass
    #     except DatabaseError as db_error:
    #         cursor.close()
    #         return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})

    try:
        profile = get_profile_by_email(cursor, user_emails[0])
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': profile})


def list_followers(request, relation):
    email = request.GET.get('user')
    if email is None:
        return JsonResponse({'code': codes.INVALID_QUERY, 'response': 'email required'})

    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user not found'})
    if relation is 'Followers':
        relationship = 'follower'
        partner_relationship = 'followee'
    else:
        relationship = 'followee'
        partner_relationship = 'follower'
    query = SELECT_FOLLOW_RELATIONS.format(relationship, partner_relationship)
    query_params = [email, ]
    since_id = request.GET.get('id')
    if since_id > 0 and since_id is not None:
        query += ''' AND {} >= %s '''.format(relationship)
        query_params.append(since_id)
    elif since_id == False and since_id is not None:
        cursor.close()
        return JsonResponse({'code': codes.INCORRECT_QUERY, 'response': 'incorrect since_id format'})

    order = request.GET.get('order', 'desc')
    if order.lower() not in ('asc', 'desc'):
        cursor.close()
        return JsonResponse({'code': codes.INCORRECT_QUERY, 'response': 'incorrect order parameter: {}'.format(order)})

    query += ''' ORDER BY Users.name ''' + order

    limit = request.GET.get('limit')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            cursor.close()
            return JsonResponse({'code': codes.INCORRECT_QUERY, 'response': 'limit should be int'})
        query += ''' LIMIT %s'''
        query_params.append(limit)

    try:
        cursor.execute(query, query_params)
    except DatabaseError as db_err:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_err)})

    followers = []
    for user_email in cursor.fetchall():
        try:
            user = get_profile_by_email(cursor, user_email[0])
        except DatabaseError as db_err:
            cursor.close()
            return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_err)})
        followers.append(user)
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': followers})


def list_followings(request):
    pass


def list_posts(request):
    email = request.GET.get('user')

    cursor = connection.cursor()
    cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    if cursor.rowcount == 0:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user not found'})

    query_params = [email, ]
    get_post_list_specified_query = SELECT_ALL_POSTS_BY_USER_EMAIL_UNSPECIFIED
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
    cursor.execute(get_post_list_specified_query, query_params)

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


def unfollow(request):
    try:
        params = loads(request.body)
    except ValueError as value_err:
        return JsonResponse({'code': codes.INVALID_QUERY, 'response': str(value_err)})

    try:
        follower = unicode(params['follower'])
        followee = unicode(params['followee'])
    except KeyError as key_error:
        return JsonResponse({'code': codes.INCORRECT_QUERY, 'response': 'Not found: {}'.format(str(key_error))})

    cursor = connection.cursor()
    user_emails = []
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [follower, ])
        user_emails.append(follower)
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [followee, ])
        user_emails.append(followee)
    except DatabaseError as db_err:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_err)})

    if len(user_emails) != 2:
        cursor.close()
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'User not found'})
    try:
        cursor.execute(DELETE_FOLLOWER, [user_emails[0], user_emails[1], ])
    except IntegrityError:
        pass
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})

    try:
        profile = get_profile_by_email(cursor, user_emails[0])
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': profile})


def update_profile(request):
    try:
        params = loads(request.body)
    except ValueError as value_error:
        return JsonResponse({'code': codes.INVALID_QUERY, 'response': str(value_error)})

    try:
        about = params['about']
        name = params['name']
        email = params['user']
    except KeyError as key_error:
        return JsonResponse({'code': codes.INCORRECT_QUERY, 'response': 'Not found: {}'.format(str(key_error))})
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_PROFILE_BY_EMAIL, [email, ])
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': str(db_error)})
    if cursor.rowcount == 0:
        return JsonResponse({'code': codes.NOT_FOUND, 'response': 'user does not exist'})

    try:
        cursor.execute(UPDATE_PROFILE, [about, name, email])
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': str(db_error)})
    cursor.execute(UPDATE_USER_FORUM, [name, email])

    try:
        profile = get_profile_by_email(cursor, email)
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': unicode(db_error)})
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': profile})