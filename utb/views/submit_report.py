from django.http import HttpResponse

from utb.models import Article, Report
from utb import utils


def handler(request):
    """
    Adds a report to the system
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                HttpResponse 400 if the arguments of the object are invalid
                JsonResponse 201 if the article has been created
    """
    is_token_valid, message = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(message, status=403)
    user_id = message

    user = utils.get_user_by_id(user_id)
    if not user:
        return HttpResponse("Missing user", status=404)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    article_url, report = object_json["url"], object_json["report"]

    if report == "L":
        report_value = Report.Values.L
    elif report == "F":
        report_value = Report.Values.F
    else:
        return HttpResponse("Invalid report value", status=400)

    qs = Article.objects.filter(id=utils.hash_digest(article_url))
    if len(qs) == 0:
        return HttpResponse("Article not found", status=404)
    article = qs[0]

    previous_status = article.get_status()

    qs = Report.objects.filter(user=user, article=article)
    if len(qs) == 0:
        report = Report(user=user,
                        article=article,
                        value=report_value.name)
        user.n_reports += 1
        user.save()
        # in the case the report was not present before, we only have to add the weight of the user to the
        # corresponding value
        if report_value == Report.Values.L:
            article.legit_reports += user.weight
        else:
            article.fake_reports += user.weight
    else:
        report = qs[0]
        old_report_value = report.value
        report.value = report_value.name
        # in case the report was already present, we take its old value and update the numbers of legit
        # and fake reports for the article accordingly
        if old_report_value != report.value:
            if report.value == Report.Values.L.name:
                article.fake_reports -= user.weight
                article.legit_reports += user.weight
            else:
                article.legit_reports -= user.weight
                article.fake_reports += user.weight
    report.save()

    updated_status = article.get_status()
    if previous_status != updated_status:
        change_article_status(report, article, previous_status, updated_status)
    return HttpResponse("Created", status=201)


def change_article_status(last_report, article, previous_status, updated_status):
    """
    Updates the database as the article status changes.
    More specifically, it updates the users weights, the article legit_reports and fake_reports
    and the website legit_articles and fake_articles
    :param last_report: the report that triggered the changes
    :param article: the article
    :param previous_status: the previous status of the article
    :param updated_status: the updated status of the article
    """

    legit_reports = 0.00
    fake_reports = 0.00

    # update the weight of the user that submitted the last_report.
    # It effectively updates only if the updated status of the article is Legit or Fake
    # If it remains undefined, the weight stays the same since the article doesn't have a defined status
    report_user = last_report.user
    if last_report.value == Report.Values.L.name:
        if updated_status == Article.Status.L:
            report_user.weight += utils.MULTIPLIER_DELTA
        legit_reports += report_user.weight
    elif last_report.value == Report.Values.F.name:
        if updated_status == Article.Status.F:
            report_user.weight += utils.MULTIPLIER_DELTA
        fake_reports += report_user.weight
    report_user.save()

    # update users weights (excluding the user that submitted the last report)
    for report in Report.objects.filter(article=article).exclude(user=report_user):
        user = report.user
        # if the status "increases" by one step we have to increase the weight of the users
        # that reported the article as legit and decrease the users that reported the article as fake
        if (previous_status == Article.Status.U and updated_status == Article.Status.L) or (
                previous_status == Article.Status.F and updated_status == Article.Status.U):
            if report.value == Report.Values.L.name:
                user.weight += utils.MULTIPLIER_DELTA
            else:
                user.weight -= utils.MULTIPLIER_DELTA
        # otherwise, we do the contrary
        elif (previous_status == Article.Status.L and updated_status == Article.Status.U) or (
                previous_status == Article.Status.U and updated_status == Article.Status.F):
            if report.value == Report.Values.L.name:
                user.weight -= utils.MULTIPLIER_DELTA
            else:
                user.weight += utils.MULTIPLIER_DELTA
        # if we have that the article goes from fake to legit, we have to increment the weight twice
        elif previous_status == Article.Status.F and updated_status == Article.Status.L:
            if report.value == Report.Values.L.name:
                user.weight += 2 * utils.MULTIPLIER_DELTA
            else:
                user.weight -= 2 * utils.MULTIPLIER_DELTA
        # same for legit to fake
        elif previous_status == Article.Status.L and updated_status == Article.Status.F:
            if report.value == Report.Values.L.name:
                user.weight -= 2 * utils.MULTIPLIER_DELTA
            else:
                user.weight += 2 * utils.MULTIPLIER_DELTA
        if report.value == Report.Values.L.name:
            legit_reports += user.weight
        else:
            fake_reports += user.weight
        user.save()
    # update website
    website = article.website
    if updated_status == Article.Status.L:
        website.legit_articles += 1
        if previous_status == Article.Status.F:
            website.fake_articles -= 1
    elif updated_status == Article.Status.F:
        website.fake_articles += 1
        if previous_status == Article.Status.L:
            website.legit_articles -= 1
    elif updated_status == Article.Status.U:
        if previous_status == Article.Status.L:
            website.legit_articles -= 1
        else:
            website.fake_articles -= 1

    website.save()

    # update article
    article.legit_reports = legit_reports
    article.fake_reports = fake_reports
    article.save()
