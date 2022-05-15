# pag

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

## Commands

### Clone

The `clone` command can be used to clone a repo by name without having to find or type out the URL:

```bash
  $ pag clone koji
  Cloning into 'koji'...
```

Or you can clone a fork:

```bash
  $ pag clone ralph/koji
  Cloning into 'koji'...
```

### Create

`pag` provides a convenience command for creating new projects::

```bash
  $ pag create factory2 "Ostensibly better than factory version 1"
```

### Fork

After you clone a repo, you can `fork` it on [pagure.io](https://pagure.io) and adjust your local `remote` settings:

```bash
  $ pag fork
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

## Perks

To enable bash completion, add the following to your `.bashrc`:

```bash
  eval "$(_PAG_COMPLETE=source pag)"
```

<!--
TODO:

- Add version output.
- Add copy&credits output.
- Add the other commands help and examples.
- Add the --help for all commands & cite that in the help output.

-->

## Credits

*Ralph Bean* as `ralph`  
*Tiago d'Almeida* as `tjapro`  
&copy; 2022
