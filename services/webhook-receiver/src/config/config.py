from pydantic import BaseModel
class setting(BaseModel):
    github_app_id:str="asdfg"
    github_app_private_key_path:str=""
    github_webhook_secret:str="mySecretKey"
    
    redis_url:str="redis://redis:6379/0"
    
    class Config:
        env_file = ".env"
    
settings = setting()