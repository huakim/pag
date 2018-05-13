import getpass
import sys

import click

from pag.app import app
from pag.utils import (
    configured,
    assert_local_repo,
    in_git_repo,
    get_default_upstream_branch,
    get_current_local_branch,
    get_tracking_branch,
    get_remote_url,
    repo_url,
    run,
    die,
)
from pag.client import client

HEADER = "Pull request title goes here."
MARKER = "# All lines below this marker are ignored."


def split_input(branch, default_repo):
    tokens = branch.split(':')
    if len(tokens) > 2:
        die("%r is a malformed repo:branch expression." % branch)
    elif len(tokens) == 1:
        repo, branch = default_repo, tokens[0]
    elif len(tokens) == 2:
        repo, branch = tokens
        repo = repo + '/' + default_repo
    else:
        raise RuntimeError('Should not be possible to get here...')
    return repo, branch


def guess_repo_name(default_repo, current_branch, username):
    """Given a name of the main repo, current branch and a user name, try to
    guess repo name where the branch is pushed. This is either the main repo,
    or a fork. In order for this to work, the branch must be set as remote
    tracking.

    Returns name of the remote repo and name of the branch on the remote.
    """
    tracking = get_tracking_branch()
    if not tracking:
        return default_repo, current_branch
    remote, branch = tracking

    remote_url = get_remote_url(remote)
    for r in (default_repo, '%s/%s' % (username, default_repo)):
        if remote_url == repo_url(r, ssh=True, git=True):
            return r, branch

    return default_repo, current_branch


@app.command('pull-request')
@assert_local_repo
@click.option('-b', '--base', help='Branch to merge the changes in')
@click.option('-h', '--head')
@configured
def pullrequest(conf, base, head):
    """
    Open a new pull request. Default behaviour is to open pull request from
    current branch to default upstream branch (usually 'master' or 'develop').

    The '--head' option can be used to specify other branch than the current
    one. Note that the name in the remote repo is needed here. You can open a
    pull request from a fork using 'YOUR_USERNAME:BRANCH_NAME' as argument to
    '--head'. Alternatively you can push the branch with `-u` to make it track
    the remote branch. In such case pag will automatically know to open the PR
    from your fork.
    """

    name = in_git_repo()
    username = conf['username']

    if base is None:
        try:
            base = get_default_upstream_branch()
        except Exception:
            click.echo("Failed to find default upstream branch for %r" % name)
            click.echo("Please specify a base branch explicitly.")
            sys.exit(1)
    else:
        name, base = split_input(base, name)

    if head is None:
        local_head = get_current_local_branch()
        name, head = guess_repo_name(name, head, username)
    else:
        name, head = split_input(head, name)
        local_head = head

    if '/' in name:
        name = 'fork/' + name

    cmd = ['git', 'log', '{base}..{head}'.format(base=base, head=local_head)]
    _, log = run(cmd, echo=False)

    def modify(line):
        if not line:
            return line
        if line[0].isspace():
            return line.strip()
        return '# ' + line

    log = '\n'.join([modify(line) for line in log.split('\n')])
    edited = click.edit(
        "\n\n".join([HEADER, MARKER, log]),
        env=dict(VIMINIT='set filetype="gitcommit"'),
    )
    if not edited.strip():
        click.echo("Aborting due to empty pull request message.")
        sys.exit(1)
    title, comment = edited.split('\n', 1)
    if not title:
        click.echo("Aborting due to empty pull request message.")
        sys.exit(1)
    comment = comment.split(MARKER)[0]
    comment = comment.strip()

    if not client.is_logged_in:
        password = getpass.getpass("FAS password for %r" % username)
        client.login(username=username, password=password)
    url = client.submit_pull_request(name, base, head, title, comment)
    click.echo(url)
