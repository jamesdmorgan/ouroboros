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
- eventstore_default_acl:
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

from ouroboros.client import Client, Acl

def update_stream(client, module):
    user_current, system_current = client.user_acl.get_acl()
    user_param = module.params.get("user")
    system_param = module.params.get("system")
    result = {}
    changed = False
    if user_param is not None:
        user_acl = Acl(**user_param)
        if user_acl != user_current:
            result['user_acl'] = user_acl.to_dict()
            changed = True
            client.user_acl.set_acl(user_acl)

    if system_param is not None:
        system_acl = Acl(**system_param)
        if system_acl != system_current:
            result['system_acl'] = system_acl.to_dict()
            changed = True
            client.system_acl.set_acl(system_acl)


    module.exit_json(changed=changed, result=result)


def main():
    module = AnsibleModule(argument_spec=dict(
        host_uri=dict(required=True, type='str'),
        admin_username=dict(required=True, type='str'),
        admin_password=dict(required=True, type='str'),
        system=dict(required=False, type='dict'),
        user=dict(required=False, type='dict'),
        ))

    uri = module.params['host_uri']
    adminuser = module.params['admin_username']
    adminpass = module.params['admin_password']

    client = Client.from_uri(uri, adminuser, adminpass)

    update_stream(client, module)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
