import click
from ouroboros.client import Client, Acl


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
@click.argument("stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def set_acl(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    client.streams.set_acl(stream, Acl(read, write, delete, metadata_read, metadata_write))


@ouro.command("grant")
@click.argument("stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def grant(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    client.streams.grant(stream, Acl(read, write, delete, metadata_read, metadata_write))

@ouro.command("revoke")
@click.argument("stream")
@click.option("--read", "-r", multiple=True)
@click.option("--write", "-w", multiple=True)
@click.option("--delete", "-d", multiple=True)
@click.option("--metadata-read", "-mr", multiple=True)
@click.option("--metadata-write", "-mw", multiple=True)
@click.pass_context
def revoke(ctx, stream, read, write, delete, metadata_read, metadata_write):
    client = make_client(ctx)
    client.streams.revoke(stream, Acl(read, write, delete, metadata_read, metadata_write))






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


def main():
    ouro(obj={})

if __name__ == '__main__':
    main()
