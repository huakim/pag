# `pag`

[`pag`](https://pagure.io/pag) helps you win at [pagure.io](https://pagure.io) !

Intended to mimic the [hub](https://github.com/github/hub) and [cli](https://cli.github.com/) tools for [github.com](https://github.com).

## Usage

```bash
  $ pag --help
  Usage: pag [OPTIONS] COMMAND [ARGS]...

  Options:
    --help  Show this message and exit.

  Commands:
    clone         Clone an existing repo.
    create        Create a new repo.
    create-issue
    default
    fork
    pull-request  Open a new pull request.
    remote        Create remote for another fork.
    review        Check out a pull request locally.
    upload        Upload new file to releases.
```

> You can do `pag <COMMAND> --help` to see the command specific help.

## Commands

### Clone

Clone an existing repo by name without having to find or type out the URL:

```bash
  $ pag clone koji
  Cloning into 'koji'...
```

You can clone a fork:

```bash
  $ pag clone ralph/koji
  Cloning into 'koji'...
```

Clone a repo in anonymous:

```bash
  $ pag clone -a koji
```

### Create

`pag` provides a convenience command for creating new projects with description:

```bash
  $ pag create factory2 "Ostensibly better than factory version 1"
```

When runned in an existing local git repository, this command will also set up remotes.

### Create an Issue

Create an issue from the command line!

```bash
  $ pag create-issue --title "WIP: What about a new command" --description "Ideas for new commands" --private
```

### Fork

After you clone a repo, you can `fork` it on [pagure.io](https://pagure.io) and adjust your local `remote` settings:

```bash
  $ pag fork
```

### Pull Request

Create a pull request from the current branch to default upstream branch.

```bash
  $ pag pull-request
```

### Remote

If you want to add the `remotes` of other forks, that's easy too.  Just do it by username:

```bash
  $ cd koji/
  $ pag remote add ausil
  $ git remote -v
  ausil   ssh://git@pagure.io/forks/ausil/koji.git (fetch)
  origin  ssh://git@pagure.io/koji.git (fetch)
  $ git pull ausil master
```

### Review

Check out a pull request locally.

```bash
  $ pag review PR_ID
```

You can use this options:

- `--list` for list opened pull requests on the current repo.
- `--cleanup` for delete the corresponding branches (BE AWARE).
- `--open` to open currently reviewed pull request in the browser.

### Upload

Upload a new file to releases.

```bash
  $ pag upload TARBALL
```

## Perks

To enable bash completion, add the following to your `.bashrc`:

```bash
  eval "$(_PAG_COMPLETE=source pag)"
```

<!--
TODO:

- Add version output.
- Add copy&credits output.
- Add the --help for all commands & cite that in the help output.

-->

## Credits

Ralph Bean <rbean@redhat.com>
Lubomír Sedlář <lubomir.sedlar@gmail.com>
Haikel Guemar <hguemar@fedoraproject.org>
Tiago d'Almeida <tjamadeira@gmail.com>

[License](./LICENSE) GNU GPL 3.0 &copy; 2016-2022
