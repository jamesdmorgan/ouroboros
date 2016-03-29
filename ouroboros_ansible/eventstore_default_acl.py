#!/usr/bin/python
#
DOCUMENTATION = """
---
module: eventstore_default_acl
short_description: Manage the default ACLs in eventstire
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
    user:
        description: The access control list for user-created streams
        required: false
    system:
        description: The access control list for system streams
        required: false
"""

EXAMPLES = '''
# Modify the default acl for user-created streams
- eventstore_stream:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: changeit
    user:
        read:
            - ops
            - services
            - devs
            - qa
        write:
            - ops
            - services
        delete:
            - ops
        metadata_read:
            - ops
            - services
            - qa
            - devs
        metadata_write:
            - ops
 '''

from future.standard_library import install_aliases
install_aliases()

from ouroboros.client import Client, NotFoundException

def update_stream(client, module):
    name = module.params.get('name')
    acl = Acl.empty()
    if "user" in module.params:
        user_acl = Acl(**module.params.get('user'))
        result['acl'] = acl.to_dict()

    try:
        client.streams.get_acl(name)
        if acl.is_empty():
            module.exit_json(changed=False)
        client.streams.set_acl(name, acl)
        result['action'] = 'update'
    except NotFoundException:
        client.streams.create(name, acl)
        result['action'] = 'create'

    module.exit_json(changed=True, result=result)

def main():
    module = AnsibleModule(argument_spec=dict(
        host_uri=dict(required=True, type='str'),
        admin_username=dict(required=True, type='str'),
        admin_password=dict(required=True, type='str'),
        system=dict(required=False, type='dict'),
        user=dict(required=False, type='dict'),
        name=dict(required=True, type='str'),
        ))

    uri = module.params['host_uri']
    adminuser = module.params['admin_username']
    adminpass = module.params['admin_password']

    client = Client.from_uri(uri, adminuser, adminpass)

    if state == "absent":
        remove_stream(client, module)
    else:
        update_stream(client, module)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
