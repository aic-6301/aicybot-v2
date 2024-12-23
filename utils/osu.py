import requests
from datetime import datetime, timedelta

import os

class tokens():
    Access_token = None
    Expirts_time = None


def get_access_token(client_id: str, client_secret: str):
    token_url = "https://osu.ppy.sh/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public identify"
    }

    response = requests.post(token_url, data=data)
    token_response = response.json()
    access_token = token_response["access_token"]
    expires_in = token_response["expires_in"]

    tokens.Expirts_time = datetime.now() + timedelta(seconds=expires_in)
    tokens.Access_token = access_token
    return access_token, tokens.Expirts_time

def get_refresh_token(client_id, client_secret):
   current_time = datetime.now()
   expirts_time = tokens.Expirts_time
   if current_time > expirts_time:
       print("期限を超えているため、トークンを更新します")
       token_url = "https://osu.ppy.sh/oauth/token"
       data = {
           "client_id": client_id,
           "client_secret": client_secret,
           "grant_type": "client_credentials",
           "scope": "public identify"
       }
   
       response = requests.post(token_url, data=data)
       token_response = response.json()
       access_token = token_response["access_token"]
       expires_in = token_response["expires_in"]
   
       expirts_time = datetime.now() + timedelta(seconds=expires_in)
       return access_token, expirts_time 
   else:
       print("期限内のため、処理を継続します")
       return tokens.Access_token, tokens.Expirts_time
   
def make_api_request(endpoint, params=None):
    access_token, expires_time = get_refresh_token(os.getenv('OSU_TOKEN'), os.getenv('OSU_SECRET_TOKEN'))
    headers = {"Authorization": f"Bearer {access_token}", 'Accept-Language': 'ja'}
    tokens.Access_token = access_token
    if params is None:
        params = {}
    full_url = f"https://osu.ppy.sh/api/v2/{endpoint}"
    if params:
        full_url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    response = requests.get(full_url, headers=headers)
    return response

def get_user(user_id: any):
    response = make_api_request(f"users/{user_id}")
    return response.json()