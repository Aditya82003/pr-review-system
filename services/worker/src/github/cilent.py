import httpx

API = "https://api.github.com"

def _headers(token:str):
    return {
        "Authorization":f"Bearer {token}",
        "Accept":"application/vnd.github+json"
    }
    
    
def create_check_run(repo_fullname,headsha,token):
    res = httpx.post(
        f"{API}/repos/{repo_fullname}/check-runs",
        headers=_headers(token),
        json={
            "name":"AI PR REVIEW",
            "head_sha":headsha,
            "status":"in_progress"
        }
    )
    res.raise_for_status() #agar response main error status hai toh error throw kar deta
    return str(res.json()["id"])