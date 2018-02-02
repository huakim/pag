import click

from pag.app import app
from pag.utils import (
    repo_url,
    run,
)


@app.command()
@click.argument('name')
@click.option('--anonymous', '-a', is_flag=True)
def clone(name, anonymous):
    """
    Clone an existing repo. Use the '-a' option when you don't have commit
    access to the repository.
    """
    use_ssh = False if anonymous else True
    url = repo_url(name, ssh=use_ssh, git=True)
    run(['git', 'clone', url, name.split('/')[-1]])
