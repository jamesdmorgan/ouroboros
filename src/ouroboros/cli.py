import click
from ouroboros.client import Client


@click.group()
@click.option("--authuser", prompt=True)
@click.option("--authpassword", prompt=True, hide_input=True)
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=2113)
@click.option("--no-https", default=False)
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
    client = Client(ctx.obj['host'],
                    ctx.obj['port'],
                    ctx.obj['authuser'],
                    ctx.obj['authpassword'])
    client.users.create(username, password, fullname, group)


if __name__ == '__main__':
    ouro(obj={})
