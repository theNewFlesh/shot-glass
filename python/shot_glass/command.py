import subprocess

import click
import lunchbox.theme as lbc
# ------------------------------------------------------------------------------

'''
Command line interface to shot-glass library
'''

click.Context.formatter_class = lbc.ThemeFormatter


@click.group()
def main():
    pass


@main.command()
def bash_completion():
    '''
    {white}BASH completion code to be written to a _shot-glass completion
    file.{clear}
    '''
    cmd = '_SHOT_GLASS_COMPLETE=bash_source shot-glass'
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.wait()
    click.echo(result.stdout.read())


@main.command()
def zsh_completion():
    '''
    {white}ZSH completion code to be written to a _shot-glass completion
    file.{clear}
    '''
    cmd = '_SHOT_GLASS_COMPLETE=zsh_source shot-glass'
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.wait()
    click.echo(result.stdout.read())


if __name__ == '__main__':
    main()
