from django.http import HttpResponse
import logging as log

from utb import utils
from utb.models import User, Friendship

LOGGING_TAG = "AddFriend: "


def handler(request):
    """
    Creates a friend relationship between two users in the database
    :param request: the request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                HttpResponse 406 if the user and the friend are the same
                HttpResponse 201 if the friendship was created
    """
    is_token_valid, message = utils.check_google_token(request)
    if not is_token_valid:
        log.error(LOGGING_TAG + "Invalid Token")
        return HttpResponse(message, status=403)
    user_id = message

    user = utils.get_user_by_id(user_id)
    if not user:
        log.error(LOGGING_TAG + "Missing user")
        return HttpResponse("Missing user", status=404)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        log.error(LOGGING_TAG + object_json["error"])
        return HttpResponse(object_json["error"], status=404)

    friend_email = object_json["friend_email"]

    qs = User.objects.filter(email=friend_email)
    if len(qs) == 0:
        log.error(LOGGING_TAG + "Friend not found")
        return HttpResponse("Friend not found", status=404)

    friend = qs[0]
    if user == friend:
        log.error(LOGGING_TAG + "User and Friend must not be the same user")
        return HttpResponse("User and friend must not be the same user", status=406)

    friendship = Friendship(user=user, friend=friend)
    friendship.save()

    return HttpResponse("Created", status=201)
