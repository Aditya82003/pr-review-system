import threading
import json
import redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import SessionLocal,engine
from db.models.review_job import ReviewJob,JobStatus

queue = redis.from_url("redis://redis:6379/0")


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
    
def _worker_loop():
    while True:
        _,raw=queue.brpop("review-jobs")
        print(raw)
        try:
            process_job(json.loads(raw))
        except Exception as e:
            print(f"Error processing job: {e}")
        
        

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Starting server")
    
    worker_thread = threading.Thread(
        target=_worker_loop,
        deaemon=True
    )
    worker_thread.start()
    print("Server started")
    yield
    print("Shutting down server")
    
    
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}