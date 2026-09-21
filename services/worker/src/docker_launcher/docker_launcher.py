import docker

docker_client = docker.from_env()
from config import settings

def launch_sandbox_job(job,clone_token:str)->None:
    docker_client.containers.run(
        settings.sandbox_image,
        detach=True,
        auto_remove=True,
        name=f"review-{job.id}",
        environment={
            "JOB_ID":job.id,
            "REPO_FULL_NAME":job.repo_full_name,
            "PR_NUMBER":str(job.pr_number),
            "HEAD_SHA":job.head_sha,
            "GIT_CLONE_TOKEN":clone_token,
            "ANTHROPY_API_KEY":settings.antropy_api_key,
            "REVIEW_MODEL":settings.review_model,
            "WORKER_CALLBACK_URL":settings.worker_callback_url   
        },
        mem_limit="1g",
        nano_cpus=1_000_000_000,
        cap_drop=["ALL"],
        security_opt=["no-new-privileges"],
        network_disabled=True
    )