from django.http import HttpResponse, HttpResponseBadRequest
from utb.models import User
from utb.utils import check_email


def add_user(request, id, name, surname, email):
    """
    Adds a user to the database
    :param request: the HTTP request
    :param id: user id
    :param name: user name
    :param surname: user surname
    :param email: user email
    :return: HttpResponseBadRequest if the parameters are invalid
    """
    if id is None or name is None or surname is None or not check_email(email):
        return HttpResponseBadRequest('Invalid arguments')
    user = User(id, name, surname, email)
    user.save()
    return HttpResponse(status=200)
