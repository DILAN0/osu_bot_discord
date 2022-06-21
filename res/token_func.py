import requests
from Token import client_s

TOKEN_URL = 'https://osu.ppy.sh/oauth/token'
API_URL = 'https://osu.ppy.sh/api/v2'

def get_token():
    data = {
        'client_id': '10055',
        'client_secret': client_s,
        'grant_type': 'client_credentials',
        'scope': 'public'
    }

    response = requests.post(TOKEN_URL, data=data)


    return response.json().get('access_token')

def response(id):
    token = get_token()
    id = id.split(' ', 1)[0]
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    params = {
        'mode': 'osu',  # https://osu.ppy.sh/docs/index.html #gamemode
        'limit': 5  # Maximum number of results
    }
    response = requests.get(f'{API_URL}/users/{id}', params=params, headers=headers)
    osu_assets = response.json()
    pp = osu_assets['statistics']['pp']
    id = osu_assets['id']
    avatar = osu_assets['avatar_url']
    return pp,id,avatar