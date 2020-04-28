from django.http import HttpResponse, JsonResponse

from .models import User, Article, Website, Report
from . import utils


def add_user(request):
    """
    Adds a user to the database
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                HttpResponse 400 if the arguments of the object are invalid
                HttpResponse 201 if the user has been created
    """
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(error_msg, status=403)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    user_id, name, surname, email = object_json["uid"], object_json["name"], object_json["surname"], object_json["email"]
    if not user_id or not name or not surname or not utils.check_email(email):
        return HttpResponse("Invalid arguments", status=400)

    user = User(id=user_id,
                name=name,
                surname=surname,
                email=email)
    user.save()
    return HttpResponse("User added", status=201)


def get_article(request):
    """
    Returns the article with the input url
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                HttpResponse 400 if the arguments of the object are invalid
                JsonResponse 200 with body (article, website) as JSON if the user has been created
    """
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(error_msg, status=403)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    url, website_name = object_json["url"], object_json["website_name"]
    if not url or not website_name:
        return HttpResponse("Invalid arguments", status=400)

    article_id = utils.hash_digest(url)
    qs = Article.objects.filter(id=article_id)
    if len(qs) == 0:
        article, website = add_article(article_id, url, website_name)
    else:
        article = qs[0]
        # here I use get because I'm sure that the website exists
        website = Website.objects.get(id=article.website.id)

    return JsonResponse(
        {
            "article": article.as_dict(),
            "website": website.as_dict()
        },
        status=200
    )


def submit_report(request):
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(error_msg, status=403)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    user_id, article_url, report = object_json["uid"], object_json["url"], object_json["report"]
    qs = User.objects.filter(id=user_id)
    if len(qs) == 0:
        return HttpResponse("User not found", status=404)
    user = qs[0]

    qs = Article.objects.filter(id=utils.hash_digest(article_url))
    if len(qs) == 0:
        return HttpResponse("Article not found", status=404)
    article = qs[0]

    report = Report(user=user,
                    article=article,
                    report_value=report)
    report.save()
    if report == "L":
        article.positive_reports += 1 * user.multiplier
    else:
        article.positive_reports += 1 * user.multiplier
    user.n_reports += 1
    article.save()
    user.save()
    

def add_article(article_id, url, website_name):
    """
    Adds an article to the database
    :param article_id: the article id
    :param url: the article url
    :param website_name: the article's website name
    :return: the tuple (Article, Website)
    """
    url = url
    article_name = utils.parse_article_name_from_url(url)
    positive_reports = 0
    negative_reports = 0

    website_id = utils.hash_digest(website_name)
    qs = Website.objects.filter(id=website_id)
    website = add_website(website_id, website_name) if len(qs) == 0 else qs[0]

    article = Article(id=article_id,
                      url=url,
                      name=article_name,
                      website=website,
                      positive_reports=positive_reports,
                      negative_reports=negative_reports)
    article.save()
    return article, website


def add_website(website_id, website_name):
    """
    Adds a website to the database and returns it
    :param website_id: the website id
    :param website_name: the website name
    :return:
    """
    website = Website(id=website_id,
                      name=website_name)
    website.save()
    return website
