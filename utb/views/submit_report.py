from django.http import HttpResponse

from utb.models import User, Article, Report
from utb import utils


def handler(request):
    # TODO TEMP
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
        article.negative_reports += 1 * user.multiplier
    user.n_reports += 1
    article.save()
    user.save()
