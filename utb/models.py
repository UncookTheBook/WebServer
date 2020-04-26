from django.db import models


class User(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    email = models.CharField(max_length=30, unique=True)
    n_reports = models.IntegerField(default=0)

    def as_dict(self):
        return {"name": self.name, "surname": self.surname, "email": self.email, "n_reports": self.n_reports}


class Website(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # hash of the name
    name = models.CharField(max_length=100, unique=True)

    def as_dict(self):
        return {"name": self.name}


class Article(models.Model):
    REPORT_VALUES = (
        ("L", "Legit"),
        ("F", "Fake"),
    )
    id = models.CharField(max_length=64, primary_key=True)  # hash of the url
    url = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=300)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    positive_reports = models.IntegerField(default=0)
    negative_reports = models.IntegerField(default=0)
    report_value = models.CharField(max_length=1, choices=REPORT_VALUES, default="L")

    def as_dict(self):
        return {"url": self.url, "name": self.name,
                "positive_reports": self.positive_reports, "negative_reports": self.negative_reports}


class Report(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)
