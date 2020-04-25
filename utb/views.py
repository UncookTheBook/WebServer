from django.http import HttpResponse, JsonResponse
from hashlib import sha256

from .models import User, Article
from . import utils



def add_user(request):
    """
    Adds a user to the database
    :param request: the HTTP request
    :return: HttpResponseBadRequest if the parameters are invalid
    """
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(error_msg, status=403)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    uid, name, surname, email = object_json["uid"], object_json["name"], object_json["surname"], object_json["email"]
    if not uid or not name or not surname or not utils.check_email(email):
        return HttpResponse("Invalid arguments", status=400)

    user = User(uid, name, surname, email)
    user.save()
    return HttpResponse("User added", status=201)


def get_article(request, link):
    """

    :param request:
    :param link:
    :return:
    """
    aid = sha256(link.encode("utf-8")).hexdigest()
    qs = Article.objects.filter(id=aid)
    if len(qs) == 0:
        return HttpResponse("Article not found", status=404)
    article = qs[0]
    return JsonResponse(article.as_dict(), status=200)
