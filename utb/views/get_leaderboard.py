from django.http import HttpResponse, JsonResponse

from utb import utils
from utb.models import User, Friendship


def handler(request):
    """
    Returns the global or friends only leaderboard
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                JsonResponse 200 containing the leaderboard if the request went through
    """
    is_token_valid, message = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(message, status=403)
    user_id = message

    requester = utils.get_user_by_id(user_id)
    if not requester:
        return HttpResponse("Missing user", status=404)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    leaderboard_type = object_json["type"]

    if leaderboard_type == "GLOBAL":
        user_position = None
        leaderboard = []
        for i, user in enumerate(sorted(list(User.objects.all()), key=lambda u: u.score(), reverse=True), 1):
            if user.id == user_id:
                user_position = i
            leaderboard.append({"name": user.name, "score": int(user.score())})
        data = {"user_position": user_position, "leaderboard": leaderboard}
        return JsonResponse(data, status=200)
    elif leaderboard_type == "FRIENDS":
        user_position = None
        leaderboard = []
        for i, user in enumerate(sorted(
                list(map(lambda friendship: friendship.friend, Friendship.objects.filter(user=requester))) + [
                    requester], key=lambda u: u.score(), reverse=True), 1):
            if user.id == user_id:
                user_position = i
            leaderboard.append({"name": user.name, "score": int(user.score())})
        data = {"user_position": user_position, "leaderboard": leaderboard}
        return JsonResponse(data, status=200)
    else:
        return HttpResponse("Wrong leaderboard type", status=400)
