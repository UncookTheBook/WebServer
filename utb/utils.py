from google.oauth2 import id_token
from google.auth.transport import requests
import re
import json
import urllib3
from bs4 import BeautifulSoup
from hashlib import sha256

# regex to check the email correctness
from utb.models import User

MULTIPLIER_DELTA = 0.01

MAIL_REGEX = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

CLIENT_ID = "234949874727-7pbe1gebujhcicmo1c0i35o948fe7oqa.apps.googleusercontent.com"


def check_email(email):
    """
    Checks that the input email is a valid email
    :param email: the input email
    :return: True if the email is valid, otherwise false
    """
    return email and re.search(MAIL_REGEX, email)


def check_google_token(request):
    """
    Checks if the authentication token of the user is valid
    See https://developers.google.com/identity/sign-in/android/backend-auth
    :param request: the http request
    :return: True if the token is valid, otherwise False and the error message
    """
    try:
        token = json.loads(request.body)["token"]
        id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return False, "Wrong issuer"

        return True, None
    except (AttributeError, ValueError) as error:
        return False, str(error)


def get_object(request):
    """
    Checks if the request body contains the object
    :param request: the request
    :return: (True, Object as dict) if the body contains the object, otherwise (False, Error as dict)
    """
    if not request.body or "object" not in json.loads(request.body):
        return False, {"error": "Missing object"}
    return True, json.loads(request.body)["object"]


def parse_article_name_from_url(url):
    """
    Parses the article name from the web page and returns it
    :param url: the article's url
    :return: the article's name
    """
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'html.parser')
    article_name = soup.title.string
    article_name = re.compile(" [-|] ").split(article_name)[0]
    return article_name


def hash_digest(string):
    """
    :param string: the input string
    :return: the SHA256 hash of the input string
    """
    return sha256(string.encode("utf-8")).hexdigest() if string is None else None


def user_exists(uid):
    """
    :param uid: the user id to be checked
    :return: True if the user exists, otherwise False
    """
    qs = User.objects.filter(id=uid)
    return len(qs) != 0
