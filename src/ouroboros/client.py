from collections import namedtuple
import requests
from requests.auth import HTTPBasicAuth
import pprint
from urllib.parse import urljoin
import uuid


JSON="application/json"
ATOM="application/vnd.eventstore.atom+json"
EVENTS="application/vnd.eventstore.events+json"

User = namedtuple(
    'user', [
        'login_name', 'full_name', 'disabled', 'links', 'groups'])


class UserNotFoundException(Exception):
    pass


class UserManager:

    def __init__(self, client):
        self.client = client

    def create(self, username, password, fullname=None, groups=[]):
        self.client.post('/users/',
                         {
                             "loginName": username,
                             "password": password,
                             "fullName": fullname or username,
                             "groups": groups
                             }, JSON)

    def get(self, username):
        response = self.client.get('/users/'+username, JSON)
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
        response = self.client.delete(user.links['delete'])
        print(response)

    def addgroup(self, username, *args):
        user = self.get(username)
        groups = set(user.groups)
        groups.update(args)

        response = self.client.put(user.links['edit'], {
            "fullName": user.full_name,
            "groups": list(groups)
        }, JSON)

    def removegroup(self, username, *args):
        user = self.get(username)
        groups = set(user.groups)
        groups.difference_update(args)

        response = self.client.put(user.links['edit'], {
            "fullName": user.full_name,
            "groups": list(groups)
        }, JSON)

    def rename(self, username, full_name):
        user = self.get(username)
        response = self.client.put(user.links['edit'], {
            "fullName": full_name,
            "groups": user.groups
        }, JSON)


class StreamManager:

    def __init__(self, client):
        self.client = client

    def create(self, name, eventid=None):
        metadata = [{
            "eventId": str(eventid or uuid.uuid4()),
            "eventType": "$user-updated"
        }]
        self.client.post("/streams/"+name+"/metadata", metadata, EVENTS)


class Client:

    def __init__(self, host, port, username, password, no_ssl=False):
        scheme = "http" if no_ssl else "https"
        self.base_uri = "{0}://{1}:{2}".format(scheme, host, port)
        self.users = UserManager(self)
        self.streams = StreamManager(self)
        self.username = username
        self.password = password

    def get_uri(self, path):
        return urljoin(self.base_uri, path)

    def post(self, path, body, content_type):
        response = requests.post(
            self.get_uri(path),
            json=body,
            auth=HTTPBasicAuth(
                self.username,
                self.password),
            headers={
                'Content-Type': content_type})
        print(response)

    def get(self, path, content_type):
        return requests.get(self.get_uri(path)+'?embed=tryharder',
                            headers={
                                'Accept': content_type
                                })

    def put(self, path, body, content_type):
        return requests.put(self.get_uri(path),
                            auth=HTTPBasicAuth(self.username, self.password),
                            json=body,
                            headers={
                                'Content-Type': content_type
                            })

    def delete(self, path):
        return requests.delete(self.get_uri(path),
            auth=HTTPBasicAuth(
                self.username,
                self.password))
