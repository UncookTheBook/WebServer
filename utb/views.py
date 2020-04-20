from django.http import HttpResponse, HttpResponseBadRequest
from .models import User
from .utils import check_email


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
    if not uid or not name or not surname or not check_email(email):
        return HttpResponseBadRequest("Invalid arguments")
    user = User(uid, name, surname, email)
    user.save()
    return HttpResponse(status=200)
