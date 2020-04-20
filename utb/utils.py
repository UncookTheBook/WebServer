import re

# regex to check the email correctness
MAIL_REGEX = '"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


def check_email(email):
    """
    Checks that the input email is a valid email
    :param email: the input email
    :return: True if the email is valid, otherwise false
    """
    return email and re.search(MAIL_REGEX, email)
