from google.oauth2 import id_token
from google.auth.transport import requests
import re
import json

# regex to check the email correctness
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
    except AttributeError or ValueError as error:
        return False, str(error)

