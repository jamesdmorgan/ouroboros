from future.standard_library import install_aliases
install_aliases()

from collections import namedtuple
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin, urlparse
import uuid


JSON="application/json"
ATOM="application/vnd.eventstore.atom+json"
EVENTS="application/vnd.eventstore.events+json"
STREAMDESC="application/vnd.eventstore.streamdesc+json"

User = namedtuple(
    'user', [
        'login_name', 'full_name', 'disabled', 'links', 'groups'])

def as_set(val):
    return set() if not val else set(val)

class Acl:

    def __init__(self, read=None, write=None, delete=None, metadata_read=None, metadata_write=None):
        self.read = read
        self.write = write
        self.delete = delete
        self.metadata_read = metadata_read
        self.metadata_write = metadata_write


    def __eq__(self, other):
        return (self.as_set(self.read) == self.as_set(other.read)
            and self.as_set(self.write) == self.as_set(other.write)
            and self.as_set(self.delete) == self.as_set(other.delete)
            and self.as_set(self.metadata_read) == self.as_set(other.metadata_read)
            and self.as_set(self.metadata_write) == self.as_set(other.metadata_write))

    def __ne__(self, other):
        return not self.__eq__(other)


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


    def merge(self, a, b):
        if not a:
            return b
        if not b:
            return a
        result = set(a)
        result.update(set(b))
        return sorted(list(result))

    def strip(self, a, b):
        if not a:
            return b
        if not b:
            return a
        result = set(a)
        result.difference_update(set(b))
        return sorted(list(result))


    def as_set(self, val):
        return set(val) if val else set()

    def grant(self, other):
        return Acl(
            read = self.merge(self.read, other.read),
            write = self.merge(self.write, other.write),
            delete = self.merge(self.delete, other.delete),
            metadata_read = self.merge(self.metadata_read, other.metadata_read),
            metadata_write = self.merge(self.metadata_write, other.metadata_write)
        )

    def revoke(self, other):
        return Acl(
            read = self.strip(self.read, other.read),
            write = self.strip(self.write, other.write),
            delete = self.strip(self.delete, other.delete),
            metadata_read = self.strip(self.metadata_read, other.metadata_read),
            metadata_write = self.strip(self.metadata_write, other.metadata_write)
        )

    def is_empty(self):
        return not any(self.to_dict())

    @staticmethod
    def empty():
        return Acl()

    @staticmethod
    def deny_all():
        return Acl(read=[], write=[], delete=[], metadata_read=[], metadata_write=[])


DEFAULT_DEFAULT_ACL=(Acl(
                        read=["$all"],
                        write=["$all"],
                        delete=["$all"],
                        metadata_read=["$all"],
                        metadata_write=["$all"]),
                    Acl(
                        read=["$admins"],
                        write=["$admins"],
                        delete=["$admins"],
                        metadata_read=["$admins"],
                        metadata_write=["$admins"]
                    ))

class NotFoundException(Exception):
    pass


class AuthenticationException(Exception):
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

    def setpassword(self, username, password):
        user = self.get(username)
        self.client.post(user.links['reset-password'], {
            'newPassword': password
        }, JSON)


class StreamManager:

    def __init__(self, client):
        self.client = client

    def create(self, name, acl=Acl.empty(), eventid=None):
        metadata = {
            "eventId": str(eventid or uuid.uuid4()),
            "eventType": "settings"
        }
        if not acl.is_empty():
            metadata["data"] = {"$acl": acl.to_dict()}

        self.client.post("/streams/"+name+"/metadata", [metadata], EVENTS)

    def get_acl(self, name):
        response = self.client.get('/streams/'+name+'/metadata', JSON)
        data = response.json()
        if "$acl" in data:
            return Acl.from_dict(data["$acl"])
        return None


    def set_acl(self, name, acl, eventid=None):
        current = self.get_acl(name)
        event = {
            "eventId": str(eventid or uuid.uuid4()),
            "eventType": "settings",
            "data": {
                "$acl": acl.to_dict()
            }
        }
        self.client.post("/streams/"+name+"/metadata", [event], EVENTS)

    def delete(self, name):
        self.client.delete('/streams/'+name)

    def grant(self, stream, acl=Acl.empty(), eventid=None):
        current = self.get_acl(stream) or Acl.empty()
        new = current.grant(acl)
        self.set_acl(stream, new, eventid)

    def revoke(self, stream, acl=Acl.empty(), eventid=None):
        current = self.get_acl(stream) or Acl.empty()
        new = current.revoke(acl)
        self.set_acl(stream, new, eventid)


class DefaultAclManager:

    def __init__(self, client, is_system=False):
        self.client = client
        self.is_system = is_system

    def get_acl(self):
        try:
            response = self.client.get('/streams/$settings', EVENTS)
        except NotFoundException:
            return DEFAULT_DEFAULT_ACL

        latest = response.json()["entries"][0]
        acl = self.client.get(latest["id"], JSON).json()
        return(Acl.from_dict(acl["$userStreamAcl"]),
               Acl.from_dict(acl["$systemStreamAcl"]))

    def set_acl(self, acl, eventid=None):
        user,system = self.get_acl()
        if self.is_system:
            system = acl.update(Acl.deny_all())
        else:
            user = acl.update(Acl.deny_all())

        event = {
            "eventId": str(eventid or uuid.uuid4()),
            "eventType": "settings",
            "data": {
                "$userStreamAcl": user.to_dict(),
                "$systemStreamAcl": system.to_dict()
            }
        }
        self.client.post("/streams/$settings", [event], EVENTS)

    def grant(self, acl=Acl.empty(), eventid=None):
        user, system = self.get_acl()
        current = system if self.is_system else user
        new = current.grant(acl)
        self.set_acl(new, eventid)

    def revoke(self, acl, eventid=None):
        user, system = self.get_acl()
        current = system if self.is_system else user
        new = current.revoke(acl)
        self.set_acl(new, eventid)


class SubscriptionManager:

    def __init__(self, client):
        self.client = client

    def get(self, group_name, stream):
        response = self.client.get('/subscriptions/{}/{}/info'.format(stream, group_name), JSON)

        data = response.json()

        return data

    def create(self,
            group_name,
            stream,
            resolve_link_tos=False,
            start_from=0,
            message_timeout=10000,
            extra_statistics=False,
            max_retry=10,
            live_buffer_size=500,
            buffer_size=500,
            read_batch_size=20,
            checkpoint_after=1000,
            min_checkpoint_count=10,
            max_checkpoint_count=500,
            max_subscriber_count=10,
            named_consumer_strategy="RoundRobin"):

        SubscriptionManager._validate_consumer_strategy(named_consumer_strategy)

        body = {
            "checkpoints": checkpoint_after,
            "resolveLinktos": resolve_link_tos,
            "startFrom": start_from,
            "messageTimeoutMilliseconds": message_timeout,
            "extraStatistics": extra_statistics,
            "maxRetryCount":max_retry,
            "liveBufferSize": live_buffer_size,
            "bufferSize": buffer_size,
            "readBatchSize": read_batch_size,
            "checkPointAfterMilliseconds": checkpoint_after,
            "minCheckPointCount": min_checkpoint_count,
            "maxCheckPointCount": max_checkpoint_count,
            "maxSubscriberCount": max_subscriber_count,
            "namedConsumerStrategy": named_consumer_strategy}


        response = self.client.put(
                "/subscriptions/{}/{}".format(stream, group_name),
                body,
                JSON)

        return body

    def delete(self, group_name, stream):
        self.client.delete('/subscriptions/{}/{}'.format(stream, group_name))

    def update(self,
            group_name,
            stream,
            resolve_link_tos=None,
            start_from=None,
            message_timeout=None,
            extra_statistics=None,
            max_retry=None,
            live_buffer_size=None,
            buffer_size=None,
            read_batch_size=None,
            checkpoint_after=None,
            min_checkpoint_count=None,
            max_checkpoint_count=None,
            max_subscriber_count=None,
            named_consumer_strategy=None):

        current = self.get(group_name, stream)['config']

        strategy = current['namedConsumerStrategy'] if named_consumer_strategy is None else named_consumer_strategy
        SubscriptionManager._validate_consumer_strategy(strategy)

        body = {
            "checkpoints": current['checkPointAfterMilliseconds'] if checkpoint_after is None else checkpoint_after,
            "resolveLinktos": current['resolveLinktos'] if resolve_link_tos is None else resolve_link_tos,
            "startFrom": current['startFrom'] if start_from is None else start_from,
            "messageTimeoutMilliseconds": current['messageTimeoutMilliseconds'] if message_timeout is None else message_timeout,
            "extraStatistics": current['extraStatistics'] if extra_statistics is None else extra_statistics,
            "maxRetryCount": current['maxRetryCount'] if max_retry is None else max_retry,
            "liveBufferSize": current['liveBufferSize'] if live_buffer_size is None else live_buffer_size,
            "bufferSize": current['bufferSize'] if buffer_size is None else buffer_size,
            "readBatchSize": current['readBatchSize'] if read_batch_size is None else read_batch_size,
            "checkPointAfterMilliseconds": current['checkPointAfterMilliseconds'] if checkpoint_after is None else checkpoint_after,
            "minCheckPointCount": current['minCheckPointCount'] if min_checkpoint_count is None else min_checkpoint_count,
            "maxCheckPointCount": current['maxCheckPointCount'] if max_checkpoint_count is None else max_checkpoint_count,
            "maxSubscriberCount": current['maxSubscriberCount'] if max_subscriber_count is None else max_subscriber_count,
            "namedConsumerStrategy": strategy}


        response = self.client.post(
                "/subscriptions/{}/{}".format(stream, group_name),
                body,
                JSON)

        return {
                "old_config": current,
                "new_config": body}

    def _validate_consumer_strategy(strategy):
        VALID_CONSUMER_STRATEGIES = [
            "RoundRobin",
            "DispatchToSingle",
            "Pinned"]

        if strategy not in VALID_CONSUMER_STRATEGIES:
            raise ValueError("Named Startegy {} is not recognised".format(strategy))


class Client:

    def __init__(self, host, port, username, password, no_ssl=False):
        scheme = "http" if no_ssl else "https"
        self.base_uri = "{0}://{1}:{2}".format(scheme, host, port)
        self.users = UserManager(self)
        self.streams = StreamManager(self)
        self.user_acl = DefaultAclManager(self)
        self.system_acl = DefaultAclManager(self, is_system=True)
        self.subscriptions = SubscriptionManager(self)
        self.username = username
        self.password = password

    def __handle(self, r):
        if r.status_code == 401:
            raise AuthenticationException()
        if r.status_code == 404:
            raise NotFoundException()
        r.raise_for_status()
        return r

    def get_uri(self, path):
        return urljoin(self.base_uri, str(path))

    def post(self, path, body, content_type):
        response = requests.post(
            self.get_uri(path),
            json=body,
            auth=HTTPBasicAuth(
                self.username,
                self.password),
            headers={
                'Content-Type': content_type})
        return self.__handle(response)

    def get(self, path, content_type):
        return self.__handle(requests.get(self.get_uri(path)+'?embed=tryharder',
                            auth=HTTPBasicAuth(self.username, self.password),
                            headers={
                                'Accept': content_type
                                }))

    def put(self, path, body, content_type):
        return self.__handle(requests.put(self.get_uri(path),
                            auth=HTTPBasicAuth(self.username, self.password),
                            json=body,
                            headers={
                                'Content-Type': content_type
                            }))

    def delete(self, path):
        return self.__handle(requests.delete(self.get_uri(path),
            auth=HTTPBasicAuth(
                self.username,
                self.password)))

    @staticmethod
    def from_uri(uri, username, password):
        parts = urlparse(uri)
        return Client(parts.hostname, parts.port, username, password,
                    no_ssl=(parts.scheme == "http"))
