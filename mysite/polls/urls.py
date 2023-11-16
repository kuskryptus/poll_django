from django.urls import path

from . import views
from .views import VoteApiView, PollDetailView

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:poll_id>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:poll_id>/vote/", views.vote, name="vote"),
    path("api/<int:poll_id>/vote/", VoteApiView.as_view(), name="vote_api"),
    path("api/<int:pk>/results/", PollDetailView.as_view(), name="poll_data"),
]
