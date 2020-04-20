from django.db import models


class User(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    email = models.CharField(max_length=30, unique=True)
    n_reports = models.IntegerField(default=0)


class Website(models.Model):
    id = models.CharField(max_length=30, primary_key=True)


class Article(models.Model):
    link = models.CharField(max_length=150, primary_key=True)
    name = models.CharField(max_length=150)
    website_id = models.ForeignKey(Website, on_delete=models.CASCADE)


class Report(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)

