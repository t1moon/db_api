from django.http import JsonResponse

from db_app.queries.profile import SELECT_PROFILE_DATA_BY_EMAIL, SELECT_FOLLOWERS_BY_EMAIL, SELECT_FOLLOWINGS_BY_EMAIL, \
    SELECT_SUBSCRIPTIONS_BY_EMAIL


def error_json_response(code, response):
    return JsonResponse({'code': code, 'response': unicode(response)})


def ok_json_response(code, response):
    return JsonResponse({'code': code, 'response': response})


def get_profile_by_email(cursor, user_email):
    cursor.execute(SELECT_PROFILE_DATA_BY_EMAIL, [user_email, ])
    profile = cursor.fetchone()
    result_profile = {
                    "about": profile[0],
                    "email": profile[1],
                    "followers": [],
                    "following": [],
                    "id": profile[2],
                    "isAnonymous": profile[3],
                    "name": profile[4],
                    "subscriptions": [],
                    "username": profile[5]
                    }
    cursor.execute(SELECT_FOLLOWERS_BY_EMAIL, [user_email, ])
    if cursor.rowcount:
        result_profile["followers"].extend([follower[0] for follower in cursor.fetchall()])
    cursor.execute(SELECT_FOLLOWINGS_BY_EMAIL, [user_email, ])
    if cursor.rowcount:
        result_profile["following"].extend([following[0] for following in cursor.fetchall()])
    cursor.execute(SELECT_SUBSCRIPTIONS_BY_EMAIL, [user_email, ])
    if cursor.rowcount:
        result_profile["subscriptions"].extend([subscription[0] for subscription in cursor.fetchall()])
    return result_profile



