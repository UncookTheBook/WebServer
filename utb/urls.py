from django.urls import path
from . import views

urlpatterns = [
    path('add_user/<str:id>/<str:name>/<str:surname>/<str:email>', views.add_user, name="add_user")
]