from django.http import HttpResponse, JsonResponse

from utb import utils
from utb.models import User, Friendship
from utb.utils import user_exists


def handler(request):
    """
    Returns the global or friends only leaderboard
    :param request: the HTTP request
    :return:    HttpResponse 403 if the verification token is invalid
                HttpResponse 404 if the object is invalid
                JsonResponse 200 containing the leaderboard if the request went through
    """
    is_token_valid, error_msg = utils.check_google_token(request)
    if not is_token_valid:
        return HttpResponse(error_msg, status=403)

    is_object_present, object_json = utils.get_object(request)
    if not is_object_present:
        return HttpResponse(object_json["error"], status=404)

    leaderboard_type, uid = object_json["type"], object_json["uid"]
    if not user_exists(uid):
        return HttpResponse("Invalid user", status=404)

    if leaderboard_type == "GLOBAL":
        data = {"leaderboard":
                    [{"name": user.name, "score": int(user.score())}
                     for user in sorted(list(User.objects.all()), key=lambda user: user.score(), reverse=True)]}
        return JsonResponse(data, status=200)
    elif leaderboard_type == "FRIENDS":
        user = User.objects.get(id=uid)
        data = {"leaderboard":
                    [{"name": user.name, "score": int(user.score())} for user in
                     sorted(list(map(lambda friendship: friendship.friend, Friendship.objects.filter(user=user))) + [user],
                            key=lambda user: user.score(), reverse=True)]}
        return JsonResponse(data, status=200)
    else:
        return HttpResponse("Wrong leaderboard type", status=400)
