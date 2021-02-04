# -*- coding: utf-8 -*-

"""Main module."""
import os 

from subprocess import Popen
import multiprocessing
from itertools import repeat

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from redmine_cli.redmine.base import Base
from redmine_cli.redmine.users import User
from redmine_cli.redmine.groups_users import GroupsUser
from redmine_cli.redmine.trackers import Tracker
from redmine_cli.redmine.enumerations import Enumeration
from redmine_cli.redmine.issues import Issue
from redmine_cli.redmine.projects import Project
from redmine_cli.redmine.time_entries import TimeEntry
from redmine_cli.redmine.members import Member
from redmine_cli.redmine.repositories import Repository
from redmine_cli.tools import construct_uri

from svn_sync_tool.logger import logger

from svnlib.svnlib import get_info

from gkn.logger import create_logger

def get_all_the_svn_links():
    """ currently reads the line from the db and get all
    the links 
    TODO : get it from the redmine database"""
    db_file = os.getenv('SVN_REPO_DB_TEXT')
    repos = []
    with open(db_file) as svn_db:
        repos = svn_db.readlines()
    new_repos = []
    for repo in repos:
        repo = repo.strip("\n").strip('"')
        repo = repo.replace("10.133.0.222","dllohsr222")
        if repo.count('\\') > 3:
            continue
        if repo.count('XT4210') > 1:
            continue
        new_repos.append(repo)
    logger.info(new_repos)
    return new_repos


def initialize_and_sync(repo, path):
    repo_name = repo.replace("svn://dllohsr222/","")
    local_repo_path = os.path.join(path, repo_name)
    if os.path.exists(local_repo_path):
        logger.info("{} already exist call sync command".format(local_repo_path))
        return
    logger.info("Creating the repo")
    process = Popen(["svnadmin","create",local_repo_path]) 
    logger.info("Command -> svnadmin create {}".format(local_repo_path))
    process.wait()
    write_pre_revorp_hook(local_repo_path, True)
    write_svn_serve_hook(local_repo_path, path)
    logger.info("Initializing svn sync")
    process = Popen(["svnsync","init","file://{}".format(local_repo_path), repo, 
    "--allow-non-empty","--username", "svnuser", "--password", "svnuser",
    "--no-auth-cache","--non-interactive"])
    logger.info("Command -> svnsync init file://{} {}".format(local_repo_path, repo))
    process.wait()
    logger.info("syncing....")
    process = Popen(["svnsync","sync","file://{}".format(local_repo_path),
    "--username", "svnuser", "--password", "svnuser",
    "--no-auth-cache","--non-interactive"])
    process.wait()
    logger.info("Command -> svnsync sync file://{}".format(local_repo_path))
    info , err = get_info(repo,"svnuser","svnuser")
    if info:
        uuid = info.get("Repository UUID")
        process = Popen(["svnadmin","setuuid",local_repo_path, str(uuid)])
        process.wait()
        logger.info("Setting {} UUID to -> {}".format(local_repo_path,uuid))
    else:
        logger.info(err)
    write_pre_revorp_hook(local_repo_path, False)
    

def write_pre_revorp_hook(local_repo_path, initial_flag = True):
    logger.info("Writing the pre hook scripts {}".format(os.path.join(local_repo_path,"hooks","pre-revprop-change")))
    with open(os.path.join(local_repo_path,"hooks","pre-revprop-change"),"w+") as hook_script:
        hook_script.write("#!/bin/sh\n")
        hook_script.write("USER=\"$3\"\n")
        if initial_flag:
            hook_script.write("if [ \"$USER\" = \"svnuser\" ]; then exit 0; fi\n")
        else:
            hook_script.write("if [ \"$USER\" = \"svnsync\" ]; then exit 0; fi\n")
        hook_script.write("echo \"Only the svnsync user can change revprops\" >&2\n")
        hook_script.write("exit 1\n")
    if os.name == 'posix':
        process = Popen(["chmod","+x",os.path.join(local_repo_path,"hooks","pre-revprop-change")]) 
        logger.info("Command -> chmod +x {}".format(os.path.join(local_repo_path,"hooks","pre-revprop-change")))
        process.wait()

def write_svn_serve_hook(local_repo_path, parent_dir):
    logger.info("Writing the svnserve scripts {}".format(os.path.join(local_repo_path,"conf","svnserve.conf")))
    with open(os.path.join(local_repo_path,"conf","svnserve.conf"),"w+") as hook_script:
        hook_script.write("[general]\n")
        hook_script.write("anon-access = none\n")
        hook_script.write("auth-access = write\n")
        hook_script.write("password-db = {}\n".format(os.path.join(parent_dir,"_global_conf","passwd")))
        hook_script.write("authz-db ={}\n".format(os.path.join(parent_dir,"_global_conf","authz")))


def initialize_svn_mirror(path , debug=True):
    repo_list = []
    if(debug):
        repo_list = get_all_the_svn_links()
    else:
        repo_list = get_repo_data()
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.starmap(initialize_and_sync, zip(repo_list, repeat(path)))
        

def get_repo_data():
    SERVER_IP = "10.133.0.77"
    PORT = 3306
    DB_NAME = "easyredmine"
    DB_TYPE = "mysql"
    USERNAME = "grafana"
    PASSWORD = "grafana"
    uri = construct_uri(SERVER_IP, PORT, DB_TYPE,
                        DB_NAME, USERNAME, PASSWORD)
    engine = create_engine(uri)
    logger.debug("Created engine")
    Base.metadata.create_all(engine, checkfirst=True)
    logger.debug("Mapped base metadata.")
    Session = sessionmaker(bind=engine)
    logger.debug("Created Session class bound to engine.")
    session = Session()
    logger.debug("Created session Object")
    repo_list_qeury = session.query(Repository)
    repo_list = []
    for repo in repo_list_qeury:
        url = repo.url
        url = url.strip("\n").strip('"')
        url = url.replace("10.133.0.222","dllohsr222")
        url = url.replace("dllohsr222.driveline.gkn.com","dllohsr222")
        if url.count('/') > 3:
            continue
        repo_list.append(url)
    session.close()
    return repo_list


def sync_repo(repo, path):
    repo_name = repo.replace("svn://dllohsr222/","")
    local_repo_path = os.path.join(path, repo_name)
    #write_pre_revorp_hook(local_repo_path, True)
    process = Popen(["svnsync","sync","file://{}".format(local_repo_path),
    "--username", "svnuser", "--password", "svnuser",
    "--no-auth-cache","--non-interactive","--disable-locking"])
    out, err = process.communicate()
    logger.info("Command -> svnsync sync file://{}".format(local_repo_path))
    #logger.info("Output {} , Error {}".format(out,err))
    #Hard coded for BAN mirror


def sync_all(path):
    repo_list = [] 
    repo_list = get_repo_data()
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.starmap(sync_repo, zip(repo_list, repeat(path)))

def create_post_commit_hook(repo, path):
    repo_name = repo.replace("svn://dllohsr222/","")
    local_repo_path = os.path.join(path, repo_name)
    
    


def write_post_commit_hook(local_repo_path, path = "/data/_repositories", mirror_path="root@10.196.2.67", env_path="/home/akshay.aithal/env/bin/svn_sync_tool"):
    """ One time thing to write the  post commit hook
    """
    logger.info("Writing the post commit hook scripts {}".format(os.path.join(local_repo_path,"hooks","post-commit")))
    if not (os.path.isdir(os.path.join(local_repo_path,"hooks"))):
        return
    with open(os.path.join(local_repo_path,"hooks","post-commit"),"w+") as hook_script:
        hook_script.write("#!/bin/sh\n")
        hook_script.write("REPOS=\"$1\"\n")
        hook_script.write("REV=\"$2\"\n")
        hook_script.write("TXN_NAME=\"$3\"\n")
        hook_script.write("ssh -t {} \"cd  /home/akshay.aithal/svn_workspace;{} sync_for_post_commit $REPOS {}\"\n".format(mirror_path,env_path,path))
        hook_script.write("exit 0\n")    
        if os.name == 'posix':
            process = Popen(["chmod","+x",os.path.join(local_repo_path,"hooks","post-commit")]) 
            logger.info("Command -> chmod +x {}".format(os.path.join(local_repo_path,"hooks","post-commit")))
            process.wait()


def check_all(host):
    repo_list = []
    repo_list = get_repo_data()
    report_file = open("repo_report.txt","w+")
    for repo in repo_list:
        logger.info("Checking {}...".format(repo))
        repo_name = repo.replace("svn://dllohsr222/","svn://{}/".format(host))
        info_repo , err = get_info(repo,"svnuser","svnuser")
        info_local , err = get_info(repo_name,"svnuser","svnuser")
        if info_local.get("Revision"):
            if info_repo.get("Revision") != info_local.get("Revision"):
                report_file.write("{} -> {} is not synced with {}  -> {}\n".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
                logger.info("{} -> {}  not matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
            else:
                logger.info("{} -> {}  is matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
        else:
            report_file.write("{} is not INITIALIZED PROPERLY!\n".format(repo_name))
            logger.info("{} is not INITIALIZED PROPERLY!\n".format(repo_name))


def check_all_and_sync(host, path):
    repo_list = []
    repo_list = get_repo_data()
    report_file = open("repo_report.txt","w+")
    for repo in repo_list:
        logger.info("Checking {}...".format(repo))
        repo_name = repo.replace("svn://dllohsr222/","svn://{}/".format(host))
        info_repo , err = get_info(repo,"svnuser","svnuser")
        info_local , err = get_info(repo_name,"svnuser","svnuser")
        if info_local.get("Revision"):
            if info_repo.get("Revision") != info_local.get("Revision"):
                sync_repo(repo,path)
                report_file.write("{} -> {} is not synced with {}  -> {}\n".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
                logger.info("{} -> {}  not matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
            else:
                logger.info("{} -> {}  is matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
        else:
            report_file.write("{} is not INITIALIZED PROPERLY!\n".format(repo_name))
            logger.info("{} is not INITIALIZED PROPERLY!\n".format(repo_name))
            initialize_and_sync(repo,path)

def get_repo_logger():
    repo_logger = create_logger("repo_report")
    import os
    import glob
    import logging
    import logging.handlers
    import time
    rotating_handler = repo_logger.handlers[1]
    # Check if log exists and should therefore be rolled
    needRoll = os.path.isfile("repo_report.log")
    # This is a stale log, so roll it
    if needRoll:    
        # Add timestamp
        repo_logger.debug('\n---------\nLog closed on %s.\n---------\n' % time.asctime())

        # Roll over on application start
        rotating_handler.doRollover()

    # Add timestamp
    repo_logger.debug('\n---------\nLog started on %s.\n---------\n' % time.asctime())
    return repo_logger

def check_all(host):
    repo_list = []
    repo_list = get_repo_data()
    repo_logger = get_repo_logger()
    for repo in repo_list:
        logger.info("Checking {}...".format(repo))
        repo_name = repo.replace("svn://dllohsr222/","svn://{}/".format(host))
        info_repo , err = get_info(repo,"svnuser","svnuser")
        info_local , err = get_info(repo_name,"svnuser","svnuser")
        if info_local.get("Revision"):
            if info_repo.get("Revision") != info_local.get("Revision"):
                repo_logger.warning("{} -> {} is not synced with {}  -> {}\n".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
                logger.info("{} -> {}  not matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
            else:
                repo_logger.info("{} -> {}  is matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
                logger.info("{} -> {}  is matching with {} -> {}".format(repo,info_repo.get("Revision"),repo_name,info_local.get("Revision")))
        else:
            if  info_local.get("Revision"):
                repo_logger.critical("{} is not INITIALIZED PROPERLY!, while {} is on {}\n".format(repo_name, repo , info_local.get("Revision") ))
                logger.info("{} is not INITIALIZED PROPERLY!\n".format(repo_name))
            else:
                repo_logger.critical("{} is not INITIALIZED PROPERLY!, while {} has same issues!!\n".format(repo_name, repo ))
                logger.info("{} is not INITIALIZED PROPERLY!\n".format(repo_name))


def write_all_post_commit(path):
    repo_list = []
    repo_list = get_repo_data()
    for repo in repo_list:
        repo_name = repo.replace("svn://dllohsr222/","")
        local_repo_path = os.path.join(path, repo_name)
        write_post_commit_hook(local_repo_path)


def sync(repo, input):
    logger.info(repo)
    logger.info(input)
    sync_repo(repo,input)


def write_all_post_commit_scripts(host, path):
    repo_list = []
    repo_list = get_repo_data()
    for repo in repo_list:
        logger.info("Checking {}...".format(repo))
        repo_name = repo.replace("svn://dllohsr222/","svn://{}/".format(host))
        info_repo , err = get_info(repo,"svnuser","svnuser")
        info_local , err = get_info(repo_name,"svnuser","svnuser")
        repo_name_2 = repo.replace("svn://dllohsr222/","")
        local_repo_path = os.path.join(path, repo_name_2)
        if info_local.get("Revision"):
            logger.info("Post commit script written for {}".format(repo))
            write_post_commit_hook(local_repo_path)
        else:
            logger.info("{} is not INITIALIZED PROPERLY!\n".format(repo_name))


def sync_for_post_commit(repo, input):
    repo = repo.replace("/srv/data/_repositories/","")
    sync_repo(repo,input)

def write_start_commit_hook(local_repo_path, initial_flag = True):
    logger.info("Writing the pre hook scripts {}".format(os.path.join(local_repo_path,"hooks","start-commit")))
    with open(os.path.join(local_repo_path,"hooks","start-commit"),"w+") as hook_script:
        hook_script.write("#!/bin/sh\n")
        hook_script.write("USER=\"$2\"\n")
        if initial_flag:
            hook_script.write("if [ \"$USER\" = \"svnuser\" ]; then exit 0; fi\n")
        else:
            hook_script.write("if [ \"$USER\" = \"svnsync\" ]; then exit 0; fi\n")
        hook_script.write("echo \"Only the svnsync user can commit\" >&2\n")
        hook_script.write("exit 1\n")
    if os.name == 'posix':
        process = Popen(["chmod","+x",os.path.join(local_repo_path,"hooks","start-commit")]) 
        logger.info("Command -> chmod +x {}".format(os.path.join(local_repo_path,"hooks","start-commit")))
        process.wait()

def write_all_start_commit(path):
    repo_list = []
    repo_list = get_repo_data()
    for repo in repo_list:
        repo_name = repo.replace("svn://dllohsr222/","")
        local_repo_path = os.path.join(path, repo_name)
        if os.path.exists(local_repo_path):
            write_start_commit_hook(local_repo_path)
            write_pre_revorp_hook(local_repo_path)