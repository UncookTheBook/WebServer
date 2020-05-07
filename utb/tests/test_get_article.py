from django.http import HttpResponse, JsonResponse, HttpRequest
from django.test import TestCase
from django.test.client import RequestFactory
from unittest.mock import Mock
import json

from utb.views import get_article
from utb.models import Website, Article
from utb import utils


class GetArticleTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        utils.check_google_token = Mock(return_value=(True, None))
        utils.parse_article_name_from_url = Mock(return_value="article_name")

    def test_missing_object(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing object", status=404)
        request = rf.post("get_article",
                          data="",
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_article",
                          data=json.dumps({}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_url(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": None, "website_name": "name"}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": "", "website_name": "name"}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_website_name(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": "url", "website_name": None}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": "url", "website_name": ""}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_get_article(self):
        rf = RequestFactory()

        expected = JsonResponse(
            {"article": {"url": "url", "name": "article_name", "legit_reports": 0, "fake_reports": 0},
             "website": {"name": "website_name"}})
        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": "url", "website_name": "website_name"}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_get_article_already_present(self):
        rf = RequestFactory()

        expected = JsonResponse(
            {"article": {"url": "url", "name": "article_name", "legit_reports": 0, "fake_reports": 0},
             "website": {"name": "website_name"}})
        website = Website(id=utils.hash_digest("website_name"),
                          name="website_name")
        website.save()
        article = Article(id=utils.hash_digest("url"),
                          url="url",
                          name="name",
                          website=website)
        article.save()
        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": "url", "website_name": "website_name"}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(article.as_dict(), json.loads(response.content)["article"])
        self.assertEquals(website.as_dict(), json.loads(response.content)["website"])

    def test_get_article_website_already_present(self):
        rf = RequestFactory()

        expected = JsonResponse(
            {"article": {"url": "url", "name": "article_name", "legit_reports": 0, "fake_reports": 0},
             "website": {"name": "website_name"}})
        expected_article = {"url": "url", "name": "article_name", "legit_reports": 0, "fake_reports": 0}
        website = Website(id=utils.hash_digest("website_name"),
                          name="website_name",
                          legit_articles=3,
                          fake_articles=1)
        website.save()

        request = rf.post("get_article",
                          data=json.dumps({"object": {"url": "url", "website_name": "website_name"}}),
                          content_type="application/json")
        response = get_article.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertEquals(expected_article, json.loads(response.content)["article"])
        self.assertEquals(website.as_dict(), json.loads(response.content)["website"])


class GetArticleTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponse("Error message", status=403)
        response = get_article.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))
