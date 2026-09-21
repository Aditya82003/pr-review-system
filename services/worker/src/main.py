import threading
import json
import redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import SessionLocal,engine
from db.models.review_job import ReviewJob,JobStatus
from db.base import Base
from config import settings
from docker_launcher.docker_launcher import launch_sandbox_job

Base.metadata.create_all(bind=engine)
 
queue = redis.from_url(settings.redis_url,socket_timeout=None)


def process_job(job_payload:dict):
    from github.auth import get_installation_token_sync
    from github.cilent import create_check_run
    db = SessionLocal()
    try:
        token = get_installation_token_sync(
            job_payload["installation_id"]
        )

        check_run_id = create_check_run(
            job_payload["repo_full_name"],
            job_payload["head_sha"],
            token,
        )

        job = ReviewJob(
            repo_full_name=job_payload["repo_full_name"],
            pr_number=job_payload["pr_number"],
            head_sha=job_payload["head_sha"],
            installation_id=job_payload["installation_id"],
            status=JobStatus.RUNNING,
            check_run_id=check_run_id,
        )

        db.add(job)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
    
    # ab yaha muje is job ko sandbox main dalna hai todo
    launch_sandbox_job(job,token)
    print("Job has been processed to the container",flush=True)

def _worker_loop():
    while True:
        try:
            print("Woker started and waiting for job ", flush=True)
            _,raw = queue.brpop("job")

            print("Received job:", raw,flush=True)

            process_job(json.loads(raw))

        except redis.exceptions.TimeoutError as e:
            print(f"Redis timeout: {e}")
            continue

        except Exception as e:
            print(f"Worker error: {e}")
            continue
        
        

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Starting server",flush=True)
    
    worker_thread = threading.Thread(
        target=_worker_loop,
        daemon=True
    )
    worker_thread.start()
    print("Server started",flush=True)
    yield
    print("Shutting down server",flush=True)
    
    
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}