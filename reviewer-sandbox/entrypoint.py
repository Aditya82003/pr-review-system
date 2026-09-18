import os
import subprocess
import sys
sys.path.append("/app")

WORKINGDIR = "/workspace/repo"
def clone_pr():
    repo = os.environ["REPO_FULL_NAME"]
    pr_number = os.environ["PR_NUMBER"]
    token = os.environ["GIT_CLONE_TOKEN"]
    url = f"https://x-access-token:{token}@github.com/{repo}.git"
    
    subprocess.run(["git","clone","--depth","50",url,WORKINGDIR],check=True)
    subprocess.run(["git","fetch","origin",f"pull/{pr_number}/head:pr-branch","--depth","50"],cwd=WORKINGDIR,check=True)
    subprocess.run(["git","checkout","pr-branch"],cwd=WORKINGDIR,check=True)
    
 
def main():
    callback_url = os.environ["ORCHESTRATOR_CALLBACK_URL"]
    job_id = os.environ["JOB_ID"]
    try:
        clone_pr()
        #todo
    except Exception as e:
        print(f"Error cloning PR: {e}")
    
if __name__ == "__main__":
    main()