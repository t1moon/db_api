import time
from django.http import JsonResponse
from json import loads
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import connection, DatabaseError, IntegrityError

from db_app.helper.helpers import get_profile_by_email
from db_app.queries.profile import INSERT_PROFILE, SELECT_PROFILE_BY_EMAIL
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
        is_anonymous = False    # default

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
    pass


def list_followers(request):
    pass


def list_followings(request):
    pass


def list_posts(request):
    pass


def unfollow(request):
    pass


def update_profile(request):
    pass
