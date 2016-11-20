from django.http import JsonResponse
from json import loads
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import connection, DatabaseError, IntegrityError

from db_app.queries.profile import INSERT_PROFILE
from db_app.helper import codes
# Create your views here.


@csrf_exempt
@require_POST
def create(request):
    try:
        params = loads(request.body)
    except ValueError as value_error:
        return JsonResponse({'code': codes.INVALID_QUERY, 'response': str(value_error)})
    try:
        email = params['email']
    except KeyError as key_error:
        return JsonResponse({'code': codes.INCORRECT_QUERY, 'response': 'Not found: {}'.format(str(key_error))})
    username = params['username']
    about = params['about']
    name = params['name']
    try:
        is_anonymous = params['isAnonymous']
    except KeyError:
        is_anonymous = False
    cursor = connection.cursor()
    try:
        cursor.execute(INSERT_PROFILE, [username, about, name, email, is_anonymous])
        user_id = cursor.lastrowid
    except IntegrityError:
        cursor.close()
        return JsonResponse({'code': codes.ALREADY_EXIST, 'response': 'User already exists'})
    except DatabaseError as db_error:
        cursor.close()
        return JsonResponse({'code': codes.UNKNOWN, 'response': str(db_error)})
    user = {"about": about,
            "email": email,
            "id": user_id,
            "isAnonymous": False,
            "name": name,
            "username": username
            }
    cursor.close()
    return JsonResponse({'code': codes.OK, 'response': user})

def details(request):
    pass


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
