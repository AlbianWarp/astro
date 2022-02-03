import requests
import random

class AlbianWarpCoreClient(object):

    def __init__(self, url="http://127.0.0.1:8000"):
        self.session = requests.Session()
        self.auth_token = None
        self.id = None
        self.username = None
        self.url = url


    def authenticate(self, username, password):
        auth_test = self.session.post(
            f"{self.url}/auth",
            json={"username": username, "password": password},
        )
        if auth_test.status_code != 200:
            return False
        self.auth_token = auth_test.json()["token"]
        user = self.session.get(f"{self.url}/auth", headers={"token": self.auth_token}).json()
        print(user)
        self.id = user['id']
        self.username = user['username']
        return True

    def get_random_online_user(self):
        who_is_online = self.session.get(f"{self.url}/who_is_online").json()
        self.auth_token = auth_test.json()["token"]
        user = self.session.get(f"{self.url}/auth", headers={"token": self.auth_token}).json()
        print(user)
        self.id = user['id']
        self.username = user['username']
        return True



    @property
    def info(self):
        return {
            "auth_token": self.auth_token,
            "id": self.id,
            "username": self.username,
            "url": self.url,
        }