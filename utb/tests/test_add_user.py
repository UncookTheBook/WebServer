from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest, HttpResponseForbidden
from django.test import TestCase
from unittest.mock import Mock

from utb import utils
from utb.views import add_user
from utb.models import User


class AddUserTestCreation(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        utils.check_google_token = Mock(return_value=(True, None))

    def test_null_or_empty_uid(self):
        uid = None
        name = "name"
        surname = "surname"
        email = "email@email.com"
        expected = HttpResponseBadRequest("Invalid arguments")

        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

        uid = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_name(self):
        uid = "uid"
        name = None
        surname = "surname"
        email = "email@email.com"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

        name = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_surname(self):
        uid = "uid"
        name = "name"
        surname = None
        email = "email@email.com"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

        surname = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

    def test_null_or_empty_email(self):
        uid = "uid"
        name = "name"
        surname = "surname"
        email = None
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

        email = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

    def test_invalid_email(self):
        uid = "uid"
        name = "name"
        surname = "surname"
        email = "email"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

        email = "valid@email.com"
        expected = HttpResponse(status=200)
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))

    def test_valid_user(self):
        uid = "uid"
        name = "name"
        surname = "surname"
        email = "valid@email.com"
        expected = HttpResponse(status=200)
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(str(response), str(expected))
        self.assertTrue(User(uid, name, surname, email) in User.objects.all())


class AddUserTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponseForbidden("Error message")
        response = add_user(HttpRequest(), "uid", "name", "surname", "valid@email.com")
        self.assertEqual(str(response), str(expected))
