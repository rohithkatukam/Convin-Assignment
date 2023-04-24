# views.py
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from rest_framework.views import APIView
from rest_framework.response import Response

class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CALENDAR_CLIENT_SECRETS_FILE,
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
            redirect_uri=request.build_absolute_uri(reverse('calendar_redirect')),
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
        )
        request.session['google_calendar_state'] = state
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('google_calendar_state', None)
        if state is None or state != request.GET.get('state'):
            return Response({'error': 'Invalid state parameter'})
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CALENDAR_CLIENT_SECRETS_FILE,
            scopes=settings.GOOGLE_CALENDAR_SCOPES,
            redirect_uri=request.build_absolute_uri(reverse('calendar_redirect')),
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        return Response({'events': events})
