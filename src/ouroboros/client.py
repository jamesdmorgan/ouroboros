from collections import namedtuple
import requests
import pprint

User = namedtuple(
    'user', [
        'login_name', 'full_name', 'disabled', 'links', 'groups'])


class UserNotFoundException(Exception):
    pass

class UserManager:

    def __init__(self, client):
        self.client = client

    def create(self, username, password, fullname=None, groups=[]):
        self.client.post('/$user-'+username,
                         {
                             "loginName": username,
                             "password": password,
                             "fullName": fullname or username,
                             "groups": groups
                             })

    def get(self, username):
        response = self.client.get_json('/users/'+username)
        if response.status_code == 404:
            raise UserNotFoundException()
        data = response.json()['data']
        return User(login_name=data['loginName'],
                    full_name=data['fullName'],
                    disabled=data['disabled'],
                    groups=data['groups'],
                    links={
                        l['rel']: l['href'] for l in data['links']
                    })

    def delete(self, username):
        user = self.get(username)
        requests.delete(user.links['delete'])


class Client:

    def __init__(self, host, port):
        self.base_uri = "http://{0}:{1}".format(host, port)
        self.users = UserManager(self)

    def get_uri(self, path):
        return self.base_uri+path

    def post(self, path, body):
        requests.post(self.get_uri(path), json=body, headers={
            'Content-Type': 'application/vnd.eventstore.atom+json'
        })

    def get(self, path):
        return requests.get(self.get_uri(path)+'?embed=tryharder',
                            headers={
                                'Accept': 'application/vnd.eventstore.atom+json'
                                })

    def get_json(self, path):
        return requests.get(self.get_uri(path)+'?embed=tryharder',
                            headers={
                                'Content-Type': 'application/json'
                                })

