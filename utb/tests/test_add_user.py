from django.http import HttpResponse, HttpRequest
from django.test.client import RequestFactory
from django.test import TestCase
from unittest.mock import Mock
import json

from utb import utils
from utb.views import add_user
from utb.models import User


class AddUserTestCreation(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        utils.check_google_token = Mock(return_value=(True, None))

    def test_missing_object(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing object", status=404)
        request = rf.post("add_user",
                          data="",
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_uid(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": None, "name": "name", "surname": "surname",
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "", "name": "name", "surname": "surname",
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_name(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": None, "surname": "surname",
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "", "surname": "surname",
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_surname(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "name", "surname": None,
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "name", "surname": "",
                                                      "email": "email@email.com"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_email(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "name", "surname": "surname",
                                                      "email": None}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "name", "surname": "surname",
                                                      "email": ""}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_email(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid arguments", status=400)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "name", "surname": "surname",
                                                      "email": "invalid.email"}}),
                          content_type="application/json")
        response = add_user(request)
        self.assertEqual(str(response), str(expected))

        expected = HttpResponse("User added", status=201)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": "uid", "name": "name", "surname": "surname",
                                                      "email": "valid@email.com"}}),
                          content_type="application/json")
        response = add_user(request)

        self.assertEqual(str(response), str(expected))

    def test_valid_user(self):
        rf = RequestFactory()
        uid = "uid"
        name = "name"
        surname = "surname"
        email = "valid@email.com"
        expected = HttpResponse("User added", status=201)
        request = rf.post("add_user",
                          data=json.dumps({"object": {"uid": uid, "name": name, "surname": surname,
                                                      "email": email}}),
                          content_type="application/json")

        response = add_user(request)
        self.assertEqual(str(response), str(expected))
        self.assertTrue(User(uid, name, surname, email) in User.objects.all())


class AddUserTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponse("Error message", status=403)
        response = add_user(HttpRequest())
        self.assertEqual(str(response), str(expected))
