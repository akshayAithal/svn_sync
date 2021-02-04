import os
#directory_path = os.path.normpath(r"D:\removeAnyTime")
directory_path = os.path.normpath(r"/data/_repositories/")
mirror_machine  = "10.196.2.67"
mirror_path = "/data/repo/"
for item in os.listdir(directory_path):
    local_repo_path = os.path.join(directory_path, item)
    if(os.path.isfile(local_repo_path)):
        continue
    print("Path {}".format(local_repo_path))
    from subprocess import Popen
    if (os.path.isdir(os.path.join(local_repo_path,"hooks"))):
        if not os.path.exists(os.path.join(local_repo_path,"hooks","post-commit.tmpl")):
            continue
        print("Writing the post commit hook scripts {}".format(os.path.join(local_repo_path,"hooks","post-commit")))
        post_commit_path = os.path.join(local_repo_path,"hooks","post-commit")
        with open(post_commit_path,"w+") as hook_script:
            hook_script.write("#!/bin/sh\n")
            hook_script.write("REPOS=\"$1\"\n")
            hook_script.write("REV=\"$2\"\n")
            hook_script.write("TXN_NAME=\"$3\"\n")
            hook_script.write("ping -q -c1 -W1 {} && ssh -t svnsync@{} \"cd /home/svnsync; svn_sync_tool sync_for_post_commit $REPOS {}\"\n".format(mirror_machine,mirror_machine,mirror_path))
            hook_script.write("exit 0\n")    
            if os.name == 'posix':
                process = Popen(["chmod","+x",os.path.join(local_repo_path,"hooks","post-commit")]) 
                print("Command -> chmod +x {}".format(os.path.join(local_repo_path,"hooks","post-commit")))
                process.wait()