# coding: utf8
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from db_app.helper import codes
from db_app.queries.common import CLEAR_TABLE, RESET_AUTO_INCREMENT, RESET_FK_CHECKS, SELECT_TABLE_STATUSES

# Create your views here.


@csrf_exempt
def clear(request):
    cursor = connection.cursor()
    cursor.execute(RESET_FK_CHECKS.format(0))
    for table in ['Followers', 'Subscriptions',
                  'Posts', 'Threads', 'Forums', 'Users', 'Threads_Head_Posts', 'Users_Forum']:
        cursor.execute(CLEAR_TABLE.format(table))
        cursor.execute(RESET_AUTO_INCREMENT.format(table))
    cursor.execute(RESET_FK_CHECKS.format(1))
    cursor.close()
    return JsonResponse({"code": codes.OK, "response": "OK"})


def status(request):
    db_name = 'db_api'
    statuses = {}
    cursor = connection.cursor()
    for entity in ['user', 'thread', 'forum', 'post']:
        cursor.execute(SELECT_TABLE_STATUSES.format(entity.capitalize()))
        data = cursor.fetchone()
        statuses[entity] = data[0]

    cursor.close()
    return JsonResponse({"code": codes.OK, "response": statuses})
