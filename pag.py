#!/usr/bin/env python

import functools
import os
import sys

import click
import requests
import yaml


CONF_FILE = os.path.expanduser('~/.config/pag')

def run(cmd):
    click.echo('  $ ' + cmd)
    return os.system(cmd)


def die(msg, code=1):
    click.echo(msg)
    sys.exit(code)


def assert_local_repo(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not os.path.exists('.git') and not os.path.isdir('.git'):
            die("fatal:  Not a git repository")
        return func(*args, **kwargs)
    return inner


def repo_url(name, ssh=False, git=False, domain='pagure.io'):
    if ssh:
        prefix = 'ssh://git@'
    else:
        prefix = 'https://'

    if '/' in name:
        suffix = 'fork/%s' % name
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

@click.group()
def pag():
    pass


@pag.command()
@click.argument('name')
@click.confirmation_option(prompt="Are you sure you want to create a new repo?")
@configured
def create(conf, name):
    click.echo('hey, %r' % name)
    click.echo("%r" % conf)


@pag.command()
@click.argument('name')
def clone(name):
    url = repo_url(name, ssh=True, git=True)
    run('git clone %s %s' % (url, name.split('/')[-1]))

@pag.group()
@assert_local_repo
def remote():
    pass

@remote.command()
@click.argument('name')
def add(name):
    url = repo_url(name)
    response = requests.head(url)
    if not bool(response):
        die("No such url %s, %r" % (url, response))

    url = repo_url(name, ssh=True, git=True)
    name = name.split('/')[0]
    return run('git remote add %s %s' % (name, url))


if __name__ == '__main__':
    pag()
