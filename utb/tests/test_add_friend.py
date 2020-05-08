import json
from unittest.mock import Mock

from django.http import HttpResponse, HttpRequest
from django.test import TestCase, RequestFactory

from utb import utils
from utb.models import User, Friendship
from utb.views import add_friend


class AddFriendTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        User(id="uid", name="name", email="email@email.com").save()
        utils.check_google_token = Mock(return_value=(True, "uid"))

    def test_missing_object(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing object", status=404)
        request = rf.post("add_friend",
                          data="",
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_friend",
                          data=json.dumps({}),
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_friend(self):
        rf = RequestFactory()

        expected = HttpResponse("Friend not found", status=404)
        request = rf.post("add_friend",
                          data=json.dumps({"object": {"friend_email": None}}),
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_friend",
                          data=json.dumps({"object": {"friend_email": ""}}),
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("add_friend",
                          data=json.dumps({"object": {"friend_email": "missing"}}),
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_same_user(self):
        rf = RequestFactory()

        expected = HttpResponse("User and friend must not be the same user", status=406)
        request = rf.post("add_friend",
                          data=json.dumps({"object": {"friend_email": "email@email.com"}}),
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_friendship(self):
        rf = RequestFactory()

        user1 = User.objects.get(id="uid")
        user2 = User(id="uid2", name="name2", email="email2@email.com")
        user2.save()

        expected = HttpResponse("Created", status=201)
        request = rf.post("add_friend",
                          data=json.dumps({"object": {"friend_email": "email2@email.com"}}),
                          content_type="application/json")
        response = add_friend.handler(request)
        self.assertEqual(str(response), str(expected))
        friendship = Friendship.objects.get(user=user1, friend=user2)
        self.assertTrue(friendship.user == user1 and friendship.friend == user2)


class AddFriendTestInvalidUser(TestCase):
    def test_invalid_user(self):
        expected = HttpResponse("Missing user", status=404)
        utils.check_google_token = Mock(return_value=(True, "uid"))
        response = add_friend.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))


class AddFriendTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponse("Error message", status=403)
        response = add_friend.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))
