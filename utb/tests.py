from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.test import TestCase
from .views import add_user


class ViewsTestCase(TestCase):
    def test_null_or_empty_uid(self):
        uid = None
        name = "name"
        surname = "surname"
        email = "email@email.com"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)
        uid = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)

    def test_null_or_empty_name(self):
        uid = "uid"
        name = None
        surname = "surname"
        email = "email@email.com"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)
        name = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)

    def test_null_or_empty_surname(self):
        uid = "uid"
        name = "name"
        surname = None
        email = "email@email.com"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)
        surname = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)

    def test_null_or_empty_email(self):
        uid = "uid"
        name = "name"
        surname = "surname"
        email = None
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)
        email = ""
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)

    def test_invalid_email(self):
        uid = "uid"
        name = "name"
        surname = "surname"
        email = "email"
        expected = HttpResponseBadRequest("Invalid arguments")
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)
        email = "valid@email.com"
        expected = HttpResponse(status=200)
        response = add_user(HttpRequest(), uid, name, surname, email)
        self.assertEqual(response.content, expected.content)

