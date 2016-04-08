import click

from pag.app import app
from pag.utils import (
    configured,
)
from pag.client import client


@app.command()
@click.argument('name')
@click.confirmation_option(prompt="Are you sure you want to create a new repo?")
@configured
def create(conf, name):

    click.echo("Trying to create %r in pagure.io" % name)
    client.create(name, username=conf['username'])

    #url = repo_url(name, ssh=True, git=True)
    #name = name.split('/')[0]
    #return run('git remote add %s %s' % (name, url))
