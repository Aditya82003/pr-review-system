import hashlib
import hmac
import json

import redis
from fastapi import FastAPI,Request,HTTPException,status

from config.config import setting

app = FastAPI()
redis = redis.from_url(setting.redis_url)

REVELANT_ACTIONS = ["opened","closed"]

def verify_signature(body,signature_header:str | None):
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid signature header")
    
    expected = "sha256=" + hmac.new(setting.encode(),body,hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected,signature_header):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid signature")


@app.post('/webhookk/github')
async def github_webhook(request:Request):
    body = request.body()
    #it verify the header it my calculate header is match then it verify the signature
    verify_signature(body,request.headers.get("X-Hub-Signature-256"))
    
    event_type = request.headers.get("X-GitHub-Event")
    #it convert json body into dict
    payload = json.loads(body)
    
    if event_type != "pull_request":
        return {"status":"ignored","reason":"not a pull request"}
    if payload.get("action") not in REVELANT_ACTIONS:
        return {"status":"ignored","reason":"not an action we care about"}
    
    job ={
        "repo_full_name": payload["repository"]["full_name"],
        "pr_number": payload["number"],
        "head_sha": payload["pull_request"]["head"]["sha"],
        "installation_id": payload["installation"]["id"],
    }
    
    redis.lpush("job",json.dumps(job))
    
    return {"status":"queued","pr":job["pr_number"]}

@app.get("/health")
def health():
    return {"status":"ok"}