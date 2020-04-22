from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from .models import User
from . import utils


def add_user(request, uid, name, surname, email):
    """
    Adds a user to the database
    :param request: the HTTP request
    :param uid: user id
    :param name: user name
    :param surname: user surname
    :param email: user email
    :return: HttpResponseBadRequest if the parameters are invalid
    """
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponseForbidden(error_msg)
    if not uid or not name or not surname or not utils.check_email(email):
        return HttpResponseBadRequest("Invalid arguments")
    user = User(uid, name, surname, email)
    user.save()
    return HttpResponse(status=200)
