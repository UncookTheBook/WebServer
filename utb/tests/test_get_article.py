from django.http import HttpResponse, JsonResponse
from django.test import TestCase
from django.test.client import RequestFactory
from hashlib import sha256

from utb.views import get_article
from utb.models import Website, Article


class GetUserTest(TestCase):

    def test_missing_article(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing article", status=404)
        link = "missing"
        request = rf.get("get_article/" + link)
        response = get_article(request, link)
        self.assertEqual(str(response), str(expected))

    def test_article(self):
        rf = RequestFactory()
        website = Website(id=sha256("website".encode("utf-8")).hexdigest(), name="website")
        website.save()
        article = Article(id=sha256("link".encode("utf-8")).hexdigest(), link="link", name="name", website_id=website)
        article.save()
        expected = JsonResponse(article.as_dict(), status=200)
        link = "link"
        request = rf.get("get_article/" + link)
        response = get_article(request, link)
        self.assertEqual(str(response), str(expected))