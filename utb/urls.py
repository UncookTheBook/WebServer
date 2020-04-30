from django.urls import path
from utb.views import add_user, get_article, submit_report, get_leaderboard

urlpatterns = [
    path("add_user", add_user.handler, name="add_user"),
    path("get_article", get_article.handler, name="get_article"),
    path("submit_report", submit_report.handler, name="submit_report"),
    path("get_leaderboard", get_leaderboard.handler, name="get_leaderboard")
]
