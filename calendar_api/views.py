from django.shortcuts import redirect
from django.urls import reverse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework.response import Response
from rest_framework.views import APIView


class GoogleCalendarInitView(APIView):
    def get(self, request):
        # Set up the OAuth 2.0 flow
        flow = Flow.from_client_secrets_file(
            'path/to/client_secrets.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        # Generate the authorization URL and redirect the user to it
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        # Exchange the authorization code for an access token
        flow = Flow.from_client_secrets_file(
            'path/to/client_secrets.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        flow.fetch_token(authorization_response=request.build_absolute_uri(),
                         )
        # Use the access token to fetch the user's calendar events
        try:
            credentials = Credentials.from_authorized_user_info(info=flow.credentials.to_json())
            service = build('calendar', 'v3', credentials=credentials)
            events_result = service.events().list(calendarId='primary', timeMin='2023-01-01T00:00:00Z', maxResults=10,
                                                  singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
            # Return the calendar events as a response
            return Response(events)
        except HttpError as error:
            # Handle any errors that may occur
            return Response({'error': str(error)})
