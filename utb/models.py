from django.db import models
import enum


class User(models.Model):
    id = models.CharField(max_length=21, primary_key=True)
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=30, unique=True)
    n_reports = models.IntegerField(default=0)
    weight = models.FloatField(default=1.00)

    def as_dict(self):
        return {"name": self.name, "email": self.email, "n_reports": self.n_reports}

    def score(self):
        return self.n_reports * self.weight


class Friendship(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friend", on_delete=models.CASCADE)


class Website(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # hash of the name
    name = models.CharField(max_length=100, unique=True)
    legit_articles = models.IntegerField(default=0)
    fake_articles = models.IntegerField(default=0)

    def as_dict(self):
        return {"name": self.name, "legit": self.legit_percentage()}

    def legit_percentage(self):
        if self.legit_articles + self.fake_articles == 0:
            return 1.00  # if there are no reports we assume that a website is legit
        percentage = (self.legit_articles * 2) / (self.legit_articles + self.fake_articles)
        return 1.00 if percentage > 1 else percentage


class Article(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # hash of the url
    url = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=300)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    legit_reports = models.FloatField(default=0.00)
    fake_reports = models.FloatField(default=0.00)

    class Status(enum.Enum):
        L = 1
        F = 2
        U = 3

    def as_dict(self):
        return {"url": self.url, "name": self.name,
                "legit_reports": int(self.legit_reports), "fake_reports": int(self.fake_reports)}

    def get_status(self):
        if self.legit_reports + self.fake_reports == 0:
            return self.Status.U
        legit_ratio = self.legit_reports / (self.legit_reports + self.fake_reports)
        if legit_ratio > 0.6:
            return self.Status.L
        elif legit_ratio < 0.4:
            return self.Status.F
        else:
            return self.Status.U


class Report(models.Model):
    class Values(enum.Enum):
        L = 1
        F = 2

    VALUES = (
        (Values.L, "Legit"),
        (Values.F, "Fake")
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    value = models.CharField(max_length=1, choices=VALUES)
