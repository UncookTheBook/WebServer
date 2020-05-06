import json
from unittest.mock import Mock

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.test import TestCase, RequestFactory

from utb import utils
from utb.models import User, Friendship
from utb.views import get_leaderboard


class GetLeaderboardTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cls_atomics = cls._enter_atomics()
        # mocks the google_token check
        utils.check_google_token = Mock(return_value=(True, None))

    def test_missing_object(self):
        rf = RequestFactory()

        expected = HttpResponse("Missing object", status=404)
        request = rf.post("get_leaderboard",
                          data="",
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_leaderboard",
                          data=json.dumps({}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_type(self):
        rf = RequestFactory()

        user = User(id="uid", name="name", email="email@email.com")
        user.save()

        expected = HttpResponse("Wrong leaderboard type", status=400)
        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": None, "uid": "uid"}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "", "uid": "uid"}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "INVALID", "uid": "uid"}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_invalid_uid(self):
        rf = RequestFactory()

        expected = HttpResponse("Invalid user", status=404)
        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "GLOBAL", "uid": None}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "GLOBAL", "uid": ""}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "GLOBAL", "uid": "not_present"}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_leaderboard(self):
        rf = RequestFactory()

        expected = JsonResponse({"leaderboard": [{"name": "user2", "score": 12}, {"name": "user1", "score": 8}]}, status=200)

        user1 = User(id="uid1", name="user1", email="user1@email.com", n_reports=4, multiplier=2.0)
        user1.save()
        user2 = User(id="uid2", name="user2", email="user2@email.com", n_reports=4, multiplier=2.3)
        user2.save()

        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "GLOBAL", "uid": "uid1"}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))

    def test_friends_leaderboard(self):
        rf = RequestFactory()

        expected = JsonResponse({"leaderboard": [{"name": "user2", "score": 12},
                                                 {"name": "user1", "score": 8},
                                                 {"name": "user3", "score": 0}]}, status=200)
        user1 = User(id="uid1", name="user1", email="user1@email.com", n_reports=4, multiplier=2.0)
        user1.save()
        user2 = User(id="uid2", name="user2", email="user2@email.com", n_reports=4, multiplier=2.3)
        user2.save()
        user3 = User(id="uid3", name="user3", email="user3@email.com", n_reports=0, multiplier=1.0)
        user3.save()
        friendship1 = Friendship(user=user1, friend=user2)
        friendship1.save()
        friendship2 = Friendship(user=user1, friend=user3)
        friendship2.save()

        request = rf.post("get_leaderboard",
                          data=json.dumps({"object": {"type": "FRIENDS", "uid": "uid1"}}),
                          content_type="application/json")
        response = get_leaderboard.handler(request)
        self.assertEqual(str(response), str(expected))


class GetLeaderboardTestGoogleSignInToken(TestCase):
    def test_invalid_token(self):
        utils.check_google_token = Mock(return_value=(False, "Error message"))
        expected = HttpResponse("Error message", status=403)
        response = get_leaderboard.handler(HttpRequest())
        self.assertEqual(str(response), str(expected))
