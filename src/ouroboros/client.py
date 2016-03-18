from collections import namedtuple
import requests
from requests.auth import HTTPBasicAuth
import pprint
from urllib.parse import urljoin
import uuid


JSON="application/json"
ATOM="application/vnd.eventstore.atom+json"
EVENTS="application/vnd.eventstore.events+json"
STREAMDESC="application/vnd.eventstore.streamdesc+json"

User = namedtuple(
    'user', [
        'login_name', 'full_name', 'disabled', 'links', 'groups'])


class Acl:

    def __init__(self, read=None, write=None, delete=None, metadata_read=None, metadata_write=None):
        self.read = read
        self.write = write
        self.delete = delete
        self.metadata_read = metadata_read
        self.metadata_write = metadata_write

    def to_dict(self):
        return {k:v for k,v in {
                "$r": self.read,
                "$w": self.write,
                "$d": self.delete,
                "$mr": self.metadata_read,
                "$mw": self.metadata_write
                }.items()
            if v is not None}

    @staticmethod
    def get_entry(v):
        if isinstance(v, str):
            return [v]
        return v

    @staticmethod
    def from_dict(data):
        return Acl(read = Acl.get_entry(data["$r"]),
                   write = Acl.get_entry(data["$w"]),
                   delete = Acl.get_entry(data["$d"]),
                   metadata_read = Acl.get_entry(data["$mr"]),
                   metadata_write = Acl.get_entry(data["$mw"]))

    def coalesce(self, first, snd):
        return first if first is not None else snd

    def update(self, other):
        return Acl(
            read = self.coalesce(self.read, other.read),
            write = self.coalesce(self.write, other.write),
            delete = self.coalesce(self.delete, other.delete),
            metadata_read = self.coalesce(self.metadata_read, other.metadata_read),
            metadata_write = self.coalesce(self.metadata_write, other.metadata_write)
        )

    def is_empty(self):
        return not any(self.to_dict())

    @staticmethod
    def empty():
        return Acl()


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

    def create(self, name, acl=Acl.empty(), eventid=None):
        metadata = {
            "eventId": str(eventid or uuid.uuid4()),
            "eventType": "$user-updated"
        }
        if not acl.is_empty():
            metadata["$acl"] = acl.to_dict()

        self.client.post("/streams/"+name+"/metadata", [metadata], EVENTS)

    def set_acl(self, name, acl, eventid=None):
        metadata = self.client.get('/streams/'+name+'/metadata', STREAMDESC)
        metadata = metadata.json()
        if "$acl" in metadata:
            current = Acl.from_dict(metadata["$acl"])
        else:
            current = Acl()

        event = {
            "eventId": str(eventid or uuid.uuid4()),
            "eventType": "$user-updated",
            "$acl": acl.update(current).to_dict()
        }
        self.client.post("/streams/"+name+"/metadata", [event], EVENTS)



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
