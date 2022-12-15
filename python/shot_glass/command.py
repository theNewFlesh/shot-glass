import subprocess

import click
# ------------------------------------------------------------------------------

'''
Command line interface to shot-glass library
'''


@click.group()
def main():
    pass


@main.command()
def bash_completion():
    '''
        BASH completion code to be written to a _shotglass completion file.
    '''
    cmd = '_SHOTGLASS_COMPLETE=bash_source shot-glass'
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.wait()
    click.echo(result.stdout.read())


@main.command()
def zsh_completion():
    '''
        ZSH completion code to be written to a _shotglass completion file.
    '''
    cmd = '_SHOTGLASS_COMPLETE=zsh_source shot-glass'
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.wait()
    click.echo(result.stdout.read())


if __name__ == '__main__':
    main()
