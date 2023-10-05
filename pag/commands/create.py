import getpass

import click

from pag.app import app
from pag.utils import (
    configured,
    in_git_repo,
    repo_url,
    run,
)
from pag.client import client

@app.command()
@click.option('--namespace', help='Project Namespace')
@click.option('--default_branch', help='Default Branch')
@click.option('--url', help='URL')
@click.option('--avatar_email', help='Avatar email')
@click.option('--mirrored_from', help='Mirror from URL')
@click.option('--create_readme', help='Create a README file automatically', is_flag=True)
@click.argument('name')
@click.argument('description')
@click.confirmation_option(prompt="Are you sure you want to create a new repo?")
@configured
def create(conf, name, description, **kwargs):
    """
    Create a new repo. When run in an existing local git repository, this
    command will also set up remotes.
    """
    if kwargs['create_readme']:
        kwargs['create_readme'] = 'y'
    else:
        del kwargs['create_readme']
        
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    click.echo("Trying to create %r in pagure.io" % name)
    if not client.is_logged_in:
        password = getpass.getpass("FAS password for %r" % conf['username'])
        client.login(username=conf['username'], password=password)
    url = client.create(name, description, **kwargs)
    click.echo("Created %s" % url)

    #local_repo = in_git_repo()
    #if local_repo is None or local_repo != name:
    #    url = repo_url(name, ssh=True, git=True)
    #    run(['git', 'clone', url, name.split('/')[-1]])
    #else:
    #    url = repo_url(name, ssh=True, git=True)
    #    name = name.split('/')[0]
    #    run(['git', 'remote', 'add', name, url])
    #    run(['git', 'remote', 'add', 'origin', url])
