import base64
import functions_framework
# ========================================

import os
import math
import pytz
import getpass
import io
import pickle
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import List

import jquantsapi
import numpy as np
#%load_ext cudf.pandas
import pandas as pd
from matplotlib import pyplot as plt
# from backtest import Backtest
from dateutil import tz
from requests import HTTPError
from xgboost.sklearn import XGBRegressor

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from oauth2client.service_account import ServiceAccountCredentials


# pandas の表示制限を調整します
pd.set_option("display.max_rows", 1000)
pd.set_option("display.max_columns", 1000)
pd.set_option("display.width", 2000)

JQ_EMAIL = os.getenv('email')
JQ_PASSWORD = os.getenv('password')


def check_refresh_token(refresh_token):
    # リフレッシュトークンを使用できるか検証します。
    test_cli = jquantsapi.Client(refresh_token=refresh_token)
    try:
        id_token = test_cli.get_id_token()
        if len(id_token) > 0:
            print("refresh_tokenは正常です。次の手順に進んでください。")
    except HTTPError:
        print("refresh_tokenを使用できません。再度値を確認してください。")
        

def test():
    credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_info, 
        scopes=['https://www.googleapis.com/auth/drive', 
                'https://www.googleapis.com/auth/drive.file', 
                'https://www.googleapis.com/auth/drive.readOnly']
    )
    res = credentials.get_access_token()




# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    #refresh_token = get_refresh_token(JQ_EMAIL, JQ_PASSWORD)
    #check_refresh_token(refresh_token)
    test()
    print(JQ_EMAIL)
    print(base64.b64decode(cloud_event.data["message"]["data"]))

