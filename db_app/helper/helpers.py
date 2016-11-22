from django.http import JsonResponse

from db_app.helper import codes
from db_app.queries.forum import SELECT_FORUM_DATA_BY_SLUG
from db_app.queries.post import SELECT_POST_DATA_BY_ID
from db_app.queries.profile import SELECT_PROFILE_DATA_BY_EMAIL, SELECT_FOLLOWERS_BY_EMAIL, SELECT_FOLLOWINGS_BY_EMAIL, \
    SELECT_SUBSCRIPTIONS_BY_EMAIL
from db_app.queries.thread import SELECT_THREAD_DATA_BY_ID


def error_json_response(code, response):
    return JsonResponse({'code': code, 'response': unicode(response)})


def ok_json_response(code, response):
    return JsonResponse({'code': code, 'response': response})


def get_forum_by_slug(cursor, slug):
    cursor.execute(SELECT_FORUM_DATA_BY_SLUG, [slug, ])
    forum = cursor.fetchone()
    return {"id": forum[0],
            "name": forum[1],
            "short_name": forum[2],
            "user": forum[3]
           }, \
           {
            "user": forum[3]
           }


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


def get_post_by_id(cursor, post_id):
    cursor.execute(SELECT_POST_DATA_BY_ID, [post_id, ])
    post = cursor.fetchone()
    return {
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
        }, \
        {
         "forum": post[2],
         "thread": post[13],
         "user": post[14]
         }


def get_thread_by_id(cursor, thread_id):
    cursor.execute(SELECT_THREAD_DATA_BY_ID, [thread_id, ])
    thread = cursor.fetchone()
    return {"date": thread[0].strftime("%Y-%m-%d %H:%M:%S"),
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
            }, \
            {
             "forum": thread[2],
             "user": thread[12]
            }



