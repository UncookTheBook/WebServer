from django.db import models


class User(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=30)
    email = models.CharField(max_length=30, unique=True)
    n_reports = models.IntegerField(default=0)
    multiplier = models.FloatField(default=1.00)

    def as_dict(self):
        return {"name": self.name, "surname": self.surname, "email": self.email, "n_reports": self.n_reports}

    def score(self):
        return self.n_reports * self.multiplier

class Friendship(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friend", on_delete=models.CASCADE)


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
    REPORT_VALUES = (
        ("L", "Legit"),
        ("F", "Fake"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    report_value = models.CharField(max_length=1, choices=REPORT_VALUES, default="L")
