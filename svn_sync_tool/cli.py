# -*- coding: utf-8 -*-

"""Console script for svn_sync_tool."""
import sys
import click

from svn_sync_tool.svn_sync_tool import initialize_svn_mirror, sync_all, check_all, write_all_post_commit, sync,check_all_and_sync, initialize_and_sync, sync_for_post_commit, write_all_post_commit_scripts, write_all_start_commit

@click.group()
def svn_sync_tool():
    """ Wrapper for multiple  clis
    """
    pass


@svn_sync_tool.command("initialize_and_sync")
@click.argument('input', type=click.Path(exists=True))
@click.option('--debug', is_flag=True)
def main(input, debug):
    """Initializes the svn sync tool"""
    initialize_svn_mirror(input,debug)
    return 0


@svn_sync_tool.command("sync")
@click.argument('repo')
@click.argument('input', type=click.Path(exists=True))
def main(repo,input):
    """Syncs the repositories"""
    sync(repo, input)
    return 0

@svn_sync_tool.command("sync_all")
@click.argument('input', type=click.Path(exists=True))
def main(input):
    """Syncs mutiple projects"""
    sync_all(input)
    return 0

@svn_sync_tool.command("write_post_commit")
@click.argument('input', type=click.Path(exists=True))
def main(input):
    """Writes post commit script for the main repo to sync"""
    write_all_post_commit(input)
    return 0


@svn_sync_tool.command("check_revisons")
@click.argument('host')
def main(host):
    """Console script for svn_sync_tool."""
    check_all(host)
    return 0

@svn_sync_tool.command("check_and_sync_all")
@click.argument('input', type=click.Path(exists=True))
@click.argument('host')
def main(host, input):
    """Console script for svn_sync_tool."""
    check_all_and_sync(host, input)
    return 0

if __name__ == "__main__":
    svn_sync_tool()  # pragma: no cover


@svn_sync_tool.command("initialize")
@click.argument('input', type=click.Path(exists=True))
@click.argument('repo')
def main(input, repo):
    """Console script for svn_sync_tool."""
    initialize_and_sync(input,repo)
    return 0

@svn_sync_tool.command("sync_for_post_commit")
@click.argument('repo')
@click.argument('input', type=click.Path(exists=True))
def main(repo,input):
    """Console script for svn_sync_tool."""
    sync_for_post_commit(repo, input)
    return 0

@svn_sync_tool.command("write_all_post_commit_scripts")
@click.argument('input', type=click.Path(exists=True))
@click.argument('host')
def main(input,host):
    """Console script for svn_sync_tool."""
    write_all_post_commit_scripts(host, input)
    return 0


@svn_sync_tool.command("write_pre_commit")
@click.argument('input', type=click.Path(exists=True))
def main(input):
    """Console script for svn_sync_tool."""
    write_all_start_commit(input)
    return 0