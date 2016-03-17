import click
from ouroboros.client import Client


def make_client(ctx):
    return Client(ctx.obj['host'],
                    ctx.obj['port'],
                    ctx.obj['authuser'],
                    ctx.obj['authpassword'])


@click.group()
@click.option("--authuser", prompt=True, envvar='ES_ADMIN_USER')
@click.option("--authpassword", prompt=True, hide_input=True, envvar='ES_ADMIN_PASS')
@click.option("--host", default="127.0.0.1", envvar='ES_HOST')
@click.option("--port", default=2113, envvar='ES_PORT')
@click.option("--no-https", default=False, envvar='ES_NO_SSL')
@click.pass_context
def ouro(ctx, authuser, authpassword, host, port, no_https):
    ctx.obj['authuser'] = authuser
    ctx.obj['authpassword'] = authpassword
    ctx.obj['host'] = host
    ctx.obj['port'] = port
    ctx.obj['ssl'] = not no_https

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


if __name__ == '__main__':
    ouro(obj={})
