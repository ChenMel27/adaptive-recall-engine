"""URL patterns for the recall app."""

from django.urls import path
from . import views

app_name = "recall"

urlpatterns = [
    # Home & setup
    path("", views.home, name="home"),
    path("start/", views.start_session, name="start_session"),

    # Mode 1: Brain Dump
    path("brain-dump/<int:attempt_id>/", views.brain_dump, name="brain_dump"),
    path("brain-dump/<int:attempt_id>/submit/", views.brain_dump_submit, name="brain_dump_submit"),

    # Mode 2: Notes Upload & Quiz
    path("notes/<int:attempt_id>/", views.notes_upload, name="notes_upload"),
    path("notes/<int:attempt_id>/submit/", views.notes_upload_submit, name="notes_upload_submit"),
    path("quiz/<int:attempt_id>/", views.quiz, name="quiz"),
    path("quiz/<int:attempt_id>/submit/", views.quiz_submit, name="quiz_submit"),

    # Session controls
    path("opt-out/<int:attempt_id>/", views.opt_out, name="opt_out"),
    path("summary/<int:attempt_id>/", views.summary, name="summary"),

    # Teacher dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
]
