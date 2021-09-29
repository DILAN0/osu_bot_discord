
import requests
from os import getenv
from pprint import pprint

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'


def get_token():
    data = {
        'client_id': '10055',
        'client_secret': 'S1q6W4jw3LQF5plV5bnxtSTXL9x3wy705BSL76hy',
        'grant_type': 'client_credentials',
        'scope': 'public'
    }

    response = requests.post(TOKEN_URL, data=data)

    return response.json().get('access_token')


def main():
    token = get_token()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'mode': 'osu',
        'limit': 5
    }

    response = requests.get(f'{API_URL}/users/9329543', params=params, headers=headers)

    beatmapset_data = response.json()

    pprint(beatmapset_data, indent=2)


if __name__ == '__main__':
    main()



