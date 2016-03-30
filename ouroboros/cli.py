import click
from ouroboros.client import Client, Acl

DEFAULT_SYSTEM_ACL = "__OUROBOROS__DEFAULT_SYSTEM_ACL"
DEFAULT_USER_ACL = "__OUROBOROS__DEFAULT_USER_ACL"

def make_client(ctx):
    return Client(ctx.obj['host'],
                    ctx.obj['port'],
                    ctx.obj['authuser'],
                    ctx.obj['authpassword'],
                    ctx.obj['no_ssl']
                  )


@click.group()
@click.option("--authuser", prompt=True, envvar='ES_ADMIN_USER')
@click.option("--authpassword", prompt=True, hide_input=True, envvar='ES_ADMIN_PASS')
@click.option("--host", default="127.0.0.1", envvar='ES_HOST')
@click.option("--port", default=2113, envvar='ES_PORT')
@click.option("--no-ssl", default=False, envvar='ES_NO_SSL', is_flag=True)
@click.pass_context
def ouro(ctx, authuser, authpassword, host, port, no_ssl):
    ctx.obj['authuser'] = authuser
    ctx.obj['authpassword'] = authpassword
    ctx.obj['host'] = host
    ctx.obj['port'] = port
    ctx.obj['no_ssl'] = no_ssl

@ouro.command()
@click.argument("username")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--fullname", "-n", default='')
@click.option("--group", "-g", multiple=True)
@click.pass_context
def useradd(ctx, username, password, fullname, group):
    client = make_client(ctx)
    client.users.create(username, password, fullname, group)

@ouro.command()
@click.argument("username")
@click.pass_context
def userdel(ctx, username):
    client = make_client(ctx)
    client.users.delete(username)

@ouro.command()
@click.argument("username")
@click.argument("group", nargs=-1)
@click.pass_context
def groupadd(ctx, group, username):
    client = make_client(ctx)
    client.users.addgroup(username, *group)

@ouro.command()
@click.argument("username")
@click.argument("fullname")
@click.pass_context
def rename(ctx, username, fullname):
    client = make_client(ctx)
    client.users.rename(username, fullname)

@ouro.command()
@click.argument("username")
@click.argument("group", nargs=-1)
@click.pass_context
def groupdel(ctx, group, username):
    client = make_client(ctx)
    client.users.removegroup(username, *group)


@ouro.command()
@click.argument("stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def streamadd(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    client.streams.create(stream, Acl(read, write, delete, metadata_read, metadata_write))


@ouro.command("set-acl")
@click.option("--system", "stream", flag_value=DEFAULT_SYSTEM_ACL)
@click.option("--user", "stream", flag_value=DEFAULT_USER_ACL)
@click.option("--stream", "stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def set_acl(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    acl = Acl(read, write, delete, metadata_read, metadata_write)
    if stream == DEFAULT_SYSTEM_ACL:
        client.system_acl.set_acl(acl)
    elif stream == DEFAULT_USER_ACL:
        client.user_acl.set_acl(acl)
    else:
        client.streams.set_acl(stream, )


@ouro.command("revoke")
@click.option("--system", "stream", flag_value=DEFAULT_SYSTEM_ACL)
@click.option("--user", "stream", flag_value=DEFAULT_USER_ACL)
@click.option("--stream", "stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def revoke(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    acl = Acl(read, write, delete, metadata_read, metadata_write)
    if stream == DEFAULT_SYSTEM_ACL:
        client.system_acl.revoke(acl)
    elif stream == DEFAULT_USER_ACL:
        client.user_acl.revoke(acl)
    else:
        client.streams.revoke(stream, acl)



@ouro.command("grant")
@click.option("--system", "stream", flag_value=DEFAULT_SYSTEM_ACL)
@click.option("--user", "stream", flag_value=DEFAULT_USER_ACL)
@click.option("--stream", "stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def grant(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    acl = Acl(read, write, delete, metadata_read, metadata_write)
    if stream == DEFAULT_SYSTEM_ACL:
        client.system_acl.grant(acl)
    elif stream == DEFAULT_USER_ACL:
        client.user_acl.grant(acl)
    else:
        client.streams.grant(stream, acl)


@ouro.command("usermod")
@click.argument("username")
@click.option("--group", "-g", multiple=True)
@click.option("--delete-group", "-d", multiple=True)
@click.option("--password")
@click.pass_context
def update_user(ctx, username, group, delete_group, password):
    client = make_client(ctx)
    if group:
        client.users.addgroup(username, *group)
    if delete_group:
        client.users.removegroup(username, *delete_group)
    if password:
        client.users.setpassword(username, password)


@ouro.command("get-acl")
@click.option("--system", "stream", flag_value=DEFAULT_SYSTEM_ACL)
@click.option("--user", "stream", flag_value=DEFAULT_USER_ACL)
@click.option("--stream", "stream")
@click.pass_context
def get_acl(ctx, stream):
    client = make_client(ctx)
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    if stream == DEFAULT_SYSTEM_ACL:
        _, acl = client.system_acl.get_acl()
    elif stream == DEFAULT_USER_ACL:
        acl, _ = client.system_acl.get_acl()
    else:
        acl = client.streams.get_acl(stream)

    pp.pprint(acl.to_dict())


def main():
    ouro(obj={})

if __name__ == '__main__':
    main()
