import jwt
import httpx
import time
from config import settings

def _read_private_key()->str:
    with open(settings.github_app_private_key_path,"r") as f:
        return f.read()

def _make_app_jwt():
    now = int(time.time())
    payload={
        "iat":now-60,
        "exp":now + (9*60),
        "iss":settings.github_app_id
    }
    return jwt.encode(payload,_read_private_key(),algorithm="RS256")

def get_installation_token_sync(installation_id:int)->str:
    app_jwt=_make_app_jwt()
    resp=httpx.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization":f"Bearer {app_jwt}",
            "Accept":"application/vnd.github+json"
        }
    )
    resp.raise_for_status()
    return resp.json()["token"]