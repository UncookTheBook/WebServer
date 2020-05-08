from django.http import HttpResponse

from utb import utils
from utb.models import User


def handler(request):
    """
    Adds a user to the database
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                HttpResponse 400 if the arguments of the object are invalid
                HttpResponse 201 if the user has been created
    """
    is_token_valid, message = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(message, status=403)
    user_id = message

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    name, email = object_json["name"], object_json[
        "email"]
    if not name or not utils.check_email(email):
        return HttpResponse("Invalid arguments", status=400)

    user = User(id=user_id,
                name=name,
                email=email)
    user.save()
    return HttpResponse("User added", status=201)
