import os
import json
import googleapiclient
from googleapiclient.discovery import build
import pickle
import pygsheets
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from simple_youtube_api.Channel import Channel


def get_config(settings_path="config.json"):
    with open(settings_path, mode="r") as json_file:
        settings = json.load(json_file)
    json_file.close()
    return settings


def get_table(config, sheet_name):
    gc = pygsheets.authorize(service_file=config["service_file_path"])
    sh = gc.open_by_key(config["table_link"])
    data = sh.worksheet_by_title(sheet_name).get_as_df()
    return data


def read_table(config, sheet_name):
    gc = pygsheets.authorize(service_file=config["service_file_path"])
    sh = gc.open_by_key(config["table_link"])
    data = sh.worksheet_by_title(sheet_name)
    return data


def make_chanel():
    # token.pickle stores the user's credentials from previously successful logins
    credentials = None
    if os.path.exists('secret/token.pickle'):
        print('Loading Credentials From File...')
        with open('secret/token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret\client_secrets.json',
                scopes=[
                    "https://www.googleapis.com/auth/youtube.upload",
                    "https://www.googleapis.com/auth/youtube.force-ssl",    
                    "https://www.googleapis.com/auth/youtube",
                    "https://www.googleapis.com/auth/youtubepartner"
                ]
            )
            flow.run_local_server(port=8080,
                                  authorization_prompt_message='')
            # flow.run_local_server(port=8080, prompt='consent',
            #                       authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('secret/token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)
    
    youtube = build("youtube", "v3", credentials=credentials)
    channel = Channel()
    channel.channel = youtube
    return channel
