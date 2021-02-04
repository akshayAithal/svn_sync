#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `svn_sync_tool` package."""

import os
import unittest
from click.testing import CliRunner

from svn_sync_tool.logger import logger
from svn_sync_tool.svn_sync_tool import get_all_the_svn_links, initialize_svn_mirror, get_repo_data, check_all, write_all_post_commit_scripts
def test_the_repo_browse():
    os.environ["SVN_REPO_DB_TEXT"] = r"C:\svn_repo\XT4210\apps\DevOps\subversion\svn_sync_tool\tests\svn_db.txt"
    repo_list = get_all_the_svn_links()
    assert len(repo_list)  == 271

def test_initialize():
    os.environ["SVN_REPO_DB_TEXT"] = r"C:\svn_repo\XT4210\apps\DevOps\subversion\svn_sync_tool\tests\db_two_values.txt"
    test_folder = r"C:\svn_repo\XT4210\apps\DevOps\subversion\svn_sync_tool\tests\Test_Folder"
    initialize_svn_mirror(test_folder)

#def test_multi_process():
#    check_multi_process()


def test_the_repo_browser_from_db():
    repo_list = get_repo_data()
    for i in repo_list:
        logger.debug(i)
    assert len(repo_list)  == 271


from svnlib.svnlib import get_info
def test_the_svn_info():
    repo_list = get_repo_data()
    info , err = get_info(repo_list[1],"svnuser","svnuser")
    logger.debug(info)

def test_check_all():
    host = "10.196.2.67"
    check_all(host)
    
def test_write_all_post_commit_scripts():
    host = "10.196.2.67"
    write_all_post_commit_scripts(host,r"C:\svn_repo\XT4210\apps\DevOps\subversion\svn_sync_tool")
    