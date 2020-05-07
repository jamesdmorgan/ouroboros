#!/usr/bin/python
#
DOCUMENTATION = """
---
module: eventstore_subscription
short_description: create, remove, and manage subscriptions in EventStore
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
    group_name:
        description: Name of the subscription group to manage
        required: true
    stream:
        description: Name of the stream this is a subscription to
        required: true
    resolve_link_tos:
        description: Tells the subscription to resolve link events.
        required: false
    start_from:
        description: Start the subscription from the position-of the event in the stream.
        required: false
    message_timeout:
        description: Sets the timeout for a client before the message will be retried (in milliseconds).
        required: false
    extra_statistics:
        description: Tells the backend to measure timings on the clients so statistics will contain histograms of them.
        required: false
    max_retry:
        description: Sets the number of times a message should be retried before considered a bad message.
        required: false
    live_buffer_size:
        description: The size of the live buffer (in memory) before resorting to paging.
        required: false
    buffer_size:
        description: The number of messages that should be buffered when in paging mode.
        required: false
    read_batch_size: 
        description: The size of the read batch when in paging mode.
    checkout_after:
        descriptions: The amount of time the system should try to checkpoint after (in milliseconds).
        required: false
    min_checkpoint_count:
        description: The minimum number of messages to write a checkpoint for.
        required: false
    max_checkpoint_count:
        description: The maximum number of messages not checkpointed before forcing a checkpoint.
        required: false
    max_subscriber_count:
        description: Sets the maximum number of allowed TCP subscribers.
        required: false
    named_consumer_strategy:
        description: RoundRobin/DispatchToSingle/Pinned
        required: false
    state:
        choices: ["absent", "present"]
        required: true
        description: Controls whether the subscription should exist or not
"""

EXAMPLES = '''
# Add the subscription 'test-sub' to stream 'events'
- eventstore_subscription:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: somepassword
    group_name: test-sub
    stream: events
    state: present

# Remove the subscription 'test-sub' from 'events' stream
- eventstore_subscription:
    host_uri: http://localhost:2113
    admin_username: admin
    admin_password: somepassword
    group_name: test-sub
    stream: events
    state: absent
'''


from future.standard_library import install_aliases
install_aliases()

from ouroboros.client import Client, NotFoundException, AuthenticationException


def remove_subscription(client, module):
    group_name = module.params['group_name']
    stream = module.params['stream']
    try:
        client.subscriptions.get(group_name, stream)
        client.subscriptions.delete(group_name, stream)
        module.exit_json(changed=True)
    except NotFoundException:
        module.exit_json(changed=False)


def get_subscription_args(module):
    args = {}

    for arg in module.params:
        if module.params[arg] is not None and arg not in ['host_uri', 'admin_username', 'admin_password', 'state']:
            args[arg] = module.params[arg]

    return args

def create_subscription(client, module):
    args = get_subscription_args(module)

    config = client.subscriptions.create(**args)

    module.exit_json(changed=True, result={
        "actions": ["create"],
        "subscription": {
            "group_name": args['group_name'],
            "stream": args['stream'],
            "config": config
        }
    })

def update_subscription(client, module):

    group_name = module.params['group_name']
    stream = module.params['stream']
    try:
        sub = client.subscriptions.get(group_name, stream)
    except NotFoundException:
        create_subscription(client, module)
        return

    args = get_subscription_args(module)

    diff = compare_configs(sub['config'], args)

    if diff == {}:
        module.exit_json(changed=False, result={
            "actions": ["none"],
            "subscription": {
                "group_name": args['group_name'],
                "stream": args['stream'],
                "config": sub['config']
            }
        })

    config = client.subscriptions.update(**args)

    module.exit_json(changed=True, result={
        "actions": ["update"],
        "subscription": {
            "group_name": args['group_name'],
            "stream": args['stream'],
            "config": config['new_config'],
            "config_diff": diff
        }
    })

def compare_configs(current_config, new_config):

    mapping = {
        "buffer_size": "bufferSize",
        "checkpoint_after": "checkPointAfterMilliseconds",
        "extra_statistics": "extraStatistics",
        "live_buffer_size": "liveBufferSize",
        "max_checkpoint_count": "maxCheckPointCount",
        "max_retry": "maxRetryCount",
        "max_subscriber_count": "maxSubscriberCount",
        "message_timeout": "messageTimeoutMilliseconds",
        "min_checkpoint_count": "minCheckPointCount",
        "named_consumer_strategy": "namedConsumerStrategy",
        "read_batch_size": "readBatchSize",
        "resolve_link_tos": "resolveLinktos",
        "start_from": "startFrom"}

    diff = {}

    for key in new_config:
        if key in ["group_name", "stream"]:
            continue

        if current_config[mapping[key]] != new_config[key]:
            diff[key] = "{} => {}".format(current_config[mapping[key]], new_config[key])

    return diff

def main():
    module = AnsibleModule(argument_spec=dict(
        host_uri=dict(required=True, type='str'),
        admin_username=dict(required=True, type='str'),
        admin_password=dict(required=True, type='str', no_log=True),
        group_name=dict(required=True, type='str'),
        stream=dict(required=True, type='str'),
        resolve_link_tos=dict(required=False, type='bool', default=None),
        start_from=dict(required=False, type='int', default=None),
        message_timeout=dict(required=False, type='int', default=None),
        extra_statistics=dict(required=False, type='bool', default=None),
        max_retry=dict(required=False, type='int', default=None),
        live_buffer_size=dict(required=False, type='int', default=None),
        buffer_size=dict(required=False, type='int', default=None),
        read_batch_size=dict(required=False, type='int', default=None),
        checkpoint_after=dict(required=False, type='int', default=None),
        min_checkpoint_count=dict(required=False, type='int', default=None),
        max_checkpoint_count=dict(required=False, type='int', default=None),
        max_subscriber_count=dict(required=False, type='int', default=None),
        named_consumer_strategy=dict(required=False, type='str', choices=['RoundRobin', 'DispatchToSingle', 'Pinned'], default=None),
        state=dict(required=True, type='str', choices=['absent', 'present'])))

    uri = module.params['host_uri']
    adminuser = module.params['admin_username']
    adminpass = module.params['admin_password']

    client = Client.from_uri(uri, adminuser, adminpass)
    state = module.params['state']

    if state == "absent":
        remove_subscription(client, module)
    else:
        update_subscription(client, module)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
