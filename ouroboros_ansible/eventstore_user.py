#!/usr/bin/python
#
DOCUMENTATION = """
---
module: eventstore_user
short_description: create, remove, and manage users in EventStore
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
    username:
        description: The login name of the user to manage
        required: true
    fullname:
        description: The fullname of the user, defaults to the username if not present
        required: false
    password:
        description: Sets the password of the user to this value. Required when
        creating a new user.
        required: false
    groups:
        required: false
        description: Optionally add the user to this set of groups. To remove all
        group memberships from a user, set this value to the empty list []
    state:
        choices: ["absent", "present"]
        required: true
        description: Controls whether the account should exist or not
"""

EXAMPLES = '''
# Add the user 'johnd' into the 'devs' group
- eventstore_user:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: changeit
    username: johnd
    password: john-is-a-bad-hacker
    fullname: John Doe
    groups:
        - devs
    state: present

# Remove the user 'johnd'
- eventstore_user:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: changeit
    username: johnd
    state: absent
'''


from future.standard_library import install_aliases
install_aliases()

from ouroboros.client import Client


def remove_user(client, module):
    user = module.params['username']
    if client.users.get(user):
        client.users.remove(user)
    module.exit_json(changed=True)


def update_user(client, module):
    user = module.params['username']
    password = module.params['password']
    user_state = None
    actions = {'pw_reset': False}
    changed = False

    if password:
        pwclient = build_client(module.params['http_uri'], user, password)
        try:
            user_state = pwclient.users.get(user)
        except AuthenticationException:
            actions['pw_reset'] = True

    if not user_state:
        try:
            user_state = client.users.get(user)
        except NotFoundException:
            pass

    if not user_state:
        create_user(client, module)

    if pw_reset:
        client.users.setpassword(user, password)
        changed = True

    current_groups = set(user_state.groups)
    desired_groups = set(module.params['groups'] or [])

    groups_to_add = list(desired_groups - current_groups)
    groups_to_remove = list(current_groups - desired_groups)

    if groups_to_add:
        client.users.addgroup(user, *groups_to_add)
        actions['groups_added'] = groups_to_add
        changed = True
    if groups_to_remove:
        client.users.removegroup(user, *groups_to_remove)
        actions['groups_removed'] = groups_to_remove
        changed = True

    module.exit_json(changed=changed, result=actions)


def main():
    module = AnsibleModule(argument_spec=dict(
        host_uri=dict(required=True, type='str'),
        admin_username=dict(required=True, type='str'),
        admin_password=dict(required=True, type='str'),
        username=dict(required=True, type='str'),
        state=dict(required=True, type='str', choices=['absent', 'present']),
        fullname=dict(required=False, default=None, type='str'),
        password=dict(required=False, default=None, type='str', no_log=True),
        groups=dict(required=False, default=None, type='list')))

    uri = module.params['host_uri']
    adminuser = module.params['admin_username']
    adminpass = module.params['admin_password']

    client = Client.from_uri(uri, adminuser, adminpass)
    state = module.params['state']

    if state == "absent":
        remove_user(client, module)
    else:
        update_user(client, module)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
