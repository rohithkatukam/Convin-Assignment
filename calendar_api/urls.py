# urls.py
from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

urlpatterns = [
    path('rest/v1/calendar/init/', GoogleCalendarInitView.as_view(), name='calendar_init'),
    path('rest/v1/calendar/redirect/', GoogleCalendarRedirectView.as_view(), name='calendar_redirect'),
]
