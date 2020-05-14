from django.http import HttpResponse
import logging as log

from utb import utils
from utb.models import User

LOGGING_TAG = "AddUser: "
log.basicConfig(level=log.INFO)


def handler(request):
    """
    Adds a user to the database
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                HttpResponse 400 if the arguments of the object are invalid
                HttpResponse 201 if the user has been created
                HttpResponse 200 if the user was already present
    """
    is_token_valid, message = utils.check_google_token(request)
    if not is_token_valid:
        log.error(LOGGING_TAG + message)
        return HttpResponse(message, status=403)
    user_id = message

    user = utils.get_user_by_id(user_id)
    if user:
        log.info(LOGGING_TAG + "User already present")
        return HttpResponse("User already present", status=200)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        log.error(LOGGING_TAG + object_json["error"])
        return HttpResponse(object_json["error"], status=404)

    name, email = object_json["name"], object_json[
        "email"]
    if not name or not utils.check_email(email):
        log.error(LOGGING_TAG + "Invalid arguments")
        return HttpResponse("Invalid arguments", status=400)

    user = User(id=user_id,
                name=name,
                email=email)
    user.save()
    log.info(LOGGING_TAG + "User " + user.email + " created")
    return HttpResponse("User added", status=201)
