#!/usr/bin/python
#
DOCUMENTATION = """
---
module: eventstore_stream
short_description: create, remove, and manage streams in EventStore
description:
    -
options:
    host_uri:
        description: The fully qualified host for eventstore, eg. https://evenstore.local:2113
        required: true
    admin_username:
        description: The username to use when modifying users
        required: true
    admin_password:
        description: The password to use when modifying users
        required: true
    name:
        description: The name of the stream to manage
        required: true
    acl:
        description: The access control list to apply to the stream. Required when creating a new stream
        required: false
    state:
        choices: ["absent", "present"]
        required: true
        description: Controls whether the stream should exist or not
"""

EXAMPLES = '''
# Create a new stream with the default acl
- eventstore_stream:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: changeit
    name: my-stream
    state: present


# Remove a stream
- eventstore_stream:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: changeit
    name: my-stream
    state: absent

# Create a stream with a custom acl
- eventstore_stream:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: changeit
    name: my-stream
    state: present
    acl:
        read:
            - devs
            - ops
            - qa
        write:
            - ops
        delete:
            - ops
        metadata_read:
            - $all
        metadata_write:
            - ops
 '''

from future.standard_library import install_aliases
install_aliases()

from ouroboros.client import Client

def remove_stream(client, module):
    pass

def update_stream(client, module):
    pass

def main():
    module = AnsibleModule(argument_spec=dict(
        host_uri=dict(required=True, type='str'),
        admin_username=dict(required=True, type='str'),
        admin_password=dict(required=True, type='str'),
        state=dict(required=True, type='str', choices=['absent', 'present']),
        acl=dict(required=False, default=dict(), type='dict')))

    uri = module.params['host_uri']
    adminuser = module.params['admin_username']
    adminpass = module.params['admin_password']

    client = Client.from_uri(uri, adminuser, adminpass)
    state = module.params['state']

    if state == "absent":
        remove_stream(client, module)
    else:
        update_stream(client, module)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
