from django.http import HttpResponse, HttpRequest
from django.test.client import RequestFactory
from django.test import TestCase
from unittest.mock import Mock
import json

from utb import utils
from utb.views import submit_report
from utb.models import User, Article, Website, Report


class SubmitReportTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        User(id="uid", name="name", email="email@email.com").save()
        utils.check_google_token = Mock(return_value=(True, "uid"))

    def test_missing_object(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing object", status=404)
        request = rf.post("submit_report",
                          data="",
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("submit_report",
                          data=json.dumps({}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_report(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid report value", status=400)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": None}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

        expected = HttpResponse("Invalid report value", status=400)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": None}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

        expected = HttpResponse("Invalid report value", status=400)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "G"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_article(self):
        rf = RequestFactory()
        user = User(id="uid", name="name", email="valid@email.com")
        user.save()

        expected = HttpResponse("Article not found", status=404)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": None,
                                                      "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

        expected = HttpResponse("Article not found", status=404)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "not_found", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_submit_report(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com")
        user.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name")
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website)
        article.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_submit_same_report_twice(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com")
        user.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name")
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website)
        article.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEqual(Report.objects.get(user=user, article=article).value, Report.Values.L.name)
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.L)

        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "F"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEqual(Report.objects.get(user=user, article=article).value, Report.Values.F.name)
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.F)

        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEqual(Report.objects.get(user=user, article=article).value, Report.Values.L.name)
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.L)

    def test_submit_report_change_status_legit_to_undefined(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com", weight=10)
        user.save()
        user2 = User(id="uid2", name="name2", email="valid2@email.com", weight=10)
        user2.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name", legit_articles=1)
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website, legit_reports=10.0, fake_reports=0.0)
        article.save()

        report1 = Report(user=user2, article=article, value=Report.Values.L.name)
        report1.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "F"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.U)
        self.assertEquals(Website.objects.get(id=website_id).legit_percentage(), 1.00)

    def test_submit_report_change_status_undefined_to_fake(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com", weight=10)
        user.save()
        user2 = User(id="uid2", name="name2", email="valid2@email.com", weight=10)
        user2.save()
        user3 = User(id="uid3", name="name3", email="valid3@email.com", weight=10)
        user3.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name")
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website, legit_reports=10.0, fake_reports=10.0)
        article.save()

        report1 = Report(user=user2, article=article, value=Report.Values.F.name)
        report1.save()
        report2 = Report(user=user3, article=article, value=Report.Values.L.name)
        report2.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "F"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.F)
        self.assertEquals(Website.objects.get(id=website_id).legit_percentage(), 0.00)

    def test_submit_report_change_status_fake_to_undefined(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com", weight=10)
        user.save()
        user2 = User(id="uid2", name="name2", email="valid2@email.com", weight=10)
        user2.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name", fake_articles=1)
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website, legit_reports=0.0, fake_reports=10.0)
        article.save()

        report1 = Report(user=user2, article=article, value=Report.Values.F.name)
        report1.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.U)
        self.assertEquals(Website.objects.get(id=website_id).legit_percentage(), 1.00)

    def test_submit_report_change_status_undefined_to_legit(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com", weight=10)
        user.save()
        user2 = User(id="uid2", name="name2", email="valid2@email.com", weight=10)
        user2.save()
        user3 = User(id="uid3", name="name3", email="valid3@email.com", weight=10)
        user3.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name")
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website, legit_reports=10.0, fake_reports=10.0)
        article.save()

        report1 = Report(user=user2, article=article, value=Report.Values.F.name)
        report1.save()
        report2 = Report(user=user3, article=article, value=Report.Values.L.name)
        report2.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.L)
        self.assertEquals(Website.objects.get(id=website_id).legit_percentage(), 1.00)

    def test_submit_report_change_status_fake_to_legit(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com", weight=50)
        user.save()
        user2 = User(id="uid2", name="name2", email="valid2@email.com", weight=10)
        user2.save()
        user3 = User(id="uid3", name="name3", email="valid3@email.com", weight=30)
        user3.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name")
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website, legit_reports=10.0, fake_reports=30.0)
        article.save()

        report1 = Report(user=user2, article=article, value=Report.Values.L.name)
        report1.save()
        report2 = Report(user=user3, article=article, value=Report.Values.F.name)
        report2.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "L"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.L)
        self.assertEquals(Website.objects.get(id=website_id).legit_percentage(), 1.00)

    def test_submit_report_change_status_legit_to_fake(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="valid@email.com", weight=50)
        user.save()
        user2 = User(id="uid2", name="name2", email="valid2@email.com", weight=10)
        user2.save()
        user3 = User(id="uid3", name="name3", email="valid3@email.com", weight=30)
        user3.save()

        website_id = utils.hash_digest("website_name")
        website = Website(id=website_id, name="website_name")
        website.save()

        article_id = utils.hash_digest("article_url")
        article = Article(id=article_id, url="article_url", website=website, legit_reports=30.0, fake_reports=10.0)
        article.save()

        report1 = Report(user=user2, article=article, value=Report.Values.F.name)
        report1.save()
        report2 = Report(user=user3, article=article, value=Report.Values.L.name)
        report2.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("submit_report",
                          data=json.dumps({"object": {"url": "article_url", "report": "F"}}),
                          content_type="application/json")
        response = submit_report.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(Article.objects.get(id=article_id).get_status(), Article.Status.F)
        self.assertEquals(Website.objects.get(id=website_id).legit_percentage(), 0.00)


class SubmitReportTestInvalidUser(TestCase):
    def test_invalid_user(self):
        expected = HttpResponse("Missing user", status=404)
        utils.check_google_token = Mock(return_value=(True, "uid"))
        response = submit_report.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))


class SubmitReportTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponse("Error message", status=403)
        response = submit_report.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))
