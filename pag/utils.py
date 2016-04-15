import functools
import os
import subprocess as sp
import sys

import click
import yaml


CONF_FILE = os.path.expanduser('~/.config/pag')


def run(cmd, echo=True, graceful=True):
    click.echo('  $ ' + " ".join(cmd))
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
    output, _ = proc.communicate()
    output = stdout.decode('utf-8')
    if echo:
        click.echo(output)
    if not graceful and proc.returncode != 0:
        sys.exit(1)
    return proc.returncode, output


def die(msg, code=1):
    click.echo(msg)
    sys.exit(code)


def in_git_repo():
    # TODO -- would be smarter to look "up" the tree, too.
    if not os.path.exists('.git') or not os.path.isdir('.git'):
        return None
    return os.getcwd().split('/')[-1]


def assert_local_repo(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not in_git_repo():
            die("fatal:  Not a git repository")
        return func(*args, **kwargs)
    return inner


def repo_url(name, ssh=False, git=False, domain='pagure.io'):
    if ssh:
        prefix = 'ssh://git@'
    else:
        prefix = 'https://'

    if '/' in name:
        suffix = 'forks/%s' % name
    else:
        suffix = '%s' % name

    if git:
        suffix = suffix + '.git'

    return prefix + domain + '/' + suffix


def create_config():
    username = raw_input("FAS username:  ")
    conf = dict(
        username=username,
    )

    with open(CONF_FILE, 'wb') as f:
        f.write(yaml.dump(conf).encode('utf-8'))

    click.echo("Wrote %r" % CONF_FILE)


def load_config():
    with open(CONF_FILE, 'rb') as f:
        return yaml.load(f.read().decode('utf-8'))

def load_or_create_config():
    if not os.path.exists(CONF_FILE):
        click.echo("%r not found.  Creating..." % CONF_FILE)
        create_config()
    return load_config()


def configured(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        config = load_or_create_config()
        return func(config, *args, **kwargs)
    return inner
