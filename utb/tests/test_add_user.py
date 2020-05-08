from django.http import HttpResponse, HttpRequest
from django.test.client import RequestFactory
from django.test import TestCase
from unittest.mock import Mock
import json

from utb import utils
from utb.views import add_user
from utb.models import User


class AddUserTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        utils.check_google_token = Mock(return_value=(True, "uid"))

    def test_missing_object(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing object", status=404)
        request = rf.post("add_user",
                          data="",
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({}),
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_name(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": None,
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": "",
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_email(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": "name",
                                                      "email": None}}),
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": "name",
                                                      "email": ""}}),
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_email(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": "name",
                                                      "email": "invalid.email"}}),
                          content_type="application/json")
        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))

        expected = HttpResponse("User added", status=201)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": "name",
                                                      "email": "valid@email.com"}}),
                          content_type="application/json")
        response = add_user.handler(request)

        self.assertEqual(str(response), str(expected))

    def test_valid_user(self):
        rf = RequestFactory()
        expected = HttpResponse("User added", status=201)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"name": "name", "email": "valid@email.com"}}),
                          content_type="application/json")

        response = add_user.handler(request)
        self.assertEqual(str(response), str(expected))
        self.assertTrue(User("uid", "name", "valid@email.com") in User.objects.all())


class AddUserTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponse("Error message", status=403)
        response = add_user.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))
