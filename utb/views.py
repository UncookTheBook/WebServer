from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from .models import User
from . import utils


def add_user(request):
    """
    Adds a user to the database
    :param request: the HTTP request
    :return: HttpResponseBadRequest if the parameters are invalid
    """
    # TODO testing
    print(request.body)
    #
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        print(error_msg)
        return HttpResponse(error_msg, status=403)
    # if not uid or not name or not surname or not utils.check_email(email):
    #     return HttpResponseBadRequest("Invalid arguments")
    # user = User(uid, name, surname, email)
    # user.save()
    return HttpResponse("User created", status=201)
