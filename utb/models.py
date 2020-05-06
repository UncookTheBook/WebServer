from django.db import models


class User(models.Model):
    id = models.CharField(max_length=21, primary_key=True)
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=30, unique=True)
    n_reports = models.IntegerField(default=0)
    multiplier = models.FloatField(default=1.00)

    def as_dict(self):
        return {"name": self.name, "email": self.email, "n_reports": self.n_reports}

    def score(self):
        return self.n_reports * self.multiplier


class Friendship(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friend", on_delete=models.CASCADE)


class Website(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # hash of the name
    name = models.CharField(max_length=100, unique=True)
    legit_reports = models.IntegerField(default=0)
    fake_reports = models.IntegerField(default=0)

    def as_dict(self):
        return {"name": self.name, "legit": self.legit_percentage()}

    def legit_percentage(self):
        if self.legit_reports + self.fake_reports == 0:
            return 1.00  # if there are no reports we assume that a website is legit
        percentage = (self.legit_reports * 2) / (self.legit_reports + self.fake_reports)
        return 1.00 if percentage > 1 else percentage


class Article(models.Model):
    ARTICLE_VALUES = (
        ("L", "Legit"),
        ("F", "Fake"),
        ("U", "Undetermined")
    )
    id = models.CharField(max_length=64, primary_key=True)  # hash of the url
    url = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=300)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    legit_reports = models.IntegerField(default=0)
    fake_reports = models.IntegerField(default=0)
    report_value = models.CharField(max_length=1, choices=ARTICLE_VALUES, default="U")

    def as_dict(self):
        return {"url": self.url, "name": self.name,
                "legit_reports": self.legit_reports, "fake_reports": self.fake_reports}


class Report(models.Model):
    REPORT_VALUES = (
        ("L", "Legit"),
        ("F", "Fake"),
    )
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    report_value = models.CharField(max_length=1, choices=REPORT_VALUES)
